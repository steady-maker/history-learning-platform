from rest_framework.serializers import ModelSerializer

from question.models import Question
from question.serializer.tag_ser import TagSimpleSerializer


class QuestionInfoSerializer(ModelSerializer):
    """
    题目信息-序列化器
    """
    tags = TagSimpleSerializer(many=True, read_only=True)
    # allow_null=True：允许 prompt 为 null，此时该字段返回 null, 此方案要外键关联，
    # prompt = PromptSimpleSerializer(source='prompt_id', read_only=True, allow_null=True)

    class Meta:
        model = Question
        # fields = '__all__'
        fields = ['id','content','code','is_high_frequency','score','difficulty','finish_time','img_list','has_sub_question','type','tags']


class SimpleQuestionSerializer(ModelSerializer):
    """题目简化—序列化器，精简返回的数据"""

    class Meta:
        model = Question
        fields = ['content','score','difficulty','finish_time']