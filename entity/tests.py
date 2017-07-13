# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from entity.models import Entity

from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

import datetime
# Create your tests here.

class EntityTestCase(TestCase):
    entityJSON1 = '''{ "id": "59560d779a4c0e4abaa1b6a8", "type": "transaction", "source_type": "local", "allowed_user": [], "created_at": "2017-06-28T14:08:10.276000", "updated_at": "2017-06-28T14:08:10.276000"}'''
    
    entityDataHeaderJSON1 = '''{"data_header":[{"source":"transaction_quantity","mapped":"Transaction_Quantity","data_type":"number"},{"source":"transaction_date","mapped":"Transaction_Date","data_type":"date"},{"source":"transaction_id","mapped":"Transaction_ID","data_type":"string"},{"source":"user_id","mapped":"User_ID","data_type":"string"},{"source":"transaction_value","mapped":"Transaction_Value","data_type":"number"}]}'''
    entityDataHeaderNoFileHeader = '''{"data_header":[{"source":"column 1", "mapped":"Transaction_Quantity", "data_type":"number"}, {"source":"column 2", "mapped":"Transaction_Date", "data_type":"date"}, {"source":"column 3", "mapped":"Transaction_ID", "data_type":"string"}, {"source":"column 4", "mapped":"User_ID", "data_type":"string"}, {"source":"column 5", "mapped":"Transaction_Value", "data_type":"number"}]}'''
    # Contains an invalid type
    entityDataHeaderInvalidType = '''{"data_header":[{"source":"transaction_quantity","mapped":"Transaction_Quantity","data_type":"asdfasdf"},{"source":"transaction_date","mapped":"Transaction_Date","data_type":"date"},{"source":"transaction_id","mapped":"Transaction_ID","data_type":"string"},{"source":"user_id","mapped":"User_ID","data_type":"string"},{"source":"transaction_value","mapped":"Transaction_Value","data_type":"number"}]}'''

    defaultFilename = 'misc/test_files/entity_data_1.csv'
    csvNoHeaderFilename = 'misc/test_files/entity_data_8_no_header.csv'
    def test_get_all_entity(self):
        Entity.objects.delete()
        c = Client()
        response = c.get('/entity/get_all_entity/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, "[]")

        self._create_entity_init(c, 'misc/test_files/entity_data_1.csv')
        response = c.get('/entity/get_all_entity/')
        self.assertEquals(response.status_code, 200)

        # Taking the first item from the list of entities sent back
        data = self._from_json(response.content)[0]
        dataComp = self._from_json(self.entityJSON1)
        del data["id"]
        del dataComp["id"]

        # Don't compare all the fields because creating an entity object fills
        # in the blank fields with defaults
        for key in dataComp:
            self.assertEquals(data[key], dataComp[key])

    def test_create_entity_first_stage(self):
        c = Client()

        Entity.objects.delete()
        response = self._create_entity_init_raw_response(c, 'misc/test_files/entity_data_1.csv')

        id = self._from_json(response.content)['entity_id']
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(Entity.objects.filter(pk=id)), 1)


    def test_create_entity_second_stage(self):
        c = Client()

        Entity.objects.delete()
        response = self._create_entity_init(c, 'misc/test_files/entity_data_1.csv')

        id = Entity.objects.first().id
        c.post('/entity/%s/create_entity_mapped/' % id,
                data=self.entityDataHeaderJSON1, content_type="application/json",
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        entity = Entity.objects.first()

        self.assertEquals(entity.data[0], {u'user_id': u'751-23-2405',
            u'transaction_date': datetime.datetime(2017, 1, 9, 0, 0),
            u'transaction_quantity': 8.0, u'transaction_id': u'228-08-3254',
            u'transaction_value': 86.17})

        self.assertEquals(entity.data[-1], {u'user_id': u'988-90-7620',
            u'transaction_date': datetime.datetime(2017, 4, 25, 0, 0),
            u'transaction_quantity': 14.0, u'transaction_id': u'293-64-2300',
            u'transaction_value': 320.89})

    def test_create_entity_second_stage_csv(self):
        c = Client()

        entity = self._create_mapped_entity(c, self.entityDataHeaderJSON1, 'misc/test_files/entity_data_1.csv')['entity']
        
        self.assertEquals(entity.data[0], {u'user_id': u'751-23-2405',
            u'transaction_date': datetime.datetime(2017, 1, 9, 0, 0),
            u'transaction_quantity': 8.0, u'transaction_id': u'228-08-3254',
            u'transaction_value': 86.17})

        self.assertEquals(entity.data[-1], {u'user_id': u'988-90-7620',
            u'transaction_date': datetime.datetime(2017, 4, 25, 0, 0),
            u'transaction_quantity': 14.0, u'transaction_id': u'293-64-2300',
            u'transaction_value': 320.89})

    def test_create_entity_second_stage_tsv(self):
        c = Client()

        entity = self._create_mapped_entity(c, self.entityDataHeaderJSON1, 'misc/test_files/entity_data_2.tsv')['entity']

        self.assertEquals(entity.data[0], {u'user_id': u'851-23-2405',
            u'transaction_date': datetime.datetime(2017, 1, 9, 0, 0),
            u'transaction_quantity': 8.0, u'transaction_id': u'228-08-3254',
            u'transaction_value': 87.17})

        self.assertEquals(entity.data[-1], {u'user_id': u'989-90-7620',
            u'transaction_date': datetime.datetime(2017, 4, 25, 0, 0),
            u'transaction_quantity': 14.0, u'transaction_id': u'294-64-2300',
            u'transaction_value': 320.89})

        
    def test_create_entity_invalid_csv(self):
        client = Client()

        response = self._create_entity_init(client, 'misc/test_files/entity_data_invalid_3.csv')

        self.assertTrue('error' in response)

    def test_create_entity_xls(self):
        c = Client()

        entity = self._create_mapped_entity(c, self.entityDataHeaderJSON1, 'misc/test_files/entity_data_5_large.xls')['entity']

        self.assertEquals(entity.data[0], {u'user_id': u'988-90-7620',
            u'transaction_date': datetime.datetime(2017, 4, 25, 0, 0),
            u'transaction_quantity': 1.0, u'transaction_id': u'293-64-2300',
            u'transaction_value': 320.89})

        self.assertEquals(entity.data[-1], {u'user_id': u'988-90-7620',
            u'transaction_date': datetime.datetime(2017, 4, 25, 0, 0),
            u'transaction_quantity': 104.0, u'transaction_id': u'293-64-2300',
            u'transaction_value': 320.89})


    def test_create_entity_xlsx(self):
        c = Client()

        entity = self._create_mapped_entity(c, self.entityDataHeaderJSON1, 'misc/test_files/entity_data_6_large.xlsx')['entity']

        self.assertEquals(entity.data[0], {u'user_id': u'988-90-7620',
            u'transaction_date': datetime.datetime(2017, 4, 25, 0, 0),
            u'transaction_quantity': 1.0, u'transaction_id': u'293-64-2300',
            u'transaction_value': 320.89})

        self.assertEquals(entity.data[-1], {u'user_id': u'988-90-7620',
            u'transaction_date': datetime.datetime(2017, 4, 25, 0, 0),
            u'transaction_quantity': 104.0, u'transaction_id': u'293-64-2300',
            u'transaction_value': 320.89})
        
        
    def test_create_entity_invalid_init_request(self):
        c = Client()
        invalid_json = ['{}',
                '{"type":"transaction"}',
                '{"source_type":"local", "type":"unicorn"}',
                '{"source_type":"source-type-with-really-long-name", "type":"transaction"}',
                '{"source_type":"invalid-type", "type":"transaction"}',
                '{"source_type":"local"}',]
        for json in invalid_json:
            self.assertTrue("error" in self._create_entity_init(c, filename=None, json=json))
            
        with open(self.defaultFilename) as fp:
            self.assertTrue("error" in self._from_json(c.post('/entity/create_entity/', {'file_upload': fp}).content))
            self.assertTrue("error" in self._from_json(c.post('/entity/create_entity/', {'entity':'{"source_type":"local", "type":"transaction"}'}).content))
            
            
    def test_create_entity_invalid_init_request_2(self):
        client = Client()
        with open(self.defaultFilename) as fp:
            resp = client.post('/entity/create_entity/',
                {'file_upload': fp, 'entity': self.entityJSON1})
            self.assertTrue('error' in self._from_json(resp.content))
        
    def test_create_entity_invalid_final_request(self):
        c = Client()
            
        # response = self._create_entity_init(c, filename=self.defaultFilename, json=self.entityJSON1)
        
        # self.assertTrue("error" in self._from_json(self._create_entity_final(c, response['entity_id'], self.entityDataHeaderJSON1)))
        
        resp = self._create_mapped_entity(c, self.entityDataHeaderInvalidType, self.defaultFilename)
        self.assertTrue("error" in self._from_json(resp['final_response'].content))
        
    
    def test_create_multiple_entity(self):
        c = Client()
        responses = []
        
        num = 20
        
        for i in range(num):
            responses += (self._create_entity_init(c, 
                    self.defaultFilename, self.entityJSON1),)
        
        for i in range(num):
            self._create_entity_final(c, 
                    responses[i]["entity_id"], self.entityDataHeaderJSON1)
            
        for i in range(num):
            self.assertTrue(Entity.objects.filter(
                pk=responses[i]["entity_id"]))
            
    def test_create_entity_no_header(self):
        client = Client()
        resp = self._create_mapped_entity(client, self.entityDataHeaderNoFileHeader,
                self.csvNoHeaderFilename, fileHeaderIncluded=False)
        
        # checking that the returned data has an autogenerated header
        for dataEntry in resp["init_response"]["data"]:
            for header_name in dataEntry:
                self.assertRegex(header_name, "^column [0-9]+$")
    
    # TODO: test that create_entity and create_entity_mapped send back 100
    # lines of data
    
    
    # Doesn't work yet because of the way excel files measure line width
    # def test_create_entity_invalid_xlsx(self):
    #     c = Client()
    #
    #     response = self._create_entity_init(c, json=self.entityDataHeaderJSON1, filename= 'misc/test_files/entity_data_7_invalid.xlsx')
    #      self.assertTrue('error' in response)


    # # TODO: Figure out how to handle this case: remove the entity from the
    # # database
    # # Uploading a csv where the error is after line 100
    # def test_create_entity_invalid_csv_after_100(self):
    #     client = Client()
    #
    #     response = self._create_entity_init(client, 'misc/test_files/entity_data_invalid_long_4.csv')
    #
    #     self.assertFalse('error' in response)
    #
    #     id = response.content)['entity_id']
    #     response = _create_entity_final(client, response, id,
    #             entityDataHeaderJSON1)
    
    
    def _to_json(self, data):
        return JSONRenderer().render(data)
        
    def _from_json(self, json_string):
        ret = JSONParser().parse(BytesIO(str(json_string)))
        return ret
    
    def _create_entity_init_raw_response(self, client,
            filename, json=entityJSON1, fileHeaderIncluded=True):
        filename = self.defaultFilename if filename is None else filename
        
        with open(filename) as fp:
            ret = client.post('/entity/create_entity/',
                {'file_upload': fp, 'entity': json, 'isFileHeaderIncluded':fileHeaderIncluded})
            return ret
        
    def _create_entity_init(self, *args, **kwargs):
        return self._from_json(self._create_entity_init_raw_response(*args, **kwargs).content)
        
    def _create_entity_final(self, client, id, data_header):
        final_response = client.post('/entity/%s/create_entity_mapped/' % id,
                data=data_header, content_type="application/json",
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        return final_response
    
    # Performs the two stages to create an entity. Returns a dictionary with
    # the created entity in the "entity" index, and the initial and final
    # responses in indexes "init_response" and "final_response", respectively
    def _create_mapped_entity(self, client, data_header, filename, fileHeaderIncluded=True):
        init_response = self._create_entity_init(client, filename, fileHeaderIncluded=fileHeaderIncluded)
        
        id = init_response['entity_id']
        
        final_response = self._create_entity_final(client, id, data_header)
        
        return {'entity':Entity.objects.get(pk=id), 'init_response':init_response, 'final_response':final_response}
