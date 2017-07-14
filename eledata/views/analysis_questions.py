from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route

from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from django.utils.six import BytesIO

from django.template.response import TemplateResponse
from django.http import HttpResponse

from eledata.serializers import *
from eledata.models.entity import *
from eledata.input_verifier import CreateEntityVerifier, CreateEntityMappedVerifier
from eledata.handlers.create_entity import *

import csv
import eledata.util
from eledata.util import InvalidInputError, string_caster
import os.path
import uuid


class AnalysisQuestionsViewSet(viewsets.ViewSet):
    @list_route(methods=['post'])
    def create_thing(self, request):
        return Response("Hello", status=200)
        
