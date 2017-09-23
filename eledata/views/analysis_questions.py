from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import list_route

from eledata.models.entity import *

from eledata.verifiers.analysis_questions import *

import eledata.util
import eledata.handlers.analysis_questions as handler

from eledata.auth import CustomLoginRequiredMixin


class AnalysisQuestionsViewSet(CustomLoginRequiredMixin, viewsets.ViewSet):
    # Returns all the analysis questions in the group of the current user

    @list_route(methods=['get'])
    def get_all_existing_analysis_questions(self, request):
        ser = eledata.serializers.analysis_questions.AnalysisQuestionSerializerSummary(
            request.user.group.analysis_settings.questions, many=True)
        return Response(ser.data, status=200)

    @list_route(methods=['get'])
    def get_all_analysis_settings(self, request):
        resp_data = handler.get_analysis_questions_settings(
            settings=request.user.group.analysis_settings)
        return Response(resp_data, status=200)

    # TODO: make it a put request
    @list_route(methods=['post'])
    def update_analysis_settings(self, request):
        """
        request will be in the format:
        {
            "analysisQuestion": [ list of labels to be altered ]
            "analysisParams": [ list of object:
                {
                    "label":<label>,
                    "choiceIndex":<index>,
                    "choiceInput":<input>
                }
                <label>: index of the parameter that was changed, (Required)
                <choiceIndex>: index of the choice selected, (Required)
                <choiceInput>: input to that choice. (Optional)
            ]
        }
        """
        verifier = UpdateAnalysisSettingsVerifier()
        group = request.user.group

        resp_data = handler.update_analysis_settings(
            request_data=request.data,
            settings=group.analysis_settings,
            verifier=verifier
        )

        group.save()
        assert verifier.verified
        return Response(resp_data, status=200)

    @list_route(methods=['put'])
    def start_analysis(self, request):
        verifier = StartAnalysisVerifier()
        group = request.user.group

        resp_data = handler.start_analysis(
            settings=group.analysis_settings,
            verifier=verifier
        )

        group.save()
        assert verifier.verified
        return Response(resp_data, status=200)
