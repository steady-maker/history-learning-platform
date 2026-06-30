from rest_framework.serializers import ModelSerializer

from biz.models import QuestionAnswer


class SimpleAnswerSerializer(ModelSerializer):
    """题目-提示词——序列化器，精简返回的数据"""

    class Meta:
        model = QuestionAnswer
        fields = ['id','answer_content']