import os
import re
from datetime import datetime

from django.http import HttpResponse

from history_web_backend.settings import MAX_FILE_SIZE, FILE_PATH, UPLOAD_PATH, MEDIA_ROOT
from utils.exception import BizException
from utils.jsonResponse import SuccessResponse
from utils.viewset import CustomModelViewSet


class FileViewSet(CustomModelViewSet):
    """
    文件上传下载接口
    """

    @staticmethod
    def upload(request, *args, **kwargs):
        upload_file = request.FILES.get("file")
        module_name = request.data.get("module_name")
        if not module_name:
            raise BizException("请输入模块名")
        if not upload_file:
            raise BizException("请上传文件")

        # 校验文件大小
        if upload_file.size > MAX_FILE_SIZE:
            raise BizException("上传文件需小于或等于100MB")

        # 安全过滤 file_type
        file_type = re.sub(r'[^a-zA-Z0-9_-]', '', module_name)

        name, ext = os.path.splitext(upload_file.name)
        time_stamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]

        save_path = os.path.join(FILE_PATH, UPLOAD_PATH, file_type)
        os.makedirs(save_path, exist_ok=True)

        file_name = time_stamp + ext

        file_disk_path = os.path.join(str(save_path), file_name)

        with open(file_disk_path, 'wb') as f:
            for chunk in upload_file.chunks():
                f.write(chunk)

        show_path = os.path.join(UPLOAD_PATH, file_type, file_name).replace('\\', '/')
        return SuccessResponse(show_path)

    @staticmethod
    def download(request, *args, **kwargs):
        search_type = request.data.get("search_type")
        if not search_type:
            raise BizException("请输入搜索类型")

        if search_type not in ["path", "name"]:
            raise BizException("搜索类型错误")

        if search_type == "path":
            # 按文件路径直接去找文件
            file_path = request.data.get("file_path")
            if not file_path:
                raise BizException("请输入文件路径")
            path = os.path.join(FILE_PATH, file_path.lstrip('/')).replace('\\', '/')
            if not os.path.exists(path):
                raise BizException("文件不存在")
            with open(path, 'rb') as f:
                response = HttpResponse(
                    f.read(),
                    content_type='application/octet-stream'
                )

            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(path)}"'
            return response

        else:
            # 按文件名一定是去 media 拿模板文件
            file_name = request.data.get("file_name")
            if not file_name:
                raise BizException("请输入文件名")

            path = os.path.join(MEDIA_ROOT, file_name).replace('\\', '/')

            if not os.path.exists(path):
                raise BizException("文件不存在")

            with open(path, 'rb') as f:
                response = HttpResponse(
                    f.read(),
                    content_type='application/octet-stream'
                )

            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
