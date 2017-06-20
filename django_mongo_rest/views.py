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
from rest_framework import mixins
from rest_framework_mongoengine import viewsets

from django.template.response import TemplateResponse

from serializers import *
from models import *


def index_view(request):
    context = {}
    return TemplateResponse(request, 'index.html', context)


class EntityViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    """
    Read-only User endpoint
    """
    serializer_class = EntitySerializer

    def get_queryset(self):
        return Entity.objects.all()
