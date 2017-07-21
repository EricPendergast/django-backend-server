from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route

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


class AnalysisQuestionsViewSet(viewsets.ViewSet):
    
    @list_route(methods=['get'])
    def get_all_existing_analysis_questions(self, request):
        ser = AnalysisQuestionSerializer(AnalysisQuestion.objects.all(), many=True)
        
        return Response(ser.data, status=200)
    
        
    @list_route(methods=['get'])
    def get_all_existing_analysis_settings(self, request):
        # This is a dummy user. In the future there will be real users.
        user = UserAnalysisQuestions.objects.get()
        resp_data = handler.get_analysis_questions_settings(user)
        
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
            user = UserAnalysisQuestions.objects.get()
            
            resp_data = handler.analysis_question_toggled(request.data, user, verifier)
            
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
            user = UserAnalysisQuestions.objects.get()
            
            resp_data = handler.change_analysis_parameter(request.data, user, verifier)
            
            assert verifier.verified
            return Response(resp_data, status=200)
        except InvalidInputError as e:
            return Response({"error":str(e)}, status=400)
            
