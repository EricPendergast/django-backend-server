from __future__ import unicode_literals

from django.test import TestCase
# from django.test import Client
from eledata.core.entity_summary import *
from eledata.core.entity_chart_summary import *
import pandas as pd
from project import settings


class CoreSummaryTestCase(TestCase):
    # TODO: test for service logs, facebook and ga
    core_test__dir = 'misc/test_files/core_test/'
    transaction_filename = core_test__dir + 'Transaction Entity.csv'
    big_transaction_filename = core_test__dir + 'big_transaction.csv'
    customer_filename = core_test__dir + 'Customers.csv'
    conversion_filename = core_test__dir + 'Conversion.csv'
    ga_filename = core_test__dir + 'GA Entity.csv'
    offline_event_filename = core_test__dir + 'Offline_Event_Entity.csv'
    subscription_filename = core_test__dir + 'Subscription Entity.csv'
    people_counter_filename = core_test__dir + 'People Counter Data.csv'

    def test_full_calculate_transaction_data(self):
        header = settings.CONSTANTS['entity']['header_option']['transaction']
        data = pd.read_csv(self.transaction_filename,
                           names=header)
        response = calculate_transaction_data(data)
        self.assertEquals(len(response), 8)
        self.assertEquals(filter(lambda x: x['key'] == 'Transaction Records', response)[0]['value'], 120000)
        self.assertEquals(filter(lambda x: x['key'] == 'Involved User', response)[0]['value'], 29476)
        self.assertEquals(filter(lambda x: x['key'] == 'First Transaction Start Date', response)[0]['value'],
                          '2017-01-01')
        self.assertEquals(filter(lambda x: x['key'] == 'Last Transaction End Date', response)[0]['value'], '2017-06-18')
        self.assertEquals(filter(lambda x: x['key'] == 'Average Transaction Value', response)[0]['value'], '999.42')
        self.assertEquals(filter(lambda x: x['key'] == 'Average Transaction Quantity', response)[0]['value'], '1.5')
        assert data.equals(pd.read_csv(self.transaction_filename, names=header))

    def test_full_calculate_large_transaction_data(self):
        header = [u'User_ID', u'Transaction_Date', u'Transaction_Quantity', u'Transaction_Value']
        data = pd.read_csv(self.big_transaction_filename, names=header)
        response = calculate_transaction_data(data)
        self.assertEquals(len(response), 8)
        assert data.equals(pd.read_csv(self.big_transaction_filename, names=header))

    def test_full_calculate_customer_data(self):
        header = settings.CONSTANTS['entity']['header_option']['customer']
        data = pd.read_csv(self.customer_filename,
                           names=header)
        response = calculate_customer_data(data)
        self.assertEquals(len(response), 7)
        self.assertEquals(filter(lambda x: x['key'] == 'Customer Records', response)[0]['value'], 30000)
        self.assertEquals(filter(lambda x: x['key'] == 'Involved Countries', response)[0]['value'], 30000)
        self.assertEquals(filter(lambda x: x['key'] == 'First Customer Join Date', response)[0]['value'], '2016-12-01')
        self.assertEquals(filter(lambda x: x['key'] == 'Latest Customer Join Date', response)[0]['value'], '2017-02-28')
        self.assertEquals(filter(lambda x: x['key'] == 'Customer Age Range', response)[0]['value'], '18 - 70')
        assert data.equals(pd.read_csv(self.customer_filename, names=header))

    def test_full_calculate_conversion_data(self):
        header = settings.CONSTANTS['entity']['header_option']['conversion']
        data = pd.read_csv(self.conversion_filename,
                           names=header)
        response = calculate_conversion_data(data)

        self.assertEquals(len(response), 8)
        self.assertEquals(filter(lambda x: x['key'] == 'Conversion Records', response)[0]['value'], 20000)
        self.assertEquals(filter(lambda x: x['key'] == 'Involved Campaigns', response)[0]['value'], 2994)
        self.assertEquals(filter(lambda x: x['key'] == 'Involved Users', response)[0]['value'], 16604)
        self.assertEquals(float(filter(lambda x: x['key'] == 'Completed Rate', response)[0]['value']), 0.56)
        self.assertEquals(filter(lambda x: x['key'] == 'First Record Start Date', response)[0]['value'], '2017-04-01')
        self.assertEquals(filter(lambda x: x['key'] == 'Last Record End Date', response)[0]['value'], '2017-08-27')
        assert data.equals(pd.read_csv(self.conversion_filename, names=header))

    # TODO: Update offline event data schema
    def test_full_calculate_offline_event_data(self):
        header = settings.CONSTANTS['entity']['header_option']['offlineEvent']
        data = pd.read_csv(self.offline_event_filename, names=header)
        response = calculate_offline_event_data(data)
        self.assertEquals(len(response), 6)
        self.assertEquals(filter(lambda x: x['key'] == 'Event Record Count', response)[0]['value'], 3000)
        self.assertEquals(filter(lambda x: x['key'] == 'Average Event Period', response)[0]['value'], '84 Days')
        self.assertEquals(filter(lambda x: x['key'] == 'First Event Start Date', response)[0]['value'], '2017-01-01')
        self.assertEquals(filter(lambda x: x['key'] == 'Last Event End Date', response)[0]['value'], '2017-06-18')
        assert data.equals(pd.read_csv(self.offline_event_filename, names=header))

    def test_full_calculate_subscription_data(self):
        header = settings.CONSTANTS['entity']['header_option']['subscription']
        data = pd.read_csv(self.subscription_filename, names=header)
        response = calculate_subscription_data(data)
        self.assertEquals(len(response), 6)
        self.assertEquals(filter(lambda x: x['key'] == 'Total Subscription', response)[0]['value'], 15080)
        self.assertEquals(filter(lambda x: x['key'] == 'Average Subscription per Day', response)[0]['value'], '88.7')
        self.assertEquals(filter(lambda x: x['key'] == 'First Record Start Date', response)[0]['value'], '2017-01-01')
        self.assertEquals(filter(lambda x: x['key'] == 'Last Record End Date', response)[0]['value'], '2017-06-19')
        assert data.equals(pd.read_csv(self.subscription_filename, names=header))

    def test_full_people_counter_data(self):
        header = settings.CONSTANTS['entity']['header_option']['peopleCounterData']
        data = pd.read_csv(self.people_counter_filename, names=header)
        response = calculate_people_counter_data(data)
        self.assertEquals(len(response), 8)
        self.assertEquals(filter(lambda x: x['key'] == 'Total Head Count', response)[0]['value'], 7524093)
        self.assertEquals(filter(lambda x: x['key'] == 'First Record Start Date', response)[0]['value'], '2017-01-12')
        self.assertEquals(filter(lambda x: x['key'] == 'Last Record End Date', response)[0]['value'], '2017-06-19')
        self.assertEquals(filter(lambda x: x['key'] == 'Average Visitor Count per Day', response)[0]['value'],
                          '47321.3')
        self.assertEquals(filter(lambda x: x['key'] == 'Maximum Visitor Count by Day', response)[0]['value'], 52637)
        self.assertEquals(filter(lambda x: x['key'] == 'Maximum Visitor Day', response)[0]['value'], '2017-02-10')
        assert data.equals(pd.read_csv(self.people_counter_filename, names=header))

    def test_full_calculate_transaction_chart_data(self):
        header = settings.CONSTANTS['entity']['header_option']['transaction']
        data = pd.read_csv(self.transaction_filename,
                           names=header)
        response = calculate_transaction_chart_data(data)

        self.assertEquals(response.keys(), ['labels', 'datasets'])
        self.assertEquals([len(x) for x in response.values()], [20, 20])
        assert data.equals(pd.read_csv(self.transaction_filename, names=header))

    def test_full_calculate_customer_chart_data(self):
        header = settings.CONSTANTS['entity']['header_option']['customer']
        data = pd.read_csv(self.customer_filename,
                           names=header)
        response = calculate_customer_chart_data(data)

        self.assertEquals(response.keys(), ['labels', 'datasets'])
        self.assertEquals([len(x) for x in response.values()], [20, 20])
        assert data.equals(pd.read_csv(self.customer_filename, names=header))

    def test_full_calculate_conversion_chart_data(self):
        header = settings.CONSTANTS['entity']['header_option']['conversion']
        data = pd.read_csv(self.conversion_filename,
                           names=header)
        response = calculate_conversion_chart_data(data)

        self.assertEquals(response.keys(), ['labels', 'datasets'])
        self.assertEquals([len(x) for x in response.values()], [13, 13])
        assert data.equals(pd.read_csv(self.conversion_filename, names=header))

    def test_full_calculate_ga_chart_data(self):
        header = settings.CONSTANTS['entity']['header_option']['googleAnalytics']
        data = pd.read_csv(self.ga_filename, names=header)
        response = calculate_ga_chart_data(data)
        self.assertEquals(response.keys(), ['labels', 'datasets'])
        self.assertEquals([len(x) for x in response.values()], [5, 2])
        assert data.equals(pd.read_csv(self.ga_filename, names=header))

    def test_full_calculate_offline_event_chart_data(self):
        header = settings.CONSTANTS['entity']['header_option']['offlineEvent']
        data = pd.read_csv(self.offline_event_filename, names=header)
        response = calculate_offline_event_chart_data(data)

        self.assertEquals(response.keys(), ['labels', 'datasets'])
        self.assertEquals([len(x) for x in response.values()], [3000, 2])
        assert data.equals(pd.read_csv(self.offline_event_filename, names=header))

    def test_full_calculate_subscription_chart_data(self):
        header = settings.CONSTANTS['entity']['header_option']['subscription']
        data = pd.read_csv(self.subscription_filename, names=header)
        response = calculate_subscription_chart_data(data)

        self.assertEquals(response.keys(), ['labels', 'datasets'])
        self.assertEquals([len(x) for x in response.values()], [170, 2])
        assert data.equals(pd.read_csv(self.subscription_filename, names=header))

    def test_full_calculate_people_counter_chart_data(self):
        header = settings.CONSTANTS['entity']['header_option']['peopleCounterData']
        data = pd.read_csv(self.people_counter_filename, names=header)
        response = calculate_people_counter_chart_data(data)

        self.assertEquals(response.keys(), ['labels', 'datasets'])
        self.assertEquals([len(x) for x in response.values()], [159, 2])
        assert data.equals(pd.read_csv(self.people_counter_filename, names=header))
