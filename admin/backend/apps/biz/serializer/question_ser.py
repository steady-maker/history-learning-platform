from rest_framework.serializers import ModelSerializer

from biz.models import Question
from biz.serializer.answer_ser import SimpleAnswerSerializer
from biz.serializer.tag_ser import TagSimpleSerializer


class QuestionInfoSerializer(ModelSerializer):
    """
    题目信息-序列化器
    """
    tags = TagSimpleSerializer(many=True, read_only=True)
    # allow_null=True：允许 prompt 为 null，此时该字段返回 null, 此方案要外键关联，
    # prompt = PromptSimpleSerializer(source='prompt_id', read_only=True, allow_null=True)

    class Meta:
        model = Question
        fields = '__all__'


class PromptQuestionSerializer(ModelSerializer):
    """题目-提示词——序列化器，精简返回的数据"""

    class Meta:
        model = Question
        fields = ['id','code','content','img_list','has_sub_question']