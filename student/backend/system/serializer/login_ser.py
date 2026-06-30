from datetime import datetime, timedelta

from captcha.models import CaptchaStore
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _
from system.models import Users
from utils.exception import BizException
from utils.request_util import save_login_log, get_request_ip


class LoginSerializer(TokenObtainPairSerializer):
    """
    登录的序列化器:
    重写djangorestframework-simplejwt的序列化器
    """
    code = serializers.CharField(max_length=6)

    class Meta:
        model = Users
        fields = "__all__"
        read_only_fields = ["id"]

    default_error_messages = {
        'no_active_account': _('该账号已被禁用,请联系管理员')
    }

    # 开启验证码验证
    def validate_code(self, captcha):
        self.image_code = CaptchaStore.objects.filter(id=self.initial_data['key']).first()
        five_minute_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
        if self.image_code and five_minute_ago > self.image_code.expiration:
            self.image_code and self.image_code.delete()
            raise BizException('验证码过期')
        else:
            if self.image_code and (self.image_code.response == captcha or self.image_code.challenge == captcha):
                self.image_code and self.image_code.delete()
            else:
                self.image_code and self.image_code.delete()
                raise BizException("图片验证码错误")

    def validate(self, attrs):
        username = attrs['username']
        password = attrs['password']
        user = Users.objects.filter(username=username).first()

        request = self.context.get('request')

        if not user:
            result = {
                "code": 400,
                "msg": "账号/密码不正确",
                "data": None
            }
            save_login_log(request=request, status="0", msg="账号/密码不正确", username=username)
            return result

        if user and user.status == "0":
            result = {
                "code": 400,
                "msg": "该账号已被禁用,请联系管理员",
                "data": None
            }
            save_login_log(request=request, status="0", msg="账号被禁用", username=username)
            return result

        if user and user.check_password(password):
            # 关键修改：手动生成JWT token，不调用super().validate(attrs)
            refresh = self.get_token(user)  # 使用查询到的user对象
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            # 设置user实例供DRF simplejwt使用
            self.user = user
            request.user = user

            save_login_log(request=request, status="1", msg="登录成功(图形验证码)")

            # 更新登录 ip
            user.login_ip = get_request_ip(request)
            user.save(update_fields=['login_ip'])

            # 缓存用户的jwt token
            # if IS_SINGLE_TOKEN:
            #     redis_conn = get_redis_connection("singletoken")
            #     k = "hte-single-token{}".format(user.id)
            #     TOKEN_EXPIRE_CONFIG = getattr(settings, 'SIMPLE_JWT', None)
            #     if TOKEN_EXPIRE_CONFIG:
            #         TOKEN_EXPIRE = TOKEN_EXPIRE_CONFIG['ACCESS_TOKEN_LIFETIME']
            #         redis_conn.set(k, data['access'], TOKEN_EXPIRE)

            result = {
                "code": 200,
                "msg": "请求成功",
                "data": data
            }
        else:
            result = {
                "code": 400,
                "msg": "账号/密码不正确",
                "data": None
            }
            save_login_log(request=request, status="0", msg="账号/密码不正确", username=username)
        return result
