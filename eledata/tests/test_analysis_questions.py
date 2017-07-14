from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from eledata.models.entity import Entity

from eledata.util import from_json, to_json

class AnalysisQuestionTestCase(TestCase):
    
    def test_basic(self):
        c = Client()
        response = c.post('/analysis_questions/create_thing', data='"some json"',
            content_type="application/json", HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status == 200)
        
