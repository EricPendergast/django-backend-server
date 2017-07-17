from rest_framework_mongoengine.serializers import DocumentSerializer
from eledata.models.entity import Entity, DataHeader
from eledata.util import InvalidInputError


class EntitySummarySerializer(DocumentSerializer):
    class Meta:
        model = Entity
        depth = 2
        fields = (
            'type', 'source_type', 'source', 'data_summary', 'data_header', 'allowed_user', 'created_at', 'updated_at'
        )
        fields = '__all__'

class DataHeaderSerializer(DocumentSerializer):
    class Meta:
        model = DataHeader
        depth = 2
        fields = '__all__'

class EntityDetailedSerializer(DocumentSerializer):
    class Meta:
        model = Entity
        depth = 2
        fields = '__all__'
