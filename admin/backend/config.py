SECRET_KEY = 'ml9z79*y7h9za=4jl#p3*eo^*i*$_#_+0ppty$n_=_x)vs!nsq'
AES_KEY_b64 = 'pHndiG/zgLLKBfNltL6ZNJuITt8y13pUBB2P5AIPNYQ='
AES_IV_b64 = '0ETL0yPXc4YWCOpFFGxwuA=='
# ================================================= #
# ************** mysql数据库 配置  ************** #
# ================================================= #
# 数据库地址
DATABASE_ENGINE = "django.db.backends.mysql"
# 数据库地址
DATABASE_HOST = "localhost"
# 数据库端口
DATABASE_PORT = 3306
# 数据库用户名
DATABASE_USER = "root"
# 数据库密码
DATABASE_PASSWORD = "123456"
# 数据库名
DATABASE_NAME = "history_all"
#数据库编码
DATABASE_CHARSET = "utf8mb4"
# 数据库长连接时间（默认为0，单位秒）即每次请求都重新连接
DATABASE_CONN_MAX_AGE = 0 # debug模式下该值应该写为0(防止调试频繁建立长连接但未销毁)，mysql默认长连接超时时间为8小时

# ================================================= #
# ************** redis 配置  ************** #
# ================================================= #

REDIS_PASSWORD = ''
REDIS_HOST = 'localhost'
REDIS_PORT = '6379'
REDIS_DB = 0
REDIS_URL = f'redis://:{REDIS_PASSWORD or ""}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'


# ================================================= #
# ************** 系统信息配置  ************** #
# ================================================= #
# 系统版本号
SYSTEM_VERSION = "1.0.0"
# 服务启动时间（全局变量）
import time
STARTUP_TIME = time.time()