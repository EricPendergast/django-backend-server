from eledata.models.analysis_questions import GroupAnalysisSettings
from eledata.serializers.analysis_questions import AnalysisQuestionSerializer, AnalysisParameterSerializer
import ast


def get_analysis_questions_settings(settings):
    assert type(settings) is GroupAnalysisSettings
    ret_data = {"analysis_questions": [], "analysis_params": []}

    # Load the analysis questions into ret_data
    for question in settings.questions:
        entry = AnalysisQuestionSerializer(question).data

        del entry['required_entities']

        ret_data["analysis_questions"] += [entry, ]

    # TODO: (issue #1) Maybe we do not need this function, just returning all params for every user fetch
    # Make sure that the parameters are in sync with the analysis questions.
    settings.update_parameters()

    # Load the parameters into ret_data
    # TODO: (issue #1) Maybe we do not need this function, just returning all params for every user fetch
    # for param in settings.parameters:
    #     if param.enabled:
    #         entry = AnalysisParameterSerializer(param).data
    #         del entry['enabled']
    #
    #         ret_data["analysis_params"] += [entry, ]
    # ----------------------------------------------------------------------------------------------------
    # ----> Return every parameter regardless of the enabled status instead
    for param in settings.parameters:
        entry = AnalysisParameterSerializer(param).data
        del entry['enabled']

        ret_data["analysis_params"] += [entry, ]

    def get_sort_key(analysis_question):
        return str(analysis_question["type"]) + " " + str(analysis_question["orientation"])

    ret_data["analysis_questions"].sort(key=get_sort_key)

    return ret_data


# TODO: (issue #1) Maybe we do not need this function, just returning all params for every user fetch
def toggle_analysis_question(request_data, settings, verifier):
    verifier.verify(0, request_data)

    label = request_data['toggled']
    # The analysis question that the user is trying to toggle
    analysis_question = None

    for q in settings.questions:
        if q.enabled and q.label == label:
            analysis_question = q
            break

    verifier.verify(1, analysis_question)

    analysis_question.selected = not analysis_question.selected

    settings.update_parameters()

    return {"msg": "Toggle successful"}


# TODO: (issue #1) Maybe we do not need this function, just returning all params for every user fetch
def change_analysis_parameter(request_data, settings, verifier):
    verifier.verify(0, request_data)
    param_to_change = settings.get_parameter(request_data["label"])
    verifier.verify(1, param_to_change, request_data["label"])
    param_to_change.choice_index = request_data["choice_index"]
    verifier.verify(2, param_to_change)

    if "choice_input" in request_data:
        param_to_change.choice_input = request_data["choice_input"]
    else:
        param_to_change.choice_input = None

    return {"msg": "Change successful"}


def update_analysis_settings(request_data, settings, verifier):
    # First Verifying for existence of both key, and hence initializing
    verifier.verify(0, request_data)
    request_analysis_questions = request_data.getlist('analysisQuestion', False)
    request_analysis_params = request_data.getlist('analysisParams', False)

    def update_analysis_question(_request_analysis_questions, _settings):

        alter_analysis_questions = []
        for _q in _settings.questions:
            if _q.label in _request_analysis_questions:
                alter_analysis_questions += [_q, ]

        verifier.verify(1, alter_analysis_questions)

        for _aq in alter_analysis_questions:
            _aq.selected = not _aq.selected
        _settings.update_parameters()

    if request_analysis_questions:
        update_analysis_question(
            _request_analysis_questions=request_analysis_questions,
            _settings=settings
        )
    else:
        verifier.verify(
            stage=1,
            alter_analysis_questions=[],
            skipped=True
        )

    def update_analysis_parameter(_request_analysis_params, _settings):
        _request_analysis_params_labels = []
        for p in _request_analysis_params:
            p = ast.literal_eval(p)
            _request_analysis_params_labels += [p[u'label'], ]

        verifier.verify(2, _request_analysis_params_labels, settings.parameters)

        for p in _request_analysis_params:

            p = ast.literal_eval(p)
            _settings.get_parameter(p[u'label']).choice_index = p[u'choiceIndex']

            if 'choiceInput' in p:
                _settings.get_parameter(p[u'label']).choice_input = p[u'choiceInput']

    if request_analysis_params:
        update_analysis_parameter(
            _request_analysis_params=request_analysis_params,
            _settings=settings
        )
    else:
        verifier.verify(
            stage=2,
            request_analysis_params_index=[],
            setting_params=settings.parameters,
        )

    return {"msg": "Change successful"}
