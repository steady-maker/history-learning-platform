# -*- coding: utf-8 -*-

"""
@Remark: 菜单模块
"""
from operator import itemgetter

from system.filter import MenuFilter
from system.models import Menu
from system.serializer.menu_ser import MenuSerializer
from system.utils import get_all_menu_dict, build_menu_tree
from utils.jsonResponse import SuccessResponse
from utils.viewset import CustomModelViewSet
from rest_framework.decorators import action


class MenuViewSet(CustomModelViewSet):
    """
    菜单管理接口
    """
    queryset = Menu.objects.all().order_by('sort')
    serializer_class = MenuSerializer
    pagination_class = None
    filterset_class = MenuFilter


    @action(methods=['get'],detail=False)
    def web_router(self, request):
        user = request.user
        role_keys = [r.key for r in user.role.all()]

        if 'admin' in role_keys:
            menus = Menu.objects.filter(status='1').order_by('sort')
        else:
            menus = Menu.objects.filter(
                role__in=user.role.filter(status='1'),
                status='1'
            ).distinct().order_by('sort')

        serializer = MenuSerializer(menus, many=True)
        tree_dict = get_all_menu_dict(serializer.data)

        tree_data = []
        for i in tree_dict:
            parent_id = tree_dict[i].get("parent_id")
            if parent_id:
                parent = tree_dict.get(parent_id)
                # 父节点不存在（被禁用）时跳过该子节点
                if not parent:
                    continue
                parent.setdefault("redirect", "noRedirect")
                parent.setdefault("alwaysShow", True)
                parent.setdefault("children", []).append(tree_dict[i])
                parent["children"] = sorted(parent["children"], key=itemgetter("sort"))
            else:
                tree_data.append(tree_dict[i])

        return SuccessResponse(tree_data)

    @action(methods=["GET"], detail=False)
    def menu_tree(self, request):
        """
        获取部门树结构
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = MenuSerializer(queryset, many=True)
        tree = build_menu_tree(serializer.data)
        return SuccessResponse(tree)
