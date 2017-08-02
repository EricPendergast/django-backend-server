from __future__ import unicode_literals

from django.test import TestCase
# from django.test import Client
from eledata.core.entity_summary import *
import pandas as pd


class CoreSummaryTestCase(TestCase):
    core_test__dir = 'misc/test_files/core_test/'
    conversion_filename = core_test__dir + 'Conversion.csv'
    offline_event_filename = core_test__dir + 'Offline_Event_Entity.csv'
    subscription_filename = core_test__dir + 'Subscription Entity.csv'

    def test_full_calculate_conversion_data(self):
        data = pd.read_csv(self.conversion_filename,
                           names=['Campaign_ID', 'Campaign_Name', 'Conversion_ID', 'User_ID', 'Response', 'Start_Date',
                                  'End_Date'])
        response = calculate_conversion_data(data)
        self.assertEquals(len(response), 7)
        self.assertEquals(response['Conversion Records'], 20000)
        self.assertEquals(response['Involved User'], 16604)
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
