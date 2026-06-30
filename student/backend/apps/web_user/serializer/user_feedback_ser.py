from rest_framework.serializers import ModelSerializer

from web_user.models import UserFeedback


class UserFeedbackSerializer(ModelSerializer):
    """
    用户反馈-序列化器
    """

    class Meta:
        model = UserFeedback
        fields = '__all__'
