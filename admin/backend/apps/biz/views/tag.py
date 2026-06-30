# -*- coding: utf-8 -*-

"""
@Remark: 题目标签管理
"""
from rest_framework.decorators import action

from biz.filter import TagFilter
from biz.models import Tag
from biz.serializer.tag_ser import TagInfoSerializer
from utils.jsonResponse import SuccessResponse
from utils.viewset import CustomModelViewSet


class TagViewSet(CustomModelViewSet):
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
    queryset = Tag.objects.all().order_by('-create_time')
    serializer_class = TagInfoSerializer
    filterset_class = TagFilter

    # @action(detail=False, methods=['put'])
    # def reset_verification_code_count(self,request):
    #     """重置验证码次数"""
    #     mobile = request.data.get('mobile')
    #     daily_key = REDIS_SMS_DAILY_KEY_PREFIX + mobile
    #     redis_conn.delete(daily_key)
    #     return SuccessResponse(msg="重置成功")

    @action(detail=False,methods=['get'])
    def get_tag_tree(self, request):
        """获取标签树"""
        # 获取所有标签
        tags = list(Tag.objects.all().values('id', 'name', 'parent_id'))

        # 构建节点映射
        tag_dict = {}
        for tag in tags:
            tag_dict[tag['id']] = {
                'value': tag['id'],
                'label': tag['name'],
                'children': []
            }

        # 构建树结构
        tree = []
        for tag in tags:
            node = tag_dict[tag['id']]
            parent_id = tag['parent_id']

            if parent_id and parent_id in tag_dict:
                # 添加到父节点
                tag_dict[parent_id]['children'].append(node)
            else:
                # 根节点
                tree.append(node)

        return SuccessResponse(msg="success", data=tree)


    # def update(self, request, *args, **kwargs):
    #     # 所选父id不能是自己，或者是自己的子类别或者是父类别,但是的话不确定要不要新增这个检查，我们后面再说 TODO
    #     data = request.get()
    #     if data['parent_id']:
    #         pass




