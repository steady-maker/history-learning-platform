from django.db import models
from django.db.models.aggregates import Max
from django.utils import timezone
from redis.commands.search.field import TextField

from question.constants import QuestionTypeEnum
from utils.models import CoreModel, admin_table_prefix, web_table_prefix


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
    is_ai_answer = models.CharField(max_length=1,blank=True,null=True,default="0",verbose_name="是否AI生成答案,0：否；1：是",help_text="是否AI生成答案,0：否；1：是")
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True,verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True,verbose_name="修改时间")

    class Meta:
        db_table = admin_table_prefix + "question_answer"
        verbose_name = '问题答案表'
        verbose_name_plural = verbose_name
        ordering = ('-create_time',)

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
    type = models.CharField(max_length=1,blank=True, null=True,default='1',verbose_name="提示词类型，1：获取提示时提示词；2：复盘时提示词；3：AI判断答案时提示词")
    tags = models.ManyToManyField("Tag", blank=True, db_table=admin_table_prefix+"prompt_tag", verbose_name="关联题目标签，用于公共提示")
    status = models.CharField(max_length=1,default="0",blank=True,verbose_name="标签启用状态，0:停用;1：启用",help_text="标签启用状态，0:停用；1：启用")

    class Meta:
        db_table = admin_table_prefix + "prompt"
        verbose_name = '提示词表'
        verbose_name_plural = verbose_name
        ordering = ('-create_time',)

    REQUIRED_FIELDS = []

class UserAnswer(models.Model):
    """用户题目回答情况表"""
    question_id = models.IntegerField(blank=True,null=True,db_index=True,verbose_name="关联题目id",help_text="关联题目id")
    sub_question_id = models.IntegerField(blank=True, null=True, db_index=True, verbose_name="子问题id",help_text="子问题id")
    user_id = models.IntegerField(blank=True,null=True,db_index=True,verbose_name="用户id",help_text="用户id")
    user_answer = models.TextField(blank=True,null=True,verbose_name="用户作答内容",help_text="用户作答内容")
    got_score = models.IntegerField(blank=True,null=True,verbose_name="用户本题得分",help_text="用户本题得分")
    answer_seq = models.IntegerField(blank=True,null=True,verbose_name="用户回答本题第x次")
    cost_time = models.IntegerField(blank=True,null=True,verbose_name="用户本题耗时(整体)")

    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True,verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True,verbose_name="修改时间")

    class Meta:
        db_table = web_table_prefix + "user_answer"
        verbose_name = '用户题目回答情况表'
        verbose_name_plural = verbose_name
        ordering = ('-create_time',)

    REQUIRED_FIELDS = []

class QuestionChatSession(models.Model):
    """用户AI提示词使用记录表"""
    user_id = models.IntegerField(db_index=True,verbose_name="用户id",help_text="用户id")
    question_id = models.IntegerField(blank=True, null=True, db_index=True, verbose_name="关联题目id",
                                      help_text="关联题目id")
    session_id = models.CharField(max_length=64,unique=True,verbose_name="会话ID")
    messages = models.JSONField(default=list,verbose_name="对话记录（OpenAI格式）")
    remaining_attempts = models.IntegerField(default=3,blank=True,null=True,verbose_name="剩余次会话次数",help_text="剩余次数")
    chat_seq = models.IntegerField(blank=True,null=True,verbose_name="用户回答本题第x次")

    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True,verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True,verbose_name="修改时间")

    class Meta:
        db_table = web_table_prefix + "question_chat_session"
        verbose_name = '题目对话会话表'
        verbose_name_plural = verbose_name
        ordering = ('-create_time',)

    REQUIRED_FIELDS = []

    @classmethod
    def get_or_create_session(cls, user_id, question_id, session_id=None):
        """获取/创建会话（前端传session_id则复用，否则新建）"""
        import uuid

        # 1. 生成会话ID（不传则新建）
        if not session_id:
            session_id = f"chat_{uuid.uuid4().hex[:8]}"

        # 2. 统一查询：当前用户 + 题目 下最大的聊天序号
        last_seq = QuestionChatSession.objects.filter(
            user_id=user_id,
            question_id=question_id
        ).aggregate(max_seq=Max('chat_seq'))['max_seq']

        chat_seq = last_seq + 1 if last_seq else 1

        # 3. 核心：get_or_create（只查3个关键字段）
        session, created = cls.objects.get_or_create(
            user_id=user_id,
            question_id=question_id,
            session_id=session_id,
            defaults={
                "messages": [],
                "chat_seq": chat_seq,  # 只有新建时才赋值
                "remaining_attempts": 3  # 可选，你自己决定
            }
        )

        return session, created

class UserQuestionCollection(models.Model):
    """用户收藏题目表"""
    user_id = models.IntegerField(db_index=True,verbose_name="用户id",help_text="用户id")
    question_id = models.IntegerField(blank=True, null=True, db_index=True, verbose_name="关联题目id",
                                      help_text="关联题目id")
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True,verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True,verbose_name="修改时间")

    class Meta:
        db_table = web_table_prefix + "user_question_collection"
        verbose_name = '用户收藏题目表'
        verbose_name_plural = verbose_name
        ordering = ('-update_time','-question_id')

class UserAnswerChatSession(models.Model):
    """用户AI使用与答案对应记录表"""
    user_id = models.IntegerField(db_index=True,verbose_name="用户id",help_text="用户id")
    question_id = models.IntegerField(blank=True, null=True, db_index=True, verbose_name="关联题目id",)
    answer_seq = models.IntegerField(blank=True, null=True, db_index=True, verbose_name="用户回答本题第x次")
    session_id = models.CharField(max_length=64,verbose_name="会话ID")

    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True,verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True,verbose_name="修改时间")

    class Meta:
        db_table = web_table_prefix + "user_answer_chat_session"
        verbose_name = '题目答案聊天会话对应表'
        verbose_name_plural = verbose_name
        ordering = ('-create_time',)

    REQUIRED_FIELDS = []


