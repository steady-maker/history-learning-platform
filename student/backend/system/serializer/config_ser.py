from rest_framework import serializers

from system.models import Config
from utils.serializers import CustomModelSerializer
from utils.validator import CustomUniqueValidator


class ConfigSerializer(CustomModelSerializer):
    """
    配置-序列化器
    """
    name = serializers.CharField(
        validators=[CustomUniqueValidator(queryset=Config.objects.all(), message="配置名称已存在，请换一个")]
    )
    key = serializers.CharField(
        validators=[CustomUniqueValidator(queryset=Config.objects.all(), message="配置键值已存在，请换一个")]
    )
    class Meta:
        model = Config
        fields = "__all__"
        read_only_fields = ["id"]