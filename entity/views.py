from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route

from django.template.response import TemplateResponse

from serializers import *
from models import *


def index_view(request):
    context = {}
    return TemplateResponse(request, 'index.html', context)


class EntityViewSet(viewsets.ViewSet):
    """
    Read-only User endpoint
    """

    """
    Get all entity summary
    """
    @list_route(methods=['get'])
    def get_all_entity(self, request):
        query_set = Entity.objects()
        serializer = EntitySummarySerializer(query_set, many=True, required=True)
        return Response(serializer.data)

    """
    Select Entity in-details
    @param: entity_type
    """
    @detail_route(methods=['get'])
    def select_entity(self, request, pk=None):
        query_set = Entity.objects(type=pk).first()
        if query_set is None:
            return Response()
        serializer = EntityDetailedSerializer(query_set)
        return Response(serializer.data)

