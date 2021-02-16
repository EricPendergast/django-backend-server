from rest_framework_mongoengine.serializers import DocumentSerializer
from eledata.models.job import *


class GeneralJobSerializer(DocumentSerializer):
    class Meta:
        model = Job
        depth = 2
        fields = ['job_engine', 'job_status', 'group', 'parameter', 'event_type']


class DetailedJobSerializer(DocumentSerializer):
    class Meta:
        model = Job
        depth = 2
        fields = '__all__'
