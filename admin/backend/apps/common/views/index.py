import traceback

from rest_framework.views import APIView
from utils.jsonResponse import SuccessResponse
from django.db import connection
from decimal import Decimal, ROUND_HALF_UP

from utils.middleware import error_logger


class GMVAPIView(APIView):
    """ 首页控制台 """

    def get(self,request):
        try:
            # 统计后台相关数据
            result = get_dashboard_statistics_2()
            result.update(get_ai_statistics())
            return SuccessResponse(data=result, msg="获取成功")
        except Exception as e:
            raise e

def get_dashboard_statistics_1():
    """
    获取后台首页所有统计数据（用户、答题、反馈）
    每个模块包含：本月新增、上月累计、总记录数、增长率
    """
    sql = """
          SELECT
              -- 1. 用户反馈统计：本月新增、上月累计、待处理、总条数
    --         ( \
    --          SELECT COUNT(*) \
    --          FROM history_web_user_feedback
    --          WHERE YEAR(create_time) = YEAR(NOW()) AND MONTH(create_time) = MONTH(NOW())) AS current_month_feedback,
    --   ( \
    --     SELECT COUNT(*) \
    --     FROM history_web_user_feedback
    --     WHERE create_time \
    --         < DATE_FORMAT(NOW() \
    --         , '%Y-%m-01 00:00:00')) AS last_month_total_feedback \
    --         , ( \
    --     SELECT COUNT(*) \
    --     FROM history_web_user_feedback \
    --     WHERE feedback_status = '0') AS pending_feedback \
    --         , ( \
    --     SELECT COUNT(*) \
    --     FROM history_web_user_feedback) AS total_feedback,

              -- 2. 答题数统计：本月新增、上月累计、总条数（总答题数）
              ( \
          SELECT COUNT(*) \
          FROM history_web_user_answer
          WHERE YEAR (create_time) = YEAR (NOW()) \
            AND MONTH (create_time) = MONTH (NOW())) AS current_month_answered_question \
              , ( \
          SELECT COUNT(*) \
          FROM history_web_user_answer
          WHERE create_time \
              < DATE_FORMAT(NOW() \
              , '%Y-%m-01 00:00:00')) AS last_month_total_answered \
              , ( \
          SELECT COUNT(*) \
          FROM history_web_user_answer) AS total_answered,

              -- 3. 用户统计：本月新增、上月累计、总条数（总用户数 = 上月累计 + 本月新增）
              ( \
          SELECT COUNT(*) \
          FROM history_web_users
          WHERE YEAR (create_time) = YEAR (NOW()) \
            AND MONTH (create_time) = MONTH (NOW())) AS current_month_new \
              , ( \
          SELECT COUNT(*) \
          FROM history_web_users
          WHERE create_time \
              < DATE_FORMAT(NOW() \
              , '%Y-%m-01 00:00:00')) AS last_month_total \
              , ( \
          SELECT COUNT(*) \
          FROM history_web_users) AS total_user; \
          """

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchone()
            if not row:
                # 异常返回默认值（含总记录数+增长率）
                return {
                    "feedback": {
                        "current_month": 0,
                        "last_month_total": 0,
                        "pending": 0,
                        "total": 0,
                        "growth_rate": 0.00
                    },
                    "answer": {
                        "current_month": 0,
                        "last_month_total": 0,
                        "total": 0,
                        "growth_rate": 0.00
                    },
                    "user": {
                        "current_month_new": 0,
                        "last_month_total": 0,
                        "total": 0,
                        "growth_rate": 0.00
                    }
                }

            # 解析基础数据（补充总记录数）
            stats = {
                "feedback": {
                    "current_month": row[0] or 0,
                    "last_month_total": row[1] or 0,
                    "pending": row[2] or 0,
                    "total": row[3] or 0  # 反馈总条数
                },
                "answer": {
                    "current_month": row[4] or 0,
                    "last_month_total": row[5] or 0,
                    "total": row[6] or 0  # 答题总条数
                },
                "user": {
                    "current_month_new": row[7] or 0,
                    "last_month_total": row[8] or 0,
                    "total": row[9] or 0  # 用户总条数
                }
            }

            # ========== 配置化循环：同时处理总记录数+增长率 ==========
            # 配置说明：模块名 → (本月字段名, 上月字段名, 总数字段名)
            stats_config = {
                "feedback": ("current_month", "last_month_total", "total"),
                "answer": ("current_month", "last_month_total", "total"),
                "user": ("current_month_new", "last_month_total", "total")
            }

            # 循环计算所有模块的增长率（总记录数已在SQL中统计，这里直接复用）
            for module, (current_field, last_field, total_field) in stats_config.items():
                current_val = stats[module][current_field]
                last_val = stats[module][last_field]
                # 总记录数已从SQL获取，无需计算，直接保留

                # 计算增长率：(本月新增 / 上月累计) × 100%
                if last_val == 0 :
                    if current_val != 0:
                        stats[module]["growth_rate"] = 100.00
                    else:
                        stats[module]["growth_rate"] = 0.00
                else:
                    growth_rate = (Decimal(current_val) / Decimal(last_val)) * 100
                    stats[module]["growth_rate"] = float(growth_rate.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP))

            # 待处理反馈率：(待处理反馈 / 总反馈数) × 100%
            if stats["feedback"]["pending"] != 0:
                stats["feedback"]["pending_rate"] = float(Decimal(stats["feedback"]["pending"]) / Decimal(stats["feedback"]["total"]) * 100.00)
            else:
                stats["feedback"]["pending_rate"] = 0.00

            return stats

    except Exception as e:
        print(f"统计数据查询失败：{str(e)}")
        # 异常返回默认值（含总记录数+增长率）
        return {
            "feedback": {
                "current_month": 0,
                "last_month_total": 0,
                "pending": 0,
                "total": 0,
                "growth_rate": 0.00,
                "pending_rate":0.00
            },
            "answer": {
                "current_month": 0,
                "last_month_total": 0,
                "total": 0,
                "growth_rate": 0.00
            },
            "user": {
                "current_month_new": 0,
                "last_month_total": 0,
                "total": 0,
                "growth_rate": 0.00
            }
        }

# =============== 统计控制板上数据查询 ===========
def get_dashboard_statistics_2():
    """
    获取后台首页统计数据（用户、答题）
    每个模块包含：本月新增、上月累计、总记录数、增长率
    """
    sql = """
          SELECT
              -- 1. 答题数统计：本月新增、上月累计、总条数
              (SELECT COUNT(*) 
               FROM history_web_user_answer
               WHERE YEAR(create_time) = YEAR(NOW()) 
                 AND MONTH(create_time) = MONTH(NOW())) AS current_month_answered_question,
              (SELECT COUNT(*) 
               FROM history_web_user_answer
               WHERE create_time < DATE_FORMAT(NOW(), '%Y-%m-01 00:00:00')) AS last_month_total_answered,
              (SELECT COUNT(*) 
               FROM history_web_user_answer) AS total_answered,

              -- 2. 用户统计：本月新增、上月累计、总条数
              (SELECT COUNT(*) 
               FROM history_web_users
               WHERE YEAR(create_time) = YEAR(NOW()) 
                 AND MONTH(create_time) = MONTH(NOW())) AS current_month_new,
              (SELECT COUNT(*) 
               FROM history_web_users
               WHERE create_time < DATE_FORMAT(NOW(), '%Y-%m-01 00:00:00')) AS last_month_total,
              (SELECT COUNT(*) 
               FROM history_web_users) AS total_user;
          """

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchone()
            if not row:
                return {
                    "answer": {
                        "current_month": 0,
                        "last_month_total": 0,
                        "total": 0,
                        "growth_rate": 0.00
                    },
                    "user": {
                        "current_month_new": 0,
                        "last_month_total": 0,
                        "total": 0,
                        "growth_rate": 0.00
                    }
                }

            # 解析数据（索引已重新对应）
            stats = {
                "answer": {
                    "current_month": row[0] or 0,
                    "last_month_total": row[1] or 0,
                    "total": row[2] or 0
                },
                "user": {
                    "current_month_new": row[3] or 0,
                    "last_month_total": row[4] or 0,
                    "total": row[5] or 0
                }
            }

            # 只计算用户、答题
            stats_config = {
                "answer": ("current_month", "last_month_total", "total"),
                "user": ("current_month_new", "last_month_total", "total")
            }

            for module, (current_field, last_field, total_field) in stats_config.items():
                current_val = stats[module][current_field]
                last_val = stats[module][last_field]

                if last_val == 0:
                    stats[module]["growth_rate"] = 100.00 if current_val != 0 else 0.00
                else:
                    growth_rate = (Decimal(current_val) / Decimal(last_val)) * 100
                    stats[module]["growth_rate"] = float(
                        growth_rate.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
                    )

            return stats

    except Exception as e:
        print(f"统计数据查询失败：{str(e)}")
        return {
            "answer": {
                "current_month": 0,
                "last_month_total": 0,
                "total": 0,
                "growth_rate": 0.00
            },
            "user": {
                "current_month_new": 0,
                "last_month_total": 0,
                "total": 0,
                "growth_rate": 0.00
            }
        }

# =============== 统计AI请求使用次数 ==============
def get_ai_statistics():
    """
    获取近15天AI使用统计数据（含环比增长率）
    包含：AI提示/判题/复盘次数、按天趋势、用户留存率、环比增长率
    """
    # ===================== 新增：环比统计SQL =====================
    # 1. 近15天（当前周期）AI总使用次数
    current_15d_ai_sql = """
        SELECT COUNT(*) AS current_total
        FROM history_web_ai_operation_log
        WHERE create_time >= DATE_SUB(CURDATE(), INTERVAL 14 DAY)
          AND create_time < DATE_ADD(CURDATE(), INTERVAL 1 DAY);
    """

    # 2. 前15天（对比周期：近30天至近15天）AI总使用次数
    prev_15d_ai_sql = """
        SELECT COUNT(*) AS prev_total
        FROM history_web_ai_operation_log
        WHERE create_time >= DATE_SUB(CURDATE(), INTERVAL 29 DAY)
          AND create_time < DATE_SUB(CURDATE(), INTERVAL 14 DAY);
    """

    # 3. 近15天（当前周期）平均留存率
    current_15d_retention_sql = """
        SELECT AVG(daily_retention_rate) AS current_avg_retention
        FROM (
            SELECT first_login_date,
                   COUNT(DISTINCT CASE WHEN login_date = DATE_ADD(first_login_date, INTERVAL 1 DAY) THEN user_id END)
                   / COUNT(DISTINCT user_id) AS daily_retention_rate
            FROM (
                SELECT id as user_id,
                       MIN(DATE(create_time)) AS first_login_date,
                       DATE(create_time) AS login_date
                FROM history_web_users
                WHERE create_time >= DATE_SUB(CURDATE(), INTERVAL 14 DAY)
                  AND create_time < DATE_ADD(CURDATE(), INTERVAL 1 DAY)
                GROUP BY user_id, DATE(create_time)
            ) AS user_login_dates
            WHERE first_login_date >= DATE_SUB(CURDATE(), INTERVAL 14 DAY)
            GROUP BY first_login_date
        ) AS daily_retention;
    """

    # 4. 前15天（对比周期）平均留存率
    prev_15d_retention_sql = """
        SELECT AVG(daily_retention_rate) AS prev_avg_retention
        FROM (
            SELECT first_login_date,
                   COUNT(DISTINCT CASE WHEN login_date = DATE_ADD(first_login_date, INTERVAL 1 DAY) THEN user_id END)
                   / COUNT(DISTINCT user_id) AS daily_retention_rate
            FROM (
                SELECT id as user_id,
                       MIN(DATE(create_time)) AS first_login_date,
                       DATE(create_time) AS login_date
                FROM history_web_users
                WHERE create_time >= DATE_SUB(CURDATE(), INTERVAL 29 DAY)
                  AND create_time < DATE_SUB(CURDATE(), INTERVAL 14 DAY)
                GROUP BY user_id, DATE(create_time)
            ) AS user_login_dates
            WHERE first_login_date >= DATE_SUB(CURDATE(), INTERVAL 29 DAY)
              AND first_login_date < DATE_SUB(CURDATE(), INTERVAL 14 DAY)
            GROUP BY first_login_date
        ) AS daily_retention;
    """
    # ===================== 原有SQL（保留） =====================
    ai_usage_sql = """
                   SELECT SUM(CASE WHEN ai_type = '1' THEN 1 ELSE 0 END) AS ai_tip_counts, 
                          SUM(CASE WHEN ai_type = '2' THEN 1 ELSE 0 END) AS ai_judge_counts, 
                          SUM(CASE WHEN ai_type = '3' THEN 1 ELSE 0 END) AS ai_review_counts, 
                          COUNT(*)                                       AS total_ai_usage
                   FROM history_web_ai_operation_log
                   WHERE create_time >= DATE_SUB(CURDATE(), INTERVAL 14 DAY)
                     AND create_time < DATE_ADD(CURDATE(), INTERVAL 1 DAY); 
                   """

    ai_trend_sql = """
                   SELECT
                       DATE(create_time) AS stat_date, 
                       SUM(CASE WHEN ai_type = '1' THEN 1 ELSE 0 END) AS ai_tip_counts, 
                       SUM(CASE WHEN ai_type = '2' THEN 1 ELSE 0 END) AS ai_judge_counts, 
                       SUM(CASE WHEN ai_type = '3' THEN 1 ELSE 0 END) AS ai_review_counts
                   FROM history_web_ai_operation_log
                   WHERE create_time >= DATE_SUB(CURDATE(), INTERVAL 14 DAY)
                     AND create_time < DATE_ADD(CURDATE(), INTERVAL 1 DAY)
                   GROUP BY DATE(create_time)
                   ORDER BY stat_date; 
                   """

    daily_retention_sql = """
                    SELECT first_login_date, 
                           COUNT(DISTINCT CASE WHEN login_date = DATE_ADD(first_login_date, INTERVAL 1 DAY) THEN user_id END) AS retained_users, 
                           COUNT(DISTINCT user_id) AS new_users, 
                           ROUND(COUNT(DISTINCT CASE WHEN login_date = DATE_ADD(first_login_date, INTERVAL 1 DAY) THEN user_id END) / COUNT(DISTINCT user_id) * 100, 2) AS daily_retention_rate_percent
                    FROM (
                        SELECT id as user_id,
                               MIN(DATE(create_time)) AS first_login_date,
                               DATE(create_time) AS login_date
                        FROM history_web_users
                        WHERE create_time >= DATE_SUB(CURDATE(), INTERVAL 14 DAY)
                          AND create_time < DATE_ADD(CURDATE(), INTERVAL 1 DAY)
                        GROUP BY user_id, DATE(create_time)
                    ) AS user_login_dates
                    WHERE first_login_date >= DATE_SUB(CURDATE(), INTERVAL 14 DAY)
                    GROUP BY first_login_date
                    ORDER BY first_login_date; 
                    """

    tag_frequency_sql = """
                            SELECT count(qt.tag_id),t.name
                            from history_question_tag  as qt
                            left join history_tag t on qt.tag_id = t.id 
                            GROUP BY qt.tag_id
                            limit 5 """

    today_data_sql = """
                SELECT
                    (SELECT COUNT(*) 
                     FROM history_web_ai_operation_log
                     WHERE DATE_FORMAT(create_time, "%Y-%m-%d") = DATE_FORMAT(NOW(), "%Y-%m-%d")) AS today_ai_use_count,
                    (SELECT COUNT(*) 
                     FROM history_web_user_answer
                     WHERE DATE_FORMAT(create_time, "%Y-%m-%d") = DATE_FORMAT(NOW(), "%Y-%m-%d")) AS today_answer_count,
                    (SELECT COUNT(*) 
                     FROM history_web_users
                     WHERE DATE_FORMAT(create_time, "%Y-%m-%d") = DATE_FORMAT(NOW(), "%Y-%m-%d")) AS today_new_user_count;
            """

    try:
        with connection.cursor() as cursor:
            # ========== 1. 计算AI使用次数环比增长率 ==========
            # 当前15天AI总次数
            cursor.execute(current_15d_ai_sql)
            current_ai_total = cursor.fetchone()[0] or 0
            # 前15天AI总次数
            cursor.execute(prev_15d_ai_sql)
            prev_ai_total = cursor.fetchone()[0] or 0
            # 计算AI增长率（保留1位小数，与前端一致）
            ai_growth_rate = 0.0
            if prev_ai_total != 0:
                ai_growth_rate = float(Decimal((current_ai_total - prev_ai_total) / prev_ai_total * 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
            elif current_ai_total > 0:
                ai_growth_rate = 100.0

            # ========== 2. 计算留存率环比增长率 ==========
            # 当前15天平均留存率
            cursor.execute(current_15d_retention_sql)
            current_retention = cursor.fetchone()[0] or 0
            # 前15天平均留存率
            cursor.execute(prev_15d_retention_sql)
            prev_retention = cursor.fetchone()[0] or 0
            # 计算留存增长率（保留1位小数）
            retention_growth_rate = 0.0
            if prev_retention != 0:
                retention_growth_rate = float(Decimal((current_retention - prev_retention) / prev_retention * 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
            elif current_retention > 0:
                retention_growth_rate = 100.0

            # ========== 3. 原有：查询AI使用明细 ==========
            cursor.execute(ai_usage_sql)
            usage_row = cursor.fetchone()
            ai_usage = {
                "ai_tip_counts": usage_row[0] or 0,
                "ai_judge_counts": usage_row[1] or 0,
                "ai_review_counts": usage_row[2] or 0,
                "total_ai_usage": current_ai_total,  # 替换为当前周期总次数
                "growth_rate": ai_growth_rate  # 新增：AI使用增长率
            }

            # ========== 4. 原有：查询AI使用趋势 ==========
            cursor.execute(ai_trend_sql)
            trend_rows = cursor.fetchall()
            ai_trend = []
            for row in trend_rows:
                ai_trend.append({
                    "stat_date": row[0].strftime("%m-%d") if row[0] else "",
                    "ai_tip_counts": row[1] or 0,
                    "ai_judge_counts": row[2] or 0,
                    "ai_review_counts": row[3] or 0
                })

            # ========== 5. 原有：查询按天留存率 ==========
            cursor.execute(daily_retention_sql)
            retention_rows = cursor.fetchall()
            daily_retention = []
            for row in retention_rows:
                daily_retention.append({
                    "first_login_date": row[0].strftime("%m-%d") if row[0] else "",
                    "retained_users": row[1] or 0,
                    "new_users": row[2] or 0,
                    "daily_retention_rate_percent": row[3] or 0.00
                })

            # ========== 查询标签出现频率 ==========
            cursor.execute(tag_frequency_sql)
            retention_rows = cursor.fetchall()
            tag_frequency = []
            for row in retention_rows:
                tag_frequency.append({
                    "value": row[0] or 0,
                    "name": row[1] or ""
                })

            # ========== 查询今日统计信息 ==========
            cursor.execute(today_data_sql)
            retention_rows = cursor.fetchall()
            today_data = {
                "today_ai_use_count": retention_rows[0][0] or 0,
                "today_answer_count": retention_rows[0][1] or 0,
                "today_new_user_count": retention_rows[0][2] or 0,
            }


            # ========== 6. 组装最终结果（新增环比字段） ==========
            current_avg_retention = round(float(Decimal(current_retention or 0).quantize(Decimal('0.0000'), rounding=ROUND_HALF_UP)) * 100, 1)
            result = {
                "ai_usage_total": ai_usage,
                "ai_usage_trend": ai_trend,
                "user_retention": {
                    "avg_15d_retention_rate": current_avg_retention,  # 保留1位小数
                    "growth_rate": retention_growth_rate,  # 新增：留存率增长率
                    "daily_retention": daily_retention
                },
                "tag_frequency": tag_frequency,
                "today_data": today_data
            }
            return result

    except Exception as e:
        error_logger.error(f"get backend index info failed,%s", traceback.format_exc())
        # 异常返回默认值（含增长率）
        return {
            "ai_usage_total": {
                "ai_tip_counts": 0,
                "ai_judge_counts": 0,
                "ai_review_counts": 0,
                "total_ai_usage": 0,
                "growth_rate": 0.0
            },
            "ai_usage_trend": [],
            "user_retention": {
                "avg_15d_retention_rate": 0.0,
                "growth_rate": 0.0,
                "daily_retention": []
            }
        }

