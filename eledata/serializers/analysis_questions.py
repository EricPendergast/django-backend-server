from rest_framework_mongoengine.serializers import DocumentSerializer

from eledata.models.analysis_questions import AnalysisParameter, AnalysisQuestion


class AnalysisParameterSerializer(DocumentSerializer):
    class Meta:
        model = AnalysisParameter
        depth = 2
        fields = ['content', 'label', 'required_question_labels', 'floating_label', 'choices', 'choice_index',
                  'choice_input', 'enabled']


class AnalysisQuestionSerializerSummary(DocumentSerializer):
    class Meta:
        model = AnalysisQuestion
        depth = 2
        fields = ['content', 'label', 'type', 'orientation', 'required_entities']


class AnalysisQuestionSerializer(DocumentSerializer):
    class Meta:
        model = AnalysisQuestion
        depth = 2
        fields = ['content', 'label', 'type', 'orientation', 'enabled', 'selected',
                  'required_entities']
