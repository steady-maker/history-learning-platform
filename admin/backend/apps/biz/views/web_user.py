# -*- coding: utf-8 -*-

"""
@Remark: 前台用户管理
"""

from rest_framework.decorators import action

from biz.filter import WebUserFilter, UserFeedbackFilter
from biz.models import WebUser, UserFeedback
from biz.serializer.user_feedback_ser import UserFeedbackSerializer
from biz.serializer.web_user_ser import WebUserInfoSerializer
from system.constants import REDIS_SMS_DAILY_KEY_PREFIX
from utils.jsonResponse import SuccessResponse
from utils.redis import redis_conn
from utils.viewset import CustomModelViewSet


class WebUserViewSet(CustomModelViewSet):
    """
    后台管理员用户接口:
    """
    perms_map = {
        "list" : "system:user:list",
        "retrieve" : "system:user:get",
        "create" : "system:user:add",
        "update" : "system:user:edit",
        "partial_update" : "system:user:edit",
        "destroy" : "system:user:rm",
        "web_user_info" : "*",
        "update_web_user_info" :  "*",
        "reset_verification_code_count" : "*",
    }
    queryset = WebUser.objects.all().order_by('-create_time')
    serializer_class = WebUserInfoSerializer
    filterset_class = WebUserFilter

    @action(detail=False, methods=['put'])
    def reset_verification_code_count(self,request):
        """重置验证码次数"""
        mobile = request.data.get('mobile')
        daily_key = REDIS_SMS_DAILY_KEY_PREFIX + mobile
        redis_conn.delete(daily_key)
        return SuccessResponse(msg="重置成功")

class WebUserFeedbackViewSet(CustomModelViewSet):
    """
    前台用户反馈接口:
    """
    # perms_map = {
    #     "list": "system:user:list",
    #     "retrieve": "system:user:get",
    #     "create": "system:user:add",
    #     "update": "system:user:edit",
    #     "partial_update": "system:user:edit",
    #     "destroy": "system:user:rm",
    #     "web_user_info": "*",
    #     "update_web_user_info": "*",
    #     "reset_verification_code_count": "*",
    # }
    queryset = UserFeedback.objects.all().order_by('-create_time')
    serializer_class = UserFeedbackSerializer
    filterset_class = UserFeedbackFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            user_ids = set([item.user_id for item in page])
            users = WebUser.objects.filter(id__in=user_ids)
            user_info_map = {item.id: item.username for item in users}
            serializer = self.get_serializer(page, many=True)
            for item in serializer.data:
                item['username'] = user_info_map.get(item['user_id'])
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")

