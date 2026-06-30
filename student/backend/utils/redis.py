from django_redis import get_redis_connection

redis_conn = get_redis_connection('default')

ADMIN_KEY_PREFIX: str = 'history_admin:'
WEB_KEY_PREFIX: str = 'history_web:'