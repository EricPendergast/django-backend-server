from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from eledata.models.entity import Entity

from eledata.util import from_json, to_json
from eledata.models.analysis_questions import *
from eledata.serializers.analysis_questions import *


class AnalysisQuestionTestCase(TestCase):
    
    analysis_params_init = [
            {u'content': u'What is your expected variation of CLV?', 'label':'clv', 'floating_label':'Variation', u'id': u'596c858d9a4c0e5f19c78f3e', u'choices': [{u'content': u'Default. Handled by Eledata', u'default_value': None}]},
            {'content':"What is your company's average monthly income?", 'label':'income', 'floating_label':'Income', 'id':'596c858d9a4c0e5f19c78f3f', 'choices': [{'content':'Default. Handled by Eledata'}, {'content':'Enter your value:', "default_value":"50,000"}]},]
    
    analysis_params_init = [AnalysisParameter(**item).save() for item in analysis_params_init]
    
    analysis_questions_init = [
            {"content": "Which customers will likely be leaving in the coming time?", "label":"leaving", "type":"predictive", "orientation":"customer", "parameters":[]}, 
            {"content": "Which products will be the most popular in the future?", "label":"poplularity", "type":"predictive", "orientation":"product", "parameters":[analysis_params_init[0]]},
            {"content": "What has caused the most customers to leave?", "label":"cause of leave", "type":"descriptive", "orientation":"customer", "parameters": analysis_params_init},]
        
    analysis_questions_init = [AnalysisQuestion(**item).save() for item in analysis_questions_init]
    
    analysis_questions_init = [AnalysisQuestionSerializer(item).data for item in analysis_questions_init]
    analysis_params_init = [AnalysisParameterSerializer(item).data for item in analysis_params_init]
    
    
    def test_get_all_questions(self):
        c = Client()
        response = c.get('/analysis_questions/get_all_existing_analysis_questions/')
        ret_data = from_json(response.content)
        
        self.assertEqual(response.status_code, 200)
        
        for item in ret_data:
            self.assertTrue(item in self.analysis_questions_init)
        
        for item in self.analysis_questions_init:
            self.assertTrue(item in ret_data)
            
    
    
    def test_get_user_analysis_settings(self):
        all_qs = AnalysisQuestion.objects.all()
        user_aqs = UserAnalysisQuestions(enabled_questions=[all_qs[0],all_qs[2]], selected_questions = [all_qs[2],])
        user_aqs.save()
        
        c = Client()
        response = c.get('/analysis_questions/get_analysis_questions_settings/')
        self.assertEqual(response.status_code, 200)
        data = response.content
        
        #TODO: Finish writing this test
        # self.assertEquals(data, {"analysis_params":[{"content":"What is your company's average monthly income?","label":None,"floating_label":None,"choices":[{"content":"Default. Handled by Eledata","default_value":None},{"content":"Enter your value:","default_value":"50,000"}],"value":None,"choice_index":0},{"content":"What is your expected variation of CLV?","label":None,"floating_label":None,"choices":[{"content":"Default. Handled by Eledata","default_value":None}],"value":None,"choice_index":0}],"analysis_questions":[{"content":"What has caused the most customers to leave?","label":"cause of leave","type":"descriptive","orientation":"customer","enabled":True,"selected":True},{"content":"Which customers will likely be leaving in the coming time?","label":"leaving","type":"predictive","orientation":"customer","enabled":True,"selected":False},{"content":"Which products will be the most popular in the future?","label":"poplularity","type":"predictive","orientation":"product","enabled":False,"selected":False}]})
        print data
        
        self.assertIn("analysis_questions", response.data)
