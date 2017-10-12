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


class OfflineEngineTest(TestCase):
    """
    Run all the tests in this file by
    $ python manage.py test eledata.tests.test_offline_engine
    """

    # put those demo input csv here for testing to share
    transactionFilename = 'misc/test_files/entity_data_1.csv'
    bigTransactionFilename = 'misc/test_files/core_test/big_transaction.csv'
    customerFilename = 'misc/test_files/core_test/Data Actual transactions from UK retailer.csv'

    '''
    Environment Setup for test cases
    '''
    def doCleanups(self):
        Event.drop_collection()

    def setUp(self):
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
    # def test_engine_1(self):
    #
    #     mock_response = {'some_key': 'some_value'}
    #
    #     engine = EngineProvider.provide("Customer.CHANGE_ME", pd.read_csv(self.transactionFilename),
    #                                     pd.read_csv(self.customerFilename))
    #
    #     engine.execute()
    #
    #     response = engine.get_processed()
    #
    #     # print or compare response with static data
    #     print(response)
    #     self.assertEquals(response, mock_response)
    #
    #     # TODO: test engine.event_init()
