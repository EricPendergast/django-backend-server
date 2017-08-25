# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from eledata.models.entity import Entity
from eledata.models.users import User, Group
from project import settings

from eledata.util import from_json, to_json

import datetime
import platform
import time


# Create your tests here.

class EntityTestCase(TestCase):
    entityJSON1 = '''{ "id": "59560d779a4c0e4abaa1b6a8", "type": "transaction", "source_type": "local", "created_at": "2017-06-28T14:08:10.276000", "updated_at": "2017-06-28T14:08:10.276000"}'''

    entityDataHeaderJSON1 = '''{"data_header":[{"source":"transaction_quantity","mapped":"Transaction_Quantity","data_type":"number"},{"source":"transaction_date","mapped":"Transaction_Date","data_type":"date"},{"source":"transaction_id","mapped":"Transaction_ID","data_type":"string"},{"source":"user_id","mapped":"User_ID","data_type":"string"},{"source":"transaction_value","mapped":"Transaction_Value","data_type":"number"}]}'''
    entityDataHeaderNoFileHeader = '''{"data_header":[{"source":"column 1", "mapped":"Transaction_Quantity", "data_type":"number"}, {"source":"column 2", "mapped":"Transaction_Date", "data_type":"date"}, {"source":"column 3", "mapped":"Transaction_ID", "data_type":"string"}, {"source":"column 4", "mapped":"User_ID", "data_type":"string"}, {"source":"column 5", "mapped":"Transaction_Value", "data_type":"number"}]}'''
    # Contains an invalid type
    entityDataHeaderInvalidType = '''{"data_header":[{"source":"transaction_quantity","mapped":"Transaction_Quantity","data_type":"asdfasdf"},{"source":"transaction_date","mapped":"Transaction_Date","data_type":"date"},{"source":"transaction_id","mapped":"Transaction_ID","data_type":"string"},{"source":"user_id","mapped":"User_ID","data_type":"string"},{"source":"transaction_value","mapped":"Transaction_Value","data_type":"number"}]}'''

    defaultFilename = 'misc/test_files/entity_data_1.csv'
    csvNoHeaderFilename = 'misc/test_files/entity_data_8_no_header.csv'

    def doCleanups(self):
        Group.drop_collection()
        User.drop_collection()

    # Log out of the old client and log into a new client
    def setUp(self):
        assert len(Group.objects) == 0
        assert len(User.objects) == 0

        User.create_admin(username="admin", password="pass", group_name="dummy_group")
        User.create_admin(username="admin2", password="pass", group_name="different_dummy_group")

        self.client = Client()
        self.client.post("/users/login/", {"username": "admin", "password": "pass"})
        self.client.post("/users/create_user/", {"username": "dummy", "password": "asdf"})
        self.client.post("/users/create_user/", {"username": "dummy3", "password": "asdf"})

        self.client.post("/users/login/", {"username": "admin2", "password": "pass"})
        self.client.post("/users/create_user/", {"username": "dummy2", "password": "asdf"})

        self.client.post("/users/login/", {"username": "dummy", "password": "asdf"})

    '''
    Sending a get request to get_all_entity and testing that it sends back all
    the entities in the database
    '''

    def test_get_all_entity(self):
        Entity.objects.delete()
        c = self.client
        response = c.get('/entity/get_all_entity/')

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, "[]")

        self._create_entity_init(c, 'misc/test_files/entity_data_1.csv')
        response = c.get('/entity/get_all_entity/')
        self.assertEquals(response.status_code, 200)

        # Taking the first item from the list of entities sent back
        data = from_json(response.content)[0]
        dataComp = from_json(self.entityJSON1)
        # don't compare their id's

        del data["id"]
        del dataComp["id"]

        # Don't compare all the fields because creating an entity object fills
        # in the blank fields with defaults. This is why it is not "for key in
        # data"
        for key in dataComp:
            self.assertEquals(data[key], dataComp[key])

    def test_get_all_entity_multiple_groups(self):
        Entity.objects.delete()
        c = self.client
        self._create_entity_init(c, self.defaultFilename)
        response = c.get('/entity/get_all_entity/').data
        self.assertEquals(len(response), 1)

        c.post('/users/logout/', {})
        c.post('/users/login/', {'username': 'dummy2', 'password': 'asdf'})
        response = c.get('/entity/get_all_entity/').data
        self.assertEquals(len(response), 0)

    '''
    Testing that sending a first stage entity creation post request (to
    entity/create_entity) puts the entity in the database.
    '''

    def test_create_entity_first_stage(self):
        c = self.client

        Entity.objects.delete()
        response = self._create_entity_init_raw_response(c, 'misc/test_files/entity_data_1.csv')

        id = from_json(response.content)['entity_id']
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(Entity.objects.filter(pk=id)), 1)

    '''
    Testing that sending a second stage entity creation post request (to
    entity/create_entity_mapped) creates and puts an entity with the csv data
    into the database.
    '''

    def test_create_entity_second_stage_csv(self):
        c = self.client

        # entity = self._create_mapped_entity(c, self.entityDataHeaderJSON1, 'misc/test_files/entity_data_1.csv')[
        #     'entity']
        info = self._create_mapped_entity(c, self.entityDataHeaderJSON1, 'misc/test_files/entity_data_1.csv')

        entity = info['entity']
        # Checking that the first and last rows of data are the same as the
        # first and last rows of the csv
        self.assertIn({u'User_ID': u'751-23-2405',
                       u'Transaction_Date': datetime.datetime(2017, 1, 9, 0, 0),
                       u'Transaction_Quantity': 8.0, u'Transaction_ID': u'228-08-3254',
                       u'Transaction_Value': 86.17}, entity.data)

        self.assertIn({u'User_ID': u'988-90-7620',
                       u'Transaction_Date': datetime.datetime(2017, 4, 25, 0, 0),
                       u'Transaction_Quantity': 14.0, u'Transaction_ID': u'293-64-2300',
                       u'Transaction_Value': 320.89}, entity.data)

    '''
    Sending a get request to get_entity_list and testing that it sends back all
    entity list with status
    '''

    def test_get_entity_list(self):
        Entity.objects.delete()
        c = self.client
        response = c.get('/entity/get_entity_list/')

        self.assertEquals(response.status_code, 200)
        self.assertEquals(from_json(response.content),
                          [{str(a): str(b) for a, b in x.items()} for x in settings.CONSTANTS['entity']['type']])

        self._create_entity_init(c, 'misc/test_files/entity_data_1.csv')
        response = c.get('/entity/get_entity_list/')

        self.assertEquals(response.status_code, 200)
        self.assertEquals((from_json(response.content)[0][u'status']), 'Pending')

        self._create_mapped_entity(c, self.entityDataHeaderJSON1, 'misc/test_files/entity_data_1.csv')
        response = c.get('/entity/get_entity_list/')

        self.assertEquals(response.status_code, 200)
        self.assertEquals((from_json(response.content)[0][u'status']), 'Ready')

    '''
    The same as 'test_create_entity_second_stage_csv' (above), except using a
    tsv file as input
    '''

    def test_create_entity_second_stage_tsv(self):
        c = self.client

        entity = self._create_mapped_entity(c, self.entityDataHeaderJSON1, 'misc/test_files/entity_data_2.tsv')[
            'entity']

        self.assertIn({u'User_ID': u'851-23-2405',
                       u'Transaction_Date': datetime.datetime(2017, 1, 9, 0, 0),
                       u'Transaction_Quantity': 8.0, u'Transaction_ID': u'228-08-3254',
                       u'Transaction_Value': 87.17}, entity.data)

        self.assertIn({u'User_ID': u'989-90-7620',
                       u'Transaction_Date': datetime.datetime(2017, 4, 25, 0, 0),
                       u'Transaction_Quantity': 14.0, u'Transaction_ID': u'294-64-2300',
                       u'Transaction_Value': 320.89}, entity.data)

    '''
    Testing that sending an invalid csv causes an error
    '''

    def test_create_entity_invalid_csv(self):
        client = self.client

        response = self._create_entity_init(client, 'misc/test_files/entity_data_invalid_3.csv')

        self.assertTrue('error' in response)

    '''
    The same as 'test_create_entity_second_stage_csv', except using a
    xls file as input
    '''

    def test_create_entity_xls(self):

        if platform.system() == "Windows":
            return

        c = self.client

        entity = self._create_mapped_entity(c, self.entityDataHeaderJSON1, 'misc/test_files/entity_data_5_large.xls')[
            'entity']

        self.assertIn({u'User_ID': u'988-90-7620',
                       u'Transaction_Date': datetime.datetime(2017, 4, 25, 0, 0),
                       u'Transaction_Quantity': 1.0, u'Transaction_ID': u'293-64-2300',
                       u'Transaction_Value': 320.89}, entity.data)

        self.assertIn({u'User_ID': u'988-90-7723',
                       u'Transaction_Date': datetime.datetime(2017, 4, 25, 0, 0),
                       u'Transaction_Quantity': 104.0, u'Transaction_ID': u'293-64-2403',
                       u'Transaction_Value': 320.89}, entity.data)

    '''
    The same as 'test_create_entity_second_stage_csv', except using a
    xlsx file as input
    '''

    def test_create_entity_xlsx(self):

        if platform.system() == "Windows":
            return

        c = self.client

        entity = self._create_mapped_entity(c, self.entityDataHeaderJSON1, 'misc/test_files/entity_data_6_large.xlsx')[
            'entity']

        self.assertIn({u'User_ID': u'988-90-7620',
                       u'Transaction_Date': datetime.datetime(2017, 4, 25, 0, 0),
                       u'Transaction_Quantity': 1.0, u'Transaction_ID': u'293-64-2300',
                       u'Transaction_Value': 320.89}, entity.data)

        self.assertIn({u'User_ID': u'988-90-7723',
                       u'Transaction_Date': datetime.datetime(2017, 4, 25, 0, 0),
                       u'Transaction_Quantity': 104.0, u'Transaction_ID': u'293-64-2403',
                       u'Transaction_Value': 320.89}, entity.data)

    '''
    Testing all the different ways json part of the initial request could be
    invalid, and making sure they all generate errors.

    Also testing an error is generated if either the file upload or the entity
    json is left out
    '''

    def test_create_entity_invalid_init_request(self):
        c = self.client
        invalid_json = ['{}',
                        '{"type":"transaction"}',
                        '{"source_type":"local", "type":"unicorn"}',
                        '{"source_type":"source-type-with-really-long-name", "type":"transaction"}',
                        '{"source_type":"invalid-type", "type":"transaction"}',
                        '{"source_type":"local"}', ]
        for json in invalid_json:
            self.assertTrue("error" in self._create_entity_init(c, filename=None, json=json))

        with open(self.defaultFilename) as fp:
            self.assertTrue("error" in from_json(c.post('/entity/create_entity/', {'file': fp}).content))
            self.assertTrue("error" in from_json(
                c.post('/entity/create_entity/', {'entity': '{"source_type":"local", "type":"transaction"}'}).content))

    '''
    Testing that an error is generated if you make an initial request without
    specifying if the header is included with 'is_header_included'.
    '''

    def test_create_entity_invalid_init_request_2(self):
        client = self.client
        with open(self.defaultFilename) as fp:
            resp = client.post('/entity/create_entity/',
                               {'file': fp, 'entity': self.entityJSON1})
            self.assertTrue('error' in from_json(resp.content))

    '''
    Testing that an error is generated if an invalid header is sent to the
    final request.
    '''

    def test_create_entity_invalid_final_request(self):
        c = self.client

        resp = self._create_mapped_entity(c, self.entityDataHeaderInvalidType,
                                          self.defaultFilename)
        self.assertTrue("error" in from_json(resp['final_response'].content))

    '''
    Testing that nothing bad happens when you create many entities at once.
    '''

    def test_create_multiple_entity(self):
        c = self.client
        # Will contain all the responses from the create_entity requests
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

    '''
    Testing that if you send a csv with no header, the program will create an
    autogenerated header.
    '''

    def test_create_entity_no_header(self):
        client = self.client
        resp = self._create_mapped_entity(client, self.entityDataHeaderNoFileHeader,
                                          self.csvNoHeaderFilename, fileHeaderIncluded=False)

        # checking that the returned data has an autogenerated header
        for dataEntry in resp["init_response"]["data"]:
            for header_name in dataEntry:
                self.assertRegex(header_name, "^column [0-9]+$")

    # Test that two users in the same group can edit the same entity, while one
    # outside that group cannot
    def test_entity_permissions(self):
        client1 = self.client

        client2 = Client()
        client2.post("/users/login/", {"username": "dummy2", "password": "asdf"})

        client3 = Client()
        client3.post("/users/login/", {"username": "dummy3", "password": "asdf"})

        id = self._create_entity_init(client1, filename=None)['entity_id']
        response = self._create_entity_final(client2, id, self.entityDataHeaderJSON1)
        self.assertIn('error', from_json(response.content))

        response = self._create_entity_final(client3, id, self.entityDataHeaderJSON1)
        self.assertNotIn('error', from_json(response.content))

    # TODO: Handle this case
    # Doesn't work yet because of the way excel files measure line width
    # def test_create_entity_invalid_xlsx(self):
    #     c = self.client
    #
    #     response = self._create_entity_init(c, json=self.entityDataHeaderJSON1, filename= 'misc/test_files/entity_data_7_invalid.xlsx')
    #      self.assertTrue('error' in response)


    # # TODO: Handle this case by removing the entity from the
    # # database
    # # Uploading a csv where the error is after line 100
    # def test_create_entity_invalid_csv_after_100(self):
    #     client = self.client
    #
    #     response = self._create_entity_init(client, 'misc/test_files/entity_data_invalid_long_4.csv')
    #
    #     self.assertFalse('error' in response)
    #
    #     id = response.content)['entity_id']
    #     response = _create_entity_final(client, response, id,
    #             entityDataHeaderJSON1)



    def _create_entity_init_raw_response(self, client,
                                         filename, json=entityJSON1, fileHeaderIncluded=True):
        filename = self.defaultFilename if filename is None else filename

        with open(filename) as fp:
            ret = client.post('/entity/create_entity/',
                              {'file': fp, 'entity': json, 'isHeaderIncluded': fileHeaderIncluded})
            return ret

    def _create_entity_init(self, *args, **kwargs):
        return from_json(self._create_entity_init_raw_response(*args, **kwargs).content)

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

        return {'entity': Entity.objects.get(pk=id), 'init_response': init_response, 'final_response': final_response}
