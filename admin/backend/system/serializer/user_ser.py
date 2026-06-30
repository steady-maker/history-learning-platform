from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from system.models import Users, Dept, Role
from system.utils import get_init_pwd
from utils.serializers import CustomModelSerializer
from utils.validator import CustomUniqueValidator


class UserSerializer(CustomModelSerializer):
    """
    用户管理-序列化器
    """
    username = serializers.CharField(
        validators=[CustomUniqueValidator(queryset=Users.objects.all(), message="用户名已存在，请换一个")]
    )
    mobile = serializers.CharField(
        validators=[CustomUniqueValidator(queryset=Users.objects.all(), message="手机号已存在，请换一个")]
    )
    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        many=True,
    )

    class Meta:
        model = Users
        read_only_fields = ["id"]
        exclude = ['password','first_name','last_name', 'is_active', 'is_superuser', 'is_staff', 'last_login']

    def get_role(self, obj):
        return list(obj.role.values_list('id', flat=True))

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user") and str(request.user) != "AnonymousUser":
            user = request.user
            validated_data.setdefault("create_by", user.id)
            validated_data.setdefault("create_name", user.username)
            validated_data.setdefault("update_by", user.id)
            validated_data.setdefault("update_name", user.username)

        roles_data = validated_data.pop('role', [])

        init_pwd = get_init_pwd()

        user = Users(**validated_data)
        user.set_password(init_pwd)
        user.save()

        if roles_data:
            user.role.set(roles_data)

        return user

class UserInfoSerializer(ModelSerializer):
        """
        用户信息-序列化器
        """

        # 角色和权限集合
        roles = serializers.SerializerMethodField()
        permissions = serializers.SerializerMethodField()

        class Meta:
            model = Users
            fields = ["id", "username", "nickname", "mobile", "email", "avatar", 'gender', "create_time",
                      "pwd_update_date", "roles", "permissions"]

        def get_roles(self, obj):
            return [r.key for r in obj.role.filter(status='1')]

        def get_permissions(self, obj):
            perms_set = set()
            for r in obj.role.filter(status='1'):
                if r.key == 'admin':
                    return ['*:*:*']

                for m in r.menu.all():
                    if m.perms:
                        perms_set.add(m.perms)
            return list(perms_set)
