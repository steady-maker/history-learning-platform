from wechatpayv3 import WeChatPay, WeChatPayType

from utils.middleware import info_logger

# constants.py
from enum import Enum


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