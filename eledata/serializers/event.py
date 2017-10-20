from rest_framework_mongoengine.serializers import DocumentSerializer
from eledata.models.event import *


class GeneralEventSerializer(DocumentSerializer):
    class Meta:
        model = Event
        depth = 2
        fields = ['event_category', 'event_type', 'event_value', 'event_desc', 'chart_type', 'chart', 'detailed_data',
                  'created_at', 'updated_at']


class DetailedEventSerializer(DocumentSerializer):
    class Meta:
        model = Event
        depth = 2
        fields = '__all__'


class DetailedJobSerializer(DocumentSerializer):
    class Meta:
        model = Job
        depth = 2
        fields = ['job_engine', 'job_status', 'group', 'parameter']


class QuestionSerializer(DocumentSerializer):
    class Meta:
        model = Event
        depth = 2
        fields = '__all__'
