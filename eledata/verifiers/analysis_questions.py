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

class ChangeAnalysisParameterVerifier(Verifier):
    def stage0(self, request_data):
        Verifier.ver_dict(request_data,
                required={"label","choice_index"})
    
    def stage1(self, param, label):
        if param is None:
            raise InvalidInputError("Parameter with label %s doesn't exist" % label)
    
    def stage2(self, parameter):
        if int(parameter.choice_index) not in range(len(parameter.choices)):
            raise InvalidInputError("'choice_index', value %s, is out of range %s" % (parameter.choice_index, range(len(parameter.choices))))
    
    stages = [stage0, stage1, stage2]
