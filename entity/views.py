from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route

from rest_framework.parsers import JSONParser
from django.utils.six import BytesIO

from django.template.response import TemplateResponse
from django.http import HttpResponse

from serializers import *
from models import *
from models import *

import csv
import util


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
        
        # The dir that the uploaded data file will be saved to
        filename = "temp/" + str(request.FILES["fileUpload"])
        
        with open(filename, "w") as file:
            file.write(request.FILES["fileUpload"].read())
        
        # Parsing the entity JSON passed in into a dictionary
        entityDict = JSONParser().parse(BytesIO(request.data["entity"]))
        entityDict["source"] = {"file":filename}
        
            

        serializer = EntityDetailedSerializer(data=entityDict)
                        
        if serializer.is_valid():
            serializer.save()
            return Response(status=200)
        else:
            return Response("Invalid serializer", status=400)
            

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
        
        entity = Entity.objects.filter(pk=pk).first()
        assert(entity is not None), "Can't find the entity with the given id: %s" % pk
        
        # We will create a dummy entity whose only purpose is to serialize the
        # two fields we give it, so we can add them to the actual entity. The
        # dummy starts as a dictionary, then as a serializer of its previous
        # self, and then becomes an Entity
        dummy = {}
        dummy['data_header'] = request.data['data_header']
        dummy['data'] = util.csv_to_list_of_dictionaries(
                open(entity.source.file, 'r'))
        
        assert type(dummy) is dict
        dummy = EntityDetailedSerializer(data=dummy)
        assert type(dummy) is EntityDetailedSerializer
        
        if dummy.is_valid():
            dummy = Entity(**dummy.validated_data)
            assert type(dummy) is Entity
            # Adding the dummy's fields to the actual entity
            entity.data_header = dummy.data_header
            entity.data = dummy.data
            # id = entity.id
            # print "Data of entity before save: %s" % entity.data
            entity.save()
            #
            # entity2 = Entity.objects.filter(id=id).first()
            # print "Data of entity retrieved after save: %s" % entity2.data
            # print "Data of entity reference after save: %s" % entity.data
            #
            # assert entity.id == entity2.id
            # print str(type(entity.data)) + " " + str(type(entity2.data))
            #
            # entity2.data = entity.data
            # assert entity2.data == entity.data
            # entity2.save()
            # entity.save()
        else:
            print "Invalid serializer"
        
        
        # print "Hello%s" % request.data['data_header']
        # dataHeaderSerializers = [DataHeaderSerializer(data=item) for item in request.data['data_header']]
        # if all(ser.is_valid() for ser in dataHeaderSerializers):
        #     entity.data_header = [item.validated_data for item in dataHeaderSerializers]
        
        # if dataHeaderSerializer.is_valid():
            # entity.data_header = dataHeaderSerializer.validated_data
            # entity.data = entityDataSerializer.validated_data
            # entity.data = entityDataJson
        
        # print "HERE"
        # entityDataJson = util.csv_to_list_of_dictionaries(open(entity.source.file, 'r'), list=entity.data)
        # entityDataSerializer =
        # print "ASDF%sASDF" % entityDataJson
        # entityDataSerializer = JSONParser().parse(BytesIO(entityDataJson))
        
            
        
        # entityData['data'] = []
        # # putting the uploaded data into 'entityData'
        # with open(entity.source.file, 'r') as file:
        #
        #     # assert request.data["file_format"] == "csv",\
        #     # "TODO: allow use of tsv file format"
        #
        #     reader = csv.reader(file)
        #
        #     firstRow = None
        #     for row in reader:
        #         if firstRow is None:
        #             firstRow = row
        #         else:
        #             assert len(row) == len(firstRow),\
        #             "Header row and subsequent row(s) are not the same length"
        #
        #             # each item in the data list is refered to as a "data
        #             # point"
        #             dataPointDict = {}
        #             for i in range(0, len(row)):
        #                 dataPointDict[firstRow[i]] = row[i]
        #
        #             entityData['data'] += (dataPointDict,)
        # print "DATA%s" % entityData
        # entitySerializer = EntityDetailedSerializer(data=entityData, required=False, allow_null=True)
        # if entitySerializer.is_valid():
        #     entityNew = entitySerializer.validated_data
        #     assert type(entityNew) is Entity
        #     entityNew.save()
        # else:
        #     print entitySerializer.errors
        #     print "Invalid serializer"
        # print "DATA%s" % entityData
        # entity.data = entityData['data']
        
        # entity.source = None
        
        # entity.save()
        return Response(status=200)
    
    # TODO: Don't leave this in
    """
    
    """
    @detail_route(methods=['get'])
    def remove_entities(self, request, pk=None):
        Entity.objects.delete()
        return Response("All entities deleted", status=200)


