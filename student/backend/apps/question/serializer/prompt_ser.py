from rest_framework.serializers import ModelSerializer
from question.models import Prompt
from question.serializer.tag_ser import TagSimpleSerializer


class PromptInfoSerializer(ModelSerializer):
    """
    提示词信息-序列化器
    """
    tags = TagSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Prompt
        fields = ['id','prompt_content','type','is_public','create_time','status','remark','tags']

class PromptSimpleSerializer(ModelSerializer):
    """提示词简要信息"""
    class Meta:
        model = Prompt
        fields = ['id','prompt_content']

