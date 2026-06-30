from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from system.filter import ConfigFilter
from system.models import Config
from system.serializer.config_ser import ConfigSerializer
from utils.jsonResponse import SuccessResponse
from utils.viewset import CustomModelViewSet


class ConfigViewSet(APIView):
    """
    配置管理接口:
    """
    permission_classes = [AllowAny]
    # queryset = Config.objects.all()
    # serializer_class = ConfigSerializer
    # filterset_class = ConfigFilter

    def get(self, request, config_key=None):
        value = Config.objects.get(key=config_key).value
        return SuccessResponse(msg=value)

