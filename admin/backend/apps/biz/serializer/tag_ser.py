from rest_framework.serializers import ModelSerializer

from biz.models import Tag


class TagInfoSerializer(ModelSerializer):
    """
    标签信息-序列化器
    """

    class Meta:
        model = Tag
        fields = '__all__'

class TagSimpleSerializer(ModelSerializer):
    """
    简单标签信息——序列化器，减少查询内容
    """
    class Meta:
        model = Tag
        fields = ['id','name']