from eledata.models.analysis_questions import GroupAnalysisSettings
from eledata.serializers.analysis_questions import AnalysisQuestionSerializer, AnalysisParameterSerializer
import ast
from event import create_new_initializing_job, start_all_initializing_job
from project.settings import CONSTANTS
from eledata.models.event import Job

def get_analysis_questions_settings(settings):
    assert type(settings) is GroupAnalysisSettings
    ret_data = {"analysis_questions": [], "analysis_params": []}

    # Load the analysis questions into ret_data
    for question in settings.questions:
        entry = AnalysisQuestionSerializer(question).data

        # disabled required_entities hiding
        # del entry['required_entities']

        ret_data["analysis_questions"] += [entry, ]

    # Make sure that the parameters are in sync with the analysis questions.
    settings.update_parameters()

    for param in settings.parameters:
        entry = AnalysisParameterSerializer(param).data
        del entry['enabled']

        ret_data["analysis_params"] += [entry, ]

    def get_sort_key(analysis_question):
        return str(analysis_question["type"]) + " " + str(analysis_question["orientation"])

    ret_data["analysis_questions"].sort(key=get_sort_key)

    return ret_data


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
        verifier.verify(2, alter_analysis_questions)

        for _aq in alter_analysis_questions:
            _aq.selected = not _aq.selected
        _settings.update_parameters()

    if request_analysis_questions:
        update_analysis_question(
            _request_analysis_questions=request_analysis_questions,
            _settings=settings
        )
    else:
        verifier.verify(stage=1, alter_analysis_questions=[], skipped=True)
        verifier.verify(stage=2, alter_analysis_questions=[], skipped=True)

    def update_analysis_parameter(_request_analysis_params, _settings):
        _request_analysis_params_labels = []
        for p in _request_analysis_params:
            p = ast.literal_eval(p)
            _request_analysis_params_labels += [p[u'label'], ]

        verifier.verify(3, _request_analysis_params_labels, settings.parameters)

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
        verifier.verify(stage=3, request_analysis_params_index=[], setting_params=settings.parameters, skipped=True)

    return {"msg": "Change successful"}


def start_analysis(group, settings, verifier):
    questions = settings.questions
    verifier.verify(stage=0, questions=questions)

    selected_questions = [x for x in questions if x.selected is True]
    verifier.verify(stage=1, selected_questions=selected_questions)

    pending_analysis_engines = []
    for selected_question in selected_questions:
        pending_analysis_engines += [selected_question.analysis_engine, ]

    _selected_obj = []

    for _selected_question in selected_questions:
        filtered_param = filter(lambda param: _selected_question.label in param.required_question_labels,
                                settings.parameters)
        _selected_obj += [dict(
            job_engine=_selected_question.analysis_engine,
            job_status=CONSTANTS.JOB.STATUS.get('INITIALIZING'),
            group=group,
            # Change params to dict before fitting them into List(Dict()) Serializing
            parameter=[x.to_mongo() for x in filtered_param]
        ), ]

    create_new_initializing_job(_selected_obj)

    start_all_initializing_job(group)

    return {"msg": "Change successful"}
