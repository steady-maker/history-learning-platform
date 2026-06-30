# -*- coding: utf-8 -*-

"""
@Remark: 自定义异常处理
"""
import traceback

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import exceptions
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, APIException, PermissionDenied, NotFound, \
    MethodNotAllowed
from rest_framework.views import exception_handler
from utils.code import BAD, SERVER_ERROR, UNAUTHORIZED, NOT_FOUND
from utils.jsonResponse import ErrorResponse
from utils.middleware import error_logger


def CustomExceptionHandler(ex, context):
    """
    统一异常拦截处理
    """
    msg = ''
    code = 500
    status = SERVER_ERROR
    response = exception_handler(ex, context)
    if isinstance(ex, AuthenticationFailed):
        code = 401
        if 'User is inactive' in str(ex.detail):
            msg = "该账号已被禁用,请联系管理员"
        elif response and response.data.get("detail") == "Given token not valid for any token type":
            msg = "身份认证已过期"
        else:
            msg = ex.detail
        status = UNAUTHORIZED
    elif isinstance(ex, NotAuthenticated):
        code = 401
        msg = ex.detail
        status = UNAUTHORIZED
    elif isinstance(ex, Http404):
        code = 404
        msg = "您访问的地址不存在"
        status = NOT_FOUND
    elif isinstance(ex,NotFound):
        code = 404
        msg = "您访问的地址不存在"
        status = NOT_FOUND
    elif isinstance(ex, BizException):
        msg = ex.detail
        code = ex.default_code
        status = ex.status_code
    elif isinstance(ex, PermissionDenied):
        msg = "您没有权限访问该资源"
        code = 403
        status = ex.status_code
    elif isinstance(ex, ObjectDoesNotExist):
        msg = "当前数据不存在，请刷新页面重试"
        code = 400
        status = BAD
        error_logger.error(traceback.format_exc())
    elif isinstance(ex, MethodNotAllowed):
        msg = ex.detail
        code = 405
        status = ex.status_code
        error_logger.error(traceback.format_exc())
    elif isinstance(ex, exceptions.APIException):
        msg = "接口服务异常，请稍后再试或联系管理员"
        status = ex.status_code
        error_logger.error(traceback.format_exc())
    elif isinstance(ex, Exception):
        msg = "系统异常，请稍后再试或联系管理员"
        error_logger.error(traceback.format_exc())

    return ErrorResponse(msg=msg, code=code, status=status)

class BizException(APIException):
    status_code = BAD
    default_detail = '业务异常'
    default_code = 400

    def __init__(self, msg=None, code=None):
        if msg is not None:
            self.detail = msg
        else:
            self.detail = self.default_detail

        if code is not None:
            self.default_code = code

def custom_page_not_found_view(request, exception):
    return ErrorResponse(
        code=404,
        msg="您访问的地址不存在")
