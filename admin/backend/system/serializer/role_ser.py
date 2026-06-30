from rest_framework import serializers

from system.models import Role
from utils.serializers import CustomModelSerializer
from utils.validator import CustomUniqueValidator


class RoleSerializer(CustomModelSerializer):
    """
    角色-序列化器
    """
    name = serializers.CharField(
        validators=[CustomUniqueValidator(queryset=Role.objects.all(), message="角色名称已存在，请换一个")]
    )
    key = serializers.CharField(
        validators=[CustomUniqueValidator(queryset=Role.objects.all(), message="权限字符已存在，请换一个")]
    )
    class Meta:
        model = Role
        fields = "__all__"
        read_only_fields = ["id"]