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
            
            # The dir that the uploaded data file will be saved to.
            # Appending the original filename to the end so that the new
            # filename has the same extension, while also making the filename
            # more recognizable.
            filename = "temp/" + str(uuid.uuid4()) \
                    + "." + str(request.FILES["file_upload"])
            
            with open(filename, "w") as file:
                file.write(request.FILES["file_upload"].read())
            
            # Parsing the entity JSON passed in into a dictionary
            entity_dict = JSONParser().parse(BytesIO(request.data["entity"]))
            
            verifier.verify(1, request.data)
            
            entity_dict["source"] = \
                    {"file":{"filename":filename, "isHeaderIncluded":request.data["isFileHeaderIncluded"]}}
                
                
            entity_dict['state'] = 1
            
            verifier.verify(2, entity_dict)
            
            response_data = {}
            serializer = EntityDetailedSerializer(data=entity_dict)
            
            verifier.verify(3, serializer)
            
            # Saving the serializer while also adding its id to the response
            response_data['entity_id'] = str(serializer.save().id)
            response_data['data'] = util.file_to_list_of_dictionaries(
                    open(entity_dict["source"]["file"]["filename"]),
                    numLines=100,
                    isHeaderIncluded=util.string_caster["bool"](
                        entity_dict["source"]["file"]["isHeaderIncluded"]))
            
            
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
            entity = Entity.objects.get(pk=pk)
            verifier.verify(0, request.data, entity, pk)
            verifier.verify(1, request.data['data_header'], entity.source.file.filename)
            
            # We will create a dummy entity whose only purpose is to serialize the
            # two fields we give it, so we can add them to the actual entity. The
            # dummy starts as a dictionary and then becomes an Entity.
            dummy = {}
            dummy['data_header'] = request.data['data_header']
            
            assert os.path.isfile(entity.source.file.filename)
            data = util.file_to_list_of_dictionaries(
                    open(entity.source.file.filename, 'r'),
                    isHeaderIncluded=entity.source.file.isHeaderIncluded)
            # Casting everything in data from strings to their proper data type
            # according to request.data['data_header']
            for item in data:
                for mapping in dummy['data_header']:
                    item[mapping["source"]] = \
                        string_caster[mapping["data_type"]](item[mapping["source"]])
            
            dummy['data'] = data
            dummySerializer = EntityDetailedSerializer(data=dummy)
            
            verifier.verify(2, dummySerializer)
            
            dummy = Entity(**dummySerializer.validated_data)
            
            # Adding the dummy's fields to the actual entity
            entity.data_header = dummy.data_header
            entity.data = dummy.data
            # assert(re.match(entity.source.file.filename,
                    # r"^temp\/[0-9a-fA-F-]{36}.*$") is not None)
            os.remove(entity.source.file.filename)
            entity.source.file = None
            entity.save()
            
            assert verifier.verified
            return Response(data[:100], status=200)
        
        except InvalidInputError as e:
            return Response({"error":str(e)}, status=400)
        
    
    
    # TODO: Security hole; Don't leave this in
    """
    
    """
    @detail_route(methods=['get'])
    def remove_entities(self, request, pk=None):
        Entity.objects.delete()
        return Response("All entities deleted", status=200)


