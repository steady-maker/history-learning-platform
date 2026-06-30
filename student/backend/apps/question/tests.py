from django.test import TestCase

# Create your tests here.
import os
from openai import OpenAI
from volcengine.maas import MaasException, MaasService

from system.models import Config

# # 从环境变量中获取您的API KEY，配置方法见：https://www.volcengine.com/docs/82379/1399008
# api_key = os.getenv('ARK_API_KEY')
#
# client = OpenAI(
#     base_url="https://ark.cn-beijing.volces.com/api/v3",
#     api_key=api_key,
# )
#
# response = client.responses.create(
#     model="doubao-seed-1-6-flash-250828",
#     input=[
#         {
#             "role": "user",
#             "content": [
#
#                 {
#                     "type": "input_image",
#                     "image_url": "https://ark-project.tos-cn-beijing.volces.com/doc_image/ark_demo_img_1.png"
#                 },
#                 {
#                     "type": "input_text",
#                     "text": "你看见了什么？"
#                 },
#             ],
#         }
#     ]
# )
#
# print(response)

from question.utils import AIClient

# 初始化火山方舟客户端
client = AIClient(provider="VOLC_ARK")

# 测试纯文本多轮对话（解题提示场景）
system_prompt = "你是历史学习助手，回答简洁，不超过50字。"
messages = [{"role": "user", "content": "请解释辛亥革命的核心意义"}]
ai_response, updated_messages = client.chat_completion_with_context(system_prompt, messages)
print("纯文本响应：", ai_response)

# 测试多模态调用（匹配官方图文示例）
multimodal_response = client.multimodal_chat(
    text="你看见了什么？",
    image_url="https://ark-project.tos-cn-beijing.volces.com/doc_image/ark_demo_img_1.png"
)
print("多模态响应：", multimodal_response)