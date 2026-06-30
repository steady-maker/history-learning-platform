from rest_framework import serializers

from system.models import DictType, DictData
from utils.serializers import CustomModelSerializer
from utils.validator import CustomUniqueValidator


class DictDataSerializer(CustomModelSerializer):
    """
    字典数据-序列化器
    """
    class Meta:
        model = DictData
        fields = ("dict_label","dict_value")