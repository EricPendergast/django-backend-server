from rest_framework_mongoengine.serializers import DocumentSerializer

from eledata.models.analysis_questions import *

class AnalysisParameterSerializer(DocumentSerializer):
    class Meta:
        model = AnalysisParameter2
        depth = 2
        fields = ['content', 'label', 'floating_label', 'choices', 'enabled', 'choice_index', 'choice_input', 'enabled']
        
class AnalysisQuestionSerializerSummary(DocumentSerializer):
    class Meta:
        model = AnalysisQuestion2
        depth = 2
        fields = ['content', 'label', 'type', 'orientation', 'parameter_labels']
    
        
class AnalysisQuestionSerializer(DocumentSerializer):
    class Meta:
        model = AnalysisQuestion2
        depth = 2
        fields = ['content', 'label', 'type', 'orientation', 'enabled', 'selected', 'parameter_labels']
        
