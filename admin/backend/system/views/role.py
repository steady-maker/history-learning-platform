from django.db.models import Q
from rest_framework.decorators import action

from system.filter import RoleFilter, UserFilter
from system.models import Role, Users
from system.serializer.role_ser import RoleSerializer
from system.serializer.user_ser import UserSerializer
from utils.jsonResponse import SuccessResponse
from utils.viewset import CustomModelViewSet


class RoleViewSet(CustomModelViewSet):
    """
    角色管理接口:
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    filterset_class = RoleFilter
    perms_map = {
        "list": "system:role:list",
        "retrieve": "system:role:get",
        "create": "system:role:add",
        "update": "system:role:edit",
        "partial_update": "system:role:edit",
        "destroy": "system:role:rm",
        "users" : "system:role:add",
        "unallocated_users" : "system:role:rm",
        "allocate" : "system:role:rm",
        "deallocate" : "system:role:rm",
    }

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        if not user.id == 1:
            qs = qs.exclude(id=1)
        return qs

    @action(detail=True)
    def users(self, request, pk=None):
        queryset = Users.objects.filter(role__id=pk)

        filterset = UserFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserSerializer(queryset, many=True)
        return SuccessResponse(serializer.data)

    @action(detail=True)
    def unallocated_users(self, request, pk=None):
        queryset = Users.objects.exclude(Q(role__id=pk) | Q(id=1))
        filterset = UserFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserSerializer(queryset, many=True)
        return SuccessResponse(serializer.data)

    @action(detail=True, methods=['PUT'])
    def allocate(self, request, pk=None):
        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return SuccessResponse()

        role = Role.objects.get(id=pk)
        user_ids = user_ids.split(',')
        users = Users.objects.filter(id__in=user_ids)
        for user in users:
            user.role.add(role)

        return SuccessResponse(msg="用户角色分配成功")

    @action(detail=True, methods=['PUT'])
    def deallocate(self, request, pk=None):
        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return SuccessResponse()

        role = Role.objects.get(id=pk)
        user_ids = user_ids.split(',')
        users = Users.objects.filter(id__in=user_ids)
        for user in users:
            user.role.remove(role)

        return SuccessResponse(msg="用户角色取消分配成功")

