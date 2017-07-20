from eledata.models.analysis_questions import *
from eledata.serializers.analysis_questions import *

from eledata.util import to_json, from_json


def get_analysis_questions_settings(user):
    assert type(user) is UserAnalysisQuestions
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
        if answered_param.enabled:
            entry = AnalysisParameterSerializer(answered_param.parameter).data
            del entry['id']
            entry['choice_input'] = answered_param.choice_input
            entry['choice_index'] = answered_param.choice_index
            
            ret_data["analysis_params"] += [entry,]
        
        
    def get_sort_key(analysis_question):
        return str(analysis_question["type"]) + " " + str(analysis_question["orientation"])
    ret_data["analysis_questions"].sort(key=get_sort_key)
    
    return ret_data



def analysis_question_toggled(request_data, user, verifier):
    verifier.verify(0, request_data)
    
    label = request_data['toggled']
    
    analysis_question = None
    
    for q in user.enabled_questions:
        if q.label == label:
            analysis_question = q
    
    verifier.verify(1, analysis_question)
    
    if analysis_question in user.selected_questions:
        user.selected_questions.remove(analysis_question)
    else: 
        # I use append because doing "+= [item,]" uses inplace modification,
        # which makes mongodb not recognize that the list was changed. This
        # could have been fixed by adding 'selected_questions' to
        # 'user._changed_fields', but this way is cleaner.
        user.selected_questions.append(analysis_question)
    
    user.update_parameters()
    user.save()
    user = UserAnalysisQuestions.objects.get(pk=user.id)
    
    return {}

