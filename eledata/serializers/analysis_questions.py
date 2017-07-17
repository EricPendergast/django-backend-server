from rest_framework_mongoengine.serializers import DocumentSerializer

from eledata.models.analysis_questions import *

class AnalysisParameterSerializer(DocumentSerializer):
    class Meta:
        model = AnalysisParameter
        depth = 2
        fields = '__all__'
        
        
class AnalysisQuestionSerializer(DocumentSerializer):
    class Meta:
        model = AnalysisQuestion
        depth = 2
        fields = '__all__'
    
    
class UserAnalysisQuestionsSerializer(DocumentSerializer):
    class Meta:
        model = UserAnalysisQuestions
        depth = 2
        fields = '__all__'
    
