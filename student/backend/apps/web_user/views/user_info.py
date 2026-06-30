# -*- coding: utf-8 -*-

"""
@Remark: 用户信息管理
"""
import datetime

from django.contrib.auth.hashers import make_password
from django.db import transaction, connection
from rest_framework.decorators import action
from rest_framework.views import APIView

from system.filter import UserFilter
from system.models import Users
from system.serializer.user_ser import UserInfoSerializer
from utils.exception import BizException
from utils.jsonResponse import SuccessResponse
from utils.viewset import CustomModelViewSet
from web_user.constants import GenderType, DEFAULT_AVATAR_BOY_PATH, DEFAULT_AVATAR_GIRL_PATH
from web_user.models import UserCheckIn
from web_user.serializer.user_feedback_ser import UserFeedbackSerializer


class WebUserViewSet(CustomModelViewSet):
    """
    用户接口:
    """
    queryset = Users.objects.all().order_by('-create_time')
    serializer_class = UserInfoSerializer
    filterset_class = UserFilter

    @action(detail=False,methods=['get'])
    def get_user_info(self, request):
        """
        获取用户信息
        :param request:
        :return:
        """
        user = request.user
        return SuccessResponse(UserInfoSerializer(user).data)

    @action(detail=False, methods=['put'])
    def update_user_info(self,request):
        """修改当前用户信息"""
        user = request.user
        if not user:
            raise BizException(msg="未获取到用户")

        update_data = request.data.copy()
        update_data.pop('avatar', None)
        Users.objects.filter(id=user.id).update(**update_data)

        user = Users.objects.get(id=user.id)
        # 根据性别设置默认头像
        if user.gender == GenderType.Boy[0]:
            user.avatar = DEFAULT_AVATAR_BOY_PATH
        else:
            user.avatar = DEFAULT_AVATAR_GIRL_PATH

        user.save(update_fields=['avatar'])
        return SuccessResponse(data=None, msg="修改成功")

    @action(detail=False, methods=['put'])
    def change_password(self,request):
        """密码修改"""
        try:
            user = request.user
            instance = Users.objects.filter(id=user.id).first()
            data = request.data
            old_pwd = data.get('oldPassword')
            new_pwd = data.get('newPassword')
            if instance:
                if instance.check_password(old_pwd):
                    with transaction.atomic():
                        instance.password = make_password(new_pwd)
                        instance.pwd_update_date = datetime.datetime.now()
                        instance.save()
                    return SuccessResponse(data=None, msg="修改成功")
                else:
                    raise BizException(msg="旧密码不正确")
            else:
                raise BizException(msg="未获取到用户")
        except Exception as e:
            raise e

    # ----------------------- 用户学习数据 ---------------------------
    @action(detail=False,methods=['get'])
    def get_user_study_data(self,request):
        """ 获取用户学习数据 """
        user_id = request.user.id
        result = get_user_study_stats(user_id)
        return SuccessResponse(data=result)

    # ----------------------- 用户每日打卡 ---------------------------
    @action(detail=False,methods=['post'])
    def user_daily_check_in(self,request):
        """ 用户每日打卡 """
        user_id = request.user.id
        user_check_in = UserCheckIn.objects.filter(user_id=user_id, check_in_date=datetime.date.today()).first()
        if user_check_in:
            return SuccessResponse(data=None, msg="今日已打卡")
        else:
            with transaction.atomic():
                UserCheckIn.objects.create(user_id=user_id, check_in_date=datetime.date.today())
            return SuccessResponse(data=None, msg="打卡成功")

    # ----------------------- 获取用户累计打卡天数 ----------------------
    @action(detail=False,methods=['get'])
    def get_user_check_in_count(self,request):
        """ 获取用户累计打卡天数 """
        user_id = request.user.id
        count = UserCheckIn.objects.filter(user_id=user_id).count()
        return SuccessResponse(data=count)


class UserFeedbackViewSet(APIView):
    """ 用户反馈意见 """
    def post(self, request):
        """ 新增用户反馈 """
        try:
            user_id = request.user.id
            data = request.data.copy()
            data["user_id"] = user_id

            serializer = UserFeedbackSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                serializer.save(user_id=user_id,create_by=request.user.id, create_name=request.user.username)
            return SuccessResponse(data=serializer.data, msg="新增成功")
        except Exception as e:
            raise e

def get_user_study_stats(user_id):
    """
    获取用户完整学习统计数据（含超越百分比）
    :param user_id: 当前用户ID
    :return: 包含所有统计字段的字典
    """
    # ========== 第一步：查询核心统计数据 ==========
    core_sql = """
    SELECT
      COUNT(*) AS total_answers,
      SUM(ua.cost_time) AS total_study_time,
      SUM(CASE WHEN q.type = "1" THEN 1 ELSE 0 END) AS choice_total,
      SUM(CASE WHEN q.type = "1" AND ua.got_score = ua.score THEN 1 ELSE 0 END) AS choice_correct,
      IF(
        SUM(CASE WHEN q.type = "1" THEN 1 ELSE 0 END) = 0, 
        0, 
        ROUND(
          SUM(CASE WHEN q.type = "1" AND ua.got_score = ua.score THEN 1 ELSE 0 END) 
          / SUM(CASE WHEN q.type = "1" THEN 1 ELSE 0 END) * 100, 
          1
        )
      ) AS choice_accuracy,
      SUM(CASE WHEN q.type = "5" THEN 1 ELSE 0 END) AS essay_total,
      IF(
        SUM(CASE WHEN q.type = "5" AND ua.score > 0 THEN ua.score ELSE 0 END) = 0, 
        0, 
        ROUND(
          SUM(CASE WHEN q.type = "5" AND ua.score > 0 THEN COALESCE(ua.got_score, 0) ELSE 0 END) 
          / SUM(CASE WHEN q.type = "5" AND ua.score > 0 THEN ua.score ELSE 0 END) * 100, 
          1
        )
      ) AS essay_accuracy,
      COUNT(CASE WHEN ua.create_time >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 ELSE NULL END) AS last_7_days_answers
    FROM history_web_user_answer ua
    LEFT JOIN history_question q ON ua.question_id = q.id
    WHERE ua.user_id = %s;
    """

    with connection.cursor() as cursor:
        # 执行核心统计
        cursor.execute(core_sql, [user_id])
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        core_stats = dict(zip(columns, row)) if row else {}

    # 空值兜底
    core_stats = {
        "total_answers": core_stats.get("total_answers", 0),
        "total_study_time": core_stats.get("total_study_time", 0),
        "choice_total": core_stats.get("choice_total", 0),
        "choice_correct": core_stats.get("choice_correct", 0),
        "choice_accuracy": core_stats.get("choice_accuracy", 0.0),
        "essay_total": core_stats.get("essay_total", 0),
        "essay_accuracy": core_stats.get("essay_accuracy", 0.0),
        "last_7_days_answers": core_stats.get("last_7_days_answers", 0),
    }

    # ========== 第二步：计算超越用户百分比 ==========
    # 若当前用户无答题数，直接返回0
    if core_stats["total_answers"] == 0:
        core_stats["beat_percent"] = 0.0
        return core_stats

    # 超越百分比SQL
    beat_sql = """
    SELECT
      IF(total_all_users = 0, 0, ROUND((less_users / total_all_users) * 100, 1)) AS beat_percent
    FROM (
      SELECT COUNT(DISTINCT user_id) AS less_users
      FROM (
        SELECT user_id, COUNT(*) AS user_total
        FROM history_web_user_answer
        GROUP BY user_id
      ) AS user_answer_count
      WHERE user_total < %s
    ) AS t1,
    (SELECT COUNT(DISTINCT user_id) AS total_all_users FROM history_web_user_answer) AS t2;
    """

    with connection.cursor() as cursor:
        # 执行超越百分比统计（传入当前用户答题数）
        cursor.execute(beat_sql, [core_stats["total_answers"]])
        beat_row = cursor.fetchone()
        core_stats["beat_percent"] = 100 - beat_row[0] if beat_row else 0.0

    # ========== 第三步：补充数据更新时间（可选） ==========
    core_stats["update_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")  # 可从数据库查最新答题时间，这里先写死

    return core_stats



