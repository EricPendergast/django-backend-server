from rest_framework_mongoengine.serializers import DocumentSerializer
from eledata.models.entity import Entity, DataHeader


class EntitySummarySerializer(DocumentSerializer):
    class Meta:
        model = Entity
        depth = 2
        fields = ['state', 'type', 'source_type', 'source', 'data_summary', 'data_summary_chart', 'data_header',
                  'created_at', 'updated_at', 'data']


class DataHeaderSerializer(DocumentSerializer):
    class Meta:
        model = DataHeader
        depth = 2
        fields = ['state', 'type', 'source_type', 'source', 'data_summary', 'data_summary_chart', 'data_header',
                  'created_at', 'updated_at', 'data']


class EntityDetailedSerializer(DocumentSerializer):
    class Meta:
        model = Entity
        depth = 2
        fields = ['state', 'type', 'source_type', 'source', 'data_summary', 'data_summary_chart', 'data_header',
                  'created_at', 'updated_at', 'data']
