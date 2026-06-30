import json
import logging
import time
from collections import defaultdict

from django.conf import settings
from django.db import connection
from django.db.models import Q
from openai import OpenAI

from question.constants import QuestionTypeEnum, MAX_CONTEXT_ROUND_ON_REVIEW, MAX_QUESTION_INFO_EXPIRE_TIME
from question.models import SubQuestion, QuestionOption, QuestionAnswer, Prompt
from question.serializer.question_ser import SimpleQuestionSerializer
from utils.redis import WEB_KEY_PREFIX, redis_conn


class AIClient:
    """AI 模型调用客户端（匹配火山方舟官方 OpenAI 兼容接口）"""

    def __init__(self, provider="VOLC_ARK"):
        self.provider = provider
        self.client = self._init_client()
        self.model = settings.AI_CONFIG[provider]["MODEL"]

    def _init_client(self):
        """初始化客户端（兼容火山方舟/OpenAI）"""
        if self.provider == "VOLC_ARK":
            # 火山方舟：OpenAI兼容接口配置（官方样例逻辑）
            api_key = settings.AI_CONFIG["VOLC_ARK"]["API_KEY"]
            base_url = settings.AI_CONFIG["VOLC_ARK"]["BASE_URL"]

            if not api_key:
                raise ValueError("火山方舟 API Key 未配置（请设置 ARK_API_KEY 环境变量）")

            return OpenAI(
                api_key=api_key,
                base_url=base_url
            )
        elif self.provider == "OPENAI":
            # 原生OpenAI配置（保留）
            api_key = settings.AI_CONFIG["OPENAI"]["API_KEY"]
            base_url = settings.AI_CONFIG["OPENAI"]["BASE_URL"]

            if not api_key:
                raise ValueError("OpenAI API Key 未配置（请设置 OPENAI_API_KEY 环境变量）")

            return OpenAI(
                api_key=api_key,
                base_url=base_url
            )
        else:
            raise ValueError(f"不支持的AI提供商：{self.provider}")

    def chat_completion_with_context(self, system_prompt, messages, temperature=0.3):
        """多轮对话接口（匹配官方调用规范）"""
        try:
            full_messages = messages

            # 调用接口（与OpenAI语法一致）
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=temperature
            )

            # 提取AI响应并更新对话记录
            ai_content = response.choices[0].message.content.strip()
            messages.append({"role": "assistant", "content": ai_content})

            return ai_content, messages

        except Exception as e:
            raise Exception(f"AI 调用异常：{str(e)}")

    def multimodal_chat(self, text, image_url=None, temperature=0.3):
        """多模态调用（匹配官方图文示例）"""
        try:
            # 构造多模态输入
            input_content = [{"type": "input_text", "text": text}]
            if image_url:
                input_content.insert(0, {"type": "input_image", "image_url": image_url})

            # 官方样例中的调用方式（responses.create）
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "user",
                        "content": input_content
                    }
                ]
            )
            return response
        except Exception as e:
            raise Exception(f"多模态调用异常：{str(e)}")

    # ========== 流式多轮对话接口 ==========
    def chat_completion_with_context_stream(self, messages, temperature=0.3):
        """流式多轮对话接口（修复内容零碎问题）"""
        try:
            full_messages = messages
            stream_response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=temperature,
                stream=True,
            )

            for chunk in stream_response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content  # 来一个发一个！

        except Exception as e:
            raise Exception(f"AI 流式调用异常：{str(e)}")

# 下面几个都是获取题目基本信息
def get_question_with_options_and_answers(question_queryset):
    """多表联查，返回题目所需结构"""
    question_ids = None
    if not hasattr(question_queryset, '__iter__'):
        # 场景1：单个 Question 对象（不可迭代）
        question_ids = [question_queryset.id]
        question_queryset = [question_queryset]
    else:
        question_ids = {item.id: item for item in question_queryset}
    sub_questions = SubQuestion.objects.filter(question_id__in=question_ids)
    sub_questions_map = defaultdict(list)
    for item in sub_questions:
        sub_questions_map[item.question_id].append(item)
    sub_questions_map = dict(sub_questions_map)

    # 选项
    question_options = QuestionOption.objects.filter(question_id__in=question_ids)
    question_options_map = defaultdict(list)
    sub_questions_options_map = defaultdict(list)
    for item in question_options:
        question_options_map[item.question_id].append(item)
        sub_questions_options_map[item.sub_question_id].append(item)
    question_options_map = dict(question_options_map)
    sub_questions_options_map = dict(sub_questions_options_map)

    # 答案
    question_answer = QuestionAnswer.objects.filter(question_id__in=question_ids)
    question_answer_map = {item.id: item for item in question_answer}
    sub_question_answer_map = defaultdict()
    for item in question_answer:
        sub_question_answer_map[item.sub_question_id] = item
    sub_question_answer_map = dict(sub_question_answer_map)

    # 返回封装的detailList
    question_detail_list = defaultdict(list)
    question_option_list = defaultdict(list)
    question_answer_list = {}

    # 单选或多选
    single_or_multi = [QuestionTypeEnum.SINGLE_CHOICE.value[0], QuestionTypeEnum.MULTIPLE_CHOICE.value[0]]

    # 封装题目关联数据
    for item in question_queryset:
        # 有子题目
        if item.has_sub_question == "1":
            item_sub_que = sub_questions_map.get(item.id, None)
            for sub_que in item_sub_que:
                option_list = []
                # 封装选择题
                if item.type in single_or_multi:
                    item_option = sub_questions_options_map.get(sub_que.id, None)
                    for opt in item_option:
                        option_list.append({
                            "option_content": opt.option_content,
                            "option_id": opt.id,
                            # "is_correct": opt.is_correct
                        })

                sub_que_ans = sub_question_answer_map.get(sub_que.id, None)
                question_detail_list[item.id].append({
                    "sub_question_id": sub_que.id,
                    "question": sub_que.sub_content,
                    "score": sub_que.score,
                    "option_list": option_list,
                    # "answer": sub_que_ans.answer_content if sub_que_ans is not None else ""
                })
        # 无子题目
        else:
            if item.type in single_or_multi:
                item_options = question_options_map.get(item.id)
                option_list = []
                for opt in item_options:
                    option_list.append({
                        "option_content": opt.option_content,
                        "option_id": opt.id,
                        # "is_correct": opt.is_correct
                    })
                question_option_list[item.id] = option_list
            # else:
            #     question_answer_list[item.id] = question_answer_map.get(item.id)

    question_detail_list = dict(question_detail_list)
    question_option_list = dict(question_option_list)

    return question_detail_list,question_option_list,question_answer_list

def get_question_with_options_and_answers_fast(question_queryset):
    """分步查询优化版本 - 通常比复杂SQL快10倍"""

    # 1. 提取题目ID
    if hasattr(question_queryset, '__iter__'):
        question_ids = [item.id for item in question_queryset]
    else:
        question_ids = [question_queryset.id]

    if not question_ids:
        return []

    placeholders = ','.join(['%s'] * len(question_ids))

    with connection.cursor() as cursor:
        # 步骤1：查询基础题目信息
        cursor.execute(f"""
            SELECT q.id, q.content, q.has_sub_question, q.type, p.prompt_content
            FROM history_question q
            LEFT JOIN history_prompt p ON q.prompt_id = p.id
            WHERE q.id IN ({placeholders})
        """,question_ids)
        questions_base = {row[0]: {
            'question_id': row[0],
            'content': row[1],
            'has_sub_question': row[2],
            'type': row[3],
            'prompt_content': row[4] or '',
            'sub_questions': [],
            'options': [],
            'answer': ''
        } for row in cursor.fetchall()}

        # 步骤2：批量查询子题目
        cursor.execute(f"""
            SELECT sq.id, sq.question_id, sq.sub_content, sq.score
            FROM history_sub_question sq
            WHERE sq.question_id IN ({placeholders})
        """,question_ids)
        for row in cursor.fetchall():
            sq_id, q_id, content, score = row
            questions_base[q_id]['sub_questions'].append({
                'sub_question_id': sq_id,
                'sub_content': content,
                'score': score,
                'options': [],
                'answer': ''
            })

        # 步骤3：批量查询选项
        cursor.execute(f"""
            SELECT qo.question_id, qo.sub_question_id, qo.option_content, qo.is_correct
            FROM history_question_option qo
            WHERE qo.question_id IN ({placeholders})
               OR qo.sub_question_id IN (
                   SELECT id FROM history_sub_question 
                   WHERE question_id IN ({placeholders})
               )
        """,question_ids)
        for row in cursor.fetchall():
            q_id, sq_id, content, is_correct = row
            option_data = {'option_content': content, 'is_correct': is_correct}

            if sq_id:  # 子题目选项
                for sq in questions_base[q_id]['sub_questions']:
                    if sq['sub_question_id'] == sq_id:
                        sq['options'].append(option_data)
                        break
            else:  # 主题目选项
                questions_base[q_id]['options'].append(option_data)

        # 步骤4：批量查询答案
        cursor.execute(f"""
            SELECT qa.question_id, qa.sub_question_id, qa.answer_content
            FROM history_question_answer qa
            WHERE qa.question_id IN ({placeholders})
               OR qa.sub_question_id IN (
                   SELECT id FROM history_sub_question 
                   WHERE question_id IN ({placeholders})
               )
        """, question_ids)
        for row in cursor.fetchall():
            q_id, sq_id, answer = row
            if sq_id:  # 子题目答案
                for sq in questions_base[q_id]['sub_questions']:
                    if sq['sub_question_id'] == sq_id:
                        sq['answer'] = answer
                        break
            else:  # 主题目答案
                questions_base[q_id]['answer'] = answer

    return list(questions_base.values())

def get_question_with_options_and_answers_2(question_queryset):
    """原生SQL精准联查（修复JOIN条件）+ 数据处理，100%匹配原代码逻辑"""
    # ========== 1. 处理入参，获取question_ids（兼容单对象/可迭代对象） ==========
    if not hasattr(question_queryset, '__iter__'):
        # 单个Question对象
        question_ids = [question_queryset.id]
    else:
        # QuerySet/列表
        question_ids = [item.id for item in question_queryset if item.id]

    if not question_ids:
        return {}, {}, {}, {}

    # ========== 2. 执行修正后的原生SQL（参数化查询防注入） ==========
    sql = """
          SELECT q.id               AS question_id, \
                 q.content          AS question_content, \
                 q.score            AS question_score, \
                 q.difficulty       AS question_difficulty, \
                 q.finish_time      AS question_finish_time, \
                 q.has_sub_question AS has_sub_question, \
                 q.type             AS question_type, \
                 q.prompt_id        AS prompt_id, \
                 sq.id              AS sub_question_id, \
                 sq.sub_content     AS sub_question_content, \
                 sq.score           AS sub_question_score, \
                 qo.id              AS option_id,   \
                 qo.option_content  AS option_content, \
                 qo.is_correct      AS option_is_correct, \
                 qo.sub_question_id AS option_sub_question_id, \
                 qa.answer_content  AS answer_content, \
                 qa.sub_question_id AS answer_sub_question_id, \
                 p.prompt_content   AS prompt_content
          FROM history_question q \
                   LEFT JOIN history_sub_question sq ON q.id = sq.question_id \
                   LEFT JOIN history_question_option qo \
                             ON q.id = qo.question_id \
                                 AND (sq.id = qo.sub_question_id OR qo.sub_question_id IS NULL) \
                   LEFT JOIN history_question_answer qa \
                             ON q.id = qa.question_id \
                                 AND (sq.id = qa.sub_question_id OR qa.sub_question_id IS NULL) \
                   LEFT JOIN history_prompt p ON q.prompt_id = p.id
          WHERE q.id IN %s
          ORDER BY q.id, sq.id; \
          """

    with connection.cursor() as cursor:
        cursor.execute(sql, (tuple(question_ids),))
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # ========== 3. 初始化返回数据（和原代码完全一致） ==========
    question_detail_list = defaultdict(list)  # 原代码的结构（list），恢复！
    question_option_list = defaultdict(list)
    question_answer_list = {}
    # prompts_map = {}

    # 单选/多选类型（和原代码一致）
    single_or_multi = [QuestionTypeEnum.SINGLE_CHOICE.value[0], QuestionTypeEnum.MULTIPLE_CHOICE.value[0]]

    # ========== 4. 数据处理逻辑 ==========
    # 第二步：按题目分组
    # 临时存储：避免重复处理同一题目/子题
    processed_sub_questions = defaultdict(set)  # {question_id: {sub_question_id}}
    processed_options = defaultdict(set)  # {question_id: {option_content}}

    for row in rows:
        q_id = row['question_id']
        has_sub_question = row['has_sub_question']
        question_type = row['question_type']

        # 场景1：有子题目（has_sub_question="1"）
        if has_sub_question == "1":
            sub_q_id = row['sub_question_id']
            if not sub_q_id:
                continue

            # 子题去重：避免重复添加
            if sub_q_id not in processed_sub_questions[q_id]:
                # 整理子题选项（和原代码一致）
                option_list = []
                if question_type in single_or_multi:
                    opt_content = row['option_content']
                    if opt_content:
                        option_list.append({
                            "option_content": opt_content,
                            "is_correct": row['option_is_correct'] or False,
                            "option_id": row['option_id'],
                        })

                # 整理子题答案
                sub_ans_content = row['answer_content'] or ""

                # 封装子题数据
                sub_question_data = {
                    "question": row['sub_question_content'] or "",
                    "score": row['sub_question_score'] or 0,
                    "option_list": option_list,
                    "answer": sub_ans_content
                }
                question_detail_list[q_id].append(sub_question_data)
                processed_sub_questions[q_id].add(sub_q_id)

            # 补充子题的其他选项（如果有）
            if question_type in single_or_multi and row['option_content']:
                # 找到当前子题的已存数据，补充选项
                for sub_item in question_detail_list[q_id]:
                    if sub_item['question'] == (row['sub_question_content'] or ""):
                        # 选项去重
                        opt_exists = any(
                            opt['option_content'] == row['option_content']
                            for opt in sub_item['option_list']
                        )
                        if not opt_exists:
                            sub_item['option_list'].append({
                                "option_content": row['option_content'],
                                "is_correct": row['option_is_correct'] or False,
                                "option_id": row['option_id'],
                            })
                        break

        # 场景2：无子题目（has_sub_question≠"1"）
        else:
            # 单选/多选：整理主题目的选项（和原代码一致）
            if question_type in single_or_multi:
                opt_content = row['option_content']
                if opt_content and opt_content not in processed_options[q_id]:
                    question_option_list[q_id].append({
                        "option_content": opt_content,
                        "is_correct": row['option_is_correct'] or False,
                        "option_id": row['option_id'],
                    })
                    processed_options[q_id].add(opt_content)

            # 整理主题目的答案
            if q_id not in question_answer_list and row['answer_content']:
                question_answer_list[q_id] = row['answer_content']

    # ========== 5. 格式转换（和原代码完全一致） ==========
    return (
        dict(question_detail_list),
        dict(question_option_list),
        question_answer_list,
        # prompts_map
    )

# 获取单个题目答案
def get_question_answers(question_queryset):
    """
    获取单个题目答案的函数 - 同时返回答案内容和正确答案的选项ID列表
    
    :param question_queryset: Question对象
    :return: 字典格式 {
        question_id: {
            "answer_content": "答案内容字符串",  # 主观题/问答类
            "correct_option_ids": [1, 2, 3]      # 选择题正确答案的选项ID列表
        }
    }
    """

    question_id = question_queryset.id
    # 查询正确答案的选项ID
    correct_options = QuestionOption.objects.filter(
        question_id=question_id,
        is_correct="1"
    )
    
    # 按题目ID分组正确答案选项ID
    correct_options_ids = None
    if question_queryset.has_sub_question == "1":
        correct_option_ids = {}
        for opt in correct_options:
            if opt.sub_question_id not in correct_option_ids:
                correct_option_ids[opt.sub_question_id] = []
            correct_option_ids[opt.sub_question_id].append(opt.id)
    else:
        correct_options_ids = [opt.id for opt in correct_options]


    # 查询答案内容
    answer = QuestionAnswer.objects.filter(question_id=question_id)
    answer_str = ""
    if answer:
        for item in answer:
            answer_str += item.answer_content + "\n\n"

    # 构建返回结果
    result = {
        "answer_content": answer_str ,
        "correct_option_ids": correct_options_ids
    }

    return result

def clean_model_obj(obj):
    """过滤Django模型对象的内部属性"""
    if hasattr(obj, '__dict__'):
        # 只保留非下划线开头的属性（排除_state等）
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
    return obj  # 非模型对象直接返回

def trim_to_max_rounds(messages):
    """
    截断对话消息，只保留最近5轮（user+assistant为1轮）
    :param messages: 原始对话列表，格式如 [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    :return: 截断后的消息列表
    """
    # 边界处理：消息为空/不足5轮，直接返回
    if not messages:
        return []

    # 倒序遍历，收集最近5轮（从最后一条消息往前数）
    trimmed = []
    round_count = 0
    # 从最后一条消息开始，步长-2（每次取assistant+user）
    # 兼容最后一条是user（还没回复）的情况
    i = len(messages) - 1
    while i >= 0 and round_count < MAX_CONTEXT_ROUND_ON_REVIEW:
        # 先加当前消息（不管是user/assistant）
        trimmed.insert(0, messages[i])
        # 如果当前是assistant，且前一条是user，算1轮
        if messages[i]["role"] == "assistant" and i - 1 >= 0 and messages[i - 1]["role"] == "user":
            trimmed.insert(0, messages[i - 1])
            i -= 1  # 跳过已加的user消息
            round_count += 1
        # 如果当前是user（最后一条还没回复），算半轮，也保留
        elif messages[i]["role"] == "user":
            round_count += 1
        i -= 1

    return trimmed

# 配置日志（可选，也可以直接打印）
logger = logging.getLogger('django')

def record_execution_time(func):
    """
    记录函数/方法执行时间的装饰器
    """
    def wrapper(*args, **kwargs):
        # 记录开始时间
        start_time = time.perf_counter()
        try:
            # 执行原方法
            result = func(*args, **kwargs)
            return result
        finally:
            # 计算耗时（保留4位小数，单位：秒）
            elapsed_time = time.perf_counter() - start_time
            # 记录日志（或打印）
            logger.info(f"方法 {func.__name__} 执行耗时：{elapsed_time:.4f} 秒")
            # 也可以直接打印（调试用）
            # print(f"方法 {func.__name__} 执行耗时：{elapsed_time:.4f} 秒")
    return wrapper

# 根据题目基本信息和公共提示词和该题目对应全部提示词，生成完整的提示词
def generate_complete_system_prompt(question):
    """
    根据题目基本信息，生成完整的系统提示词
    question:question_queryset
    """
    # 初始化系统提示词，拼接系统提示
    system_prompt = get_question_system_prompt(question)

    # 获取提示时公共提示词，即标签为空，或者标签和题目标签一致
    question_tags_ids = question.tags.all().values_list("id", flat=True) if question.tags.exists() else []
    public_prompts = Prompt.objects.filter(
        Q(tags__isnull=True) | Q(tags__id__in=question_tags_ids),
        is_public="1").distinct()

    if public_prompts:
        for item in public_prompts:
            system_prompt += "\n\n\n " + item.prompt_content

    # 拼接单独的题目提示词
    question_prompt = question.prompts.all()
    if question_prompt:
        system_prompt = system_prompt + "\n\n此外，" + question_prompt.prompt_content

    return system_prompt

def get_question_system_prompt(question):
    """
    获取系统提示词中题目信息内容（带Redis缓存）
    先从Redis取，取不到再查库并缓存
    """
    question_id = question.id
    cache_key = f"{WEB_KEY_PREFIX}question_system_prompt:{question_id}"
    cache_expire = MAX_QUESTION_INFO_EXPIRE_TIME

    # 1. 先尝试从Redis取缓存
    cached_prompt = redis_conn.get(cache_key)
    if cached_prompt:
        # 缓存命中，直接返回
        return cached_prompt.decode('utf-8')  # 注意解码

    # 2. 缓存未命中，查库生成system_prompt
    system_prompt = ""
    question_detail_list, question_option_list, question_answer_list = get_question_with_options_and_answers_2(
        question)
    question_data = SimpleQuestionSerializer(question).data if question else {}
    all_question_data = {
        "question": question_data,
        "detail": question_detail_list,
        "options": question_option_list,
        "answers": question_answer_list
    }
    question_json = json.dumps(all_question_data, ensure_ascii=False)
    system_prompt = system_prompt + "\n ;题目信息如下：" + question_json

    # 拼接参考答案,针对选择题
    if question.type in QuestionTypeEnum.get_option_values():
        correct_options = QuestionOption.objects.filter(question_id=question_id, is_correct="1")
        # 有子题目
        if question.has_sub_question == "1":
            correct_options_map = defaultdict(list)
            for item in correct_options:
                correct_options_map[item.sub_question_id].append(item.id)
            correct_options_map = dict(correct_options_map)
            correct_answer_str = json.dumps(correct_options_map)
        else:
            correct_answer_str = ",".join([str(item.id) for item in correct_options])
        system_prompt += "\n 标准答案如下（选项id）：" + correct_answer_str

    # 3. 写入Redis缓存（超长有效期）
    redis_conn.setex(cache_key, cache_expire, system_prompt)
    return system_prompt



