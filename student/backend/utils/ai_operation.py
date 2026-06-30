import logging
import threading
from django.db import transaction, IntegrityError

from system.models import AIOperationLog

# 配置日志
logger = logging.getLogger('ai_operation')

class AIOperationTracker:
    """AI操作埋点工具类（异步+幂等+异常隔离）"""
    @staticmethod
    def record_operation(user_id, ai_type, business_type=None, ip='', device=''):
        """
        异步记录AI操作日志
        :param user_id: 用户ID
        :param ai_type: AI类型（tip/judge/review）
        :param business_id: 关联业务ID（答题ID）
        :param business_type: 业务类型（subjective_answer）
        :param ip: 用户IP
        :param device: 设备信息
        """
        def _async_record():
            try:
                with transaction.atomic():
                    AIOperationLog.objects.create(
                        user_id=user_id,
                        ai_type=ai_type,
                        # business_id=business_id,
                        # business_type=business_type,
                        ip=ip,
                        device=device[:100]  # 截断避免超长
                    )
                logger.info(f'AI埋点成功：ai_type={ai_type}, user_id={user_id}')
            except IntegrityError as e:
                # 捕获唯一索引异常（重复埋点），仅记录日志
                logger.info(f'AI埋点重复：ai_type={ai_type}, error={str(e)}')
            except Exception as e:
                # 其他异常不影响主业务，仅记录错误
                logger.error(f'AI埋点失败：ai_type={ai_type}, user_id={user_id}, error={str(e)}')

        # 异步执行埋点（不阻塞主业务）
        threading.Thread(target=_async_record).start()