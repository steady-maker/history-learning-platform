from utils.redis import WEB_KEY_PREFIX

REDIS_SMS_CODE_KEY_PREFIX: str = f"{WEB_KEY_PREFIX}sms:code:"
REDIS_SMS_MINUTE_KEY_PREFIX: str = f"{WEB_KEY_PREFIX}sms:minute:"
REDIS_SMS_DAILY_KEY_PREFIX: str = f"{WEB_KEY_PREFIX}sms:daily:"
REDIS_SLIDER_KEY_PREFIX: str = f"{WEB_KEY_PREFIX}slider:"


# 用户默认头像
USER_AVATAR_PATH = 'http://127.0.0.1:19000/media/images/default-avatar-boy.png'