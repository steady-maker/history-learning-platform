from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField

from utils.models import CoreModel, admin_table_prefix

class Dept(CoreModel):
    name = models.CharField(max_length=64, verbose_name="部门名称", help_text="部门名称")
    sort = models.IntegerField(default=1, verbose_name="显示排序", help_text="显示排序")
    leader = models.CharField(max_length=32, verbose_name="负责人", null=True, blank=True, help_text="负责人")
    mobile = models.CharField(max_length=32, verbose_name="联系电话", null=True, blank=True, help_text="联系电话")

    status = models.CharField(max_length=1, default="1", verbose_name="部门状态", null=True, blank=True,
                                 help_text="部门状态")
    is_delete = models.CharField(max_length=1, default="0", verbose_name="是否逻辑删除", help_text="是否逻辑删除")
    parent_id = models.BigIntegerField(default=0, verbose_name="上级部门id", help_text="上级部门id")

    class Meta:
        db_table = admin_table_prefix + "dept"
        verbose_name = '部门表'
        verbose_name_plural = verbose_name
        ordering = ('sort',)

class Users(AbstractUser, CoreModel):
    username = models.CharField(max_length=50, unique=True, db_index=True, verbose_name='用户账号', help_text="用户账号")
    email = models.EmailField(max_length=60, verbose_name="邮箱", null=True, blank=True, help_text="邮箱")
    mobile = models.CharField(max_length=30,verbose_name="电话", null=True, blank=True, help_text="电话")
    avatar = models.CharField(max_length=200,verbose_name="头像", null=True, blank=True, help_text="头像")
    name = models.CharField(max_length=40, verbose_name="姓名", null=True, blank=True, help_text="姓名")
    nickname = models.CharField(max_length=100, help_text="用户昵称", verbose_name="用户昵称",default="")
    gender = models.CharField(max_length=1, default="1", verbose_name="性别", null=True, blank=True, help_text="性别")
    date_joined = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='加入时间',
                                       help_text="加入时间")
    role = models.ManyToManyField(to='Role', verbose_name='关联角色', db_constraint=False, help_text="关联角色")
    # dept = models.ForeignKey(Dept, on_delete=models.SET_DEFAULT, default=1, verbose_name="部门", help_text="部门")
    is_delete = models.CharField(max_length=1, default="0", verbose_name="是否逻辑删除", help_text="是否逻辑删除")
    login_ip = models.CharField(max_length=32, verbose_name="最后登录ip", null=True, blank=True, help_text="最后登录ip")
    pwd_update_date = models.DateTimeField(null=True, blank=True, verbose_name='密码最后更新时间', help_text="密码最后更新时间")
    status = models.CharField(max_length=1, default="1", verbose_name="用户状态", null=True, blank=True,
                                 help_text="用户状态")
    class Meta:
        db_table = admin_table_prefix + "users"
        verbose_name = '用户表'
        verbose_name_plural = verbose_name
        ordering = ('-create_time',)

class Role(CoreModel):
    name = models.CharField(max_length=64, verbose_name="角色名称", help_text="角色名称")
    key = models.CharField(max_length=64, verbose_name="权限字符", help_text="权限字符")
    sort = models.IntegerField(default=1, verbose_name="角色顺序", help_text="角色顺序")
    status = models.CharField(max_length=1, default="1", verbose_name="角色状态", help_text="角色状态")
    menu = models.ManyToManyField(to='Menu', verbose_name='关联菜单', db_constraint=False, help_text="关联菜单")
    menu_check_strictly = models.BooleanField(default=True, verbose_name="是否父子联动", help_text="是否父子联动")

    class Meta:
        db_table = admin_table_prefix + 'role'
        verbose_name = '角色表'
        verbose_name_plural = verbose_name
        ordering = ('sort',)

    def __str__(self):
        return self.name

class Menu(CoreModel):
    MENU_TYPE_CHOICES = (
        ("M", "目录"),
        ("C", "菜单"),
        ("F", "按钮"),
    )
    name = models.CharField(max_length=50, verbose_name="菜单名称")
    parent_id = models.BigIntegerField(default=0, verbose_name="父菜单ID")
    sort = models.IntegerField(default=0, verbose_name="显示顺序")
    path = models.CharField(max_length=200, default="", null=True, blank=True, verbose_name="路由地址")
    component = models.CharField(max_length=255, null=True, blank=True, verbose_name="组件路径")
    query = models.CharField(max_length=255, null=True, blank=True, verbose_name="路由参数")
    route_name = models.CharField(max_length=50, default="", null=True, blank=True, verbose_name="路由名称")
    is_frame = models.CharField(max_length=1, default="0", verbose_name="是否为外链（0否 1是）")
    menu_type = models.CharField(max_length=1, choices=MENU_TYPE_CHOICES, default="", verbose_name="菜单类型（M目录 C菜单 F按钮）")
    visible = models.CharField(max_length=1, default="1", verbose_name="菜单状态（0隐藏 1显示）")
    status = models.CharField(max_length=1, default="1", verbose_name="菜单状态（0禁用 1启用）")
    perms = models.CharField(max_length=100, null=True, blank=True, verbose_name="权限标识")
    icon = models.CharField(max_length=100, default="#", verbose_name="菜单图标")

    class Meta:
        db_table = admin_table_prefix + "menu"
        verbose_name = "菜单权限表"
        verbose_name_plural = "菜单权限表"
        ordering = ('sort',)

    def __str__(self):
        return self.name

class DictType(CoreModel):
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="字典名称", help_text="字典名称")
    type = models.CharField(max_length=100, blank=True, null=True, verbose_name="字典类型", help_text="字典类型")
    status = CharField(max_length=1, default="1", blank=True, null=True, verbose_name="状态(0禁用 1启用)", help_text="状态(0禁用 1启用)")


    class Meta:
        db_table = admin_table_prefix + 'dict_type'
        verbose_name = "字典类型表"
        verbose_name_plural = verbose_name
        ordering = ('type',)

class DictData(CoreModel):
    dict_code = models.BigAutoField(primary_key=True, verbose_name="字典编码")
    dict_sort = models.IntegerField(default=0, verbose_name="字典排序")
    dict_label = models.CharField(max_length=100, default="", verbose_name="字典标签")
    dict_value = models.CharField(max_length=100, default="", verbose_name="字典键值")
    dict_type = models.CharField(max_length=100, default="", verbose_name="字典类型")
    css_class = models.CharField(max_length=100, null=True, blank=True, verbose_name="样式属性（其他样式扩展）")
    list_class = models.CharField(max_length=100, null=True, blank=True, verbose_name="表格回显样式")
    is_default = models.CharField(max_length=1, default="N", verbose_name="是否默认（Y是 N否）")
    status = models.CharField(max_length=1, default="0", verbose_name="状态（0禁用 1启用）")

    class Meta:
        db_table = admin_table_prefix + "dict_data"
        verbose_name = "字典数据表"
        verbose_name_plural = verbose_name
        ordering = ["dict_sort", "dict_type"]

    def __str__(self):
        return self.dict_label

class Config(CoreModel):
    name = models.CharField(max_length=100, verbose_name="配置名称", help_text="配置名称")
    key = models.CharField(max_length=100, verbose_name="配置键", help_text="配置键")
    value = models.CharField(max_length=100, verbose_name="配置值", help_text="配置值")
    type = models.CharField(max_length=1, verbose_name="系统内置", help_text="系统内置")

    class Meta:
        db_table = admin_table_prefix + 'config'
        verbose_name = '系统配置'
        verbose_name_plural = verbose_name
        ordering = ('-create_time',)


class LoginTypeEnum(models.IntegerChoices):
    FRONT = 1, '前台登录'
    BACKEND = 2, '后台登录'

class LoginLog(CoreModel):
    username = models.CharField(max_length=32, verbose_name="登录用户名", null=True, blank=True, help_text="登录用户名")
    ip = models.CharField(max_length=32, verbose_name="登录ip", null=True, blank=True, help_text="登录ip")
    agent = models.CharField(max_length=1500,verbose_name="agent信息", null=True, blank=True, help_text="agent信息")
    browser = models.CharField(max_length=200, verbose_name="浏览器名", null=True, blank=True, help_text="浏览器名")
    os = models.CharField(max_length=150, verbose_name="操作系统", null=True, blank=True, help_text="操作系统")
    login_type = models.IntegerField(default=1, choices=LoginTypeEnum, verbose_name="登录类型", help_text="登录类型")
    region = models.CharField(max_length=200, verbose_name="登录地区", null=True, blank=True, help_text="登录地区")
    status = models.CharField(max_length=1, default="1", verbose_name="状态（0失败 1成功）")

    class Meta:
        db_table = admin_table_prefix + 'login_log'
        verbose_name = '登录日志'
        verbose_name_plural = verbose_name
        ordering = ('-create_time',)