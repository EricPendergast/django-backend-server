# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django_mongo_rest.models import Entity
from rest_framework import response
from rest_framework.decorators import api_view
from serializers import EntitySerializer

# Create your views here.


@api_view(['GET'])
def index(request):
    entity = Entity.objects(type__contains="transaction").first()
    return response.Response(EntitySerializer(entity).data, status=200)
