import django_filters
from django.db.models.query_utils import Q

from biz.models import WebUser, Tag, Question, Prompt, UserFeedback


class WebUserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='username', lookup_expr='icontains')
    mobile = django_filters.CharFilter(field_name='mobile', lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    start_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    end_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = WebUser
        fields = ['username']

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
    content = django_filters.CharFilter(field_name='content', lookup_expr='icontains')
    code = django_filters.CharFilter(field_name='code', lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    start_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    end_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = Question
        fields = ['content','code','status','start_time','end_time']

class PromptFilter(django_filters.FilterSet):
    prompt_content = django_filters.CharFilter(field_name='content', lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    start_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    end_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = Prompt
        fields = ['prompt_content', "status", "start_time", "end_time" ]

class UserFeedbackFilter(django_filters.FilterSet):
    content = django_filters.CharFilter(field_name='content', lookup_expr='icontains')
    feedback_status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    start_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    end_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = UserFeedback
        fields = ['content', "feedback_status", "start_time", "end_time" ]
