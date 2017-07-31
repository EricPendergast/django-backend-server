from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from django.utils.six import BytesIO

from django.template.response import TemplateResponse
from django.http import HttpResponse

from eledata.serializers.analysis_questions import *
from eledata.models.entity import *
from eledata.handlers.create_entity import *
from eledata.verifiers.analysis_questions import *

import csv
import eledata.util
from eledata.util import InvalidInputError, string_caster
import os.path
import uuid
import eledata.handlers.analysis_questions as handler

from eledata.auth import CustomLoginRequiredMixin

class AnalysisQuestionsViewSet(CustomLoginRequiredMixin, viewsets.ViewSet):
    raise_exception=True
    
    # Returns all the analysis questions in the group of the current user
    @list_route(methods=['get'])
    def get_all_existing_analysis_questions(self, request):
        ser = AnalysisQuestionSerializerSummary(request.user.group.analysis_settings.questions, many=True)
        
        return Response(ser.data, status=200)
        
    
    @list_route(methods=['get'])
    def get_all_analysis_settings(self, request):
        
        resp_data = handler.get_analysis_questions_settings(
                settings=request.user.group.analysis_settings)
        
        return Response(resp_data, status=200)
    
    
    @list_route(methods=['post'])
    def toggle_analysis_question(self, request):
        '''
        request will be in the format:
        {
            "toggled":<label>
        }
        
        where <label> is the label of the analysis question that was toggled.
        '''
        
        try:
            verifier = ToggleAnalysisQuestionVerifier()
            group = request.user.group
            
            resp_data = handler.toggle_analysis_question(
                    request_data=request.data,
                    settings=group.analysis_settings,
                    verifier=verifier)
            
            group.save()
            
            assert verifier.verified
            return Response(resp_data, status=200)
        except InvalidInputError as e:
            return Response({"error":str(e)}, status=400)
    
    
    @list_route(methods=['post'])
    def change_analysis_parameter(self, request):
        '''
        The request should be in the format:
        {
            "label":<param_label>,
            "choice_index":<index>,
            "choice_input":<input>
        }
        Where <param_label> is the label of the parameter that was changed,
        <index> is the index of the choice selected, and <input> is the input
        to that choice. <param_label> and <index> are required, <input> is
        optional
        '''
        
        try:
            verifier = ChangeAnalysisParameterVerifier()
            group = request.user.group
            
            resp_data = handler.change_analysis_parameter(
                    request_data=request.data,
                    settings=group.analysis_settings,
                    verifier=verifier)
            
            group.save()
            
            assert verifier.verified
            return Response(resp_data, status=200)
        except InvalidInputError as e:
            return Response({"error":str(e)}, status=400)
            
