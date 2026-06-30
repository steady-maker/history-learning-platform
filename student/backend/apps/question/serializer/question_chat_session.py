from rest_framework.serializers import ModelSerializer

from question.models import QuestionChatSession


class QuestionChatSessionInfoSerializer(ModelSerializer):
    """
    用户ai使用记录信息-序列化器
    """

    class Meta:
        model = QuestionChatSession
        fields = '__all__'