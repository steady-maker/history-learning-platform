# -*- coding: utf-8 -*-
import base64

from captcha.models import CaptchaStore
from captcha.views import captcha_image
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from system.constants import USER_AVATAR_PATH
from system.serializer.login_ser import LoginSerializer
from system.serializer.register_ser import RegisterSerializer
from utils.exception import BizException
from utils.jsonResponse import SuccessResponse


class CaptchaView(APIView):
    """
    获取图片验证码
    """
    permission_classes = [AllowAny]

    def get(self, request):
        hashkey = CaptchaStore.generate_key()
        captcha_id = CaptchaStore.objects.filter(hashkey=hashkey).first().id
        image = captcha_image(request, hashkey)
        image_base = base64.b64encode(image.content)
        json_data = {"key": captcha_id, "image_base": image_base.decode('utf-8')}
        return SuccessResponse(data=json_data)

class LoginView(TokenObtainPairView):
    """
    登录接口
    """
    serializer_class = LoginSerializer
    permission_classes = []


class RegisterView(APIView):
    """注册接口"""
    permission_classes = []

    def post(self, request):
        """
        注册接口
        """
        request_data = request.data.copy()
        request_data['avatar'] = USER_AVATAR_PATH
        serializer = RegisterSerializer(data=request_data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            # 注册后自动登录（可选）
            return SuccessResponse(data=None, msg="注册成功")
        raise BizException("注册失败")