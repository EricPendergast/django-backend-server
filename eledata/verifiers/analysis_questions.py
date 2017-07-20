from eledata.verifiers.verifier import Verifier
from eledata.util import InvalidInputError

class ToggleAnalysisQuestionVerifier(Verifier):
    def stage0(self, request_data):
        if 'toggled' not in request_data:
            raise InvalidInputError('"toggled" field missing from request')
    
    def stage1(self, analysis_question):
        if analysis_question is None:
            raise InvalidInputError("Analysis question either is not enabled or doesn't exist")
        
    stages = [stage0, stage1]
