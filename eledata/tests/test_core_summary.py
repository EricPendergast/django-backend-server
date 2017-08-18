from __future__ import unicode_literals

from django.test import TestCase
# from django.test import Client
from project import settings
from eledata.core.entity_summary import *
import pandas as pd


class CoreSummaryTestCase(TestCase):
    # TODO: test for service logs, facebook and ga
    core_test__dir = 'misc/test_files/core_test/'
    transaction_filename = core_test__dir + 'Transaction Entity.csv'
    customer_filename = core_test__dir + 'Customer Entity.csv'
    conversion_filename = core_test__dir + 'Conversion.csv'
    offline_event_filename = core_test__dir + 'Offline_Event_Entity.csv'
    subscription_filename = core_test__dir + 'Subscription Entity.csv'
    people_counter_filename = core_test__dir + 'People Counter Data.csv'

    def test_full_calculate_transaction_data(self):
        data = pd.read_csv(self.transaction_filename,
                           names=settings.CONSTANTS['entity']['header_option']['transaction'])
        response = calculate_transaction_data(data)
        self.assertEquals(len(response), 8)
        self.assertEquals(response['Transaction Records'], 120000)
        self.assertEquals(response['Involved User'], 29476)
        self.assertEquals(response['First Transaction Start Date'], '2017-01-01')
        self.assertEquals(response['Last Transaction End Date'], '2017-06-18')
        self.assertEquals(response['Average Transaction Value'], '999.42')
        self.assertEquals(response['Average Transaction Quantity'], '1.5')

    def test_full_calculate_customer_data(self):
        data = pd.read_csv(self.customer_filename,
                           names=settings.CONSTANTS['entity']['header_option']['customer'])
        response = calculate_customer_data(data)
        self.assertEquals(len(response), 7)
        self.assertEquals(response['Customer Records'], 30000)
        self.assertEquals(response['Involved Countries'], 150)
        self.assertEquals(response['First Customer Join Date'], '2017-01-13')
        self.assertEquals(response['Latest Customer Join Date'], '2017-06-19')
        self.assertEquals(response['Customer Age Range'], '18 - 80')

    def test_full_calculate_conversion_data(self):
        data = pd.read_csv(self.conversion_filename,
                           names=['Campaign_ID', 'Campaign_Name', 'Conversion_ID', 'User_ID', 'Response', 'Start_Date',
                                  'End_Date'])
        response = calculate_conversion_data(data)

        self.assertEquals(len(response), 8)
        self.assertEquals(response['Conversion Records'], 20000)
        self.assertEquals(response['Involved Campaigns'], 2994)
        self.assertEquals(response['Involved Users'], 16604)
        self.assertEquals(float(response['Completed Rate']), 0.56)
        self.assertEquals(response['First Record Start Date'], '2017-04-01')
        self.assertEquals(response['Last Record End Date'], '2017-08-27')

    def test_full_calculate_offline_event_data(self):
        data = pd.read_csv(self.offline_event_filename, names=['No.', 'Type of Event', 'Start Date', 'End Date'])
        response = calculate_offline_event_data(data)
        self.assertEquals(len(response), 6)
        self.assertEquals(response['Event Record Count'], 3000)
        self.assertEquals(response['Average Event Period'], '84 Days')
        self.assertEquals(response['First Event Start Date'], '2017-01-01')
        self.assertEquals(response['Last Event End Date'], '2017-06-18')

    def test_full_calculate_subscription_data(self):
        data = pd.read_csv(self.subscription_filename, names=['Name', 'Timestamp', 'Subscription', 'Action'])
        response = calculate_subscription_data(data)
        self.assertEquals(len(response), 6)
        self.assertEquals(response['Total Subscription'], 15080)
        self.assertEquals(response['Average Subscription per Day'], '88.7')
        self.assertEquals(response['First Record Start Date'], '2017-01-01')
        self.assertEquals(response['Last Record End Date'], '2017-06-19')

    def test_full_people_counter_data(self):
        data = pd.read_csv(self.people_counter_filename, names=['Timestamp', 'PeopleInflow', 'PeopleOutflow'])
        response = calculate_people_counter_data(data)
        self.assertEquals(len(response), 8)
        self.assertEquals(response['Total Head Count'], 7524093)
        self.assertEquals(response['First Record Start Date'], '2017-01-12')
        self.assertEquals(response['Last Record End Date'], '2017-06-19')
        self.assertEquals(response['Average Visitor Count per Day'], '47321.3')
        self.assertEquals(response['Maximum Visitor Count by Day'], 52637)
        self.assertEquals(response['Maximum Visitor Day'], '2017-02-10')
