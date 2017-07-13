from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route

from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from django.utils.six import BytesIO

from django.template.response import TemplateResponse
from django.http import HttpResponse

from serializers import *
from models import *
from input_verifier import CreateEntityVerifier, CreateEntityMappedVerifier
from handler import *

import csv
import util
from util import InvalidInputError, string_caster
import os.path
import uuid
import re



def index_view(request):
    context = {}
    return HttpResponse("index stub page")
    # return TemplateResponse(request, 'index.html', context)
    

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


        
    """
    Creating entity (without mapping information)
    @param: entity_type
    """
    @list_route(methods=['post'])
    def create_entity(self, request):
        # 0. checking (to be developed afterwards)
        # 1. getting csv/tsv information, header information, uploaded data
        # 2. save file to temp dir
        # 3. save basic entity information, temp dir folder "progressing" state in mongo
        # 4. return 100 rows of data
        
        try:
            verifier = CreateEntityVerifier()
            verifier.verify(0, request)
            
            response_data = EntityViewSetHandler.create_entity(
                    request_data=request.data,
                    request_file=request.FILES["file_upload"],
                    verifier=verifier)
            
            assert verifier.verified, "Verification failed"
            return Response(response_data, status=200)
        except InvalidInputError as e:
            return Response({"error":str(e)}, status=400)
        
        
    """
    Creating entity (with mapping information)
    @param: entity_type
    """
    @detail_route(methods=['post'])
    def create_entity_mapped(self, request, pk=None):
        # 0. checking (to be developed afterwards)
        # 1. getting targeted entity from data
        # 2. getting header_name/ column_type mapping information from data
        # 3. validating mapping (to be developed afterwards)
        # 4. return 100 rows of data
        
        try:
            verifier = CreateEntityMappedVerifier()
            response_data = EntityViewSetHandler.create_entity_mapped(
                    request_data = request.data, 
                    verifier = verifier,
                    pk = pk)
            
            assert verifier.verified
            return Response(response_data, status=200)
        except InvalidInputError as e:
            return Response({"error":str(e)}, status=400)
        
