import os
import platform
import sys
from datetime import timedelta
from pathlib import Path

from config import *

BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

system = platform.system().lower()
DEBUG = False
if system == "windows":
    DEBUG = True
    BASE_LOG_DIR = os.path.join(BASE_DIR, "logs")
    FILE_PATH = MEDIA_ROOT
elif system in ("linux", "darwin"):  # Linux 或 macOS
    BASE_LOG_DIR = '/var/log/history/'
    FILE_PATH = "/data/history/"
else:
    raise RuntimeError(f"Unsupported system: {system}")

if not os.path.exists(BASE_LOG_DIR):
    os.mkdir(BASE_LOG_DIR)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-&n4wi26se(_@l+rnhk+nh802=pl98y1zu_66)_v=v&)fhq$gs6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    "rest_framework",
    'simple_history',
    'django_apscheduler',
    'captcha',
    'system',
    'biz',
    'common',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'utils.middleware.RequestLogMiddleware',
]

ROOT_URLCONF = 'history_admin_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'history_admin_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': DATABASE_ENGINE,
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
        'PORT': DATABASE_PORT,
        'CONN_MAX_AGE':DATABASE_CONN_MAX_AGE,
        'OPTIONS': {
                    'charset':DATABASE_CHARSET
                }
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"{REDIS_URL}",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 512,  # 连接池的连接(最大连接)
            },
        }
    }
}

REDIS_TIMEOUT = 7 * 24 * 60 * 60
CUBES_REDIS_TIMEOUT = 60 * 60
NEVER_REDIS_TIMEOUT = 365 * 24 * 60 * 60

AUTH_USER_MODEL = 'system.Users'
ALL_MODELS_OBJECTS = []  # 所有app models 对象

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = False # 设置为中国时间


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
UPLOAD_PATH = "upload/"
DOWNLOAD_PATH = "download/"
MEDIA_URL = "/media/"
IMAGE_PATH = os.path.join(MEDIA_ROOT, 'images')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================================================= #
# ******************* 跨域的配置 ******************* #
# ================================================= #
# 如果为True，则将不使用白名单，并且将接受所有来源。默认为False
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_ALL_ORIGINS = True
# Content-Disposition 头部添加到 Access-Control-Expose-Headers 中，允许客户端 JavaScript 访问该头部
CORS_EXPOSE_HEADERS= ['Content-Disposition']

# ================================================= #
# ****************** simplejwt配置 ***************** #
# ================================================= #
SIMPLE_JWT = {
    # token有效时长
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    # token刷新后的有效时间
    'REFRESH_TOKEN_LIFETIME': timedelta(days=3),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'ROTATE_REFRESH_TOKENS': True
}

# ================================================= #
# ********************* 日志配置 ******************* #
# ================================================= #
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s][%(levelname)s]""[%(filename)s:%(lineno)d][%(message)s]"
        }
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",  # 保存到文件，根据时间自动切
            "filename": os.path.join(BASE_LOG_DIR, "history_admin_info.log"),
            "backupCount": 3,  # 备份数为3  xx.log --> xx.log.2018-08-23_00-00-00 --> xx.log.2018-08-24_00-00-00 --> ...
            "when": "D",  # 每天一切， 可选值有S/秒 M/分 H/小时 D/天 W0-W6/周(0=周一) midnight/如果没指定时间就默认在午夜
            "formatter": "standard",
            "encoding": "utf-8",
            "delay": True,
        },
        "warn": {
            "level": "WARNING",
            "class": "logging.handlers.TimedRotatingFileHandler",  # 保存到文件，根据时间自动切
            "filename": os.path.join(BASE_LOG_DIR, "history_admin_warning.log"),
            "backupCount": 3,  # 备份数为3  xx.log --> xx.log.2018-08-23_00-00-00 --> xx.log.2018-08-24_00-00-00 --> ...
            "when": "D",  # 每天一切， 可选值有S/秒 M/分 H/小时 D/天 W0-W6/周(0=周一) midnight/如果没指定时间就默认在午夜
            "formatter": "standard",
            "encoding": "utf-8",
            "delay": True,
        },
        # 专门用来记错误日志
        "error": {
            "level": "ERROR",
            "class": "logging.handlers.TimedRotatingFileHandler",  # 保存到文件，根据时间自动切
            "filename": os.path.join(BASE_LOG_DIR, "history_admin_err.log"),  # 日志文件
            "backupCount": 3,  # 备份数为3  xx.log --> xx.log.2018-08-23_00-00-00 --> xx.log.2018-08-24_00-00-00 --> ...
            "when": "D",  # 每天一切， 可选值有S/秒 M/分 H/小时 D/天 W0-W6/周(0=周一) midnight/如果没指定时间就默认在午夜
            "formatter": "standard",
            "encoding": "utf-8",
            "delay": True,
        },
    },
    "loggers": {
        "info": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": True,  # 向不向更高级别的logger传递
        },
        "warn": {
            "handlers": ["warn"],
            "level": "WARNING",
            "propagate": True,
        },
        "error": {
            "handlers": ["error"],
            "level": "ERROR",
            "propagate": True,
        }
    }
}

# ================================================= #
# *************** REST_FRAMEWORK配置 *************** #
# ================================================= #

REST_FRAMEWORK = {
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",  # 日期时间格式配置
    'DATE_FORMAT': "%Y-%m-%d",
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',

    ),
    'DEFAULT_PAGINATION_CLASS': 'utils.pagination.CustomPagination',  # 自定义分页
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'rest_framework_simplejwt.authentication.JWTTokenUserAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    # 不要修改这里的权限类，避免忘记改的接口被公开访问，公开接口单独加 AllowAny
    # 无需认证的接口需要在ViewSet中配置 permission_classes = [AllowAny]
    'DEFAULT_PERMISSION_CLASSES': (
        'utils.permission.RolePermission',
    ),
    #限速设置
    # 'DEFAULT_THROTTLE_CLASSES': (
    #         'rest_framework.throttling.AnonRateThrottle',   #未登陆用户
    #         'rest_framework.throttling.UserRateThrottle'    #登陆用户
    # ),
    # 'DEFAULT_THROTTLE_RATES': {
    #     'anon': '30/minute',                   #未登录用户每分钟可以请求30次，还可以设置'100/day',天数
    #     'user': '60/minute'                    #已登录用户每分钟可以请求60次
    # },
    'EXCEPTION_HANDLER': 'utils.exception.CustomExceptionHandler',  # 自定义的异常处理
    # #线上部署正式环境，关闭web接口测试页面
            # 'DEFAULT_RENDERER_CLASSES':(
            #     'rest_framework.renderers.JSONRenderer',
            # ),
}

# ================================================= #
# **************** 验证码配置  ******************* #
# ================================================= #
CAPTCHA_STATE = True
CAPTCHA_IMAGE_SIZE = (160, 60)  # 设置 captcha 图片大小
CAPTCHA_LENGTH = 4  # 字符个数
CAPTCHA_TIMEOUT = 1  # 超时(minutes)
CAPTCHA_OUTPUT_FORMAT = '%(image)s %(text_field)s %(hidden_field)s '
CAPTCHA_FONT_SIZE = 42  # 字体大小
CAPTCHA_FOREGROUND_COLOR = '#409eff'  # 前景色
CAPTCHA_BACKGROUND_COLOR = '#FFFFFF'  # 背景色
CAPTCHA_NOISE_FUNCTIONS = (
    'captcha.helpers.noise_arcs', # 线
    # 'captcha.helpers.noise_dots', # 点
)
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge' #字母验证码
# CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge' # 加减乘除验证码


# ================================================= #
# ***************** 其他常量配置  ******************* #
# ================================================= #
MAX_FILE_SIZE = 104857600  # 限制最大文件100MB
