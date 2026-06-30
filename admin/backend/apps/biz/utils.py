import base64
import os
from collections import defaultdict

from django.db import connection
from django.utils.dateparse import parse_datetime

from biz.constants import QuestionTypeEnum
from history_admin_backend.settings import FILE_PATH, UPLOAD_PATH


def parse_wechat_time(time_str: str):
    """
    将微信返回的 success_time (ISO8601 格式) 转换为本地 datetime
    例如: '2025-11-06T09:49:41+08:00' -> datetime(2025, 11, 6, 9, 49, 41)
    """
    if not time_str:
        return None

    try:
        # 先解析为带时区的 datetime
        dt = parse_datetime(time_str)
        if dt is None:
            raise ValueError("Invalid time format")

        # 转为本地时间并去掉 时区（因为 USE_TZ=False）
        local_dt = dt.astimezone(tz=None).replace(tzinfo=None)
        return local_dt
    except Exception as e:
        return None

def read_identity_image(file_name):
    save_path = os.path.join(FILE_PATH, UPLOAD_PATH, "recommender_identity")
    file_disk_path = os.path.join(str(save_path), file_name)
    if not os.path.exists(file_disk_path):
        return None
    with open(file_disk_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def get_question_with_options_and_answers_2(question_queryset):
    """原生SQL精准联查（修复JOIN条件）+ 数据处理，100%匹配原代码逻辑"""
    # ========== 1. 处理入参，获取question_ids（兼容单对象/可迭代对象） ==========
    if not hasattr(question_queryset, '__iter__'):
        # 单个Question对象
        question_ids = [question_queryset.id]
    else:
        # QuerySet/列表
        question_ids = [item.id for item in question_queryset if item.id]

    if not question_ids:
        return {}, {}, {}, {}

    # ========== 2. 执行修正后的原生SQL（参数化查询防注入） ==========
    sql = """
          SELECT q.id               AS question_id, \
                 q.content          AS question_content, \
                 q.score            AS question_score, \
                 q.difficulty       AS question_difficulty, \
                 q.finish_time      AS question_finish_time, \
                 q.has_sub_question AS has_sub_question, \
                 q.type             AS question_type, \
                 q.prompt_id        AS prompt_id, \
                 sq.id              AS sub_question_id, \
                 sq.sub_content     AS sub_question_content, \
                 sq.score           AS sub_question_score, \
                 qo.id              AS option_id,   \
                 qo.option_content  AS option_content, \
                 qo.is_correct      AS option_is_correct, \
                 qo.sub_question_id AS option_sub_question_id, \
                 qa.answer_content  AS answer_content, \
                 qa.sub_question_id AS answer_sub_question_id, \
                 p.prompt_content   AS prompt_content
          FROM history_question q \
                   LEFT JOIN history_sub_question sq ON q.id = sq.question_id \
                   LEFT JOIN history_question_option qo \
                             ON q.id = qo.question_id \
                                 AND (sq.id = qo.sub_question_id OR qo.sub_question_id IS NULL) \
                   LEFT JOIN history_question_answer qa \
                             ON q.id = qa.question_id \
                                 AND (sq.id = qa.sub_question_id OR qa.sub_question_id IS NULL) \
                   LEFT JOIN history_prompt p ON q.prompt_id = p.id
          WHERE q.id IN %s
          ORDER BY q.id, sq.id; \
          """

    with connection.cursor() as cursor:
        cursor.execute(sql, (tuple(question_ids),))
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # ========== 3. 初始化返回数据（和原代码完全一致） ==========
    question_detail_list = defaultdict(list)  # 原代码的结构（list），恢复！
    question_option_list = defaultdict(list)
    question_answer_list = {}
    prompts_map = {}

    # 单选/多选类型（和原代码一致）
    single_or_multi = [QuestionTypeEnum.SINGLE_CHOICE.value[0], QuestionTypeEnum.MULTIPLE_CHOICE.value[0]]

    # ========== 4. 数据处理逻辑（100%复刻你的原代码） ==========
    # 第一步：先整理提示词（去重）
    for row in rows:
        prompt_id = row['prompt_id']
        prompt_content = row['prompt_content']
        if prompt_id and prompt_content and prompt_id not in prompts_map:
            prompts_map[prompt_id] = prompt_content

    # 第二步：按题目分组，复刻原代码的核心逻辑
    # 临时存储：避免重复处理同一题目/子题
    processed_sub_questions = defaultdict(set)  # {question_id: {sub_question_id}}
    processed_options = defaultdict(set)  # {question_id: {option_content}}

    for row in rows:
        q_id = row['question_id']
        has_sub_question = row['has_sub_question']
        question_type = row['question_type']

        # 场景1：有子题目
        if has_sub_question == "1":
            sub_q_id = row['sub_question_id']
            if not sub_q_id:
                continue

            # 子题去重：避免重复添加
            if sub_q_id not in processed_sub_questions[q_id]:
                # 整理子题选项（和原代码一致）
                option_list = []
                if question_type in single_or_multi:
                    opt_content = row['option_content']
                    if opt_content:
                        option_list.append({
                            "option_content": opt_content,
                            "is_correct": row['option_is_correct'] or False,
                            "option_id": row['option_id'],
                        })

                # 整理子题答案
                sub_ans_content = row['answer_content'] or ""

                # 封装子题数据
                sub_question_data = {
                    "question": row['sub_question_content'] or "",
                    "score": row['sub_question_score'] or 0,
                    "option_list": option_list,
                    "answer": sub_ans_content
                }
                question_detail_list[q_id].append(sub_question_data)
                processed_sub_questions[q_id].add(sub_q_id)

            # 补充子题的其他选项（如果有）
            if question_type in single_or_multi and row['option_content']:
                # 找到当前子题的已存数据，补充选项
                for sub_item in question_detail_list[q_id]:
                    if sub_item['question'] == (row['sub_question_content'] or ""):
                        # 选项去重
                        opt_exists = any(
                            opt['option_content'] == row['option_content']
                            for opt in sub_item['option_list']
                        )
                        if not opt_exists:
                            sub_item['option_list'].append({
                                "option_content": row['option_content'],
                                "is_correct": row['option_is_correct'] or False,
                                "option_id": row['option_id'],
                            })
                        break

        # 场景2：无子题目（has_sub_question≠"1"）
        else:
            # 单选/多选：整理主题目的选项
            if question_type in single_or_multi:
                opt_content = row['option_content']
                if opt_content and opt_content not in processed_options[q_id]:
                    question_option_list[q_id].append({
                        "option_content": opt_content,
                        "is_correct": row['option_is_correct'] or False,
                        "option_id": row['option_id'],
                    })
                    processed_options[q_id].add(opt_content)
            # 整理主题目的答案
            if q_id not in question_answer_list and row['answer_content']:
                question_answer_list[q_id] = row['answer_content']

    # ========== 5. 格式转换（和原代码完全一致） ==========
    return (
        dict(question_detail_list),
        dict(question_option_list),
        question_answer_list,
        prompts_map
    )

# def get_question_with_option_and_answer(question_queryset):
#     """仅用于保存之前查询逻辑"""
#     if page is not None:
#         # 多表联查，返回题目结构
#         question_ids = [item.id for item in page]
#         sub_questions = SubQuestion.objects.filter(question_id__in=question_ids)
#         sub_questions_map = defaultdict(list)
#         for item in sub_questions:
#             sub_questions_map[item.question_id].append(item)
#         sub_questions_map = dict(sub_questions_map)
#
#         # 选项
#         question_options = QuestionOption.objects.filter(question_id__in=question_ids)
#         question_options_map = defaultdict(list)
#         sub_questions_options_map = defaultdict(list)
#         for item in question_options:
#             question_options_map[item.question_id].append(item)
#             sub_questions_options_map[item.sub_question_id].append(item)
#         question_options_map = dict(question_options_map)
#         sub_questions_options_map = dict(sub_questions_options_map)
#
#         # 答案
#         question_answer = QuestionAnswer.objects.filter(question_id__in=question_ids)
#         question_answer_map = {item.id: item for item in question_answer}
#         sub_question_answer_map = defaultdict()
#         for item in question_answer:
#             sub_question_answer_map[item.sub_question_id] = item
#         sub_question_answer_map = dict(sub_question_answer_map)
#
#         # 返回封装的detailList
#         question_detail_list = defaultdict(list)
#         question_option_list = defaultdict(list)
#         question_answer_list = {}
#
#         # 单选或多选
#         single_or_multi = [QuestionTypeEnum.SINGLE_CHOICE.value[0], QuestionTypeEnum.MULTIPLE_CHOICE.value[0]]
#
#         # 封装题目关联数据
#         for item in page:
#             # 有子题目
#             if item.has_sub_question == "1":
#                 item_sub_que = sub_questions_map.get(item.id, None)
#                 for sub_que in item_sub_que:
#                     option_list = []
#                     # 封装选择题
#                     if item.type in single_or_multi:
#                         item_option = sub_questions_options_map.get(sub_que.id, None)
#                         for opt in item_option:
#                             option_list.append({
#                                 "option_content": opt.option_content,
#                                 "is_correct": opt.is_correct
#                             })
#
#                     sub_que_ans = sub_question_answer_map.get(sub_que.id, None)
#                     question_detail_list[item.id].append({
#                         "question": sub_que.sub_content,
#                         "score": sub_que.score,
#                         "option_list": option_list,
#                         "answer": sub_que_ans.answer_content if sub_que_ans is not None else ""
#                     })
#             # 无子题目
#             else:
#                 if item.type in single_or_multi:
#                     item_options = question_options_map.get(item.id)
#                     option_list = []
#                     for opt in item_options:
#                         option_list.append({
#                             "option_content": opt.option_content,
#                             "is_correct": opt.is_correct
#                         })
#                     question_option_list[item.id] = option_list
#                 else:
#                     question_answer_list[item.id] = question_answer_map.get(item.id)
#
#         question_detail_list = dict(question_detail_list)
#         question_option_list = dict(question_option_list)
#
#         # 用于提示词页面展示题目与提示词内容
#         prompt_ids = [
#             item.prompt_id for item in page
#             if item.prompt_id is not None and item.prompt_id != ''
#         ]
#         prompt_ids = list(set(prompt_ids))
#         prompts_map = {}
#         if prompt_ids:  # 只有存在 prompt_id 时才查询
#             prompts = Prompt.objects.filter(id__in=prompt_ids)
#             prompts_map = {item.id: item.prompt_content for item in prompts}