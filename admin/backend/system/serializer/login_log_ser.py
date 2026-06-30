from system.models import LoginLog
from utils.serializers import CustomModelSerializer


class LoginLogSerializer(CustomModelSerializer):
    """
    登录日志-序列化器
    """
    class Meta:
        model = LoginLog
        fields = "__all__"
        read_only_fields = ["id"]