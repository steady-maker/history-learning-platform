import django_filters

from system.models import Users, Menu, Dept, DictType, Role, Config, LoginLog


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='username', lookup_expr='icontains')
    mobile = django_filters.CharFilter(field_name='mobile', lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    start_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    end_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = Users
        fields = ['username']

class MenuFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')

    class Meta:
        model = Menu
        fields = ['name']


class DeptFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')

    class Meta:
        model = Dept
        fields = ['name']


class DictTypeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    type = django_filters.CharFilter(field_name='type', lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    start_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    end_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = DictType
        fields = ['name']

class RoleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    key = django_filters.CharFilter(field_name='key', lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    start_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    end_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = Role
        fields = ['name']

class ConfigFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    key = django_filters.CharFilter(field_name='key', lookup_expr='icontains')
    type = django_filters.CharFilter(field_name='type', lookup_expr='exact')
    start_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    end_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = Config
        fields = ['name']

class LoginLogFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='username', lookup_expr='icontains')
    ip = django_filters.CharFilter(field_name='ip', lookup_expr='startswith')
    region = django_filters.CharFilter(field_name='region', lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    login_type = django_filters.CharFilter(field_name='login_type', lookup_expr='exact')
    start_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    end_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = LoginLog
        fields = ['username']
