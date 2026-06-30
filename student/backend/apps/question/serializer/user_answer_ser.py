from rest_framework import serializers

from question.models import UserAnswer
from question.serializer.tag_ser import TagSimpleSerializer


class UserQuestionListSerializer(serializers.ModelSerializer):
    """用户题目列表序列化器（适配text类型content字段）"""
    # 核心调整：content字段改为CharField（兼容text类型，DRF会自动适配）
    user_score = serializers.IntegerField(read_only=True, label="用户本题总得分")
    full_score = serializers.IntegerField(read_only=True, label="题目满分")
    content = serializers.CharField(read_only=True, label="题干内容", allow_null=True, allow_blank=True)  # 适配text类型

    tags = TagSimpleSerializer(many=True, read_only=True, label="题目标签")

    # 动态添加的字段
    is_collect = serializers.CharField(read_only=True, label="是否收藏：1=是，0=否")
    is_right = serializers.CharField(read_only=True, label="是否做对：1=是，0=否")

    class Meta:
        model = UserAnswer
        fields = [
            'question_id', 'user_id', 'answer_seq', 'cost_time',
            'user_score', 'full_score', 'content',  # text类型的content已适配
            'is_collect', 'is_right', 'tags'
        ]