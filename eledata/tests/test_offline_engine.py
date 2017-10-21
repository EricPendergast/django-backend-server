# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from eledata.models.event import Event
from eledata.models.users import User, Group
import eledata.handlers.event as event_handler
from project.settings import CONSTANTS
import datetime
from eledata.core_engine.provider import EngineProvider
import pandas as pd
import pprint


class OfflineEngineTest(TestCase):
    """
    Run all the tests in this file by
    $ python manage.py test eledata.tests.test_offline_engine
    """

    # put those demo input csv here for testing to share
    transactionFilename = 'misc/test_files/transaction_records.tsv'
    bigTransactionFilename = 'misc/test_files/core_test/big_transaction.csv'
    customerFilename = 'misc/test_files/customer_records.tsv'

    '''
    Environment Setup for test cases
    '''
    def doCleanups(self):
        Event.drop_collection()
        Group.drop_collection()
        User.drop_collection()
        Event.drop_collection()

    def setUp(self):
        Group.drop_collection()
        User.drop_collection()
        Event.drop_collection()
        assert len(Group.objects) == 0
        assert len(User.objects) == 0
        assert len(Event.objects) == 0

        self.admin = User.create_admin(username="admin", password="pass", group_name="dummy_group")
        self.admin_group = Group.objects.get(name="dummy_group")
        self.admin_client = Client()
        self.admin_client.post("/users/login/", {"username": "admin", "password": "pass"})

    """
    Demo testing for some stats engine
    """
    def test_engine_1(self):

        mock_response = {'some_key': 'some_value'}
        params = {'duration': 5, 'rule': 'nosale', 'rule_param': 6}

        engine = EngineProvider.provide("Question.question_07", self.admin_group, params, pd.read_csv(self.transactionFilename, sep='\t'),
                                        pd.read_csv(self.customerFilename, sep='\t'))

        engine.execute()

        responses = engine.responses
        engine.event_init()
        # print(response.keys())
        # print or compare response with static data
        pprint.pprint(responses)
        # self.assertEquals(response, mock_response)

        # TODO: test engine.event_init()
