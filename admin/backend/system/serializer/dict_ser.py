from rest_framework import serializers

from system.models import DictType, DictData
from utils.serializers import CustomModelSerializer
from utils.validator import CustomUniqueValidator


class DictTypeSerializer(CustomModelSerializer):
    """
    字典类型-序列化器
    """
    name = serializers.CharField(
        validators=[CustomUniqueValidator(queryset=DictType.objects.all(), message="字典名称已存在，请换一个")]
    )
    type = serializers.CharField(
        validators=[CustomUniqueValidator(queryset=DictType.objects.all(), message="字典类型已存在，请换一个")]
    )
    class Meta:
        model = DictType
        fields = "__all__"
        read_only_fields = ["id"]

class DictDataSerializer(CustomModelSerializer):
    """
    字典数据-序列化器
    """
    class Meta:
        model = DictData
        fields = "__all__"