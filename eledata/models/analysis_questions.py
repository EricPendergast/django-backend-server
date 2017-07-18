from __future__ import unicode_literals
from mongoengine import *
import datetime

    
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
    label = StringField()
    floating_label = StringField()
    choices = EmbeddedDocumentListField(AnalysisParameterChoice)
    
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
    choice_input_value = StringField()
    


'''
Contains the state of the analysis questions for a given user. This includes
the selected questions, the enabled questions, and the parameters that must be
filled out
'''
# class UserAnalysisQuestions(EmbeddedDocument):
class UserAnalysisQuestions(Document):
    selected_questions = ListField(ReferenceField(AnalysisQuestion))
    enabled_questions = ListField(ReferenceField(AnalysisQuestion))
    parameters = ListField(EmbeddedDocumentField(AnalysisParameterAnswered))
    
    def update_parameters(self):
        # Maps each analysis parameter to its corresponding answered version in
        # 'self.parameters', mapping to 'None' if no answered version exists
        current_parameters = dict([(answered.parameter, answered) for answered in self.parameters])
        
        new_parameters = {}
        for question in self.selected_questions:
            for parameter in question.parameters:
                
                if parameter in current_parameters:
                    new_parameters[parameter] = current_parameters[parameter]
                else:
                    # new_param = AnalysisParameterAnswered()
                    # new_param.parameter = parameter
                    # new_parameters[parameter] = new_param
                    new_parameters[parameter] = AnalysisParameterAnswered(parameter=parameter)
                    
        self.parameters = list(new_parameters.values())
        
