from rest_framework_mongoengine.serializers import DocumentSerializer

from eledata.models.analysis_questions import AnalysisParameter, AnalysisQuestion


class AnalysisParameterSerializer(DocumentSerializer):
    class Meta:
        model = AnalysisParameter
        depth = 2
        fields = ['content', 'label', 'floating_label', 'choices', 'enabled', 'choice_index', 'choice_input', 'enabled']


class AnalysisQuestionSerializerSummary(DocumentSerializer):
    class Meta:
        model = AnalysisQuestion
        depth = 2
        fields = ['content', 'label', 'icon', 'type', 'orientation', 'parameter_labels', 'required_entities']


class AnalysisQuestionSerializer(DocumentSerializer):
    class Meta:
        model = AnalysisQuestion
        depth = 2
        fields = ['content', 'label', 'icon', 'type', 'orientation', 'enabled', 'selected', 'parameter_labels',
                  'required_entities']
