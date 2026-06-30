# -*- coding: utf-8 -*-

"""
@Remark: 字典管理
"""
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from system.models import DictData
from system.serializer.dict_ser import DictDataSerializer
from utils.jsonResponse import SuccessResponse


class DictDataViewSet(APIView):
    """
    字典管理接口:
    """
    permission_classes = [AllowAny]
    queryset = DictData.objects.all()
    serializer_class = DictDataSerializer
    filterset_fields = ['dict_type']

    def get(self, request, dict_type=None):
        queryset = self.queryset.filter(dict_type=dict_type).order_by('dict_sort')
        serializer = self.serializer_class(queryset, many=True)
        return SuccessResponse(serializer.data)