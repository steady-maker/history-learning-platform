# -*- coding: utf-8 -*-

"""
@Remark: 题库管理
"""
import datetime
import json
import random
import re
from collections import defaultdict

from django.db import transaction
from elastic_transport import TransportError
from elasticsearch import Elasticsearch, exceptions as es_exceptions
from rest_framework.decorators import action

from history_web_backend import settings
from question.constants import QuestionTypeEnum, AiTypeEnum, MAX_QUESTION_INFO_EXPIRE_TIME
from question.filter import QuestionFilter
from question.models import Question, UserAnswer, QuestionOption, QuestionAnswer, SubQuestion, \
    UserQuestionCollection, UserAnswerChatSession, QuestionChatSession
from question.serializer.question_ser import QuestionInfoSerializer
from question.serializer.user_answer_ser import UserQuestionListSerializer
from question.utils import get_question_with_options_and_answers, AIClient, get_question_answers, \
    generate_complete_system_prompt
from utils.ai_operation import AIOperationTracker
from utils.exception import BizException
from utils.jsonResponse import SuccessResponse
from utils.middleware import error_logger
from utils.redis import WEB_KEY_PREFIX, redis_conn
from utils.viewset import CustomModelViewSet

# 初始化 ES 客户端
es = Elasticsearch(settings.ELASTICSEARCH_URL)

class QuestionViewSet(CustomModelViewSet):
    """
    题库题目处理接口:
    """
    queryset = Question.objects.all().order_by('-create_time')
    serializer_class = QuestionInfoSerializer
    filterset_class = QuestionFilter

    def list(self, request, *args, **kwargs):
        try:
            keyword = request.GET.get("content", "")
            queryset = self.filter_queryset(self.get_queryset())

            # ========== ES 先检测是否可用 ==========
            if keyword.strip():
                # 先判断 ES 是否存活
                es_available = False
                try:
                    # 超短超时，防止卡死
                    es_available = es.ping(request_timeout=0.5)
                except (ConnectionError, TransportError, Exception):
                    es_available = False

                # 如果 ES 可用，才走 ES
                if es_available:
                    try:
                        es_response = es.search(
                            index="questions",
                            query={
                                "query_string": {
                                    "default_field": "content",
                                    "query": keyword.replace(" ", " AND ")
                                }
                            },
                            size=10000
                        )
                        match_ids = [int(hit["_source"]["id"]) for hit in es_response["hits"]["hits"]]
                        queryset = queryset.filter(id__in=match_ids)
                    except Exception as e:
                        queryset = queryset.filter(content__icontains=keyword)
                        error_logger.error(f"ES 查询异常：{e}")
                else:
                    # ES 完全不可用 → 直接降级
                    queryset = queryset.filter(content__icontains=keyword)
                    error_logger.error(f"ES 查询异常：降级为mysql搜索")

            page = self.paginate_queryset(queryset)
            if page is not None:
                # 批量从缓存获取
                result = [self.get_question_from_cache(item) for item in page]
                return self.get_paginated_response(result)
                # question_detail_list, question_option_list, question_answer_list = get_question_with_options_and_answers(
                #     page)
                # serializer = self.get_serializer(page, many=True)
                # for idx, item_data in enumerate(serializer.data):
                #     item_data['option_list'] = question_option_list.get(item_data['id'])
                #     item_data['answer'] = question_answer_list.get(item_data['id'])
                #     item_data['detailList'] = question_detail_list.get(item_data['id'])
                # return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return SuccessResponse(data=serializer.data, msg="获取成功")
        except Exception as e:
            raise e

    def get_question_from_cache(self,question):
        """
        获取题目完整信息（带Redis缓存，和项目风格一致）
        先从Redis取，取不到再查库并缓存
        """
        question_id = question.id
        cache_key = f"{WEB_KEY_PREFIX}question:detail:{question_id}"
        cache_expire = MAX_QUESTION_INFO_EXPIRE_TIME  # 用你统一的过期时间

        # 1. 先读缓存
        cached_data = redis_conn.get(cache_key)
        if cached_data:
            return json.loads(cached_data)

        # 2. 缓存未命中 → 查库 + 组装数据
        question_detail_list, question_option_list, question_answer_list = get_question_with_options_and_answers(
            question)

        # 序列化
        question_data = self.get_serializer(question).data
        question_data['option_list'] = question_option_list.get(question_id)
        question_data['detailList'] = question_detail_list.get(question_id)
        question_data['answer'] = question_answer_list.get(question_id)

        # 3. 存入Redis
        redis_conn.setex(
            cache_key,
            cache_expire,
            json.dumps(question_data, ensure_ascii=False)
        )

        return question_data

    def retrieve(self, request, *args, **kwargs):
        """返回单条记录"""
        try:
            instance = self.get_object()
            s_data = None
            if instance is not None:
                question_detail_list, question_option_list, question_answer_list = get_question_with_options_and_answers(
                    instance)
                serializer = self.get_serializer(instance)
                s_data = serializer.data
                s_data['option_list'] = question_option_list.get(s_data['id'])
                s_data['detailList'] = question_detail_list.get(s_data['id'])

            return SuccessResponse(data=s_data, msg="获取成功")
        except Exception as e:
            raise e

    # --------------------- 用户题目列表 --------------------------
    @action(detail=False,methods=['get'])
    def user_question_list(self,request):
        """用户题目列表"""
        try:
            user_id = request.user.id
            if not user_id:
                raise BizException("用户不存在")

            # 查询用户最新做过题目
            sql = """
                  SELECT null as id, ua.question_id, \
                         ua.user_id, \
                         SUM(IF(ua.got_score IS NULL, 0, ua.got_score)) AS user_score, \
                         q.score                                        AS full_score, \
                         q.content, \
                         ua.cost_time, \
                         ua.answer_seq
                  FROM history_web_user_answer ua
                           LEFT JOIN history_question q ON ua.question_id = q.id
                  WHERE (ua.question_id, ua.user_id, ua.answer_seq) IN (SELECT question_id, user_id, MAX(answer_seq) \
                                                                        FROM history_web_user_answer \
                                                                        WHERE user_id = %s  \
                                                                        GROUP BY question_id, user_id)
                    AND ua.user_id = %s 
                  GROUP BY ua.question_id, ua.user_id, ua.answer_seq, q.score, q.content, ua.cost_time
                  ORDER BY ua.answer_seq DESC; 
                  """

            results = UserAnswer.objects.raw(sql, [user_id, user_id])
            question_ids = [item.question_id for item in results]

            question_map = {q.id:q for q in Question.objects.filter(id__in=question_ids).prefetch_related('tags')}

            # 找出用户做过的题目，并标记是否收藏,是否做对
            user_collection_question_ids = set(UserQuestionCollection.objects.filter(user_id=user_id).values_list('question_id',flat=True))
            for item in results:
                # 是否收藏
                if item.question_id in user_collection_question_ids:
                     item.is_collect = '1'
                else:
                    item.is_collect = '0'

                # 是否做对
                if item.full_score != item.user_score:
                    item.is_right = '0'
                else:
                    item.is_right = '1'

                # 补充标签信息
                question = question_map.get(item.question_id)
                item.tags = question.tags.all() if question else []

            user_questions = list(results)
            serializer = UserQuestionListSerializer(user_questions, many=True)

            # 空数据处理
            return SuccessResponse(
                data=serializer.data if serializer.data else [],
                msg="获取成功" if serializer.data else "暂无作答记录"
            )
        except Exception as e:
            raise e

    # --------------------- 用户某一题已做过记录列表 ----------------
    @action(detail=False,methods=['get'])
    def question_done_list(self,request):
        """用户某一题已做过记录列表"""
        question_id = request.GET.get("question_id", "")

        # 查询用户对该题目已做过记录
        detailed_groups = UserAnswer.objects.filter(
            question_id=question_id,
            user_id=request.user.id
        ).values(
            'id',
            'sub_question_id', # 子问题id
            'answer_seq',  # 第几次答题
            'got_score',  # 本次得分
            'cost_time',  # 耗时
            'create_time',  # 答题时间
            'user_answer',  # 答题内容
        )

        # 补充本题正确答案
        question = Question.objects.get(id=question_id)
        question_answer_list = get_question_answers(question)

        handle_data = defaultdict(dict)
        for item in detailed_groups:
            answer_seq = item['answer_seq']

            # 公共逻辑：只赋值一次
            if 'cost_time' not in handle_data[answer_seq]:
                handle_data[answer_seq]['cost_time'] = item['cost_time']
                handle_data[answer_seq]['create_time'] = item['create_time']
                handle_data[answer_seq]['answer_seq'] = answer_seq
            if 'total_score' not in handle_data[answer_seq]:
                handle_data[answer_seq]['total_score'] = item['got_score']
            else :
                handle_data[answer_seq]['total_score'] += item['got_score']

            # 主体答案存储
            if question.has_sub_question != "1":
                # 主题目
                key = question.id
            else:
                # 子题目
                key = item['sub_question_id']

            # 存答案
            handle_data[answer_seq][key] = {
                "answer": item['user_answer'],
                "got_score": item['got_score']
            }

        # 查询本次回答对应的ai聊天信息
        answer_seq_list = [item['answer_seq'] for item in detailed_groups]

        chat_sessions = UserAnswerChatSession.objects.filter(
            user_id=request.user.id,
            question_id=question_id,
            answer_seq__in=answer_seq_list
        ).values('answer_seq', 'session_id')

        session_ids = [item['session_id'] for item in chat_sessions]
        chat_sessions = {item['answer_seq']:item for item in chat_sessions}
        session_msg = QuestionChatSession.objects.filter(session_id__in=session_ids)
        session_msg = {item.session_id:item.messages for item in session_msg}

        for seq, item in handle_data.items():
            item_session_id = chat_sessions.get(seq, {}).get('session_id')
            item['session_id'] = item_session_id

            # 取出会话所有消息
            full_msgs = session_msg.get(item_session_id, [])

            # 只保留 role == assistant 的消息，不合并、不修改
            item['session_msg'] = [
                msg for msg in full_msgs
                if msg.get("role") == "assistant"
            ]

        result_data = {
            "record_list": handle_data,
            "question_answer_list": question_answer_list if handle_data else ""
        }

        # 点击某一具体题目时，只需回显答案以及右侧对应的ai提示记录即可

        return SuccessResponse(data=result_data, msg="获取成功")

    # --------------------- 每日一题 ------------------------------
    @action(detail=False,methods=['get'])
    def daily_question(self,request):
        """每日一题"""
        # 从题库中随机获取一道题目，作为随机一题
        available_questions = Question.objects.filter(status=1)
        total = available_questions.count()

        if total == 0:
            return None  # 无可用题目

        # 2. 用当天日期生成固定的随机种子（核心逻辑）
        today = datetime.date.today()
        # 把日期转成固定数字（比如20260310）作为随机种子
        seed = int(today.strftime("%Y%m%d"))
        random.seed(seed)  # 固定种子 → 当天随机结果唯一

        # 3. 生成固定偏移量
        offset = random.randint(0, total - 1)
        question = available_questions[offset:offset+1].first()
        if question is None:
            raise BizException("题库为空")
        serializer = self.get_serializer(question)
        return SuccessResponse(data=serializer.data, msg="获取成功")

    # --------------------- 用户收藏题目 ------------------------------
    @action(detail=False,methods=['post'])
    def user_question_collection(self,request):
        """用户收藏题目"""
        try:
            user_id = request.user.id
            if not user_id:
                raise BizException("用户不存在")
            question_id = request.data.get('question_id')
            if not question_id:
                raise BizException("题目ID不能为空")
            with transaction.atomic():
                UserQuestionCollection.objects.create(user_id=user_id,question_id=question_id)
            return SuccessResponse(msg="收藏成功")
        except Exception as e:
            raise e

    # --------------------- 用户取消收藏题目 ------------------------------
    @action(detail=False,methods=['post'])
    def user_question_cancel_collection(self,request):
        """用户取消收藏题目"""
        try:
            user_id = request.user.id
            if not user_id:
                raise BizException("用户不存在")
            question_id = request.data.get('question_id')
            if not question_id:
                raise BizException("题目ID不能为空")
            with transaction.atomic():
                UserQuestionCollection.objects.filter(user_id=user_id,question_id=question_id).delete()
            return SuccessResponse(msg="取消收藏成功")
        except Exception as e:
            raise e

    # -------------------------- 客观题提交接口（单选/多选） --------------------------
    @action(detail=False, methods=['post'])
    def handle_submit_choice_answer(self, request, *args, **kwargs):
        """处理选择题（单选/多选）答案提交，无AI处理"""
        try:
            #  基础参数校验
            question_id = request.data.get('question_id')
            user_submit_answer = request.data.get('user_answer')
            cost_time = request.data.get('cost_time',None)
            chat_session_id = request.data.get('chat_session_id',None)
            if not question_id:
                raise BizException("题目ID不能为空")
            if not user_submit_answer:
                raise BizException("请选择答案")

            # 查询题目（仅处理选择类题型）
            instance = Question.objects.filter(id=question_id).first()
            if not instance:
                raise BizException("未获取到题目信息")
            if instance.type not in QuestionTypeEnum.get_option_values():
                raise BizException("该接口仅支持选择题提交")

            # 获取正确答案
            correct_options = QuestionOption.objects.filter(question_id=question_id, is_correct="1")
            sub_question = SubQuestion.objects.filter(question_id=question_id)
            sub_question = {item.id:item for item in sub_question}
            correct_answer_str = QuestionAnswer.objects.filter(question_id=question_id).first()
            correct_answer_str = correct_answer_str.answer_content if correct_answer_str else ""

            # 查看用户已回答该问题次数
            last_user_answer = UserAnswer.objects.filter(question_id=question_id, user_id=request.user.id).order_by('-create_time').first()
            user_answer_count = last_user_answer.answer_seq + 1 if last_user_answer else 1

            user_answer_list = []
            user_score_map = {}
            # 存在子问题
            if instance.has_sub_question == "1":
                correct_answer = defaultdict(list)
                for item in correct_options:
                    correct_answer[item.sub_question_id].append(item.id)
                correct_answer = dict(correct_answer)

                for key,value in correct_answer.items():
                    user_score = choice_question_rating(sub_question.get(key),user_submit_answer.get(str(key)),value,instance.type)
                    user_score_map[key] = user_score
                    # 保存用户答案
                    user_answer_list.append(UserAnswer(
                        question_id=question_id,
                        sub_question_id=key,
                        user_id=request.user.id,
                        user_answer=user_submit_answer,
                        got_score=user_score,
                        answer_seq=user_answer_count,
                        cost_time=cost_time
                    ))
            else:
                correct_answer = [item.id for item in correct_options]
                user_score = choice_question_rating(instance,user_submit_answer,correct_answer,instance.type)
                user_score_map[question_id] = user_score
                user_answer_list.append(UserAnswer(
                    question_id=question_id,
                    user_id=request.user.id,
                    user_answer=user_submit_answer,
                    got_score=user_score,
                    answer_seq=user_answer_count,
                    cost_time=cost_time
                ))

            with transaction.atomic():
                UserAnswer.objects.bulk_create(user_answer_list)

                UserAnswerChatSession.objects.create(
                    user_id=request.user.id,
                    question_id=question_id,
                    answer_seq=user_answer_count,
                    session_id=chat_session_id,
                )

            return SuccessResponse(
                data={"user_score": user_score_map, "correct_answer": correct_answer,"correct_answer_str":correct_answer_str},
                msg="提交成功"
            )
        except Exception as e:
            raise e

    # -------------------------- 主观题提交接口（问答/简答） --------------------------
    @action(detail=False, methods=['post'])
    def handle_subjective_answer(self, request, *args, **kwargs):
        """处理主观题（问答/简答）答案提交（依赖AI评分）"""
        try:
            # 1. 基础参数校验
            question_id = request.data.get('question_id')
            user_submit_answer = request.data.get('user_answer')
            cost_time = request.data.get('cost_time',None)
            chat_session_id = request.data.get('chat_session_id',None)
            user = request.user

            if not question_id:
                raise BizException("题目ID不能为空")
            if not user_submit_answer:
                raise BizException("请填写答案")

            # 2. 查询题目（仅处理非选择类题型）
            instance = Question.objects.filter(id=question_id).first()
            if not instance:
                raise BizException("未获取到题目信息")
            if instance.type in QuestionTypeEnum.get_option_values():
                raise BizException("该接口仅支持主观题提交")

            # 查询题目基本信息
            question = Question.objects.filter(id=question_id).first()

            # 初始化系统提示词，只能初始化一次，否则容易产生幻觉
            system_prompt = None
            if not chat_session_id:
                # 初始化系统提示词，拼接系统提示
                system_prompt = generate_complete_system_prompt(question)

            session, _ = QuestionChatSession.get_or_create_session(
                user_id=user.id,
                question_id=question_id,
                session_id=chat_session_id
            )
            history_messages = session.messages.copy()  # 拷贝，避免修改原数据
            if system_prompt:
                history_messages.insert(0, {"role": "system", "content": system_prompt})

            # 拼接用户答案
            user_submit_answer_json = json.dumps(user_submit_answer)
            ask_prompt = "\n 用户答案如下：" + user_submit_answer_json + "请为该用户进行评分"
            history_messages.append({"role": "user", "content": ask_prompt})

            ai_client = AIClient(provider="VOLC_ARK")

            ai_response, message = ai_client.chat_completion_with_context(
                system_prompt=system_prompt,
                messages=history_messages,
                temperature=0.3
            )
            session.messages = message

            user_answer_list = []  # 保存用户答案
            # 查看用户已回答该问题次数
            last_user_answer = UserAnswer.objects.filter(question_id=question_id, user_id=request.user.id).order_by('-create_time').first()
            user_answer_count = last_user_answer.answer_seq + 1 if last_user_answer else 1

            correct_answer_str = ""
            return_user_score = {}
            # 有子问题，需要对子问题进行评分
            if question.has_sub_question == "1":
                # user_submit_answer = json.loads(user_submit_answer)
                user_score = extract_score(ai_response, question.has_sub_question)  # {1:0, 2:0, 3:0...}

                # 把分数转成 列表 [0, 0, 0]，按顺序取分
                score_list = [user_score.get(i + 1, 0) for i in range(len(user_score))]

                # 遍历答案 + 按顺序自动匹配分数
                for index, (key, value) in enumerate(user_submit_answer.items()):
                    # key 是真实子问题ID 分数按 顺序 取
                    got_score = score_list[index] if index < len(score_list) else 0
                    return_user_score[key] = got_score
                    user_answer_list.append(UserAnswer(
                        question_id=question_id,
                        sub_question_id=key,
                        user_id=request.user.id,
                        user_answer=value,
                        got_score=got_score,
                        answer_seq=user_answer_count,
                        cost_time=cost_time
                    ))

                # 拼接正确答案（原逻辑不动）
                question_answer = QuestionAnswer.objects.filter(question_id=question_id).order_by("id")
                user_score = return_user_score
                correct_answer_str = ""
                for item in question_answer:
                    correct_answer_str += item.answer_content + "\n\n\n"
            else:
                user_score = extract_score(ai_response,question.has_sub_question,question.id)  # 提取AI返回的分数
                user_submit_answer_str = user_submit_answer[str(question_id)]
                # 保存用户答案
                user_answer_list.append(UserAnswer(
                    question_id=question_id,
                    user_id=request.user.id,
                    user_answer=user_submit_answer_str,
                    got_score=user_score.get(question_id),
                    answer_seq=user_answer_count,
                    cost_time=cost_time
                ))
                question_answer = QuestionAnswer.objects.filter(question_id=question_id).first()
                correct_answer_str = question_answer.answer_content

            # 异步埋点（AI判题）
            AIOperationTracker.record_operation(
                user_id=request.user.id,
                ai_type=AiTypeEnum.JUDGE.value[0],  # AI判题
                ip=request.META.get('REMOTE_ADDR', ''),
                device=request.META.get('HTTP_USER_AGENT', '')
            )

            with transaction.atomic():
                session.save()

                UserAnswer.objects.bulk_create(user_answer_list)

                UserAnswerChatSession.objects.create(
                    user_id=request.user.id,
                    question_id=question_id,
                    answer_seq=user_answer_count,
                    session_id=session.session_id,
                )

            return SuccessResponse(
                data={"user_score": user_score, "correct_answer": correct_answer_str,"ai_response":ai_response,"session_id":session.session_id},
                msg="提交成功"
            )

        except Exception as e:
            raise e

def extract_score(ai_response, has_sub_question,single_question_id=None):
    """
    从AI回复中提取最终得分，支持子题目和非子题目两种场景
    :param single_question_id: 无子题目时题目id
    :param ai_response: AI的原始回复字符串
    :param has_sub_question: 字符串类型，"0"表示无子题目，"1"表示有子题目
    :return: 字典类型 {题目id: score}，提取失败返回空字典{}
    """
    # 初始化返回结果
    result = {}

    if has_sub_question == "1":
        # 修正正则：匹配 子问题 1 得分：4 （兼容任意空格）
        # 匹配规则：子问题 + 任意空格 + 数字 + 任意空格 + 得分： + 数字
        matches = re.findall(r"子问题\s*(\d+)\s*得分：\s*(\d+)", ai_response)
        if matches:
            # 转换为 {序号: 分数} → {1:4, 2:6, 3:4}
            result = {int(question_id): int(score) for question_id, score in matches}
    elif has_sub_question == "0":
        # 无子题目：匹配「最终得分：数字」格式，无修改
        match = re.search(r"最终得分：\s*(\d+)", ai_response)
        if match:
            result = {single_question_id: int(match.group(1))}

    return result

def choice_question_rating(question,user_submit_answer,correct_ids,type):
    """
    选择题评分逻辑
    :param question: 问题对象
    :param user_submit_answer: 用户提交答案
    :param correct_ids: 正确答案的选项ID列表
    :return: 整数类型的得分
    """
    user_score = 0
    # 单选评分逻辑
    if type == QuestionTypeEnum.SINGLE_CHOICE.value[0]:
        if user_submit_answer == correct_ids:
            user_score = question.score  # 全对得满分

    # 多选评分逻辑
    elif type == QuestionTypeEnum.MULTIPLE_CHOICE.value[0]:
        has_wrong = any(x not in correct_ids for x in user_submit_answer)
        if not has_wrong:
            correct_count = len(user_submit_answer)
            if correct_count == len(correct_ids):
                user_score = question.score
            elif correct_count >= 1:
                user_score = 2  # 部分正确得分（可配置化）

    return user_score

def is_es_available(es_client):
    """检测 ES 是否可以连接"""
    try:
        # 只发送ping，不查数据
        return es_client.ping()
    except Exception:
        return False
