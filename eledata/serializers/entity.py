from rest_framework_mongoengine.serializers import DocumentSerializer
from eledata.models.entity import Entity, DataHeader


class EntitySummarySerializer(DocumentSerializer):
    class Meta:
        model = Entity
        depth = 2
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
