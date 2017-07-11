from rest_framework_mongoengine.serializers import DocumentSerializer
from models import Entity, DataHeader
import util


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
    def validate(self, attrs):
        raise util.InvalidInputError("Invalid serializer")
        return attrs
    
    class Meta:
        model = Entity
        depth = 2
        fields = '__all__'
