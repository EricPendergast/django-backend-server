from __future__ import unicode_literals

from django.test import TestCase
from eledata.core.entity_h2o_engine import *
from eledata.core.entity_summary import *

from django.test import Client
from eledata.models.entity import Entity
from eledata.models.users import User, Group

from eledata.util import from_json
import h2o

# from project import settings
# from eledata.util import to_json
# from project import settings
# import pandas as pd
# import platform
# import time


class CoreH2OTestCase(TestCase):
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    entityJSON1 = '''{
        "id": "59560d779a4c0e4abaa1b6a8", "type": "transaction", "source_type": "local",
        "created_at": "2017-06-28T14:08:10.276000", "updated_at": "2017-06-28T14:08:10.276000"}'''

    entityDataHeaderJSON1 = '''{
        "data_header": [{"source": "transaction_quantity", "mapped": "Transaction_Quantity", "data_type": "number"},
                        {"source": "transaction_date", "mapped": "Transaction_Date", "data_type": "date"},
                        {"source": "transaction_id", "mapped": "Transaction_ID", "data_type": "string"},
                        {"source": "user_id", "mapped": "User_ID", "data_type": "string"},
                        {"source": "transaction_value", "mapped": "Transaction_Value", "data_type": "number"}]}'''
    entityDataHeaderNoFileHeader = '''{
        "data_header": [{"source": "column 4", "mapped": "Transaction_Quantity", "data_type": "number"},
                        {"source": "column 3", "mapped": "Transaction_Date", "data_type": "date"},
                        {"source": "column 1", "mapped": "Transaction_ID", "data_type": "string"},
                        {"source": "column 2", "mapped": "User_ID", "data_type": "string"},
                        {"source": "column 5", "mapped": "Transaction_Value", "data_type": "number"}]}'''
    # Contains an invalid type
    entityDataHeaderInvalidType = '''{
        "data_header": [{"source": "transaction_quantity", "mapped": "Transaction_Quantity", "data_type": "asdfasdf"},
                        {"source": "transaction_date", "mapped": "Transaction_Date", "data_type": "date"},
                        {"source": "transaction_id", "mapped": "Transaction_ID", "data_type": "string"},
                        {"source": "user_id", "mapped": "User_ID", "data_type": "string"},
                        {"source": "transaction_value", "mapped": "Transaction_Value", "data_type": "number"}]}'''

    defaultTransactionFilename = 'misc/test_files/entity_data_1.csv'
    bigTransactionFilename = 'misc/test_files/core_test/big_transaction.csv'
    csvNoHeaderFilename = 'misc/test_files/entity_data_8_no_header.csv'

    def doCleanups(self):
        Group.drop_collection()
        User.drop_collection()
        Entity.drop_collection()
        # h2o.cluster().shutdown()

    def setUp(self):
        # h2o.init()
        assert len(Group.objects) == 0
        assert len(User.objects) == 0

        User.create_admin(username="admin", password="pass", group_name="dummy_group")

        self.client = Client()
        self.client.post("/users/login/", {"username": "admin", "password": "pass"})

    def test_first_clv_analysis(self):
        # h2o.init()
        # print(h2o.frames())
        with open(self.defaultTransactionFilename) as fp:
            ret = self.client.post('/entity/create_entity/',
                                   {'file': fp, 'entity': self.entityJSON1, 'isHeaderIncluded': True})

        rid = from_json(ret.content)['entity_id']
        self.client.post('/entity/%s/create_entity_mapped/' % rid,
                         data=self.entityDataHeaderJSON1, content_type="application/json",
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        user_group = Group.objects(name="dummy_group").get()
        entity_h2o_engine = EntityH2OEngine.init_engine(user_group)

        # testing get_user_list
        response = entity_h2o_engine.get_transaction_based_user_list()
        self.assertEquals(list(response), [u'_id'])
        self.assertEquals(len(response), 10)

        # testing get_time_window
        time_range_response = entity_h2o_engine.get_time_window()
        self.assertEquals(time_range_response.keys(), [u'last_date', u'_id', u'first_date'])
        last_date, _id, first_date = [time_range_response[x] for x in list(time_range_response)]

        self.assertEquals(first_date, datetime.datetime(2016, 9, 4, 0, 0, 0))
        self.assertEquals(last_date, datetime.datetime(2017, 5, 3, 0, 0, 0))

        # testing get_clv_in_window
        response = entity_h2o_engine.get_clv_in_window(start_date=first_date, end_date=last_date)
        self.assertEquals(list(response.keys()), [u'_id', u'clv'])
        self.assertEquals(response['_id'].count(), 10)
        self.assertEquals(round(response['clv'].max(), 2), 42.75)
        self.assertEquals(round(response['clv'].mean(), 2), 24.29)
        self.assertEquals(round(response['clv'].min(), 2), 9.57)

        # ha1 = h2o.H2OFrame(python_obj=pd.DataFrame(response))
        # print(response)

        # testing get_rmf_in_window
        response = entity_h2o_engine.get_rmf_in_window(start_date=first_date, end_date=last_date)
        self.assertEquals(list(response.keys()),
                          [u'_id', u'frequency', u'monetary_amount', u'monetary_quantity', u'recency'])
        self.assertEquals(list(response['frequency']), [1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        self.assertEquals([round(x, 2) for x in list(response['monetary_amount'])],
                          [42.75, 12.42, 15.71, 37.86, 36.21, 9.92, 9.57, 21.92, 20.85, 35.65])
        self.assertEquals([round(x, 2) for x in list(response['monetary_quantity'])],
                          [2.0, 1.0, 1.33, 1.56, 0.67, 0.22, 0.89, 0.33, 1.56, 1.56])
        self.assertEquals([round(x, 2) for x in list(response['recency'])],
                          [241.0, 138.0, 108.0, 175.0, 40.0, 21.0, 114.0, 0.0, 50.0, 8.0])

        # ha2 = h2o.H2OFrame(python_obj=pd.DataFrame(response))
        # print(response)

        response = entity_h2o_engine.get_allowance_in_window(start_date=first_date, end_date=last_date)
        self.assertEquals(list(response.keys()), [u'_id', u'std_monetary_amount'])
        self.assertEquals(list(response['std_monetary_amount']), [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        # ha3 = h2o.H2OFrame(python_obj=pd.DataFrame(response))
        # print(response)

        # print(entity_h2o_engine.get_dynamic_rmf_in_window(start_date=first_date, end_date=last_date))

        # from h2o.estimators.random_forest import H2ORandomForestEstimator
        # model = H2ORandomForestEstimator(
        #     model_id="rf_covType_v2",
        #     ntrees=50,
        #     max_depth=30,
        #     col_sample_rate_per_tree=0.95,
        #     stopping_rounds=10,
        #     stopping_tolerance=0.01,
        #     score_each_iteration=True,
        #     seed=3000000)
        # print(h2o.frames())
        # print(len(h2o.frames()['frames']))
        # h2o.remove(ha1)
        # h2o.remove(ha2)
        # h2o.remove(ha3)
        # print(h2o.frames())
        # print(len(h2o.frames()['frames']))
        # h2o.cluster().shutdown()

    # Test take 2 mins (atm) so i am not running this (atm) YOLO
    # def test_big_clv_analysis(self):
    #     print ("--------" + str(datetime.datetime.now()) + "-------------")
    #     print(
    #         self.WARNING + "Following test \"test_big_clv_analysis\" takes a relatively long time, please wait."
    #         + self.ENDC)
    #
    #     with open(self.bigTransactionFilename) as fp:
    #         ret = self.client.post('/entity/create_entity/',
    #                                {'file': fp, 'entity': self.entityJSON1, 'isHeaderIncluded': False})
    #
    #     rid = from_json(ret.content)['entity_id']
    #     self.client.post('/entity/%s/create_entity_mapped/' % rid,
    #                      data=self.entityDataHeaderNoFileHeader, content_type="application/json",
    #                      HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    #
    #     user_group = Group.objects(name="dummy_group").get()
    #     entity_h2o_engine = EntityH2OEngine.init_engine(user_group)
    #     # print("Length of user: " + str(len(entity_h2o_engine.get_user_list())))
    #
    #     # testing get_time_window
    #     time_range_response = EntityH2OEngine.get_time_window()
    #     # self.assertEquals(time_range_response.keys(), [u'last_date', u'_id', u'first_date'])
    #     last_date, _id, first_date = [time_range_response[x] for x in list(time_range_response)]
    #
    #     # self.assertEquals(first_date, datetime.datetime(2016, 9, 4, 0, 0, 0))
    #     # self.assertEquals(last_date, datetime.datetime(2017, 5, 3, 0, 0, 0))
    #
    #     # testing get_clv_in_window
    #     # response = entity_h2o_engine.get_clv_in_window(start_date=first_date, end_date=last_date)
    #     # print(response)
    #     # self.assertEquals(list(response.keys()), [u'_id', u'sum_purchase_amount'])
    #     # self.assertEquals(response['_id'].count(), 23570)
    #     # self.assertEquals(response['sum_purchase_amount'].max(), 13990.93)
    #     # self.assertEquals(response['sum_purchase_amount'].mean(), 106.08042554094187)
    #     # self.assertEquals(response['sum_purchase_amount'].min(), 0.0)
    #
    #     # testing get_rmf_in_window
    #     # response = entity_h2o_engine.get_rmf_in_window(start_date=first_date, end_date=last_date)
    #     # print(response)
    #     # self.assertEquals(list(response.keys()),
    #     #                   [u'_id', u'frequency', u'monetary_amount', u'monetary_quantity', u'recency'])
    #     # self.assertEquals(list(response['frequency']), [1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    #     # self.assertEquals([round(x, 2) for x in list(response['monetary_amount'])],
    #     #                   [12.42, 9.57, 37.86, 9.92, 42.75, 20.85, 36.21, 21.92, 15.71, 35.65])
    #     # self.assertEquals([round(x, 2) for x in list(response['monetary_quantity'])],
    #     #                   [1.00, 0.89, 1.56, 0.22, 2.00, 1.56, 0.67, 0.33, 1.33, 1.56])
    #     # self.assertEquals([round(x, 2) for x in list(response['recency'])],
    #     #                   [138, 114, 175, 21, 241, 50, 40, 0, 108, 8])
    #
    #     response = entity_h2o_engine.get_dynamic_rmf_in_window(start_date=first_date, end_date=last_date)
    #     print(response)
    #     # self.assertEquals(list(response.keys()), [u'_id', u'sum_purchase_amount'])
    #     print ("--------" + str(datetime.datetime.now()) + "-------------")
