# -*- coding: utf-8 -*-

"""
@Remark: 用户管理
"""
import datetime

from django.contrib.auth.hashers import make_password
from rest_framework.decorators import action
from rest_framework.response import Response
from system.filter import UserFilter
from system.models import Users, Dept
from system.serializer.user_ser import UserSerializer, UserInfoSerializer
from system.utils import get_init_pwd
from utils.exception import BizException
from utils.jsonResponse import SuccessResponse
from utils.viewset import CustomModelViewSet

class UserViewSet(CustomModelViewSet):
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
        "reset_pwd" : "system:user:reset_pwd",
        "user_info" : "*",
        "update_user_info" :  "*",
        "change_password" : "*",
    }
    queryset = Users.objects.filter(is_delete="0").order_by('-create_time')
    serializer_class = UserSerializer
    filterset_class = UserFilter

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        dept_id = self.request.GET.get('dept_id')
        if dept_id:
            def get_sub_ids(parent_id):
                sub_ids = []
                children = Dept.objects.filter(parent_id=parent_id, status="1", is_delete="0")
                for child in children:
                    sub_ids.append(child.id)
                    sub_ids.extend(get_sub_ids(child.id))
                return sub_ids

            dept_ids = [int(dept_id)] + get_sub_ids(int(dept_id))
            qs = qs.filter(dept_id__in=dept_ids)

        if not user.id == 1:
            qs = qs.exclude(id=1)
        return qs

    @action(detail=False)
    def user_info(self, request):
        """获取当前用户信息"""
        user = request.user
        serializer = UserInfoSerializer(user)
        return Response({
            "code": 200,
            "msg": "获取成功",
            "user": serializer.data
        })

    @action(detail=False, methods=['put'])
    def update_user_info(self,request):
        """修改当前用户信息"""
        user = request.user
        Users.objects.filter(id=user.id).update(**request.data)
        return SuccessResponse(data=None, msg="修改成功")

    @action(detail=False, methods=['put'])
    def change_password(self,request):
        """密码修改"""
        user = request.user
        instance = Users.objects.filter(id=user.id).first()
        data = request.data
        old_pwd = data.get('oldPassword')
        new_pwd = data.get('newPassword')
        if instance:
            if instance.check_password(old_pwd):
                instance.password = make_password(new_pwd)
                instance.pwd_update_date = datetime.datetime.now()
                instance.save()
                return SuccessResponse(data=None, msg="修改成功")
            else:
                raise BizException(msg="旧密码不正确")
        else:
            raise BizException(msg="未获取到用户")

    @action(detail=False, methods=['put'])
    def reset_pwd(self,request):
        user_id = int(request.data.get('user_id'))
        init_pwd = get_init_pwd()
        user = Users.objects.get(id=user_id)
        user.set_password(init_pwd)
        user.pwd_update_date = None
        user.save()
        return SuccessResponse()
