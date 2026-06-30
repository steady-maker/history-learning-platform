# -*- coding: utf-8 -*-

"""
@Remark: 题库管理
"""
from biz.constants import PromptTypeEnum
from biz.filter import PromptFilter
from biz.models import Prompt, Tag, Question
from biz.serializer.prompt_ser import PromptInfoSerializer
from utils.exception import BizException
from utils.jsonResponse import SuccessResponse
from utils.viewset import CustomModelViewSet


class PromptViewSet(CustomModelViewSet):
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
    queryset = Prompt.objects.all().order_by('-create_time')
    serializer_class = PromptInfoSerializer
    filterset_class = PromptFilter
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(is_public='1')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")

    def create(self, request, *args, **kwargs):
        try:
            # 提取基础参数（不变）
            is_public = request.data.get('is_public', "0")
            tags = request.data.get('tags', [])
            question_id = request.data.get('id', None)

            # 题目关联提示词
            if is_public == '0':
                prompt_type_content = [
                    ('1', request.data.get('when_prompted_content', None)),
                    ('3', request.data.get('when_rating_content', None)),
                    ('2', request.data.get('during_review_content', None))
                ]

                # 批量创建提示词
                created_instances = []
                for type_val, content in prompt_type_content:
                    if not content:
                        continue
                    prompt_data = request.data.copy()
                    prompt_data.update({'type': type_val, 'prompt_content': content, 'is_public': is_public})
                    serializer = self.get_serializer(data=prompt_data)
                    serializer.is_valid(raise_exception=True)
                    instance = serializer.save()

                    created_instances.append(instance)

                # 4. 关联题目（核心修改：多对多批量添加）
                if is_public == '0' and question_id and created_instances:
                    # 先获取题目实例
                    question = Question.objects.filter(id=question_id).first()
                    if question:
                        question.prompts.add(*created_instances)  # 批量添加多个提示词
            else:
                # 公共提示词
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                instance = serializer.save()
                if tags:
                    valid_tags = Tag.objects.filter(id__in=tags)
                    instance.tags.set(valid_tags)

            return SuccessResponse(msg=f"新增成功")
        except Exception as e:
            raise e

    def update(self, request, *args, **kwargs):
        try:
            is_public = request.data.get('is_public', '0')
            partial = kwargs.pop('partial', False)
            tags = request.data.get('tags', None)
            question_id = request.data.get('id', None)  # 题目ID（非公共提示词需传）

            if is_public == '0':
                # 非公共提示词：清空旧的 + 批量加新的
                if not question_id:
                    raise BizException("未传入关联题目ID")

                # 1. 获取题目实例
                question = Question.objects.filter(id=question_id).first()
                if not question:
                    raise BizException("关联题目不存在")

                # 2. 核心：先清空该题目所有旧提示词关联（一次性清理，无残留）
                question.prompts.clear()

                # 3. 提取三类提示词内容
                prompt_type_content = [
                    ('1', request.data.get('when_prompted_content', None)),
                    ('3', request.data.get('when_rating_content', None)),
                    ('2', request.data.get('during_review_content', None))
                ]

                # 4. 批量创建新提示词 + 绑定到题目
                created_instances = []
                for type_val, content in prompt_type_content:
                    if not content:
                        continue  # 空内容跳过

                    # 直接创建新提示词
                    prompt_data = request.data.copy()
                    prompt_data.update({
                        'type': type_val,
                        'prompt_content': content,
                        'is_public': is_public
                    })
                    serializer = self.get_serializer(data=prompt_data)
                    serializer.is_valid(raise_exception=True)
                    prompt_instance = serializer.save()

                    # 绑定到当前题目
                    question.prompts.add(prompt_instance)
                    created_instances.append(prompt_instance)

                return SuccessResponse(msg="更新成功")

            else:
                # 公共提示词：单条更新（原有逻辑保留）
                instance = self.get_object()

                # 绑定标签
                valid_tags = Tag.objects.filter(id__in=tags)
                instance.tags.set(valid_tags)

                # 序列化更新
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                if getattr(instance, '_prefetched_objects_cache', None):
                    instance._prefetched_objects_cache = {}

                return SuccessResponse(msg="更新成功")
        except Exception as e:
            raise e

    def destroy(self, request, *args, **kwargs):
        is_public = request.data.get('is_public',0)
        instance = self.get_object_list()
        if is_public == "0":
            prompt_ids = (item.id for item in instance)
            # 删除题目提示词的题目与提示词的关联
            Question.objects.filter(prompt_id__in=prompt_ids).update(prompt_id=None)
        self.perform_destroy(instance)
        return SuccessResponse(data=[], msg="删除成功")






