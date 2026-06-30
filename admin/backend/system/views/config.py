import time

import psutil
from django.db import connection
from rest_framework.decorators import action

from history_admin_backend import settings
from system.filter import ConfigFilter
from system.models import Config
from system.serializer.config_ser import ConfigSerializer
from utils.jsonResponse import SuccessResponse
from utils.viewset import CustomModelViewSet


class ConfigViewSet(CustomModelViewSet):
    """
    配置管理接口:
    """
    queryset = Config.objects.all()
    serializer_class = ConfigSerializer
    filterset_class = ConfigFilter

    @action(detail=False, methods=['get'], url_path=r'key/(?P<config_key>[^/]+)')
    def get_config_by_key(self, request, config_key=None):
        value = Config.objects.get(key=config_key).value
        return SuccessResponse(msg=value)


    @action(detail=False, methods=['get'], url_path=r'system_info')
    def system_info(self, request):
        """获取系统信息：版本、运行时长、服务器负载、数据库容量"""
        try:
            # 1. 系统版本
            system_version = settings.SYSTEM_VERSION

            # 2. 运行时长（计算当前时间 - 服务启动时间）
            elapsed_seconds = int(time.time() - settings.STARTUP_TIME)
            days = elapsed_seconds // 86400
            hours = (elapsed_seconds % 86400) // 3600
            minutes = (elapsed_seconds % 3600) // 60
            uptime = f"{days}天{hours}小时{minutes}分钟"

            # 3. 服务器负载（CPU使用率，避免第一次返回0，调用两次）
            psutil.cpu_percent(interval=0.1)
            server_load = round(psutil.cpu_percent(interval=1), 1)

            # 4. 数据库容量（MySQL，自动适配MB/GB单位）
            with connection.cursor() as cursor:
                # 先查询总字节数，避免单位换算导致的精度丢失
                cursor.execute("""
                               SELECT SUM(data_length + index_length) AS total_bytes
                               FROM information_schema.TABLES
                               WHERE table_schema = DATABASE()
                               """)
                total_bytes = cursor.fetchone()[0] or 0  # 空值默认0

            # 自动判断单位：≥1GB显示GB，否则显示MB
            if total_bytes >= 1024 * 1024 * 1024:
                db_size = round(total_bytes / 1024 / 1024 / 1024, 2)
                db_size_str = f"{db_size}GB"
            else:
                db_size = round(total_bytes / 1024 / 1024, 2)
                db_size_str = f"{db_size}MB"

            return SuccessResponse(
                data={
                    "version": system_version,
                    "uptime": uptime,
                    "server_load": f"{server_load}%",
                    "db_size": db_size_str  # 适配后的单位字符串
                }
            )
        except Exception as e:
            raise e