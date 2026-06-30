from system.filter import LoginLogFilter
from system.models import LoginLog
from system.serializer.login_log_ser import LoginLogSerializer
from utils.viewset import CustomModelViewSet


class LoginLogViewSet(CustomModelViewSet):
    """
    登录日志管理接口:
    """
    queryset = LoginLog.objects.all()
    serializer_class = LoginLogSerializer
    filterset_class = LoginLogFilter
    http_method_names = ['get']