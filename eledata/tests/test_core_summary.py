from __future__ import unicode_literals
import pandas as pd
from project.settings import CONSTANTS
from django.test import TestCase
from eledata.core_engine.entity_stats_engine.chart_entity_stats_engine import ChartEntityStatsEngine
from eledata.core_engine.entity_stats_engine.summary_entity_stats_engine import SummaryEntityStatsEngine


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
        header = CONSTANTS.ENTITY.HEADER_OPTION.get('TRANSACTION')
        data = pd.read_csv(self.transaction_filename,
                           names=header)
        response = SummaryEntityStatsEngine.calculate_transaction_data(data)
        self.assertEquals(len(response), 8)
        self.assertEquals(filter(lambda x: x['key'] == 'transactionRecords', response)[0]['value'], 120000)
        self.assertEquals(filter(lambda x: x['key'] == 'involvedUser', response)[0]['value'], 29476)
        self.assertEquals(filter(lambda x: x['key'] == 'firstTransactionStartDate', response)[0]['value'],
                          '2017-01-01')
        self.assertEquals(filter(lambda x: x['key'] == 'lastTransactionEndDate', response)[0]['value'], '2017-06-18')
        self.assertEquals(filter(lambda x: x['key'] == 'averageTransactionValue', response)[0]['value'], '999.42')
        self.assertEquals(filter(lambda x: x['key'] == 'averageTransactionQuantity', response)[0]['value'], '1.5')
        assert data.equals(pd.read_csv(self.transaction_filename, names=header))

    def test_full_calculate_large_transaction_data(self):
        header = [u'User_ID', u'Transaction_Date', u'Transaction_Quantity', u'Transaction_Value']
        data = pd.read_csv(self.big_transaction_filename, names=header)
        response = SummaryEntityStatsEngine.calculate_transaction_data(data)
        self.assertEquals(len(response), 8)
        assert data.equals(pd.read_csv(self.big_transaction_filename, names=header))

    def test_full_calculate_customer_data(self):
        header = CONSTANTS.ENTITY.HEADER_OPTION.get('CUSTOMER')
        data = pd.read_csv(self.customer_filename,
                           names=header)
        response = SummaryEntityStatsEngine.calculate_customer_data(data)
        self.assertEquals(len(response), 7)
        self.assertEquals(filter(lambda x: x['key'] == 'customerRecords', response)[0]['value'], 30000)
        self.assertEquals(filter(lambda x: x['key'] == 'involvedCountries', response)[0]['value'], 30000)
        self.assertEquals(filter(lambda x: x['key'] == 'firstCustomerJoinDate', response)[0]['value'], '2016-12-01')
        self.assertEquals(filter(lambda x: x['key'] == 'latestCustomerJoinDate', response)[0]['value'], '2017-02-28')
        self.assertEquals(filter(lambda x: x['key'] == 'customerAgeRange', response)[0]['value'], '18 - 70')
        assert data.equals(pd.read_csv(self.customer_filename, names=header))

    def test_full_calculate_conversion_data(self):
        header = CONSTANTS.ENTITY.HEADER_OPTION.get('CONVERSION')
        data = pd.read_csv(self.conversion_filename,
                           names=header)
        response = SummaryEntityStatsEngine.calculate_conversion_data(data)

        self.assertEquals(len(response), 8)
        self.assertEquals(filter(lambda x: x['key'] == 'conversionRecords', response)[0]['value'], 20000)
        self.assertEquals(filter(lambda x: x['key'] == 'involvedCampaigns', response)[0]['value'], 2994)
        self.assertEquals(filter(lambda x: x['key'] == 'involvedUsers', response)[0]['value'], 16604)
        self.assertEquals(float(filter(lambda x: x['key'] == 'completedRate', response)[0]['value']), 0.56)
        self.assertEquals(filter(lambda x: x['key'] == 'firstRecordStartDate', response)[0]['value'], '2017-04-01')
        self.assertEquals(filter(lambda x: x['key'] == 'lastRecordEndDate', response)[0]['value'], '2017-08-27')
        assert data.equals(pd.read_csv(self.conversion_filename, names=header))

    # TODO: Update offline event data schema
    def test_full_calculate_offline_event_data(self):
        header = CONSTANTS.ENTITY.HEADER_OPTION.get('OFFLINE_EVENT')
        data = pd.read_csv(self.offline_event_filename, names=header)
        response = SummaryEntityStatsEngine.calculate_offline_event_data(data)
        self.assertEquals(len(response), 6)
        self.assertEquals(filter(lambda x: x['key'] == 'eventRecordCount', response)[0]['value'], 3000)
        self.assertEquals(filter(lambda x: x['key'] == 'averageEventPeriod', response)[0]['value'], '84 Days')
        self.assertEquals(filter(lambda x: x['key'] == 'firstEventStartDate', response)[0]['value'], '2017-01-01')
        self.assertEquals(filter(lambda x: x['key'] == 'lastEventEndDate', response)[0]['value'], '2017-06-18')
        assert data.equals(pd.read_csv(self.offline_event_filename, names=header))

    def test_full_calculate_subscription_data(self):
        header = CONSTANTS.ENTITY.HEADER_OPTION.get('SUBSCRIPTION')
        data = pd.read_csv(self.subscription_filename, names=header)
        response = SummaryEntityStatsEngine.calculate_subscription_data(data)
        self.assertEquals(len(response), 6)
        self.assertEquals(filter(lambda x: x['key'] == 'totalSubscription', response)[0]['value'], 15080)
        self.assertEquals(filter(lambda x: x['key'] == 'averageSubscriptionPerDay', response)[0]['value'], '88.7')
        self.assertEquals(filter(lambda x: x['key'] == 'firstRecordStartDate', response)[0]['value'], '2017-01-01')
        self.assertEquals(filter(lambda x: x['key'] == 'lastRecordEndDate', response)[0]['value'], '2017-06-19')
        assert data.equals(pd.read_csv(self.subscription_filename, names=header))

    def test_full_people_counter_data(self):
        header = CONSTANTS.ENTITY.HEADER_OPTION.get('PEOPLE_COUNTER_DATA')
        data = pd.read_csv(self.people_counter_filename, names=header)
        response = SummaryEntityStatsEngine.calculate_people_counter_data(data)
        self.assertEquals(len(response), 8)
        self.assertEquals(filter(lambda x: x['key'] == 'totalHeadCount', response)[0]['value'], 7524093)
        self.assertEquals(filter(lambda x: x['key'] == 'firstRecordStartDate', response)[0]['value'], '2017-01-12')
        self.assertEquals(filter(lambda x: x['key'] == 'lastRecordEndDate', response)[0]['value'], '2017-06-19')
        self.assertEquals(filter(lambda x: x['key'] == 'averageVisitorCountPerDay', response)[0]['value'],
                          '47321.3')
        self.assertEquals(filter(lambda x: x['key'] == 'maximumVisitorCountByDay', response)[0]['value'], 52637)
        self.assertEquals(filter(lambda x: x['key'] == 'maximumVisitorDay', response)[0]['value'], '2017-02-10')
        assert data.equals(pd.read_csv(self.people_counter_filename, names=header))

    def test_full_calculate_transaction_chart_data(self):
        header = CONSTANTS.ENTITY.HEADER_OPTION.get("TRANSACTION")
        data = pd.read_csv(self.transaction_filename,
                           names=header)
        response = ChartEntityStatsEngine.calculate_transaction_chart_data(data)

        self.assertEquals(response.keys(), ['labels', 'datasets'])
        self.assertEquals([len(x) for x in response.values()], [20, 1])
        assert data.equals(pd.read_csv(self.transaction_filename, names=header))

    def test_full_calculate_customer_chart_data(self):
        header = CONSTANTS.ENTITY.HEADER_OPTION.get('CUSTOMER')
        data = pd.read_csv(self.customer_filename,
                           names=header)
        response = ChartEntityStatsEngine.calculate_customer_chart_data(data)

        self.assertEquals(response.keys(), ['labels', 'datasets'])
        self.assertEquals([len(x) for x in response.values()], [20, 1])
        assert data.equals(pd.read_csv(self.customer_filename, names=header))

    def test_full_calculate_conversion_chart_data(self):
        header = CONSTANTS.ENTITY.HEADER_OPTION.get('CONVERSION')
        data = pd.read_csv(self.conversion_filename,
                           names=header)
        response = ChartEntityStatsEngine.calculate_conversion_chart_data(data)

        self.assertEquals(response.keys(), ['labels', 'datasets'])
        self.assertEquals([len(x) for x in response.values()], [13, 1])
        assert data.equals(pd.read_csv(self.conversion_filename, names=header))

    def test_full_calculate_ga_chart_data(self):
        header = CONSTANTS.ENTITY.HEADER_OPTION.get('GOOGLE_ANALYTICS')
        data = pd.read_csv(self.ga_filename, names=header)
        response = ChartEntityStatsEngine.calculate_ga_chart_data(data)
        self.assertEquals(response.keys(), ['labels', 'datasets'])
        self.assertEquals([len(x) for x in response.values()], [5, 2])
        assert data.equals(pd.read_csv(self.ga_filename, names=header))

    def test_full_calculate_offline_event_chart_data(self):
        header = CONSTANTS.ENTITY.HEADER_OPTION.get('OFFLINE_EVENT')
        data = pd.read_csv(self.offline_event_filename, names=header)
        response = ChartEntityStatsEngine.calculate_offline_event_chart_data(data)

        self.assertEquals(response.keys(), ['labels', 'datasets'])
        self.assertEquals([len(x) for x in response.values()], [3000, 2])
        assert data.equals(pd.read_csv(self.offline_event_filename, names=header))

    def test_full_calculate_subscription_chart_data(self):
        header = CONSTANTS.ENTITY.HEADER_OPTION.get('SUBSCRIPTION')
        data = pd.read_csv(self.subscription_filename, names=header)
        response = ChartEntityStatsEngine.calculate_subscription_chart_data(data)

        self.assertEquals(response.keys(), ['labels', 'datasets'])
        self.assertEquals([len(x) for x in response.values()], [170, 2])
        assert data.equals(pd.read_csv(self.subscription_filename, names=header))

    def test_full_calculate_people_counter_chart_data(self):
        header = CONSTANTS.ENTITY.HEADER_OPTION['PEOPLE_COUNTER_DATA']
        data = pd.read_csv(self.people_counter_filename, names=header)
        response = ChartEntityStatsEngine.calculate_people_counter_chart_data(data)

        self.assertEquals(response.keys(), ['labels', 'datasets'])
        self.assertEquals([len(x) for x in response.values()], [159, 2])
        assert data.equals(pd.read_csv(self.people_counter_filename, names=header))
