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
from models import *

import csv
import util
import datetime
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


    def _verify_create_entity(self, request):
        # TODO: Replace valid types tuples with enums/lists/dictionaries to
        # decouple them from this specific method
        if not ('entity' in request.data):
            raise util.InvalidInputError("No entity data in request")
        
        entity_dict = JSONParser().parse(BytesIO(request.data["entity"]))
        if not ('type' in entity_dict and 
                entity_dict['type'] in ("transaction", "Something else...")):
            raise util.InvalidInputError("Invalid or missing entity 'type' field")
        if not ('source_type' in entity_dict and 
                entity_dict['source_type'] in ("local", "something else...")):
            raise util.InvalidInputError("Invalid or missing entity 'source_type' field")
        if 'file_upload' not in request.FILES:
            raise util.InvalidInputError("No request 'file_upload' field")
        
        
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
            self._verify_create_entity(request)
            
            # The dir that the uploaded data file will be saved to.
            # Appending the original filename to the end so that the new
            # filename has the same extension, and also makes the filename more
            # recognizable.
            filename = "temp/" + str(uuid.uuid4()) \
                    + "." + str(request.FILES["file_upload"])
            
            with open(filename, "w") as file:
                file.write(request.FILES["file_upload"].read())
            
            # Parsing the entity JSON passed in into a dictionary
            entity_dict = JSONParser().parse(BytesIO(request.data["entity"]))
            entity_dict["source"] = {"file":filename}
            
            response_data = {}
            
            serializer = EntityDetailedSerializer(data=entity_dict)
                            
            if serializer.is_valid():
                response_data['entity_id'] = str(serializer.save().id)
            else:
                raise util.InvalidInputError("Invalid serializer")
            
            response_data['data'] = util.file_to_list_of_dictionaries(
                    open(entity_dict["source"]["file"]), numLines=100)
            
            return Response(response_data, status=200)
        except util.InvalidInputError as e:
            return Response({"error":str(e)}, status=400)
        
    '''
    Checks that the user input is of the correct format. Throws an
    InvalidInputError exception if in the wrong format
    Ensures the following:
        - 'entity' exists
        - request.data has a 'data_header' element
        - 'entity' has a source file field
        - the data header has all the valid fields, and valid types
    '''
    
    def _verify_create_entity_mapped(self, request, entity):
        if entity is None:
            raise util.InvalidInputError("Can't find the entity with the given id: %s" % pk)
        if not ('data_header' in request.data):
            raise util.InvalidInputError("No data header.")
        if entity.source.file == None:
            raise util.InvalidInputError("Can't find the entity source file.")
        
        for mapping in request.data['data_header']:
            if not ({"source","mapped","data_type"} <= set(mapping) and
                    StringCaster.contains(mapping["data_type"])):
                raise InvalidInputError("Invalid data header")
            

    """
    Creating entity (without mapping information)
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
            entity = Entity.objects.get(pk=pk)
            self._verify_create_entity_mapped(request, entity)
            
            
            # We will create a dummy entity whose only purpose is to serialize the
            # two fields we give it, so we can add them to the actual entity. The
            # dummy starts as a dictionary, then becomes a serializer of its
            # previous self, and then becomes an Entity
            dummy = {}
            dummy['data_header'] = request.data['data_header']
            
            assert os.path.isfile(entity.source.file)
            data = util.file_to_list_of_dictionaries(open(entity.source.file, 'r'))
            # Casting everything in data from strings to their proper data type
            # according to request.data['data_header']
            for item in data:
                for mapping in dummy['data_header']:
                    item[mapping["source"]] = \
                        StringCaster[mapping["data_type"]](item[mapping["source"]])
            
            dummy['data'] = data
            
            dummy = EntityDetailedSerializer(data=dummy)
            assert type(dummy) is EntityDetailedSerializer
            
            if dummy.is_valid():
                dummy = Entity(**dummy.validated_data)
                assert type(dummy) is Entity
                # Adding the dummy's fields to the actual entity
                entity.data_header = dummy.data_header
                entity.data = dummy.data
                # assert(re.match(entity.source.file,
                        # r"^temp\/[0-9a-fA-F-]{36}.*$") is not None)
                os.remove(entity.source.file)
                entity.source.file = None
                entity.save()
                return Response(data[:100], status=200)
            else:
                raise util.InvalidInputError("Invalid serializer")
        
        except util.InvalidInputError as e:
            return Response({"error":str(e)}, status=400)
        
    
    
    # TODO: Security hole; Don't leave this in
    """
    
    """
    @detail_route(methods=['get'])
    def remove_entities(self, request, pk=None):
        Entity.objects.delete()
        return Response("All entities deleted", status=200)




        
# Takes a string representation of a type and returns a function that casts
# strings to that type
class StringCaster:
    
    # I implement the meta class so that I can use the static [] operator on
    # StringCaster.
    # Explanation: when you call object[something], it looks at the class of
    # 'object' to find the code for __getitem__. So when you call
    # StringCaster[something], it looks to the class of StringCaster, which we
    # defined as StringCaster.Meta, and executes its __getitem__ method.
    class Meta(type):
        def __getitem__(cls, key):
            return StringCaster._objects[key]
        
    @staticmethod
    def contains(key):
        return key in StringCaster._objects
    
    
    __metaclass__= Meta
    
    # Contains the user-defined casting methods
    class Casters:
        @staticmethod
        def _string_to_date(str):
            return datetime.datetime.strptime(str, '%d/%m/%Y')
        
    _objects = {
        "string":str,
        "date":Casters._string_to_date,
        "number":float
    }
    
