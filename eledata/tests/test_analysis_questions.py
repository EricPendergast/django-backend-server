from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from eledata.models.entity import Entity
from eledata.models.users import User, Group
from eledata.models.analysis_questions import GroupAnalysisSettings

from eledata.util import from_json, to_json, debug_deep_compare
from eledata.models.analysis_questions import *
from eledata.serializers.analysis_questions import *


class AnalysisQuestionTestCase(TestCase):
    
    analysis_params_init = [
            {u'content': u'What is your expected variation of CLV?', 'label':'clv', 'floating_label':'Variation', u'choices': [{u'content': u'Default. Handled by Eledata', u'default_value': None}]},
            {'content':"What is your company's average monthly income?", 'label':'income', 'floating_label':'Income', 'choices': [{'content':'Default. Handled by Eledata'}, {'content':'Enter your value:', "default_value":"50,000"}]},]
    
    analysis_params_init_objs = [AnalysisParameter(**item) for item in analysis_params_init]
    
    analysis_questions_init = [
            {"content": "Which customers will likely be leaving in the coming time?", "label":"leaving", "type":"predictive", "orientation":"customer", "parameter_labels":[]}, 
            {"content": "Which products will be the most popular in the future?", "label":"popularity", "type":"predictive", "orientation":"product", "parameter_labels":[analysis_params_init[0]['label']]},
            {"content": "What has caused the most customers to leave?", "label":"cause of leave", "type":"descriptive", "orientation":"customer", "parameter_labels": [a['label'] for a in analysis_params_init]},]
        
    analysis_questions_init_objs = [AnalysisQuestion(**item) for item in analysis_questions_init]
    
    
    def doCleanups(self):
        User.drop_collection()
        Group.drop_collection()
        
    
    def test_get_all_questions(self):
        c, _ = self._create_default_user()
        response = c.get('/analysis_questions/get_all_existing_analysis_questions/')
        ret_data = from_json(response.content)

        self.assertEqual(response.status_code, 200)

        for item in ret_data:
            self.assertIn(item, self.analysis_questions_init)

        for item in self.analysis_questions_init:
            self.assertIn(item, ret_data)



    def test_get_user_analysis_settings(self):
        c,_ = self._create_default_user()

        response = c.get('/analysis_questions/get_all_analysis_settings/')
        self.assertEqual(response.status_code, 200)
        data = from_json(response.content)

        self.assertTrue(_same_elements(data['analysis_params'],
                [{u'choice_index': 0, u'label': u'clv', u'choices': [{u'content': u'Default. Handled by Eledata', u'default_value': None}], u'content': u'What is your expected variation of CLV?', u'floating_label': u'Variation', u'choice_input': None}, {u'choice_index': 0, u'label': u'income', u'choices': [{u'content': u'Default. Handled by Eledata', u'default_value': None}, {u'content': u'Enter your value:', u'default_value': u'50,000'}], u'content': u"What is your company's average monthly income?", u'floating_label': u'Income', u'choice_input': None}]))

        del data['analysis_params']
        self.assertEquals(data, {
            u'analysis_questions': [
            {u'orientation': u'customer', u'selected': True, u'enabled': True, u'label': u'cause of leave', u'content': u'What has caused the most customers to leave?', u'type': u'descriptive'},
            {u'orientation': u'customer', u'selected': False, u'enabled': True, u'label': u'leaving', u'content': u'Which customers will likely be leaving in the coming time?', u'type': u'predictive'},
            {u'orientation': u'product', u'selected': False, u'enabled': False, u'label': u'popularity', u'content': u'Which products will be the most popular in the future?', u'type': u'predictive'}]})

        self.assertIn("analysis_questions", response.data)


    def test_toggle_analysis_question(self):
        c, user = self._create_default_user()

        def is_label_selected(user, label):
            for question in user.group.analysis_settings.questions:
                if question.label == label:
                    return question.selected
            return False

        response = c.post('/analysis_questions/toggle_analysis_question/', data = {"toggled":"leaving"})
        user.reload()
        self.assertTrue(is_label_selected(user, "leaving"))
        self.assertTrue(is_label_selected(user, "cause of leave"))
        self.assertFalse(is_label_selected(user, "invalid label"))


        c.post('/analysis_questions/toggle_analysis_question/', data = {"toggled":"leaving"})
        user.reload()
        self.assertFalse(is_label_selected(user, "leaving"))


        c.post('/analysis_questions/toggle_analysis_question/', data = {"toggled":"cause of leave"})
        user.reload()
        self.assertFalse(is_label_selected(user, "leaving"))
        
        
        # This analysis question is not enabled, so nothing should change, and
        # an error should be generated
        response = c.post('/analysis_questions/toggle_analysis_question/', data = {"toggled":"popularity"})
        self.assertTrue('error' in from_json(response.content))
        user.reload()
        self.assertFalse(is_label_selected(user, "popularity"))
        
        
        response = c.post('/analysis_questions/toggle_analysis_question/', data = {"something":"something else"})
        self.assertIn("error", from_json(response.content))
        

    def test_change_analysis_parameter(self):
        c, user = self._create_default_user()
        
        def assert_analysis_parameter_is(user, label, choice_index, choice_input):
            param = user.group.analysis_settings.get_parameter(label=label)
            self.assertTrue(param is not None)
            self.assertEqual(param.choice_index, choice_index)
            self.assertEqual(param.choice_input, choice_input)

        assert_analysis_parameter_is(user, "income", 0, None)

        response = c.post('/analysis_questions/change_analysis_parameter/',
                data = {"label":"income",
                "choice_index":1, "choice_input":"30000"})
        user.reload()
        assert_analysis_parameter_is(user, "income", 1, "30000")


        response = c.post('/analysis_questions/change_analysis_parameter/',
                data = {"label":"income",
                "choice_index":1})
        user.reload()
        assert_analysis_parameter_is(user, "income", 1, None)


        response = c.post('/analysis_questions/change_analysis_parameter/',
                data = {"label":"not a label",
                "choice_index":1})
        self.assertIn("error", from_json(response.content))


        response = c.post('/analysis_questions/change_analysis_parameter/',
                data = {"label":"income",
                "choice_index":-1})
        self.assertIn("error", from_json(response.content))

        response = c.post('/analysis_questions/change_analysis_parameter/',
                data = {"label":"income",
                "choice_index":2})
        self.assertIn("error", from_json(response.content))
        
    def test_same_elements(self):
        self.assertTrue(_same_elements([5,6,7,3], [3,6,7,5]))
        self.assertTrue(not _same_elements([5,6,7,4], [3,6,7,5]))
        self.assertTrue(not _same_elements([3,6,7,5], [5,6,7,3,8]))
        
    def _create_default_user(self):
        assert len(User.objects) == 0
        assert len(Group.objects) == 0

        c = Client()
        c.post("/users/create_user/", {"username":"dummy1", "password":"asdf", "group":"dummy_group"})
        
        group = Group.objects.get(name="dummy_group")
        
        statuses = {"leaving":{'enabled':True,'selected':False},
                 "popularity":{'enabled':False,'selected':False},
                 "cause of leave":{'enabled':True,'selected':True}}
        
        for label in statuses:
            q = group.analysis_settings.get_question(label)
            q.enabled = statuses[label]['enabled']
            q.selected = statuses[label]['selected']
        
        group.save()
        
        c.post("/users/login/", {"username":"dummy1", "password":"asdf"})
        
        return (c, User.objects.get(username="dummy1"))
    
    
    # TODO: Write a test that accounts for multiple groups
        
# Checks whether list1 and list2 have the same elements, regardless of order
def _same_elements(list1, list2):
    for item in list1:
        if item not in list2:
            return False
    
    for item in list2:
        if item not in list1:
            return False
    
    return True
        
        
