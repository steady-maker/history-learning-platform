from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.db.models import CharField
from django.utils import timezone

from utils.models import CoreModel, web_table_prefix, admin_table_prefix


class Users(AbstractBaseUser, CoreModel):
    mobile = models.CharField(max_length=30, unique=True, db_index=True,null=True, verbose_name="电话", help_text="电话")
    username = models.CharField(max_length=50,unique=True, db_index=True, verbose_name='用户名', help_text="用户名")
    password = models.CharField(max_length=20,verbose_name="密码",help_text="密码")
    email = models.EmailField(max_length=60, null=True, blank=True, verbose_name="邮箱", help_text="邮箱")
    avatar = models.CharField(max_length=200, null=True, blank=True, verbose_name="头像", help_text="头像")
    gender = models.CharField(max_length=1, default="1", verbose_name="性别", null=True, blank=True, help_text="性别")
    login_ip = models.CharField(max_length=32, null=True, blank=True, verbose_name="最后登录ip", help_text="最后登录ip")
    status = models.CharField(max_length=1, default="1", null=True, blank=True, verbose_name="用户状态",
                                 help_text="用户状态")
    class Meta:
        db_table = web_table_prefix + "users"
        verbose_name = '用户表'
        verbose_name_plural = verbose_name
        ordering = ('-create_time',)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []


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
    type = models.CharField(max_length=100, verbose_name="系统内置", help_text="系统内置（Y是 N否）")

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

class AIOperationLog(models.Model):
    """AI操作埋点日志Model"""
    # AI类型枚举
    AI_TYPE_CHOICES = (
        ('1', 'AI提示'),
        ('2', 'AI判题'),
        ('3', 'AI复盘'),
    )
    # 业务类型枚举
    BUSINESS_TYPE_CHOICES = (
        ('subjective_answer', '主观题答题'),
        ('objective_answer', '客观题答题'),
    )

    user_id = models.BigIntegerField(verbose_name='操作用户ID', db_index=True)
    ai_type = models.CharField(
        verbose_name='AI操作类型',
        max_length=1,
        choices=AI_TYPE_CHOICES,
        db_index=True
    )
    # business_id = models.BigIntegerField(verbose_name='关联业务ID')  # 答题ID/复盘ID,暂时为冗余字段
    # business_type = models.CharField(
    #     verbose_name='业务类型',
    #     max_length=20,
    #     choices=BUSINESS_TYPE_CHOICES
    # )   # 题目类型，暂时不用
    ip = models.CharField(verbose_name='用户IP', max_length=50, default='')
    device = models.CharField(verbose_name='设备信息', max_length=100, default='')
    create_time = models.DateTimeField(
        verbose_name='操作时间',
        # auto_now_add=True 等价于 default=timezone.now 且不可修改
        default=timezone.now,
        db_index=True
    )

    class Meta:
        db_table = web_table_prefix + 'ai_operation_log'
        verbose_name = 'AI操作日志'
        verbose_name_plural = 'AI操作日志'
        ordering = ['-create_time']
        # 幂等兜底：联合唯一索引（杜绝重复埋点），暂时不需要
        # unique_together = [('business_type', 'business_id', 'ai_type')]
        # 统计优化：AI类型+时间联合索引
        indexes = [
            models.Index(fields=['ai_type', 'create_time']),
            models.Index(fields=['user_id', 'ai_type']),
        ]

    def __str__(self):
        return f'{self.get_ai_type_display()}-用户{self.user_id}-{self.create_time.strftime("%Y-%m-%d")}'