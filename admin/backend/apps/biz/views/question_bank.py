# -*- coding: utf-8 -*-

"""
@Remark: 题库管理
"""
from collections import defaultdict

from django.db import transaction
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from apps.biz.constants import QuestionTypeEnum
from biz.filter import QuestionFilter
from biz.models import Question, Tag, Prompt, QuestionAnswer, QuestionOption, SubQuestion
from biz.serializer.question_ser import QuestionInfoSerializer, PromptQuestionSerializer
from biz.utils import get_question_with_options_and_answers_2
from utils.exception import BizException
from utils.jsonResponse import SuccessResponse
from utils.redis import WEB_KEY_PREFIX, redis_conn
from utils.viewset import CustomModelViewSet


class QuestionViewSet(CustomModelViewSet):
    """
    后台管理员用户接口:
    """
    # perms_map = {
        # "list" : "system:user:list",
        # "retrieve" : "system:user:get",
        # "create" : "system:user:add",
        # "update" : "system:user:edit",
        # "partial_update" : "system:user:edit",
        # "destroy" : "system:user:rm",
        # "web_user_info" : "*",
        # "update_web_user_info" :  "*",
        # "reset_verification_code_count" : "*",
    # }
    queryset = Question.objects.all().order_by('-create_time')
    serializer_class = QuestionInfoSerializer
    filterset_class = QuestionFilter

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                question_detail_list, question_option_list, question_answer_list, prompts_map = get_question_with_options_and_answers_2(page)

                serializer = self.get_serializer(page, many=True)
                for idx, item_data in enumerate(serializer.data):
                    prompt_id = item_data.get('prompt_id')
                    item_data['prompt_content'] = prompts_map.get(prompt_id, None)
                    item_data['option_list'] = question_option_list.get(item_data['id'])
                    item_data['answer'] = question_answer_list.get(item_data['id'])
                    item_data['detailList'] = question_detail_list.get(item_data['id'])
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return SuccessResponse(data=serializer.data, msg="获取成功")
        except Exception as e:
            raise e

    @action(detail=False, methods=["get"])
    def get_prompt_question(self, request, *args, **kwargs):
        """用于提示词页面展示题目与提示词内容（适配多对多关联，无related_name依赖）"""
        try:
            # 1. 获取题目列表（带分页）
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            target_qs = page if page is not None else queryset

            # 2. 提取所有题目ID（用于批量查询）
            question_ids = [item.id for item in target_qs]
            if not question_ids:
                # 无题目数据时直接返回
                if page is not None:
                    return self.get_paginated_response([])
                return SuccessResponse(data=[], msg="获取成功")

            # 3. 方式2：直接查询多对多中间表 + 提示词表（无related_name依赖）
            # 第一步：获取「题目ID-提示词ID」映射关系
            QuestionPrompt = Question.prompts.through  # 获取中间表模型
            q_p_relation = QuestionPrompt.objects.filter(
                question_id__in=question_ids
            ).values('question_id', 'prompt_id')

            # 提取所有关联的提示词ID
            prompt_ids = [item['prompt_id'] for item in q_p_relation]
            if not prompt_ids:
                # 无关联提示词时，直接序列化题目并返回
                serializer = PromptQuestionSerializer(target_qs, many=True)
                serialized_data = serializer.data
                # 补充空的提示词字段
                for item_data in serialized_data:
                    item_data.update({
                        'when_prompted_content': '',
                        'when_rating_content': '',
                        'during_review_content': '',
                        # 'prompt_status': '',
                        # 'prompt_create_time': '',
                        # 'prompt_remark': ''
                    })
                if page is not None:
                    return self.get_paginated_response(serialized_data)
                return SuccessResponse(data=serialized_data, msg="获取成功")

            # 第二步：批量查询所有关联的提示词
            prompts = Prompt.objects.filter(
                id__in=prompt_ids
            ).values('id', 'prompt_content', 'type')

            # 4. 构建双层映射：「题目ID→提示词ID列表」+「提示词ID→提示词信息」
            # 4.1 提示词ID→提示词信息
            prompt_info_map = {p['id']: p for p in prompts}
            # 4.2 题目ID→提示词ID列表
            question_prompt_ids_map = {}
            for relation in q_p_relation:
                q_id = relation['question_id']
                p_id = relation['prompt_id']
                if q_id not in question_prompt_ids_map:
                    question_prompt_ids_map[q_id] = []
                question_prompt_ids_map[q_id].append(p_id)

            # 5. 构建「题目ID→分类提示词信息」
            question_prompts_map = {}
            for q_id, p_ids in question_prompt_ids_map.items():
                question_prompts_map[q_id] = {
                    'when_prompted_content': '',  # type=1 提示时
                    'when_rating_content': '',  # type=3 打分时
                    'during_review_content': '',  # type=2 复盘时
                    # 'prompt_status': '',
                    # 'prompt_create_time': '',
                    # 'prompt_remark': ''
                }
                # 遍历当前题目关联的所有提示词
                for p_id in p_ids:
                    prompt = prompt_info_map.get(p_id)
                    if not prompt:
                        continue
                    # 按类型填充内容
                    p_type = prompt['type']
                    if p_type == '1':
                        question_prompts_map[q_id]['when_prompted_content'] = prompt['prompt_content']
                    elif p_type == '3':
                        question_prompts_map[q_id]['when_rating_content'] = prompt['prompt_content']
                    elif p_type == '2':
                        question_prompts_map[q_id]['during_review_content'] = prompt['prompt_content']
                    # 填充通用字段（取第一个有效提示词的属性）
                    #     question_prompts_map[q_id]['prompt_create_time'] = prompt['create_time']
                    #     question_prompts_map[q_id]['prompt_remark'] = prompt['remark']

            # 6. 序列化题目并关联提示词数据
            serializer = PromptQuestionSerializer(target_qs, many=True)
            serialized_data = serializer.data
            for item_data in serialized_data:
                q_id = item_data.get('id')
                prompt_info = question_prompts_map.get(q_id, {})
                # 关联提示词字段
                item_data.update({
                    'when_prompted_content': prompt_info.get('when_prompted_content', ''),
                    'when_rating_content': prompt_info.get('when_rating_content', ''),
                    'during_review_content': prompt_info.get('during_review_content', ''),
                    # 'prompt_status': prompt_info.get('prompt_status', ''),
                    # 'prompt_create_time': prompt_info.get('prompt_create_time', ''),
                    # 'prompt_remark': prompt_info.get('prompt_remark', '')
                })

            # 7. 返回结果（兼容分页）
            if page is not None:
                return self.get_paginated_response(serialized_data)
            return SuccessResponse(data=serialized_data, msg="获取成功")

        except Exception as e:
            raise e

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                question_type = request.data.get('type',None)
                detail_list = request.data.get('detailList',[])
                if not question_type:
                    raise BizException("请选择题目类型")
                tags = request.data.get('tags', [])

                # 先保存（主）题目
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                instance = serializer.save()
                ori_question_id = instance.id
                if tags:
                    valid_tags = Tag.objects.filter(id__in=tags)
                    instance.tags.set(valid_tags)

                self.add_related_option_and_answer(question_type, request.data, ori_question_id, detail_list)
            return SuccessResponse(data=serializer.data, msg="新增成功")
        except ValidationError as e:
            if e.detail.get('code')[0].code == 'unique':
                raise BizException("题目编号已存在")
        except Exception as e :
            raise e

    def add_related_option_and_answer(self,question_type,request_data,ori_question_id,detail_list):
        # 单选或多选
        single_or_multi = [QuestionTypeEnum.SINGLE_CHOICE.value[0], QuestionTypeEnum.MULTIPLE_CHOICE.value[0]]
        if question_type in single_or_multi:
            options = request_data.get('option_list',[])
            if options:
                for item in options:
                    question_option = QuestionOption(
                        question_id=ori_question_id,
                        option_content=item['option_content'],
                        is_correct=item['is_correct']
                    )
                    question_option.save()

        answer = request_data.get('answer',None)
        if answer:
            question_answer = QuestionAnswer(
                question_id=ori_question_id,
                answer_content=answer
            )
            question_answer.save()

        if detail_list:
            for item in detail_list:
                # 保存子问题
                sub_question = SubQuestion(
                    question_id=ori_question_id,
                    sub_content=item['question'],
                    score=item['score']
                )
                sub_question.save()

                # 单选或者多选处理选项
                if question_type in single_or_multi:
                    options = item['option_list']
                    for opt in options:
                        question_option = QuestionOption(
                            question_id=ori_question_id,
                            sub_question_id=sub_question.id,
                            option_content=opt['option_content'],
                            is_correct=opt['is_correct']
                        )
                        question_option.save()

                # 处理答案
                sub_question_answer = QuestionAnswer(
                    question_id=ori_question_id,
                    sub_question_id=sub_question.id,
                    answer_content=item['answer']
                )
                sub_question_answer.save()

    def update(self,request, *args, **kwargs):
        try:
            with transaction.atomic():
                question_type = request.data.get('type',None)
                detail_list = request.data.get('detailList',[])
                tags = request.data.get('tags', [])
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                ori_question_id = instance.id
                clear_question_cache(ori_question_id) # 清除题目相关信息缓存
                if tags:
                    valid_tags = Tag.objects.filter(id__in=tags)
                    instance.tags.set(valid_tags)
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                # 先删除原来关联的记录
                SubQuestion.objects.filter(question_id=ori_question_id).delete()
                QuestionAnswer.objects.filter(question_id=ori_question_id).delete()
                QuestionOption.objects.filter(question_id=ori_question_id).delete()

                # 新增关联记录
                self.add_related_option_and_answer(question_type, request.data, ori_question_id, detail_list)

            return SuccessResponse(data=serializer.data, msg="更新成功")
        except Exception as e:
            raise e

    def destroy(self, request, *args, **kwargs):
        """暂未考虑已关联题目之类的删除逻辑，暂时考新增时存在错误录入等情况下的简单删除"""

        try:
            with transaction.atomic():
                instance = self.get_object_list()
                question_ids = [item.id for item in instance]
                for question_id in question_ids:
                    clear_question_cache(question_id)
                QuestionAnswer.objects.filter(question_id__in=question_ids).delete()
                QuestionOption.objects.filter(question_id__in=question_ids).delete()
                self.perform_destroy(instance)
            return SuccessResponse(data=[], msg="删除成功")
        except Exception as e:
            raise e

def clear_question_cache(question_id):
    """清除指定题目的system_prompt缓存"""
    cache_key = f"{WEB_KEY_PREFIX}question_system_prompt:{question_id}"
    redis_conn.delete(cache_key)



