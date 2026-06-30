# -*- coding: utf-8 -*-

"""
@Remark: 题目标签管理
"""
from rest_framework.decorators import action

from question.filter import TagFilter
from question.models import Tag
from question.serializer.tag_ser import TagInfoSerializer
from utils.jsonResponse import SuccessResponse
from utils.viewset import CustomModelViewSet


class TagViewSet(CustomModelViewSet):
    """
    后端标签接口:
    """
    queryset = Tag.objects.all().order_by('-create_time')
    serializer_class = TagInfoSerializer
    filterset_class = TagFilter

    @action(detail=False,methods=['get'])
    def get_tag_tree(self, request):
        """获取标签树"""
        # 获取所有标签
        tags = list(Tag.objects.all().values('id', 'name', 'parent_id'))

        # 构建节点映射
        tag_dict = {}
        for tag in tags:
            tag_dict[tag['id']] = {
                'value': tag['id'],
                'label': tag['name'],
                'children': []
            }

        # 构建树结构
        tree = []
        for tag in tags:
            node = tag_dict[tag['id']]
            parent_id = tag['parent_id']

            if parent_id and parent_id in tag_dict:
                # 添加到父节点
                tag_dict[parent_id]['children'].append(node)
            else:
                # 根节点
                tree.append(node)

        return SuccessResponse(msg="success", data=tree)







