from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from eledata.models.entity import Entity

from eledata.util import from_json, to_json
from eledata.models.analysis_questions import *


class AnalysisQuestionTestCase(TestCase):
    analysis_questions_init = [{"content": "Which customers will likely be leaving in the coming time?", "label":"leaving", "type":"predictive", "orientation":"customer", "parameters":[]}, {"content": "Which products will be the most popular in the future?", "label":"poplularity", "type":"predictive", "orientation":"product", "parameters":[]},]
    
    for question in analysis_questions_init:
        AnalysisQuestion(**question).save()
        
    
    def test_get_all_questions(self):
        c = Client()
        response = c.get('/analysis_questions/get_all_existing_analysis_questions/')
        ret_data = from_json(response.content)
        for item in ret_data:
            del item['id']
            self.assertTrue(item in self.analysis_questions_init)
        
        for item in self.analysis_questions_init:
            self.assertTrue(item in ret_data)
        
        self.assertEqual(response.status_code, 200)
