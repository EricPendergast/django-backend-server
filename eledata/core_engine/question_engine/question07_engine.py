from eledata.core_engine.base_engine import BaseEngine
from eledata.serializers.event import GeneralEventSerializer
import pandas as pd
import datetime
from eledata.verifiers.event import *
from eledata.models.entity import Entity
from bson import objectid
from project.settings import CONSTANTS


class Question07Engine(BaseEngine):
    responses = None
    transaction_data = None
    customer_data = None
    rule = None
    rule_param = None
    # Constants for age groups
    AGE_BINS = [0, 14, 34, 54, 110]
    AGE_MAPPING = {
        '(0, 14]': '< 15 Years Old',
        '(14, 34]': '15 - 34 Years Old',
        '(34, 54]': '35 - 54 Years Old',
        '(54, 110]': '> 54 Years Old'
    }

    def __init__(self, group, params, transaction_data=None, customer_data=None):
        super(Question07Engine, self).__init__(group, params)
        if params:  # enable empty params for engine checking
            selected_param = filter(lambda x: x['content'] == 'churner_definition', params)[0]
            self.rule = selected_param['choices'][int(selected_param['choice_index'])]['content']
            self.rule_param = selected_param.get('choice_input') if 'choice_input' in selected_param \
                else selected_param['choices'][int(selected_param['choice_index'])].get('default_value')
        # self.transaction_data = pd.DataFrame(transaction_data)
        # self.customer_data = pd.DataFrame(customer_data)
        # self.transaction_data['Transaction_Date'] = pd.to_datetime(self.transaction_data['Transaction_Date'])

    def execute(self):
        transaction = Entity.objects(group=self.group, type='transaction').first()[u'data']
        customer = Entity.objects(group=self.group, type='customer').first()[u'data']

        self.transaction_data = pd.DataFrame(transaction)
        self.customer_data = pd.DataFrame(customer)

        self.responses = self.get_processed(self.transaction_data, self.customer_data, self.params)

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

    def get_processed(self, transaction_data, customer_data, params):
        """
        Main function for processing
        :param transaction_data: DataFrame, transaction records
        :param customer_data: DataFrame, customer records
        :param params: dictionary, user specified parameters for the question
        :return: List of response dictionaries
        """
        num_month_observe_list = range(1, 13)
        characteristics = ['Age', 'Gender', 'Country']
        responses = []

        # Get a list of targeted customers using the user specified rule and param
        get_ids, merge_data = Question07Engine.get_rules(self.rule)
        target_customers = get_ids(transaction_data, self.rule_param)

        event_id = objectid.ObjectId()
        # Generate response to display different number of months of result
        for num_month_observe in num_month_observe_list:
            # Generate 3 type of responses for each number of months
            for characteristic in characteristics:
                observed_target_customers = reduce(lambda x, y: x.append(y), target_customers[:num_month_observe])

                # Get detailed records for each customer from merging the transaction and customer records
                detailed_data = merge_data(transaction_data, customer_data, observed_target_customers)

                # Construct response
                responses.append(
                    {
                        "event_id": event_id,
                        "event_category": CONSTANTS.EVENT.CATEGORY.get("INSIGHT"),
                        "event_type": "question_07",    # Customers that stopped buying in the past 6 months
                        "event_value": {
                            "key": "total_customers_lost",
                            "value": len(observed_target_customers),
                        },
                        "tabs": {
                            "month": map(lambda x: str(x), num_month_observe_list),
                            "characteristics": characteristics
                        },
                        "selected_tab": {
                            "month": str(num_month_observe),
                            "characteristics": characteristic
                        },
                        "event_desc": Question07Engine.get_event_desc(detailed_data, characteristic),
                        "detailed_desc": Question07Engine.get_detailed_event_desc(detailed_data, characteristic),
                        "analysis_desc": Question07Engine.get_analysis_desc(transaction_data, customer_data),
                        "chart_type": "Bar",
                        "chart": Question07Engine.get_chart(detailed_data, characteristic, num_month_observe, target_customers),
                        "detailed_data": Question07Engine.transform_detailed_data(detailed_data)    # Transform detailed data from DF to a list of dict
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
    def get_rules(rule):
        """
        Return the corresponding rule to select target customers as a function ref
        :param rule: string, name of the rule, must match one of the keys in the map
        :return: function ref, used to select target customers
        """
        mapping = {
            'no_sale': [Question07Engine.get_nosale_customers, Question07Engine.merge_nosale_data]
        }
        return mapping.get(rule)

    @staticmethod
    def get_nosale_customers(transaction_data, num_month_nosale):
        """
        Return the user id of the customers that have had no sale for the specified number of months for each observed month,
        in a list with each element representing a month
        e.g. Current month = Oct, num_month_nosale = 5
            The 4th element in the resulting list will be customers lost in June (i.e. customers with no sales in the pass 5 months (Jan - May))
        :param transaction_data: DataFrame, transaction records
        :param num_month_nosale: unicode, the number of months for which there are no sale
        :return: list of series of int, user id of the customers with no sales, with each series representing a month
        """
        num_month_nosale = int(num_month_nosale)

        last_transactions = transaction_data.groupby(['User_ID'])['Transaction_Date'].max().reset_index()

        results = []
        # Get the user IDs for each month
        for month_observe in range(1, 13):
            transaction_startdate = Question07Engine.get_start_date(month_observe + num_month_nosale + 1)
            transaction_enddate = Question07Engine.get_start_date(month_observe + num_month_nosale).replace(day=1)
            results.append(last_transactions.loc[
                (last_transactions['Transaction_Date'] >= transaction_startdate) & (last_transactions['Transaction_Date'] < transaction_enddate), 'User_ID'].astype(str))
        return results

    @staticmethod
    def merge_nosale_data(transaction_data, customer_data, observed_target_customers):
        """
        Merge the transaction and customer records for the supplied customer IDs and return a DataFrame with the relevant columns
        :param transaction_data: DataFrame, transaction records
        :param customer_data: DataFrame, customer records
        :param observed_target_customers: list of int, customer IDs to return
        :return: DataFrame, merged records
        """
        total_transaction = transaction_data[transaction_data['User_ID'].isin(observed_target_customers)].groupby(['User_ID'])['Transaction_Quantity'].sum().reset_index()
        total_transaction = total_transaction.merge(transaction_data.groupby(['User_ID'])['Transaction_Date'].max().reset_index(), on='User_ID')
        total_transaction = total_transaction.rename(index=str, columns={'Transaction_Quantity': 'Total_Quantity', 'Transaction_Date': 'Last_Transaction_Date'})

        target_customers_data = customer_data[customer_data['User_ID'].isin(observed_target_customers)].copy()

        return total_transaction.merge(target_customers_data, left_on='User_ID', right_on='User_ID') \
            [['User_ID', 'Display_Name', 'Age', 'Gender', 'Country', 'Total_Quantity', 'Last_Transaction_Date']]

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
    def get_event_desc(detailed_data, characteristic):
        """
        Group the records by the specified characteristic, return the total count and count for groups in a python structure
        :param detailed_data: DataFrame, targeted customer records, should be output from get_detailed_data
        :param characteristic: string, column to group by
        :return: python structure matching the Event model, with total count and count for each group
        """

        # Age needs to be grouped in bins
        if characteristic == 'Age':
            stats = detailed_data.groupby(pd.cut(detailed_data[characteristic], Question07Engine.AGE_BINS)).size().reset_index()
            stats[characteristic] = stats[characteristic].astype(str).replace(Question07Engine.AGE_MAPPING)
        else:
            stats = detailed_data.groupby(detailed_data[characteristic]).size().reset_index()
        stats = stats.rename(columns={0: 'Count'}).sort_values(['Count'], ascending=False).reset_index(drop=True)

        # Total count
        results = [
            {
                "key": "total_customers_lost",
                "value": stats['Count'].sum(),
                "isFullWidth": True
            }
        ]
        # Count for each group
        for index, row in stats.iterrows():
            results.append({"key": 'tab', "value": '{0}. {1}: {2}'.format(index+1, row[characteristic], row['Count']), "isFullWidth": True})

        return results

    @staticmethod
    def get_detailed_event_desc(detailed_data, characteristic):
        """
        Group the records by the specified characteristic, return the average transaction quantity for overall customers lost and for each group
        :param detailed_data: DataFrame, targeted customer records, should be output from get_detailed_data
        :param characteristic: string, column to group by
        :return: python structure matching the Event model, with overall average transaction quantity per customer lost and for each group
        """

        # Age needs to be grouped in bins
        if characteristic == 'Age':
            stats = detailed_data.groupby(pd.cut(detailed_data[characteristic], Question07Engine.AGE_BINS)).mean()['Total_Quantity'].reset_index()
            stats[characteristic] = stats[characteristic].astype(str).replace(Question07Engine.AGE_MAPPING)
            stats['Total_Quantity'] = stats['Total_Quantity'].fillna(value=0).astype(int)
        else:
            stats = detailed_data.groupby(detailed_data[characteristic]).mean()['Total_Quantity'].reset_index()
        stats = stats.sort_values(['Total_Quantity'], ascending=False).reset_index(drop=True)

        # Overall average
        results = [
            {
                "key": 'average_quantity_per_lost_customers',
                "value": '{0:.2f}'.format(detailed_data['Total_Quantity'].mean()),
                "isFullWidth": True
            }
        ]
        # Average per group
        for index, row in stats.iterrows():
            results.append({"key": 'tab', "value": '{0}. {1}: {2:.2f}'.format(index + 1, row[characteristic], row['Total_Quantity']), "isFullWidth": True})

        return results

    @staticmethod
    def get_analysis_desc(transaction_data, customer_data):
        """
        Return the count of transaction records and customer records in a python structure
        :param transaction_data: DataFrame, transaction records
        :param customer_data: DataFrame, customer records
        :return: python structure matching the Event model, contains the number of transaction and customer records
        """
        results = [
            {
                "key": "involved_dataset_transaction",
                "value": len(transaction_data)
            },
            {
                "key": "involved_dataset_customer",
                "value": len(customer_data)
            }
        ]

        return results

    @staticmethod
    def get_chart(detailed_data, characteristic, num_month_observe, target_customers):
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
        labels = []
        start_date = datetime.date.today().replace(day=1)
        chart_stats = []
        # Add data month by month to the lists
        for i in range(num_month_observe):
            # Construct labels for the X axis
            start_date = (start_date - datetime.timedelta(days=1)).replace(day=1)
            labels.append('{0}-{1}'.format(start_date.year, start_date.month))

            # Get the targeted customer records of the current month
            stats = detailed_data[detailed_data['User_ID'].isin(target_customers[i])]

            # Group and count the customers by the characteristic
            if characteristic == 'Age':
                stats = stats.groupby(pd.cut(stats[characteristic], Question07Engine.AGE_BINS)).size().reset_index()
                stats[characteristic] = stats[characteristic].astype(str).replace(Question07Engine.AGE_MAPPING)
            else:
                stats = stats.groupby(stats[characteristic]).size().reset_index()
                for group in pd.unique(detailed_data[characteristic]):
                    if len(stats[stats[characteristic] == group]) == 0:
                        stats = stats.append({characteristic: group, 0: 0}, ignore_index=True)
                stats = stats.sort_values(characteristic).reset_index()
            for index, row in stats.iterrows():
                if len(chart_stats) < index + 1:
                    chart_stats.append([row[characteristic], [row[0]]])
                else:
                    chart_stats[index][1].append(row[0])

        # Construct data for the chart
        datasets = []
        for record in chart_stats:
            datasets.append(
                {
                    "label": record[0],
                    "data": reversed(record[1]),
                    "fill": False
                }
            )

        # Construct the chart with the data, labels and other meta fields
        results = {
            "labels": reversed(labels),
            "datasets": datasets,
            "x_label": 'month',
            "y_label": 'number_lost_customers',
            "x_stacked": True,
            "y_stacked": True
        }

        return results
