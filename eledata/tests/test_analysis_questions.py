from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from eledata.models.users import User, Group

from eledata.util import from_json
from eledata.models.analysis_questions import AnalysisQuestion, AnalysisParameter

TestCase.maxDiff = None


class AnalysisQuestionTestCase(TestCase):
    admin = None
    admin_client = None

    analysis_params_init = [
        {'content': 'What is your expected variation of CLV?', 'label': 'clv', 'required_question_labels': ['leaving'],
         'floating_label': 'Variation',
         'choices': [{u'content': u'Default. Handled by Eledata', u'default_value': None}]},
        {'content': "What is your company's average monthly income?", 'label': 'income',
         'required_question_labels': ['repeat', 'recommendedProduct', 'churn', 'growth', 'revenue'],
         'floating_label': 'Income', 'choices': [{'content': 'Default. Handled by Eledata'},
                                                 {'content': 'Enter your value:', "default_value": "50,000"}]}, ]

    analysis_params_init_objs = [AnalysisParameter(**item) for item in analysis_params_init]

    analysis_questions_init = [
        {"content": "Which customers will likely be leaving in the coming time?", "label": "leaving",
         "icon": "maps/directionsRun", "type": "predictive", "orientation": "customer",
         "required_entities": ["transaction", "customer"]},
        {"content": "Which products will be the most popular in the future?", "label": "popularity",
         "icon": "action/trendingUp", "type": "predictive", "orientation": "product",
         "required_entities": ["transaction"]},
        {"content": "What has caused the most customers to leave?", "label": "cause of leave",
         "icon": "maps/directionsRun", "type": "descriptive", "orientation": "hiddenInsight",
         "required_entities": ["transaction", "customer"]}, ]

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
        c, _ = self._create_default_user()

        response = c.get('/analysis_questions/get_all_analysis_settings/')
        self.assertEqual(response.status_code, 200)
        data = from_json(response.content)

        self.assertTrue(
            _same_elements(
                data['analysis_params'],
                [{u'choice_index': 0, u'choice_input': None, u'label': u'clv',
                  u'choices': [{u'content': u'Default. Handled by Eledata',
                                u'default_value': None}],
                  u'content': u'What is your expected variation of CLV?',
                  u'floating_label': u'Variation',
                  u'required_question_labels': [u'leaving']},
                 {u'choice_index': 0, u'choice_input': None, u'label': u'income',
                  u'choices': [{u'content': u'Default. Handled by Eledata',
                                u'default_value': None},
                               {u'content': u'Enter your value:',
                                u'default_value': u'50,000'}],
                  u'content': u"What is your company's average monthly income?",
                  u'floating_label': u'Income',
                  u'required_question_labels': [u'repeat', u'recommendedProduct',
                                                u'churn', u'growth', u'revenue']},
                 {u'choice_index': 0, u'choice_input': None,
                  u'label': u'prediction_window', u'choices': [
                     {u'content': u'Default. Handled by EleData',
                      u'default_value': None}, {
                         u'content': u'My expected prediction window (in month) would be: ',
                         u'default_value': u'3'}],
                  u'content': u'What is your expected prediction window among your predictive questions ?',
                  u'floating_label': u'Prediction Window',
                  u'required_question_labels': [u'repeat', u'recommendedProduct',
                                                u'churn', u'growth', u'revenue']}]
            )
        )

        del data['analysis_params']
        self.assertEquals(data, {
            u'analysis_questions': [
                {u'orientation': u'hiddenInsight', u'selected': True, u'enabled': True, u'label': u'cause of leave',
                 u'icon': u'maps/directionsRun', u'content': u'What has caused the most customers to leave?',
                 u'type': u'descriptive'},
                {u'orientation': u'customer', u'selected': False, u'enabled': True, u'label': u'leaving',
                 u'icon': u'maps/directionsRun',
                 u'content': u'Which customers will likely be leaving in the coming time?', u'type': u'predictive'},
                {u'orientation': u'product', u'selected': False, u'enabled': False, u'label': u'popularity',
                 u'icon': u'action/trendingUp', u'content': u'Which products will be the most popular in the future?',
                 u'type': u'predictive'}]})

        self.assertIn("analysis_questions", response.data)

    def test_update_analysis_settings(self):
        c, user = self._create_default_user()

        def is_label_selected(_user, label):
            for question in _user.group.analysis_settings.questions:
                if question.label == label:
                    return question.selected
            return False

        def assert_analysis_parameter_is(_user, label, choice_index, choice_input):
            param = _user.group.analysis_settings.get_parameter(label=label)
            self.assertTrue(param is not None)
            self.assertEqual(param.choice_index, choice_index)
            self.assertEqual(param.choice_input, choice_input)

        # checking initial setup
        assert_analysis_parameter_is(user, "income", 0, None)
        self.assertFalse(is_label_selected(user, "leaving"))
        self.assertTrue(is_label_selected(user, "cause of leave"))
        self.assertFalse(is_label_selected(user, "popularity"))
        self.assertFalse(is_label_selected(user, "invalid label"))

        # first enabling leaving question, with new param setting
        c.post('/analysis_questions/update_analysis_settings/',
               data={
                   "analysisQuestion": ["cause of leave", "leaving"],
                   "analysisParams": [{
                       "label": "clv",
                       "choiceIndex": 0,
                   }]
               })
        user.reload()
        self.assertTrue(is_label_selected(user, "leaving"))
        self.assertFalse(is_label_selected(user, "cause of leave"))

        # enabling disabled question, expect an error
        response = c.post('/analysis_questions/update_analysis_settings/',
                          data={
                              "analysisQuestion": ["popularity"],
                              "analysisParams": []
                          })
        self.assertIn("error", from_json(response.content))

        # simply changing parameter setting only
        assert_analysis_parameter_is(user, "clv", 0, None)
        c.post('/analysis_questions/update_analysis_settings/',
               data={
                   "analysisQuestion": [],
                   "analysisParams": [{
                       "label": "clv",
                       "choiceIndex": 1,
                   }]
               })
        user.reload()
        assert_analysis_parameter_is(user, "clv", 1, None)

        # changing other questions, updating choiceInput at the same request
        c.post('/analysis_questions/update_analysis_settings/',
               data={
                   "analysisQuestion": ['cause of leave'],
                   "analysisParams": [{
                       "label": "clv",
                       "choiceIndex": 0,
                       "choiceInput": "Testing Without Validation"
                   }]
               })
        user.reload()
        assert_analysis_parameter_is(user, "clv", 0, "Testing Without Validation")

    def test_start_analysis(self):
        c, user = self._create_default_user()
        c.put('/analysis_questions/start_analysis/')

    def test_same_elements(self):
        self.assertTrue(_same_elements([5, 6, 7, 3], [3, 6, 7, 5]))
        self.assertTrue(not _same_elements([5, 6, 7, 4], [3, 6, 7, 5]))
        self.assertTrue(not _same_elements([3, 6, 7, 5], [5, 6, 7, 3, 8]))

    # TODO: Write a test that accounts for multiple groups
    # def test_multiple_groups(self):
    #     admin2 = User.create_admin(username="admin2", password="pass", group_name="dummy_group2")

    def _create_default_user(self):
        assert len(User.objects) == 1
        assert len(Group.objects) == 1

        c = Client()
        self.admin_client.post("/users/create_user/",
                               {"username": "dummy1", "password": "asdf", "group": "dummy_group"})

        group = Group.objects.get(name="dummy_group")

        statuses = {"leaving": {'enabled': True, 'selected': False},
                    "popularity": {'enabled': False, 'selected': False},
                    "cause of leave": {'enabled': True, 'selected': True}}

        for label in statuses:
            q = group.analysis_settings.get_question(label)
            q.enabled = statuses[label]['enabled']
            q.selected = statuses[label]['selected']

        group.save()

        c.post("/users/login/", {"username": "dummy1", "password": "asdf"})

        return c, User.objects.get(username="dummy1")

    def setUp(self):
        self.admin = User.create_admin(username="admin", password="pass", group_name="dummy_group")

        self.admin_client = Client()
        self.admin_client.post("/users/login/", {"username": "admin", "password": "pass"})


# Checks whether list1 and list2 have the same elements, regardless of order
def _same_elements(list1, list2):
    for item in list1:
        if item not in list2:
            return False

    for item in list2:
        if item not in list1:
            return False

    return True
