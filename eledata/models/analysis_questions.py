from __future__ import unicode_literals
from mongoengine import *
import datetime
import eledata.util as util

    
#TODO: add __str__ methods to all models
'''
An analysis parameter is a question that the user answers that helps eledata
answer the analysis question. Each analysis parameter is a multiple choice
question, where each choice may have additional typed input.

Some analysis questions may have the same analysis parameters, so to avoid
repetition, all parameters are stored in a pool and are referenced to by
analysis questions.
'''
class AnalysisParameter(Document):
    class AnalysisParameterChoice(EmbeddedDocument):
        content = StringField()
        default_value = StringField()
        
    content = StringField()
    label = StringField(unique=True)
    floating_label = StringField()
    choices = EmbeddedDocumentListField(AnalysisParameterChoice)
    
    def __str__(self):
        return self.label
    
'''
An analysis question is a question the user asks and eledata answers. There is
a predefined list of analysis questions (AnalysisQuestion.objects.all()), and
this list is shared across users through references. Each AnalysisQuestion
contains no user input.
'''
class AnalysisQuestion(Document):
    # Content of the question. e.g. "Which customers will be likely leaving in the coming time?"
    content = StringField()
    # Short descriptor of the question.  e.g. "leaving"
    label = StringField()
    ## Categorical information
    type = StringField()
    orientation = StringField()
    ##
    
    # The list of question parameters the user would need to fill out if they
    # select this question
    parameters = ListField(ReferenceField(AnalysisParameter))

    def __str__(self):
        return self.label
    

'''
There is one AnalysisQuestionAnswered for each answered question. Contains the
user's answer to the question (in the form of the index of the multiple choice
answer and the optional input value), as well as a reference to the question
itself
'''
class AnalysisParameterAnswered(EmbeddedDocument):
    parameter = ReferenceField(AnalysisParameter)
    choice_index = IntField(default=0)
    # The value the user inputted to the choice. This value may be null, since
    # not all choices take inputs.
    choice_input = StringField()
    # enabled = BooleanField(default=False)
    enabled = BooleanField()
    
    def __str__(self):
        return "(parameter=" + str(self.parameter) + ", enabled=" + str(self.enabled) + ")"

'''
Contains the state of the analysis questions for a given user. This includes
the selected questions, the enabled questions, and the parameters that must be
filled out
'''
# At some point this will be embedded in a user document, but for now, it is
# standalone
# class UserAnalysisQuestions(EmbeddedDocument):
class UserAnalysisQuestions(Document):
    selected_questions = ListField(ReferenceField(AnalysisQuestion))
    enabled_questions = ListField(ReferenceField(AnalysisQuestion))
    parameters = EmbeddedDocumentListField(AnalysisParameterAnswered)
    
    '''
    Each question has a list of parameters it needs, so this method figures out
    which parameters need to be added to 'parameters' based on all the selected
    questions. This method does not remove anything from 'parameters'. This has
    the effect of saving the users answers to parameters of deselected
    questions.
    
    Does not call self.save()
    '''
    def update_parameters(self):
        current_parameters = set(item.parameter for item in self.parameters)
        
        # Will contain all the parameters that need to be in 'self.parameters',
        # based off of the selected questions
        all_needed_parameters = set()
        for question in self.selected_questions:
            all_needed_parameters.update(question.parameters)
            
        for parameter in all_needed_parameters:
            if parameter not in current_parameters:
                enabled = parameter in all_needed_parameters
                
                self.parameters.append(AnalysisParameterAnswered(parameter=parameter, enabled=enabled))
        
        
