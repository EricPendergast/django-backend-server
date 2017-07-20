from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from eledata.models.entity import Entity

from eledata.util import from_json, to_json, debug_deep_compare
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
        self._create_default_user()

        c = Client()
        response = c.get('/analysis_questions/get_all_existing_analysis_settings/')
        self.assertEqual(response.status_code, 200)
        data = from_json(response.content)

        self.assertTrue(_same_elements(data['analysis_params'],
                [{u'choice_index': 0, u'label': u'clv', u'choices': [{u'content': u'Default. Handled by Eledata', u'default_value': None}], u'content': u'What is your expected variation of CLV?', u'floating_label': u'Variation', u'choice_input': None}, {u'choice_index': 0, u'label': u'income', u'choices': [{u'content': u'Default. Handled by Eledata', u'default_value': None}, {u'content': u'Enter your value:', u'default_value': u'50,000'}], u'content': u"What is your company's average monthly income?", u'floating_label': u'Income', u'choice_input': None}]))

        del data['analysis_params']
        self.assertEquals(data, {
            u'analysis_questions': [
            {u'orientation': u'customer', u'selected': True, u'enabled': True, u'label': u'cause of leave', u'content': u'What has caused the most customers to leave?', u'type': u'descriptive'},
            {u'orientation': u'customer', u'selected': False, u'enabled': True, u'label': u'leaving', u'content': u'Which customers will likely be leaving in the coming time?', u'type': u'predictive'},
            {u'orientation': u'product', u'selected': False, u'enabled': False, u'label': u'poplularity', u'content': u'Which products will be the most popular in the future?', u'type': u'predictive'}]}
)

        self.assertIn("analysis_questions", response.data)
        
    
    def test_toggle_analysis_question(self):
        user = self._create_default_user()
        c = Client()
        
        def is_label_selected(user, label):
            for question in user.selected_questions:
                if question.label == label:
                    return True
            return False
            
        
        c.post('/analysis_questions/toggle_analysis_question/', data = {"toggled":"leaving"})
        user.reload()
        self.assertTrue(is_label_selected(user, "leaving"))
        self.assertTrue(is_label_selected(user, "cause of leave"))
        
        
        c.post('/analysis_questions/toggle_analysis_question/', data = {"toggled":"leaving"})
        user.reload()
        self.assertFalse(is_label_selected(user, "leaving"))
        self.assertTrue(is_label_selected(user, "cause of leave"))
        
        
        c.post('/analysis_questions/toggle_analysis_question/', data = {"toggled":"cause of leave"})
        user.reload()
        self.assertFalse(is_label_selected(user, "leaving"))
        self.assertFalse(is_label_selected(user, "cause of leave"))
        
    
    
    def _create_default_user(self):
        # getting all the questions, but in a way that the order will always be
        # the same
        all_qs = [AnalysisQuestion.objects.get(label=item['label']) for item in self.analysis_questions_init]
        UserAnalysisQuestions.objects.delete()
        user_aqs = UserAnalysisQuestions(enabled_questions=[all_qs[0],all_qs[2]], selected_questions = [all_qs[2],])
        user_aqs.save()
        return user_aqs
    
def _same_elements(list1, list2):
    for item in list1:
        if item not in list2:
            return False
    
    for item in list2:
        if item not in list1:
            return False
    
    return True
        
