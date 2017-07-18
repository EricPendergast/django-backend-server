from eledata.models.analysis_questions import *
from eledata.serializers.analysis_questions import *

from eledata.util import to_json, from_json

def get_analysis_questions_settings(user):
    ret_data = {"analysis_questions":[], "analysis_params":[]}
    
    # Load the analysis questions into ret_data, adding user specific
    # information
    for question in AnalysisQuestion.objects.all():
        entry = AnalysisQuestionSerializer(question).data
        entry['enabled'] = question in user.enabled_questions
        entry['selected'] = question in user.selected_questions
        
        del entry['parameters']
        del entry['id']
        
        ret_data["analysis_questions"] += [entry,]
    
    user.update_parameters()
        
    for answered_param in user.parameters:
        entry = AnalysisParameterSerializer(answered_param.parameter).data
        del entry['id']
        entry['choice_input_value'] = answered_param.choice_input_value
        entry['choice_index'] = answered_param.choice_index
        
        ret_data["analysis_params"] += [entry,]
        
        
    def get_sort_key(analysis_question):
        return str(analysis_question["type"]) + " " + str(analysis_question["orientation"])
    ret_data["analysis_questions"].sort(key=get_sort_key)
    
    return ret_data
