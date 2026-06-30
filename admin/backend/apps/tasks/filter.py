from django_apscheduler.models import DjangoJob
import django_filters


class DjangoJobFilter(django_filters.FilterSet):
    class Meta:
        model = DjangoJob
        fields = ['id']
