# -*- coding: utf-8 -*-

"""
@Remark: 自定义序列化器
"""
from rest_framework.serializers import ModelSerializer, Serializer

from utils.exception import BizException


class CustomModelSerializer(ModelSerializer):
    """
    使用序列化器新增和修改时,自动写入创建人、修改人
    """
    def save(self, **kwargs):
        return super().save(**kwargs)

    def create(self, validated_data):
        """创建时自动写入创建人、修改人"""
        request = self.context.get("request")
        if request and hasattr(request, "user") and str(request.user) != "AnonymousUser":
            user = request.user
            validated_data.setdefault("create_by", user.id)
            validated_data.setdefault("create_name", user.username)
            validated_data.setdefault("update_by", user.id)
            validated_data.setdefault("update_name", user.username)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """更新时自动写入修改人"""
        request = self.context.get("request")
        if request and hasattr(request, "user") and str(request.user) != "AnonymousUser":
            user = request.user
            validated_data["update_by"] = user.id
            validated_data["update_name"] = user.username
        return super().update(instance, validated_data)

    def handle_serializer_validation_error(self,default_message="数据验证失败") -> None:
        """
        处理序列化器验证错误的通用方法
        当序列化器验证失败时，提取第一个错误信息并抛出BizException异常

        Args:
            default_message: 当无法获取具体错误时的默认提示信息
        Raises:
            BizException: 包含具体错误信息的业务异常
        """
        # 验证通过直接返回，无需处理
        if self.is_valid():
            return

        errors = self.errors
        # 极端情况：is_valid()为False但errors为空，用默认提示
        if not errors:
            raise BizException(default_message)

        # 获取第一个字段名
        first_field = next(iter(errors))
        # 获取该字段的第一个错误
        first_error = errors[first_field][0]

        raise BizException(first_error)