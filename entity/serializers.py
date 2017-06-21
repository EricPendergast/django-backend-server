from rest_framework_mongoengine.serializers import DocumentSerializer
from models import Entity


class EntitySummarySerializer(DocumentSerializer):
    class Meta:
        model = Entity
        depth = 2
        fields = (
            'type', 'source_type', 'source', 'data_summary', 'data_header', 'allowed_user', 'created_at', 'updated_at'
        )


class EntityDetailedSerializer(DocumentSerializer):
    class Meta:
        model = Entity
        depth = 2
        fields = '__all__'
