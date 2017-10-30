from eledata.core_engine.base_engine import BaseEngine
from eledata.serializers.event import GeneralEventSerializer
import pandas as pd
import datetime
from eledata.verifiers.event import *
from eledata.models.entity import Entity
from bson import objectid
from project.settings import CONSTANTS
import numpy as np
from collections import defaultdict

class Question12Engine(BaseEngine):
    responses = None
    transaction_data, customer_data, campaign_data, conversion_data, channel_data = (None,) * 5
    NUMBER_MAPPING = {
        1: 'one',
        2: 'two',
        3: 'three',
        4: 'four',
        5: 'five',
        6: 'six'
    }

    def __init__(self, event_id, group, params, transaction_data=None, customer_data=None, campaign_data=None, conversion_data=None, channel_data=None):
        super(Question12Engine, self).__init__(event_id, group, params)

        self.transaction_data = pd.DataFrame(transaction_data)
        self.customer_data = pd.DataFrame(customer_data)
        # self.transaction_data['Transaction_Date'] = pd.to_datetime(self.transaction_data['Transaction_Date'])
        self.campaign_data = campaign_data
        self.conversion_data = conversion_data
        self.channel_data = channel_data

    def execute(self):
        # transaction = Entity.objects(group=self.group, type='transaction').first()[u'data']
        # customer = Entity.objects(group=self.group, type='customer').first()[u'data']
        #
        # self.transaction_data = pd.DataFrame(transaction)
        # self.customer_data = pd.DataFrame(customer)

        self.responses = self.get_processed(self.transaction_data, self.customer_data, self.campaign_data, self.conversion_data, self.channel_data)

    def event_init(self):
        """
        Simple validations on the data structure
        Saves response from each event one by one
        :return: None
        """
        for response in self.responses:
            verifier = QuestionVerifier()
            serializer = GeneralEventSerializer(data=response)
            verifier.verify(0, self.group)
            verifier.verify(1, serializer)
            # pprint(serializer.validated_data)
            entity = serializer.create(serializer.validated_data)

            entity.group = self.group
            entity.save()

        return None

    def get_processed(self, transaction_data, customer_data, campaign_data, conversion_data, channel_data):
        """
        Main function for processing
        :param transaction_data: DataFrame, transaction records
        :param customer_data: DataFrame, customer records
        :param params: dictionary, user specified parameters for the question
        :return: List of response dictionaries
        """
        event_id = objectid.ObjectId()
        num_month_observe_list = range(1, 13)
        dimensions = ['Impressions', 'Clicks', 'Spending']
        responses = []

        # Generate response to display different number of months of result
        for num_month_observe in num_month_observe_list:
            # print campaign_data.head()
            observed_campaigns = campaign_data[
                (campaign_data['Start_Date'] >= Question12Engine.get_start_date(num_month_observe))
                & (campaign_data['End_Date'] < Question12Engine.get_start_date(0))].copy()

            # Get detailed records for each customer from merging the transaction and customer records
            detailed_data = observed_campaigns.groupby(['Channel_ID']).mean()[['Impressions', 'Clicks', 'Spending']].reset_index()
            converted_conversion = conversion_data.copy()
            converted_conversion['Transaction_ID'] = conversion_data.loc[conversion_data['Transaction_ID'] != 'None', 'Transaction_ID'].astype(int)
            first_transactions = transaction_data.groupby(['User_ID'])['Transaction_ID'].min().reset_index()
            observed_conversions = observed_campaigns.merge(
                converted_conversion, on=['Campaign_ID']
            ).merge(
                transaction_data, on=['User_ID', 'Transaction_ID']
            ).merge(
                first_transactions, on=['User_ID', 'Transaction_ID']
            )

            campaign_details = campaign_data.merge(
                observed_conversions.groupby(['Campaign_ID'])['Start_Date'].count().reset_index().rename(index=str, columns={'Start_Date': 'First_Sale_Count'}),
                on=['Campaign_ID']
            ).merge(
                channel_data[['Channel_ID', 'Channel_Name']],
                on=['Channel_ID']
            )

            # first_sale_conversions = (observed_conversions - first_transactions).dropna().reset_index()
            first_sale_count = observed_conversions.groupby(['Channel_ID'])['User_ID'].count().reset_index().rename(index=str, columns={'User_ID': 'First_Sale_Count'})
            detailed_data = detailed_data.merge(first_sale_count, on=['Channel_ID']).merge(channel_data[['Channel_ID', 'Channel_Name']], on=['Channel_ID']).sort_values(['First_Sale_Count']).reset_index(drop=True)

            for dimension in dimensions:
                detailed_data['Ratio'] = detailed_data[dimension] / detailed_data['First_Sale_Count']
                # Construct response
                responses.append(
                    {
                        "event_id": event_id,
                        "event_category": CONSTANTS.EVENT.CATEGORY.get("INSIGHT"),
                        "event_type": "question_12",  # Customers that stopped buying in the past 6 months
                        "event_value": {
                            "key": "channel_highest_first_conversion",
                            "value": detailed_data.loc[0, 'Channel_Name'],
                        },
                        "tabs": {
                            "month": map(lambda x: str(x), num_month_observe_list),
                            "dimension": dimensions
                        },
                        "selected_tab": {
                            "month": str(num_month_observe),
                            "dimension": dimension
                        },
                        "event_desc": Question12Engine.get_event_desc(detailed_data),
                        "detailed_desc": Question12Engine.get_detailed_event_desc(detailed_data, dimension),
                        "analysis_desc": Question12Engine.get_analysis_desc(transaction=transaction_data, customer=customer_data, campaign=campaign_data, conversion=conversion_data, channel=channel_data),
                        "chart_type": "bubble",
                        "chart": Question12Engine.get_chart(campaign_details, dimension),
                        "detailed_data": Question12Engine.transform_detailed_data(campaign_details)  # Transform detailed data from DF to a list of dict
                    }
                )




        return responses

    @staticmethod
    def get_start_date(num_month, end_date=datetime.date.today()):
        """
        Move the date back for the specified number of months (day set to the start of the month)
        e.g. num_month = 5, end_date = 2017-12-20 return start_date = 2017-07-01
        :param num_month: int, number of months to move
        :param end_date: datetime.date, date to move, default to the current date
        :return: datetime.date, end_date moved back by num_month
        """
        start_date = end_date.replace(day=1)
        # Has to be done in a loop and not just using timedelta because each month has different number of days and we could end up in the wrong month
        for i in range(num_month):
            start_date = (start_date - datetime.timedelta(days=1)).replace(day=1)
        return start_date

    @staticmethod
    def transform_detailed_data(detailed_data):
        """
        Transform the supplied DF to a python structure with fields matching the Event model
        :param detailed_data: DataFrame, targeted customer records, should be output from get_detailed_data
        :return: python structure matching the Event model, contains detailed data
        """
        results = {"data": detailed_data.to_dict(orient='records'), "columns": []}
        for field in results['data'][0].keys():
            results["columns"].append(
                {
                    "key": field,
                    "sortable": True,
                    "label": field.replace('_', ' ')
                }
            )
        return results

    @staticmethod
    def get_event_desc(detailed_data):
        """
        Group the records by the specified characteristic, return the total count and count for groups in a python structure
        :param detailed_data: DataFrame, targeted customer records, should be output from get_detailed_data
        :param characteristic: string, column to group by
        :return: python structure matching the Event model, with total count and count for each group
        """

        # Total count
        total_count = detailed_data['First_Sale_Count'].sum()
        results = [
            {
                "key": "total_converted_first_sale",
                "value": total_count,
                "isFullWidth": True
            }
        ]
        # Count for each group
        for index, row in detailed_data.sort_values(['First_Sale_Count'], ascending=False).reset_index(drop=True).iterrows():
            results.append({"key": '{0}'.format(Question12Engine.NUMBER_MAPPING[index+1]), "value": '{0}: {1} ({2:.2f}%)'.format(row['Channel_Name'], row['First_Sale_Count'], row['First_Sale_Count'] * 100 / total_count), "isFullWidth": True})

        return results

    @staticmethod
    def get_detailed_event_desc(detailed_data, dimension):
        """
        Group the records by the specified characteristic, return the average transaction quantity for overall customers lost and for each group
        :param detailed_data: DataFrame, targeted customer records, should be output from get_detailed_data
        :param characteristic: string, column to group by
        :return: python structure matching the Event model, with overall average transaction quantity per customer lost and for each group
        """

        # Overall average
        results = [
            {
                "key": 'average_{0}_per_first_sale'.format(dimension.lower()),
                "value": '{0:.2f}'.format(detailed_data[dimension].sum() / detailed_data['First_Sale_Count'].sum()),
                "isFullWidth": True
            }
        ]
        # Average per group
        for index, row in detailed_data.sort_values(['Ratio'], ascending=False).reset_index(drop=True).iterrows():
            results.append({"key": '{0}'.format(Question12Engine.NUMBER_MAPPING[index+1]), "value": '{0}: {1:.2f}'.format(row['Channel_Name'], row['Ratio']), "isFullWidth": True})

        return results

    @staticmethod
    def get_analysis_desc(**kwargs):
        """
        Return the count of transaction records and customer records in a python structure
        :param transaction_data: DataFrame, transaction records
        :param customer_data: DataFrame, customer records
        :return: python structure matching the Event model, contains the number of transaction and customer records
        """
        results = []
        for k, v in kwargs.iteritems():
            results.append(
                {
                    "key": 'involved_dataset_{0}'.format(k),
                    "value": len(v)
                }
            )

        return results

    @staticmethod
    def get_chart(campaign_details, dimension):
        """
        Calculate the number of lost customers each month, used for the chart portion in the response, return in python structure
        :param detailed_data: DataFrame, targeted customer records, should be output from get_detailed_data
        :param characteristic: string, column to group by
        :param num_month_observe: number of months of results to include in the chart
        :param target_customers: targeted customer IDs returned by the specified rule
        :return: python structure matching the Event model, contains chart portion of the response
        """
        # TODO: make this function reusable
        # TODO: ordering issue still exist
        chart_stats = defaultdict(list)
        # Add data month by month to the lists
        for index, row in campaign_details.iterrows():
            chart_stats[row['Channel_Name']].append(
                {
                    'x': row[dimension],
                    'y': row['First_Sale_Count'],
                    'r': 1
                }
            )

        # Construct data for the chart
        datasets = []
        for channel in chart_stats:
            datasets.append(
                {
                    "label": channel,
                    "data": chart_stats[channel]
                }
            )

        # Construct the chart with the data, labels and other meta fields
        results = {
            "labels": chart_stats.keys(),
            "datasets": datasets,
            "x_label": dimension.lower(),
            "y_label": 'number_first_sale'
        }

        return results
