# -*- coding: utf-8 -*-

"""
@Remark: 字典管理
"""
from rest_framework.decorators import action

from system.filter import DictTypeFilter
from system.models import DictType, DictData
from system.serializer.dict_ser import DictTypeSerializer, DictDataSerializer
from utils.jsonResponse import SuccessResponse
from utils.viewset import CustomModelViewSet, CustomDjangoFilterBackend


class DictTypeViewSet(CustomModelViewSet):
    """
    字典管理接口:
    """
    queryset = DictType.objects.all()
    serializer_class = DictTypeSerializer
    filterset_class = DictTypeFilter
    ordering = ['-create_time']

    @action(detail=False, methods=['get'])
    def option_select(self, request):
        queryset = self.filter_queryset(self.get_queryset()).values('id', 'name', 'type')
        serializer = self.serializer_class(queryset, many=True)
        return SuccessResponse(data=serializer.data)


class DictDataViewSet(CustomModelViewSet):
    """
    字典管理接口:
    """
    queryset = DictData.objects.all()
    serializer_class = DictDataSerializer
    filterset_fields = ['dict_type']


    @action(detail=False, methods=['get'], url_path='type/(?P<dict_type>[^/.]+)')
    def get_data_by_code(self, request, dict_type=None):
        queryset = self.queryset.filter(dict_type=dict_type).order_by('dict_sort')
        serializer = self.serializer_class(queryset, many=True)
        return SuccessResponse(serializer.data)