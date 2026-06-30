import base64
import json
import logging
import threading
import uuid
import traceback
from django.utils.deprecation import MiddlewareMixin

from utils.request_util import get_request_ip

local = threading.local()  # 获取当前线程对象

info_logger = logging.getLogger("info")
error_logger = logging.getLogger("error")


class RequestLogFilter(logging.Filter):
    """
    日志过滤器，将当前请求线程的request信息保存到日志的record上下文
    record带有formater需要的信息。
    """

    def filter(self, record):
        record.method = getattr(local, 'method', "none")
        record.path = getattr(local, 'path', "none")
        record.request_id = getattr(local, 'request_id', "none")
        record.params = getattr(local, 'params', "none")
        record.body = getattr(local, 'body', "none")
        record.user = getattr(local, 'user', "none")
        return True


class RequestLogMiddleware(MiddlewareMixin):
    """
    将request的信息记录在当前的请求线程上。
    """
    def process_request(self, request):
        # 以下逻辑是 实现请求进来打印 相关请求参数
        local.request_id = str(uuid.uuid1())  # 线程对象里面加入uuid
        body = {}
        try:
            body = request.body.decode()
            if body:
               body = json.loads(body)
        except:
            pass
        token = request.META.get("HTTP_AUTHORIZATION")
        local.user = "guest"
        if token:
            try:
                user_base64 = token.split(".")[1]
                missing_padding = 4 - len(user_base64) % 4
                if missing_padding:
                    user_base64 += '=' * missing_padding

                local.user = str(base64.b64decode(bytes(user_base64, 'utf-8')), encoding='utf-8')
            except:
                local.user = token
                pass

        local.method = request.method
        local.params = request.GET.dict()
        local.path = request.path_info
        local.body = json.dumps(body)
        local.ip = get_request_ip(request)

        request_info = {
            "ip": get_request_ip(request),
            "request_id": local.request_id,
            'method': request.method,
            'path': request.path_info,
            'params': request.GET.dict(),
            'body': body,
            'user': local.user,
        }

        info_logger.info(f'requests: {json.dumps(request_info, ensure_ascii=False)}')

    def process_response(self, request, response):
            """
            当请求是媒体请求时，需要设置对应的响应头以方便浏览器可以缓存媒体的当前播放时间，从而解决拉进度条会回弹到原点的bug
            """
            if request.path.endswith(".mp3"):
                response["Accept-Ranges"] = "bytes"
            token = request.META.get("HTTP_AUTHORIZATION")
            local.user = "guest"
            if token:
                try:
                    user_base64 = token.split(".")[1]
                    missing_padding = 4 - len(user_base64) % 4
                    if missing_padding:
                        user_base64 += '=' * missing_padding

                    local.user = str(base64.b64decode(bytes(user_base64, 'utf-8')), encoding='utf-8')
                except Exception as e:
                    local.user = token
                    error_logger.error(
                        "process_response failed:  \n%s" % (traceback.format_exc()))
                    pass
            data = response.status_code
            # if response.data:
            #     data = response.data
            local.method = request.method
            local.params = request.GET.dict()
            local.path = request.path_info
            local.ip = get_request_ip(request)
            local.response = data

            request_info = {
                "ip": get_request_ip(request),
                "request_id": local.request_id,
                'method': request.method,
                'path': request.path_info,
                'params': request.GET.dict(),
                'user': local.user,
                "response": data,
            }

            info_logger.info('response: %r' % request_info)
            return response

