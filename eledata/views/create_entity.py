from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from eledata.auth import CustomLoginRequiredMixin

from django.http import HttpResponse

from eledata.serializers.entity import *
from eledata.models.entity import *
from eledata.verifiers.entity import *
from eledata.handlers.create_entity import *

from eledata.util import InvalidInputError, string_caster
import uuid
import re



def index_view(request):
    context = {}
    return HttpResponse("index stub page")
    

class EntityViewSet(CustomLoginRequiredMixin, viewsets.ViewSet):
    """
    Read-only User endpoint
    """

    """
    Get all entity summary
    """
    @list_route(methods=['get'])
    def get_all_entity(self, request):
        query_set = Entity.objects(group=request.user.group)
        serializer = EntitySummarySerializer(query_set, many=True, required=True)
        return Response(serializer.data)


    """
    Select Entity in-details
    @param: entity_type
    """
    @detail_route(methods=['get'])
    def select_entity(self, request, pk=None):
        entity = Entity.objects(type=pk).first()
        if entity is None:
            return Response()
        if entity.group != request.user.group:
            return Response({"error":"User does not have permission to access this entity"})
        serializer = EntityDetailedSerializer(entity)
        return Response(serializer.data)

        
    """
    Creates an entity (without mapping information). Adds it to the group of
    the user who made the request
    
    If there is an error, the response will contain an "error" key, which will
    map to the error message. Otherwise it will send a response with the
    following:
    
        "entity_id", which maps to the id of the newly created entity
        "data", which maps to the first 100 lines of data parsed from the input
            file, with the original headers, or generated headers if no headers
            were given
    """
    @list_route(methods=['post'])
    def create_entity(self, request):
        # 0. checking (to be developed afterwards)
        # 1. getting csv/tsv information, header information, uploaded data
        # 2. save file to temp dir
        # 3. save basic entity information, temp dir folder "progressing" state in mongo
        # 4. return 100 rows of data
    
        verifier = CreateEntityVerifier()
        verifier.verify(0, request)
        
        response_data = EntityViewSetHandler.create_entity(
                request_data=request.data,
                request_file=request.FILES['file'],
                group=request.user.group,
                verifier=verifier)
        
        assert verifier.verified
        return Response(response_data, status=200)
    
        
    """
    Creating entity (with mapping information)
    """
    @detail_route(methods=['post'])
    def create_entity_mapped(self, request, pk=None):
        # 0. checking (to be developed afterwards)
        # 1. getting targeted entity from data
        # 2. getting header_name/ column_type mapping information from data
        # 3. validating mapping (to be developed afterwards)
        # 4. return 100 rows of data
        
        verifier = CreateEntityMappedVerifier()
        response_data = EntityViewSetHandler.create_entity_mapped(
                request_data = request.data, 
                verifier = verifier,
                pk = pk,
                group = request.user.group)
        
        assert verifier.verified
        return Response(response_data, status=200)
    
