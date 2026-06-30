import django_filters
from django.db.models import Count, Q

from question.models import Tag, Question, Prompt

class TagFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    tag_key = django_filters.CharFilter(field_name='tag_key', lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    start_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    end_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = Tag
        fields = ['name','tag_key','status','start_time','end_time']

class QuestionFilter(django_filters.FilterSet):
    # content = django_filters.CharFilter(field_name='content', lookup_expr='icontains')
    code = django_filters.CharFilter(field_name='code', lookup_expr='icontains')
    type = django_filters.CharFilter(field_name='type', lookup_expr='exact')
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    start_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    end_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    # 重写filter_queryset，实现标签交集筛选
    def filter_queryset(self, queryset):
        # 先执行原有筛选逻辑
        queryset = super().filter_queryset(queryset)

        # 手动处理tag_ids的交集筛选
        tag_ids_str = self.request.GET.get('tag_ids', '')
        if tag_ids_str:
            try:
                # 拆分并转成整数列表
                tag_id_list = [int(id.strip()) for id in tag_ids_str.split(',') if id.strip().isdigit()]
                if tag_id_list and len(tag_id_list) > 0:
                    # 步骤1：筛选出关联任意一个目标标签的记录
                    queryset = queryset.filter(tags__id__in=tag_id_list)

                    # 步骤2：按Question分组，统计关联的目标标签数量
                    queryset = queryset.annotate(
                        matched_tag_count=Count('tags', filter=Q(tags__id__in=tag_id_list), distinct=True)
                    )

                    # 步骤3：只保留匹配数量等于标签总数的记录（交集）
                    queryset = queryset.filter(matched_tag_count=len(tag_id_list))

            except ValueError:
                # 处理非数字ID的异常
                pass

        return queryset

    class Meta:
        model = Question
        fields = ['code', 'type', 'status', 'start_time', 'end_time']

class PromptFilter(django_filters.FilterSet):
    prompt_content = django_filters.CharFilter(field_name='content', lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    start_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    end_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = Prompt
        fields = ['prompt_content', "status", "start_time", "end_time" ]
