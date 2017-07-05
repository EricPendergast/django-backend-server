# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from entity.models import Entity

# Create your tests here.

class EntityTestCase(TestCase):
    init_post = """--AaZz
        Content-Disposition: form-data; name="fileUpload"; filename="test_data_upload_2.txt"
        Content-Type: text/plain

        asdfasdf_quantity,transaction_date,user_id,transaction_id,transaction_value
        8,"09/01/2017","751-23-2405","228-08-3254",86.17
        --AaZz
        Content-Disposition: form-data; name="file_format"

        csv
        --AaZz
        Content-Disposition: form-data; name="entity"
        ContentType: application/json

        {
                "id": "59560d779a4c0e4abaa1b6a8",
                "type": "transaction",
                "source_type": "local",
                "allowed_user": [],
                "created_at": "2017-06-28T14:08:10.276000",
                "updated_at": "2017-06-28T14:08:10.276000"
        }

        --AaZz--
            def setUp(self):
                pass
        """
    
    def test_entity_initial_post(self):
        c = Client()
        response = c.post('/entity/create_entity/', data=self.init_post, **{'CONTENT_TYPE':'multipart/form-data; boundary=AaZz'})

        assert Entity.objects.count() == 1
        assert response.status == 200
