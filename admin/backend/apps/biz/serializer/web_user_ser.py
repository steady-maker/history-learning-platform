from rest_framework.serializers import ModelSerializer

from biz.models import WebUser


class WebUserInfoSerializer(ModelSerializer):
    """
    用户信息-序列化器
    """

    class Meta:
        model = WebUser
        fields = ["id", "username", "mobile", "email", "avatar", 'gender', "remark", "create_time", "status"]
