from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from django.utils.six import BytesIO

from eledata.serializers.entity import *
from eledata.models.entity import *

import csv
from eledata import util
from eledata.util import InvalidInputError, string_caster
import os.path
import uuid


class EntityViewSetHandler():
    
    @staticmethod
    def create_entity(request_data, request_file, verifier):
        # The dir that the uploaded data file will be saved to.
        # Appending the original filename to the end so that the new
        # filename has the same extension, while also making the filename
        # more recognizable.
        filename = "temp/" + str(uuid.uuid4()) + "." + str(request_file)
        
        with open(filename, "w") as file:
            file.write(request_file.read())
        
        # Parsing the entity JSON passed in into a dictionary
        entity_dict = JSONParser().parse(BytesIO(request_data["entity"]))
        
        verifier.verify(1, request_data)
        
        entity_dict["source"] = {"file":
               {"filename":filename,
                "isHeaderIncluded":request_data["isFileHeaderIncluded"]}}
               
            
        entity_dict['state'] = 1
        
        verifier.verify(2, entity_dict)
        
        response_data = {}
        serializer = EntityDetailedSerializer(data=entity_dict)
        
        verifier.verify(3, serializer)
        
        # Saving the serializer while also adding its id to the response
        response_data['entity_id'] = str(serializer.save().id)
        # Loading the first 100 lines of data from the request file
        response_data['data'] = util.file_to_list_of_dictionaries(
                open(entity_dict["source"]["file"]["filename"]),
                numLines=100,
                isHeaderIncluded=util.string_caster["bool"](
                    entity_dict["source"]["file"]["isHeaderIncluded"]))
        
        return response_data
            
    
    
    @staticmethod
    def create_entity_mapped(request_data, verifier, pk):
        entity = Entity.objects.get(pk=pk)
        verifier.verify(0, request_data, entity, pk)
        verifier.verify(1, request_data['data_header'], entity.source.file.filename)
        
        # We will create a dummy entity whose only purpose is to serialize the
        # two fields we give it, so we can add them to the actual entity. The
        # dummy starts as a dictionary and then becomes an Entity.
        dummy = {}
        dummy['data_header'] = request_data['data_header']
        
        assert os.path.isfile(entity.source.file.filename)
        data = util.file_to_list_of_dictionaries(
                open(entity.source.file.filename, 'r'),
                isHeaderIncluded=entity.source.file.isHeaderIncluded)
        
        for item in data:
            for mapping in dummy['data_header']:
                item[mapping["mapped"]] = item[mapping["source"]]
                del item[mapping["source"]]
        # Casting everything in data from strings to their proper data type
        # according to request.data['data_header']
        for item in data:
            for mapping in dummy['data_header']:
                item[mapping["mapped"]] = \
                    string_caster[mapping["data_type"]](item[mapping["mapped"]])
            
        
        dummy['data'] = data
        dummySerializer = EntityDetailedSerializer(data=dummy)
        
        verifier.verify(2, dummySerializer)
        
        dummy = Entity(**dummySerializer.validated_data)
        
        # Adding the dummy's fields to the actual entity
        entity.data_header = dummy.data_header
        entity.data = dummy.data
        os.remove(entity.source.file.filename)
        entity.source.file = None
        entity.state = 2
        entity.save()
        
        return entity.data[:100]
            
