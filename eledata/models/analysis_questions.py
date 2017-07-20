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
# class UserAnalysisQuestions(EmbeddedDocument):
class UserAnalysisQuestions(Document):
    selected_questions = ListField(ReferenceField(AnalysisQuestion))
    enabled_questions = ListField(ReferenceField(AnalysisQuestion))
    parameters = EmbeddedDocumentListField(AnalysisParameterAnswered)
    
    test_field = StringField(default="default")
    
    def update_parameters(self):
        #TODO: make variable names better
        parameter_set = set()
        self_parameter_set = set(item.parameter for item in self.parameters)
        
        for question in self.selected_questions:
            parameter_set.update(question.parameters)
            
        for parameter in parameter_set:
            if parameter not in self_parameter_set:
                bool_val = parameter in parameter_set
                
                # param1 = AnalysisParameterAnswered(parameter=parameter)
                # param1.enabled = bool_val
                # param1.parameter = parameter
                # self.parameters += [AnalysisParameterAnswered(parameter=parameter),]
                # self.parameters[-1].enabled = bool_val
                
                param2 = AnalysisParameterAnswered(parameter=parameter, enabled=bool_val)
                
                # assert dir(param2) == dir(param1)
                # self.save()
                
                # for field in dir(param1):
                #     if hasattr(param1, field) and hasattr(param2, field):
                #         if getattr(param1, field) != getattr(param2, field):
                #             print "Two objects differ by field: %s" % field
                #             print "obj1: %s,    obj2: %s" % (getattr(param1, field), getattr(param2, field))
                #     elif hasattr(param1, field) != hasattr(param2, field):
                #         print "Two objects differ by field: %s" % field
                # if param1 == param2:
                    # print "They are equal"
                # else:
                    # print "They are not equal"
                
                self.parameters += [param2,]
                # self.save()
                # self.parameters[-1].enabled=bool_val
                # TODO: remember to change this back
                # self.parameters[-1]._changed_fields = []
                # util.debug_deep_compare(param1, param2)
                # print "Equal?: " + str(
                
                # self.parameters += [AnalysisParameterAnswered(parameter=parameter, enabled=bool_val),]
                
        # for parameter in self.parameters:
            # parameter.enabled = (parameter.parameter in parameter_set)
            # parameter.enabled = True
        
        # print len(self.parameters)
        # self.parameters[0].enabled = True
        # self.parameters[1].enabled = True
        # print self.parameters
        
    # TODO: This method is broken
    # parameters should hold all possible parameters. This method should only
    # set their 'enabled' field to true or false
    # def update_parameters(self):
    #     # Maps each analysis parameter to its corresponding answered version in
    #     # 'self.parameters', mapping to 'None' if no answered version exists
    #     current_parameters = dict([(answered.parameter, answered) for answered in self.parameters])
    #
    #     new_parameters = {}
    #     for question in self.selected_questions:
    #         for parameter in question.parameters:
    #
    #             if parameter in current_parameters:
    #                 new_parameters[parameter] = current_parameters[parameter]
    #             else:
    #                 new_parameters[parameter] = AnalysisParameterAnswered(parameter=parameter)
    #
    #     self.parameters = list(new_parameters.values())
        
