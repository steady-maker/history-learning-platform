from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models.base import Model

from apps.biz.constants import QuestionTypeEnum
from utils.models import CoreModel, admin_table_prefix, make_uuid, web_table_prefix

class WebUser(AbstractBaseUser, CoreModel):
    """前台用户表"""
    mobile = models.CharField(max_length=30, unique=True, db_index=True, null=True, blank=True, verbose_name="电话",
                              help_text="电话")
    username = models.CharField(max_length=50, unique=True, db_index=True, verbose_name='用户名', help_text="用户名")
    password = models.CharField(max_length=20, verbose_name="密码", help_text="密码")
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

    USERNAME_FIELD = "mobile"
    REQUIRED_FIELDS = []

class Question(CoreModel):
    """题目表"""
    code = models.CharField(max_length=100,unique=True,db_index=True,verbose_name="题目唯一编号",help_text="题目唯一编号")
    content = models.TextField(verbose_name="题目内容",help_text="题目内容")
    is_high_frequency = models.CharField(max_length=1,default="0",blank=True,verbose_name="是否高频考点",help_text="是否高频考点")
    score = models.IntegerField(default=1,blank=True,verbose_name="题目分值",help_text="题目分值")
    difficulty = models.CharField(max_length=1,blank=True,default=1,verbose_name="题目难度，1：低；2：中；3：高",help_text="题目难度，1：低；2：中；3：高")
    finish_time = models.IntegerField(blank=True,null=True,verbose_name="题目建议完成时间")
    img_list = models.JSONField(default=list,blank=True,verbose_name="相关图片",help_text="相关图片")
    tags = models.ManyToManyField("Tag", blank=True, db_table=admin_table_prefix+"question_tag", verbose_name="关联标签")
    has_sub_question = models.CharField(max_length=1,default="0",blank=True,null=True,verbose_name="是否有子问题,0:否;1:是",help_text="是否有子问题,0:否;1:是")
    prompts = models.ManyToManyField(
        "Prompt",  # 关联提示词表
        blank=True,
        db_table=admin_table_prefix + "question_prompt",  # 指定中间表名（可选）
        verbose_name="关联提示词",
        help_text="关联的各类提示词（提示时/打分时/复盘时）"
    )
    status = models.CharField(max_length=1, default="0",blank=True,verbose_name="题目审核状态，0：未审核；1：已审核；2：已上架",help_text="题目审核状态，0：未审核；1：已审核；2：已上架")
    type = models.CharField(
        max_length=1,
        verbose_name="题目类型",
        choices=QuestionTypeEnum.get_choices(),
        default=QuestionTypeEnum.SHORT_ANSWER.value[0]  # 默认问答
    )

    class Meta:
        db_table = admin_table_prefix + "question"
        verbose_name = '题目表'
        verbose_name_plural = verbose_name
        ordering = ('-create_time',)

    REQUIRED_FIELDS = []

class QuestionOption(models.Model):
    """题目选项表（选择题）"""
    question_id = models.IntegerField(blank=True,null=True,db_index=True,verbose_name="关联题目id",help_text="关联题目id")
    sub_question_id = models.IntegerField(blank=True,null=True,db_index=True,verbose_name="子问题id",help_text="子问题id")
    option_content = models.TextField(verbose_name="选项内容",help_text="选项内容")
    option_label = models.CharField(max_length=2,verbose_name="选项标签，如A，B，C",help_text="选项标签，如A，B，C")
    is_correct = models.CharField(max_length=1,blank=True,null=True,default="0",verbose_name="该选项是否正确答案",help_text="该选项是否正确答案")
    # sort = models.SmallIntegerField(verbose_name="选项排序",help_text="选项排序")

    class Meta:
        db_table = admin_table_prefix + "question_option"
        verbose_name = '题目选项表（选择题）'
        verbose_name_plural = verbose_name
        ordering = ('question_id',)

    REQUIRED_FIELDS = []

class SubQuestion(models.Model):
    """子问题表"""
    question_id = models.IntegerField(db_index=True,verbose_name="关联题目id",help_text="关联题目id")
    sub_content = models.TextField(verbose_name="子问题内容",help_text="子问题内容")
    score = models.IntegerField(default=1,blank=True,verbose_name="题目分值",help_text="题目分值")

    class Meta:
        db_table = admin_table_prefix + "sub_question"
        verbose_name = '子问题表'
        verbose_name_plural = verbose_name
        ordering = ('-question_id',)

    REQUIRED_FIELDS = []

class QuestionAnswer(models.Model):
    """问题答案表"""
    question_id = models.IntegerField(blank=True,null=True,db_index=True,verbose_name="关联题目id",help_text="关联题目id")
    sub_question_id = models.IntegerField(blank=True,null=True,db_index=True,verbose_name="子问题id",help_text="子问题id")
    answer_content = models.TextField(verbose_name="题目答案",help_text="题目答案")

    class Meta:
        db_table = admin_table_prefix + "question_answer"
        verbose_name = '问题答案表'
        verbose_name_plural = verbose_name
        ordering = ('-question_id','-sub_question_id')

    REQUIRED_FIELDS = []

class Tag(CoreModel):
    """题目标签表"""
    name = models.CharField(max_length=100,verbose_name="标签名称",help_text="标签名称")
    tag_key = models.CharField(max_length=100,verbose_name="标签key",help_text="标签key")
    parent_id = models.IntegerField(blank=True,null=True,verbose_name="父标签id",help_text="父标签id")
    status = models.CharField(max_length=1,default="0",blank=True,verbose_name="标签启用状态，0:停用",help_text="标签启用状态，0:停用")

    class Meta:
        db_table = admin_table_prefix + "tag"
        verbose_name = '题目标签表'
        verbose_name_plural = verbose_name
        ordering = ('-create_time',)

    REQUIRED_FIELDS = []

class Prompt(CoreModel):
    """提示词表"""
    prompt_content = models.TextField(verbose_name="提示词内容",help_text="提示词内容")
    is_public = models.CharField(max_length=1, blank=True, null=True,default='0',verbose_name="是否公共提示词,0：否；1：是",help_text="是否公共提示词,0：否；1：是")
    type = models.CharField(max_length=1,blank=True, null=True,default='1',verbose_name="提示词类型，1：进行提示时提示词；2：复盘时提示词；3：AI判断答案时提示词")
    tags = models.ManyToManyField("Tag", blank=True, db_table=admin_table_prefix+"prompt_tag", verbose_name="关联题目标签，用于公共提示")
    status = models.CharField(max_length=1,default="0",blank=True,verbose_name="标签启用状态，0:停用;1：启用",help_text="标签启用状态，0:停用；1：启用")

    class Meta:
        db_table = admin_table_prefix + "prompt"
        verbose_name = '提示词表'
        verbose_name_plural = verbose_name
        ordering = ('-create_time',)

    REQUIRED_FIELDS = []

class UserFeedback(CoreModel):
    """用户反馈表"""
    user_id = models.IntegerField(db_index=True,verbose_name="用户id",help_text="用户id")
    content = models.TextField(blank=True,null=True,verbose_name="反馈内容",help_text="反馈内容")
    feedback_status = models.CharField(max_length=1,default="0",blank=True,verbose_name="反馈状态，0:待处理;1：处理中;2：处理完成",help_text="反馈状态，0:待处理；1：处理中；2：处理完成")

    class Meta:
        db_table = web_table_prefix + "user_feedback"
        verbose_name = '用户反馈表'
        verbose_name_plural = verbose_name
        ordering = ('-create_time',)

    REQUIRED_FIELDS = []

# class StatisticalAnalysis(CoreModel):
#     """题目统计分析,暂时不用"""
#     question_id = models.IntegerField(verbose_name="题目id",help_text="题目id")
