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
                          required={"label", "choice_index"})

    def stage1(self, param, label):
        if param is None:
            raise InvalidInputError("Parameter with label %s doesn't exist" % label)

    def stage2(self, parameter):
        if int(parameter.choice_index) not in range(len(parameter.choices)):
            raise InvalidInputError("'choice_index', value %s, is out of range %s" % (
                parameter.choice_index, range(len(parameter.choices))))

    stages = [stage0, stage1, stage2]


class UpdateAnalysisSettingsVerifier(Verifier):
    def stage0(self, request_data):
        request_analysis_questions = request_data.getlist('analysisQuestion', False)
        request_analysis_params = request_data.getlist('analysisParams', False)

        if not request_analysis_questions and not request_analysis_params:
            raise InvalidInputError("No request are submitted")

    def stage1(self, alter_analysis_questions, skipped=False):
        if skipped:
            return

        if not alter_analysis_questions:
            raise InvalidInputError("No analysis questions are updated")
        for _q in alter_analysis_questions:
            if _q.enabled is False:
                raise InvalidInputError("Disabled questions are toggling")

    def stage2(self, request_analysis_params_index, setting_params, skipped=False):
        if skipped:
            return
        for param in setting_params:
            if param.label not in request_analysis_params_index and param.enabled is True:
                raise InvalidInputError("Missing enabled analysis parameter setting")

            if param.label in request_analysis_params_index and param.enabled is False:
                raise InvalidInputError("Received prohibited analysis parameter setting")

    stages = [stage0, stage1, stage2]
