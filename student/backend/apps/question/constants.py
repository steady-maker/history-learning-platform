# constants.py
from enum import Enum, unique
from typing import Any


class QuestionTypeEnum(Enum):
    """题目类型枚举类"""
    SINGLE_CHOICE = ('1', '单选')  # 单选
    MULTIPLE_CHOICE = ('2', '多选')  # 多选
    FILL_BLANK = ('3', '填空')  # 填空
    JUDGE = ('4', '判断')  # 判断
    SHORT_ANSWER = ('5', '问答')  # 问答

    @classmethod
    def get_choices(cls):
        """生成Django模型需要的choices格式（元组列表）"""
        return [(member.value[0], member.value[1]) for member in cls]

    @classmethod
    def get_label(cls, code):
        """根据编码获取中文标签（比如 '1' → '单选'）"""
        for member in cls:
            if member.value[0] == code:
                return member.value[1]
        return ''

    @classmethod
    def get_code(cls, label):
        """根据中文标签获取编码（比如 '单选' → '1'）"""
        for member in cls:
            if member.value[1] == label:
                return member.value[0]
        return ''

    @classmethod
    def get_option_values(cls):
        """返回单选+多选的编码（1、2）"""
        return [
            cls.SINGLE_CHOICE.value[0],
            cls.MULTIPLE_CHOICE.value[0]
        ]

class PromptTypeEnum(Enum):
    """提示词类型枚举"""
    WHEN_PROMPTED = ('1','在提示时')
    WHEN_RATING = ('2','在打分时')
    DURING_REVIEW = ('3','在复盘时')

    @classmethod
    def get_prompt_type_length(cls):
        """获取提示词类型个数长度"""
        return len(list(cls))

    @classmethod
    def get_choices(cls):
        """生成Django模型需要的choices格式（元组列表）"""
        return [(member.value[0], member.value[1]) for member in cls]

    @classmethod
    def get_label(cls, code):
        """根据编码获取中文标签（比如 '1' → '单选'）"""
        for member in cls:
            if member.value[0] == code:
                return member.value[1]
        return ''

class AiTypeEnum(Enum):
    """提示词类型枚举"""
    TIP = ('1','AI提示')
    JUDGE = ('2','AI判题')
    REVIEW = ('3','AI复盘')

    @classmethod
    def get_choices(cls):
        """生成Django模型需要的choices格式（元组列表）"""
        return [(member.value[0], member.value[1]) for member in cls]

    @classmethod
    def get_label(cls, code):
        """根据编码获取中文标签（比如 '1' → '单选'）"""
        for member in cls:
            if member.value[0] == code:
                return member.value[1]
        return ''


# -------------------------- 业务类型枚举 --------------------------
# class BusinessTypeEnum(ChoicesEnum):
#     SUBJECTIVE_ANSWER = ('subjective_answer', '主观题答题')
#     OBJECTIVE_ANSWER = ('objective_answer', '客观题答题')
#
#     def __init__(self, value, label):
#         self.value = value
#         self.label = label


# 允许用户提示的最大次数
MAX_ASK_COUNT =  3

# 用户在复盘后与AI交流保留最大上下文轮数
MAX_CONTEXT_ROUND_ON_REVIEW = 5

# 记录题目基本信息的redis最长过期时间
MAX_QUESTION_INFO_EXPIRE_TIME = 365 * 24 * 60 * 60 # 365天，等同于“永久”,可能要考虑热点击穿问题