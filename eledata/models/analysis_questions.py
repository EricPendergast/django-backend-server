from __future__ import unicode_literals
from mongoengine import *

    
'''
An analysis parameter is a question that the user answers that helps eledata
answer the analysis question. Each analysis parameter is a multiple choice
question, where each choice may have additional typed input.
'''
class AnalysisParameter(EmbeddedDocument):
    class AnalysisParameterChoice(EmbeddedDocument):
        content = StringField()
        default_value = StringField()
        
    content = StringField()
    label = StringField()
    floating_label = StringField()
    choices = EmbeddedDocumentListField(AnalysisParameterChoice)
    enabled = BooleanField()
    
    choice_index = IntField(default=0)
    # The value the user inputted to the choice. This value may be null, since
    # not all choices take inputs.
    choice_input = StringField()
    enabled = BooleanField()
    
    def __str__(self):
        return self.label
    
    

'''
An analysis question is a question the user selects for Eledata to answer.
Analysis questions can share parameters, so to avoid repetition, each analysis
question contains a list of the only the labels of its parameters.
'''
class AnalysisQuestion(EmbeddedDocument):
    # Content of the question. e.g. "Which customers will be likely leaving in
    # the coming time?"
    content = StringField()
    # Short descriptor of the question.  e.g. "leaving"
    label = StringField()
    ## Categorical information
    type = StringField()
    orientation = StringField()
    ##
    enabled = BooleanField(default=False)
    selected = BooleanField()
    # The list of question parameters the user would need to fill out if they
    # select this question
    parameter_labels = ListField(StringField())

    def __str__(self):
        return self.label
    
    
'''
Contains the analysis settings for a group. This includes the list of questions
and the list of parameters to those questions, answers.
'''
class GroupAnalysisSettings(EmbeddedDocument):
    # questions = DynamicEmbeddedDocument(AnalysisQuestion)
    questions = EmbeddedDocumentListField(AnalysisQuestion)
    #TODO: This should probably be changed to a dictionary
    parameters = EmbeddedDocumentListField(AnalysisParameter)
    # parameters = DynamicEmbeddedDocument(AnalysisParameter)
    
    '''
    Each question has a list of parameters it needs, so this method figures out
    which parameters should be enabled in 'parameters' based on all the
    questions in 'questions' with selected==True
    
    Does not call self.save()
    '''
    def update_parameters(self):
        # Will contain the labels of all the parameters that should be enabled
        enabled_parameter_labels = set()
        
        for question in self.questions:
            if question.selected:
                enabled_parameter_labels.update(question.parameter_labels)
        
        for parameter in self.parameters:
            parameter.enabled = parameter.label in enabled_parameter_labels
        
        
    def get_question(self, label):
        # return getattr(self.questions, label, None)
        for question in self.questions:
            if question.label == label:
                return question
        return None
    
    
    def get_parameter(self, label):
        # return getattr(self.parameters, label, None)
        for param in self.parameters:
            if param.label == label:
                return param
        return None
