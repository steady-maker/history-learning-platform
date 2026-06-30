from rest_framework.serializers import ModelSerializer

from system.models import Users


class UserInfoSerializer(ModelSerializer):
    """
    用户信息-序列化器
    """


    class Meta:
        model = Users
        fields = ["id", "username", "mobile", "email", "avatar", 'gender', "create_time",]
