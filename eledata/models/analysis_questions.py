from __future__ import unicode_literals
from mongoengine import *
import datetime


'''
Contains the state of the analysis questions for a given user. This includes
the selected questions, the enabled questions, and the parameters that must be
filled out
'''
class UserAnalysisQuestions(EmbeddedDocument):
    selected_questions = ListField(ReferenceField(AnalysisQuestion))
    enabled_questions = ListField(ReferenceField(AnalysisQuestion))
    
    parameters = ListField(EmbeddedDocumentField(AnalysisParameterAnswered))
    
    

'''
There is one AnalysisQuestionAnswered for each answered question. Contains the
user's answer to the question, as well as a reference to the question itself
'''
# class AnalysisQuestion(Document):
#     # The question prototype that this model contains the answer to
#     question = ReferenceField(AnalysisQuestionPrototype)
    
    
class AnalysisParameterAnswered(EmbeddedDocument):
    prototype = ReferenceField(AnalysisParameter)
    answer = IntField()
    choice_value = StringField()
    
'''
There is one AnalysisQuestion for each question in the user settings.  i.e. all
users share the same question prototypes. This model will never contain any
user input.
'''
class AnalysisQuestion(Document):
    text = StringField()
    label = StringField()
    # whether the question predictive or descriptive
    type = StringField()
    # orientation = StringField()
    input_params = ListField(ReferenceField(AnalysisParameter))

class AnalysisParameter(Document):
    text = StringField()
    choices = EmbeddedDocumentListField(AnalysisParameterChoice)
    
class AnalysisParameterChoice(EmbeddedDocument):
    text = StringField()
    default_value = StringField()
