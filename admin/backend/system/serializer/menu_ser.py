from rest_framework import serializers

from system.models import Menu
from utils.exception import BizException
from utils.serializers import CustomModelSerializer
from utils.validator import CustomUniqueValidator


class MenuSerializer(CustomModelSerializer):
    """
    菜单序列化
    """
    name = serializers.CharField(
        validators=[CustomUniqueValidator(queryset=Menu.objects.all(), message="菜单名称已存在，请换一个")]
    )
    class Meta:
        model = Menu
        fields = "__all__"

    def validate(self, attrs):
        menu_type = attrs.get("menu_type") or getattr(self.instance, "menu_type", None)

        msg = ""

        if menu_type in ["M", "C"]:
            if not attrs.get("path"):
                msg = "路由地址不能为空"

        if msg:
            raise BizException(msg)

        return attrs