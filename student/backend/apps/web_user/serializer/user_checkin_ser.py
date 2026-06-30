from rest_framework.serializers import ModelSerializer

from web_user.models import UserCheckIn


class UserCheckInSerializer(ModelSerializer):
    """
    用户反馈-序列化器
    """

    class Meta:
        model = UserCheckIn
        fields = '__all__'
