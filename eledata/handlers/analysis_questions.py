from eledata.models.analysis_questions import GroupAnalysisSettings
from eledata.serializers.analysis_questions import AnalysisQuestionSerializer, AnalysisParameterSerializer



def get_analysis_questions_settings(settings):
    assert type(settings) is GroupAnalysisSettings
    ret_data = {"analysis_questions":[], "analysis_params":[]}
    
    # Load the analysis questions into ret_data
    for question in settings.questions:
        entry = AnalysisQuestionSerializer(question).data
        
        del entry['parameter_labels']
        
        ret_data["analysis_questions"] += [entry,]
    
    # Make sure that the parameters are in sync with the analysis questions.
    settings.update_parameters()
        
    # Load the parameters into ret_data
    for param in settings.parameters:
        if param.enabled:
            entry = AnalysisParameterSerializer(param).data
            del entry['enabled']
            
            ret_data["analysis_params"] += [entry,]
        
        
    def get_sort_key(analysis_question):
        return str(analysis_question["type"]) + " " + str(analysis_question["orientation"])
    ret_data["analysis_questions"].sort(key=get_sort_key)
    
    return ret_data



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
    
    return {"msg":"Toggle successful"}



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
    
    return {"msg":"Change successful"}
    
