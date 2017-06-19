from rest_framework_mongoengine.serializers import DocumentSerializer
from models import Entity


class EntitySerializer(DocumentSerializer):
    class Meta:
        model = Entity
        depth = 2
        fields = '__all__'
