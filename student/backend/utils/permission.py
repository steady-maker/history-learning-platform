# -*- coding: utf-8 -*-

"""
@Remark: 自定义权限
"""

from rest_framework.permissions import IsAuthenticated


class RolePermission(IsAuthenticated):
    """
    基于角色和菜单权限的 DRF 权限类
    """

    @staticmethod
    def get_permission_from_role(request):
        """
        根据用户角色返回权限列表
        超管角色（key='admin'）返回 ['*:*:*']
        普通角色返回角色菜单的 perms 列表
        """
        return ['*:*:*']
        # user = request.user
        # if not user or not user.is_authenticated:
        #     return []
        #
        # perms_set = set()
        # for role in user.role.prefetch_related('menu').all():
        #     if role.key == 'admin':
        #         return ['*:*:*']  # 超管直接返回全部权限
        #     for menu in role.menu.all():
        #         if menu.perms:
        #             perms_set.add(menu.perms)
        #
        # return list(perms_set)

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        perms = self.get_permission_from_role(request)

        # 如果用户是超管，直接允许访问
        if '*:*:*' in perms:
            return True

        # 如果 view 没有 perms_map 属性，也允许访问
        if not hasattr(view, "perms_map"):
            return True

        # 当前方法名
        method_name = view.action if hasattr(view, 'action') else view.basename

        # 遍历 view 的 perms_map 判断是否有权限
        perms_map = view.perms_map
        for method, perm in perms_map.items():
            if method_name == method or method == "*":
                if perm == "*":  # "*" 表示不需要配置权限，登录即可访问
                    return True
                elif perm in perms:  # 普通权限匹配
                    return True

        # 没有匹配权限，拒绝访问
        return False
