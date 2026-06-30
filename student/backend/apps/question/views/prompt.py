# -*- coding: utf-8 -*-

"""
@Remark: 题库管理
"""
import json
import traceback

from django.http import StreamingHttpResponse
from django.utils.decorators import method_decorator
from django_redis import get_redis_connection
from rest_framework.decorators import action

from question.constants import MAX_ASK_COUNT, AiTypeEnum, QuestionTypeEnum
from question.filter import PromptFilter
from question.models import Prompt, Question, QuestionChatSession
from question.serializer.prompt_ser import PromptInfoSerializer
from question.serializer.question_ser import SimpleQuestionSerializer
from question.utils import AIClient, record_execution_time, \
    get_question_with_options_and_answers_2, generate_complete_system_prompt
from utils.ai_operation import AIOperationTracker
from utils.exception import BizException
from utils.jsonResponse import SuccessResponse
from utils.middleware import error_logger
from utils.viewset import CustomModelViewSet


class PromptViewSet(CustomModelViewSet):
    """
    后台管理员用户接口:
    """
    # perms_map = {
        # "list" : "system:user:list",
        # "retrieve" : "system:user:get",
        # "create" : "system:user:add",
        # "update" : "system:user:edit",
        # "partial_update" : "system:user:edit",
        # "destroy" : "system:user:rm",
        # "web_user_info" : "*",
        # "update_web_user_info" :  "*",
        # "reset_verification_code_count" : "*",
    # }
    queryset = Prompt.objects.all().order_by('-create_time')
    serializer_class = PromptInfoSerializer
    filterset_class = PromptFilter
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")

    # ========== 获取AI提示整篇接口，响应时间长，暂时弃用 ==========
    @method_decorator(record_execution_time)
    @action(detail=False,methods=['post'])
    def get_question_prompt(self, request):
        """请求ai获取提示信息,响应流程极长，10s以上"""
        try:
            # 1. 获取基础参数（新增session_id和user_message）
            question_id = request.data.get("question_id")
            session_id = request.data.get("session_id")  # 前端传的会话ID（多轮复用）
            user = request.user  # 假设已做用户认证

            if not question_id:
                raise BizException("缺少题目信息！")

            # 2. 获取题目信息
            question = Question.objects.filter(id=question_id).first()
            if not question:
                raise BizException("题目不存在！")

            # 3. 获取/创建会话（加载历史对话记录）
            session, _ = QuestionChatSession.get_or_create_session(
                user_id=user.id,
                question_id=question_id,
                session_id=session_id
            )
            history_messages = session.messages  # 历史对话记录

            # 5. 拼接本轮消息
            system_prompt = ""
            if len(history_messages) == 0:
                # 第一轮：添加题目基础信息
                # ask_question = clean_model_obj(question)
                question_detail_list, question_option_list, question_answer_list, _ = get_question_with_options_and_answers_2(question)
                question_data = SimpleQuestionSerializer(question).data if question else {}
                all_question_data = {
                    "question": question_data,
                    "detail": question_detail_list,  # 如果是模型对象，也可以用对应的序列化器处理
                    "options": question_option_list,
                    "answers": question_answer_list
                }

                # 一键转JSON（无需担心datetime，序列化器已转为字符串）
                question_json = json.dumps(all_question_data, ensure_ascii=False)

                # 拼接题目信息
                system_prompt = system_prompt + "题目信息如下：" + question_json

                # 拼接公共提示词内容
                public_prompts_str = ""
                public_prompts = Prompt.objects.filter(tags__in=question.tags.all()).distinct()
                for item in public_prompts:
                    public_prompts_str += "\n " + item.prompt_content

                if public_prompts_str != "" :
                    system_prompt = system_prompt +  public_prompts_str

                # 拼接单独的题目提示词
                question_prompt = Prompt.objects.filter(id=question.prompt_id).first()
                if question_prompt:
                 system_prompt = system_prompt + "此外，" + question_prompt.prompt_content

                history_messages.append({"role": "user", "content": system_prompt})
            else:
                # 非第一轮
                system_prompt = "请再给出一次提示"
                history_messages.append({"role": "user", "content": system_prompt})

            # 6. 限制对话轮数（最多3轮）
            user_msg_count = len([m for m in history_messages if m["role"] == "user"])
            if user_msg_count > 3:
                raise BizException("最多支持3轮对话")

            # 7. 调用AI（带上下文）
            ai_client = AIClient(provider="VOLC_ARK")  # 开发阶段用OpenAI
            ai_response, updated_messages = ai_client.chat_completion_with_context(
                system_prompt=system_prompt,
                messages=history_messages,
                temperature=0.3
            )

            # 8. 保存更新后的对话记录到数据库
            session.messages = updated_messages
            session.save()
            result_message = [item for item in updated_messages if item['role'] == "assistant"]

            # 9. 返回结果（包含会话ID+对话记录+AI响应）
            return SuccessResponse(data= {
                    "session_id": session.session_id,  # 前端后续请求需携带
                    "messages": result_message,  # 完整对话记录（用于前端渲染）
                    "ai_response": ai_response,  # 本轮AI响应
                    "remaining_rounds": 3 - user_msg_count  # 剩余对话轮数
            })

        except Exception as e:
            raise e

    # ========== 获取AI提示流式接口 ==========
    @action(detail=False, methods=['post'])
    def get_question_prompt_stream(self, request):
        """返回题目提示内容，流式返回AI提示信息：边接收AI内容，边推送给前端"""
        try:
            question_id = request.data.get("question_id")
            session_id = request.data.get("session_id")
            user = request.user

            if not question_id:
                # 流式中无法返回JSON错误，直接yield错误信息
                def error_generator():
                    yield json.dumps({"type":"error","code": 400, "msg": "缺少题目信息！"})

                return StreamingHttpResponse(error_generator(), content_type="application/json")

            question = Question.objects.filter(id=question_id).first()
            if not question:
                def error_generator():
                    yield json.dumps({"type":"error","code": 404, "msg": "题目不存在！"})

                return StreamingHttpResponse(error_generator(), content_type="application/json")

            # 初始化系统提示词，只能初始化一次，否则容易产生幻觉
            system_prompt = None
            if not session_id:
                # 初始化系统提示词，拼接系统提示
                system_prompt = generate_complete_system_prompt(question)

            # 创建聊天session
            session, _ = QuestionChatSession.get_or_create_session(
                user_id=user.id,
                question_id=question_id,
                session_id=session_id
            )

            if session.remaining_attempts <= 0:
                def error_generator():
                    yield json.dumps({"type":"error","code": 400, "msg": "最多支持3轮对话"})

                return StreamingHttpResponse(error_generator(), content_type="application/json")

            history_messages = session.messages.copy()  # 拷贝，避免修改原数据
            if system_prompt:
                history_messages.insert(0, {"role": "system", "content": system_prompt})

            # 拼接提问信息
            if system_prompt:
                session.remaining_attempts -= 1
                ask_prompt = "现在，请给出第一次提示"
                history_messages.append({"role": "user", "content": ask_prompt})
            else:
                session.remaining_attempts -= 1
                ask_prompt = "请再给出一次提示"
                history_messages.append({"role": "user", "content": ask_prompt})

            # 异步埋点（AI提示）
            AIOperationTracker.record_operation(
                user_id=request.user.id,
                ai_type=AiTypeEnum.TIP.value[0],  # AI提示
                ip=request.META.get('REMOTE_ADDR', ''),
                device=request.META.get('HTTP_USER_AGENT', '')
            )

            # 3. 返回流式响应（关键配置）
            response = StreamingHttpResponse(
                ai_stream_generator(history_messages,session,system_prompt),
                content_type="text/event-stream; charset=utf-8"
            )
            # 禁用缓存和缓冲，确保实时推送
            response['Cache-Control'] = 'no-cache'
            response['X-Accel-Buffering'] = 'no'  # 禁用Nginx缓冲
            # response['Connection'] = 'keep-alive'
            # response['Transfer-Encoding'] = 'chunked'  # 分块传输
            return response

        except Exception as e:
            raise e

    @action(detail=False, methods=['post'])
    def get_question_review_prompt_stream(self, request):
        """统一 AI 复盘接口（自动适配：单选/多选/填空/判断/问答）"""
        try:
            question_id = request.data.get("question_id")
            session_id = request.data.get("session_id")
            user_submit_answer = request.data.get('user_answer')
            user = request.user

            # 参数校验
            if not user_submit_answer:
                raise BizException("未添加答案信息")
            if not question_id:
                def error_generator():
                    yield json.dumps({"type": "error", "code": 400, "msg": "缺少题目信息！"})

                return StreamingHttpResponse(error_generator(), content_type="application/json")

            question = Question.objects.filter(id=question_id).first()
            if not question:
                def error_generator():
                    yield json.dumps({"type": "error", "code": 404, "msg": "题目不存在！"})

                return StreamingHttpResponse(error_generator(), content_type="application/json")

            # 系统提示词
            system_prompt = None
            if not session_id:
                system_prompt = generate_complete_system_prompt(question)

            # 会话管理
            session, _ = QuestionChatSession.get_or_create_session(
                user_id=user.id,
                question_id=question_id,
                session_id=session_id
            )
            history_messages = session.messages.copy()
            if system_prompt:
                history_messages.insert(0, {"role": "system", "content": system_prompt})

            if question.type in QuestionTypeEnum.get_option_values():
                #  客观题：单选、多选（需要对比选项ID）
                user_answer_json = json.dumps(user_submit_answer, ensure_ascii=False)
                ask_prompt = (
                        "\n 用户答案如下（用户所选题目对应id）："
                        + user_answer_json
                        + " 请对比正确答案并为该用户进行复盘"
                )
            else:
                # 主观/其他题型：填空、判断、问答
                user_answer_str = str(user_submit_answer).strip()
                ask_prompt = f"""
                            === 用户答案数据如下，请对比正确答案并为该用户进行复盘 ===
                            {user_answer_str}
                            ======================================================
                                        """

            history_messages.append({"role": "user", "content": ask_prompt})

            # AI 操作埋点
            AIOperationTracker.record_operation(
                user_id=request.user.id,
                ai_type=AiTypeEnum.REVIEW.value[0], # AI复盘
                ip=request.META.get('REMOTE_ADDR', ''),
                device=request.META.get('HTTP_USER_AGENT', '')
            )

            # 流式响应返回
            response = StreamingHttpResponse(
                ai_stream_generator(history_messages, session, system_prompt),
                content_type="text/event-stream; charset=utf-8"
            )
            response['Cache-Control'] = 'no-cache'
            response['X-Accel-Buffering'] = 'no'
            return response

        except Exception as e:
            raise e

    def ai_prompt_cache(self,question_id,ai_tips):
        redis_conn = get_redis_connection("default")
        cache_key = f"ai_tips:{question_id}"
        cached_tips = redis_conn.get(cache_key)
        if cached_tips:
            return SuccessResponse(data= {"ai_tips": cached_tips.decode()})
        # 否则调用AI，再缓存
        redis_conn.setex(cache_key, 3600 * 24, ai_tips)  # 缓存1天

def ai_stream_generator(history_messages,session,system_prompt):
    # 先返回元信息
    meta_data = {
        "type": "meta",
        "data": {
            "session_id": session.session_id,
        }
    }
    yield json.dumps(meta_data, ensure_ascii=False) + "\n"  # 换行分隔，方便前端解析
    # 强制刷新缓冲区
    import sys
    sys.stdout.flush()


    # 第二步：调用AI流式接口，逐段返回内容
    ai_client = AIClient(provider="VOLC_ARK")
    try:
        # 关键：调用AI客户端的流式方法
        stream_iterator = ai_client.chat_completion_with_context_stream(
            # system_prompt=system_prompt,
            messages=history_messages,
            temperature=0.3
        )

        full_ai_response = ""

        # 逐字返回
        for chunk_content in stream_iterator:
            if chunk_content:
                full_ai_response += chunk_content
                content_data = {
                    "type": "content",
                    "data": chunk_content
                }
                yield json.dumps(content_data, ensure_ascii=False) + "\n"

        # 结束
        end_data = {
            "type": "end",
            "data": {"msg": "生成完成"}
        }
        yield json.dumps(end_data, ensure_ascii=False) + "\n"

        # 第三步：保存会话记录（流式结束后）
        # 更新历史消息
        history_messages.append({"role": "assistant", "content": full_ai_response})
        session.messages = history_messages
        session.save()

    except Exception as e:
        error_data = {
            "type": "error",
            "data": {"msg": f"AI生成失败"}
        }
        yield json.dumps(error_data, ensure_ascii=False) + "\n"
        sys.stdout.flush()
        error_logger.error("ai调用失败 %s", traceback.format_exc())
        return  # 终止生成器

    # ========== 客观题AI复盘内容 ==========
    # @action(detail=False, methods=['post'])
    # def get_choice_question_review_prompt_stream(self, request):
    #     """返回AI复盘内容"""
    #     try:
    #         # 1. 原有参数校验+数据查询逻辑（完全复用）
    #         question_id = request.data.get("question_id")
    #         session_id = request.data.get("session_id")
    #         user = request.user
    #
    #         user_submit_answer = request.data.get('user_answer')
    #         if not user_submit_answer:
    #             raise BizException("未添加答案信息")
    #
    #         if not question_id:
    #             # 流式中无法返回JSON错误，直接yield错误信息
    #             def error_generator():
    #                 yield json.dumps({"type":"error","code": 400, "msg": "缺少题目信息！"})
    #             return StreamingHttpResponse(error_generator(), content_type="application/json")
    #
    #         question = Question.objects.filter(id=question_id).first()
    #         if not question:
    #             def error_generator():
    #                 yield json.dumps({"type":"error","code": 404, "msg": "题目不存在！"})
    #             return StreamingHttpResponse(error_generator(), content_type="application/json")
    #
    #         # 初始化系统提示词，只能初始化一次，否则容易产生幻觉
    #         system_prompt = None
    #         if not session_id:
    #             # 初始化系统提示词，拼接系统提示
    #             system_prompt = generate_complete_system_prompt(question)
    #
    #         session, _ = QuestionChatSession.get_or_create_session(
    #             user_id=user.id,
    #             question_id=question_id,
    #             session_id=session_id
    #         )
    #         history_messages = session.messages.copy()  # 拷贝，避免修改原数据
    #         if system_prompt:
    #             history_messages.insert(0, {"role": "system", "content": system_prompt})
    #
    #         # 拼接用户答案
    #         user_submit_answer = json.dumps(user_submit_answer)
    #         ask_prompt = "\n 用户答案如下（用户所选题目对应id，）：" + user_submit_answer + "请对比正确答案并为该用户进行复盘"
    #         history_messages.append({"role": "user", "content": ask_prompt})
    #
    #         # 异步埋点（AI复盘）
    #         AIOperationTracker.record_operation(
    #             user_id=request.user.id,
    #             ai_type=AiTypeEnum.REVIEW.value[0],  # AI复盘
    #             ip=request.META.get('REMOTE_ADDR', ''),
    #             device=request.META.get('HTTP_USER_AGENT', '')
    #         )
    #
    #         # 3. 返回流式响应（关键配置）
    #         response = StreamingHttpResponse(
    #             ai_stream_generator(history_messages, session, system_prompt),
    #             content_type="text/event-stream; charset=utf-8"
    #         )
    #         # 禁用缓存和缓冲，确保实时推送
    #         response['Cache-Control'] = 'no-cache'
    #         response['X-Accel-Buffering'] = 'no'  # 禁用Nginx缓冲
    #         # response['Transfer-Encoding'] = 'chunked'  # 分块传输
    #         return response
    #     except Exception as e:
    #         raise e

    # ========== 主观题AI复盘内容 ==========
    # @action(detail=False, methods=['post'])
    # def get_subjective_question_review_prompt_stream(self, request):
    #     """返回AI复盘内容"""
    #     try:
    #         # 1. 原有参数校验+数据查询逻辑（完全复用）
    #         question_id = request.data.get("question_id")
    #         session_id = request.data.get("session_id")
    #         user = request.user
    #
    #         user_submit_answer = request.data.get('user_answer')
    #         if not user_submit_answer:
    #             raise BizException("未添加答案信息")
    #
    #         if not question_id:
    #             # 流式中无法返回JSON错误，直接yield错误信息
    #             def error_generator():
    #                 yield json.dumps({"type":"error","code": 400, "msg": "缺少题目信息！"})
    #             return StreamingHttpResponse(error_generator(), content_type="application/json")
    #
    #         question = Question.objects.filter(id=question_id).first()
    #         if not question:
    #             def error_generator():
    #                 yield json.dumps({"type":"error","code": 404, "msg": "题目不存在！"})
    #             return StreamingHttpResponse(error_generator(), content_type="application/json")
    #
    #         # 初始化系统提示词，只能初始化一次，否则容易产生幻觉
    #         system_prompt = None
    #         if not session_id:
    #             # 初始化系统提示词，拼接系统提示
    #             system_prompt = generate_complete_system_prompt(question)
    #
    #         session, _ = QuestionChatSession.get_or_create_session(
    #             user_id=user.id,
    #             question_id=question_id,
    #             session_id=session_id
    #         )
    #         history_messages = session.messages.copy()  # 拷贝，避免修改原数据
    #         if system_prompt:
    #             history_messages.insert(0, {"role": "system", "content": system_prompt})
    #
    #         # 拼接用户答案
    #         user_submit_answer_str = str(user_submit_answer)
    #         ask_prompt = f"""
    #                 === 用户答案数据（JSON格式）如下,请对比正确答案并为该用户进行复盘===
    #                  {user_submit_answer_str}
    #                 ======="""
    #         history_messages.append({"role": "user", "content": ask_prompt})
    #
    #         # 异步埋点（AI复盘）
    #         AIOperationTracker.record_operation(
    #             user_id=request.user.id,
    #             ai_type=AiTypeEnum.REVIEW.value[0],  # AI复盘
    #             ip=request.META.get('REMOTE_ADDR', ''),
    #             device=request.META.get('HTTP_USER_AGENT', '')
    #         )
    #
    #         # 3. 返回流式响应（关键配置）
    #         response = StreamingHttpResponse(
    #             ai_stream_generator(history_messages, session, system_prompt),
    #             content_type="text/event-stream; charset=utf-8"
    #         )
    #         # 禁用缓存和缓冲，确保实时推送
    #         response['Cache-Control'] = 'no-cache'
    #         response['X-Accel-Buffering'] = 'no'  # 禁用Nginx缓冲
    #         # response['Transfer-Encoding'] = 'chunked'  # 分块传输
    #         return response
    #     except Exception as e:
    #         raise e



