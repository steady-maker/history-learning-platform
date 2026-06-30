from django_apscheduler.models import DjangoJob
from utils.serializers import CustomModelSerializer


class DjangoJobSerializer(CustomModelSerializer):
    class Meta:
        model = DjangoJob
        exclude = ('job_state',)
