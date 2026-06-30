# -*- coding: utf-8 -*-

"""
@Remark: 自定义的JsonResonpse文件
"""

from rest_framework.response import Response
from utils.code import OK, BAD, SERVER_ERROR


class SuccessResponse(Response):
    """
    不包含分页信息的接口返回,主要用于单条数据查询
    (1)默认code返回 200, 不支持指定其他返回码
    """

    def __init__(self, data=None, msg='success', status=OK, template_name=None, headers=None, exception=False,
                 content_type=None, count = None):
        std_data = {
            "code": 200,
            "data": data,
            "msg": msg
        }
        if count is not None:
            std_data["count"] = count
        super().__init__(std_data, status, template_name, headers, exception, content_type)

class ErrorResponse(Response):
    """
    不要使用这个返回，直接用 BizException 抛出异常
    """
    def __init__(self, data=None, msg='error', code=500, status=SERVER_ERROR, template_name=None, headers=None,
                 exception=False, content_type=None):
        std_data = {
            "code": code,
            "data": data,
            "msg": msg
        }
        super().__init__(std_data, status, template_name, headers, exception, content_type)
