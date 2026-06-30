from utils.models import CoreModel, web_table_prefix
from django.db import models

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

class UserCheckIn(models.Model):
    """用户打卡记录表"""
    user_id = models.IntegerField(verbose_name="用户ID", db_index=True)  # 加索引提升查询效率
    check_in_date = models.DateField(verbose_name="打卡日期")
    check_in_time = models.DateTimeField(auto_now_add=True, verbose_name="打卡时间")

    class Meta:
        db_table = web_table_prefix + "user_check_in"
        verbose_name = "用户打卡记录"
        verbose_name_plural = "用户打卡记录"
        ordering = ["-check_in_date"]