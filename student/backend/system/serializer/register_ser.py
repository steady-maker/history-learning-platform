# 注册序列化器
from datetime import datetime, timedelta

from captcha.models import CaptchaStore
from rest_framework import serializers

from system.models import Users
from utils.exception import BizException


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=11, min_length=2, error_messages={
        "max_length": "账号长度不能超过11位",
        "min_length": "账号长度不能少于2位",
        "blank": "账号不能为空"
    })
    password = serializers.CharField(write_only=True, error_messages={"blank": "密码不能为空"})
    confirmPassword = serializers.CharField(write_only=True, error_messages={"blank": "确认密码不能为空"})
    code = serializers.CharField(max_length=20, error_messages={"blank": "验证码不能为空"})

    class Meta:
        model = Users
        fields = ['username', 'password', 'confirmPassword', 'code','avatar']

    def validate(self, attrs):
        username = attrs['username']
        password = attrs['password']
        confirm_password = attrs['confirmPassword']

        # 检查用户名是否已存在
        if Users.objects.filter(username=username).exists():
            raise BizException("该用户名已存在")

        # 密码一致性检查
        if password != confirm_password:
            raise BizException("两次输入的密码不一致")

        return attrs

    def create(self, validated_data):
        # 直接使用create方法，然后手动设置密码
        user = Users.objects.create(
            username=validated_data['username'],
            avatar=validated_data['avatar'],
            status="1"  # 默认启用状态
        )
        # 使用set_password方法正确哈希密码
        user.set_password(validated_data['password'])
        user.save()
        return user

    #开启验证码验证
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