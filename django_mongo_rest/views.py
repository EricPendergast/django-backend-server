# # -*- coding: utf-8 -*-
# from __future__ import unicode_literals
# from django_mongo_rest.models import Entity, DataSummary
# from rest_framework import response
# from rest_framework.decorators import api_view
# from serializers import EntitySerializer
# import datetime
#
# # Create your views here.
#
#
# @api_view(['GET'])
# def index(request):
#     # entity = Entity.objects(type__contains="transaction")
#     # data_summary = [
#     #     DataSummary(
#     #         key="Conversion Records",
#     #         value='1',
#     #         order=1,
#     #     ),
#     #     DataSummary(
#     #         key="Customer Records",
#     #         value='20',
#     #         order=2,
#     #     ),
#     #     DataSummary(
#     #         key="First Conversion Start Date",
#     #         value=str(datetime.datetime.now()),
#     #         order=7,
#     #
#     #     ),
#     # ]
#     entity = Entity.objects(type="transaction").first()
#     # entity.data_summary = data_summary
#     # entity.save()
#     # entity.data_summary
#     entity_serializer = EntitySerializer(entity)
#     # print(entity_serializer)
#     return response.Response(entity_serializer.data, status=200)
#     # return response.Response({"source_type": entity.source_type}, status=200)

from rest_framework import viewsets
from rest_framework.response import Response

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

    def get_all_entity(self, request):
        query_set = Entity.objects()
        serializer = EntitySerializer(query_set, many=True, required=True)
        return Response(serializer.data)

    def select_entity(self, request, entity_type=None):
        query_set = Entity.objects(type=entity_type).first()
        if query_set is None:
            return Response()
        serializer = EntitySerializer(query_set)
        return Response(serializer.data)
