from eledata.core_engine.base_engine import BaseEngine
from eledata.serializers.event import QuestionSerializer, GeneralEventSerializer
import pandas as pd
import datetime
from eledata.verifiers.event import *
from pprint import pprint


class Question08Engine(BaseEngine):
    responses = None
    transaction_data = None
    customer_data = None
    # Constants for age groups
    AGE_BINS = [0, 14, 34, 54, 110]
    AGE_MAPPING = {
        '(0, 14]': '< 15 Years Old',
        '(14, 34]': '15 - 34 Years Old',
        '(34, 54]': '35 - 54 Years Old',
        '(54, 110]': '> 54 Years Old'
    }

    def __init__(self, group, params, transaction_data, customer_data):
        super(Question08Engine, self).__init__(group, params)
        # TODO: Align transaction_data and customer_data with DB schema

        self.transaction_data = pd.DataFrame(transaction_data)
        self.customer_data = pd.DataFrame(customer_data)

    def execute(self):
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
        rule = Question08Engine.get_rule(params['rule'])
        target_customers = rule(transaction_data, params['rule_param'])

        # Generate response to display different number of months of result
        for num_month_observe in num_month_observe_list:
            # Generate 3 type of responses for each number of months
            for characteristic in characteristics:
                observed_target_customers = reduce(lambda x, y: x.append(y), target_customers[:num_month_observe])
                target_customers_data = customer_data[customer_data['ID'].isin(observed_target_customers)].copy()

                # Aggregate transaction records for the targeted customers
                total_transaction = transaction_data[transaction_data['User_ID'].isin(observed_target_customers)].groupby(['User_ID'])['Transaction_Quantity'].sum().reset_index()
                total_transaction = total_transaction.merge(transaction_data.groupby(['User_ID'])['Transaction_Date'].max().reset_index(), on='User_ID')
                total_transaction = total_transaction.rename(index=str, columns={'Transaction_Quantity': 'Total_Quantity', 'Transaction_Date': 'Last_Transaction_Date'})

                # Get detailed records for each customer from merging the transaction and customer records
                detailed_data = Question08Engine.get_detailed_data(total_transaction, target_customers_data)

                # Construct response
                responses.append(
                    {
                        "event_category": "insight",
                        "event_type": "question_08",    # Customers that stopped buying in the past 6 months
                        "event_value": "Total Customers Lost: {0}".format(len(observed_target_customers)),
                        "tabs": {
                            "Month": num_month_observe_list,
                            "Characteristics": characteristics
                        },
                        "selected_tab": {
                            "Month": num_month_observe,
                            "Characteristics": characteristic
                        },
                        "event_desc": Question08Engine.get_event_desc(detailed_data, characteristic),
                        "detailed_desc": Question08Engine.get_detailed_event_desc(detailed_data, characteristic),
                        "analysis_desc": Question08Engine.get_analysis_desc(transaction_data, customer_data),
                        "chart_type": "bar",
                        "chart": Question08Engine.get_chart(detailed_data, characteristic, num_month_observe, target_customers),
                        "detailed_data": Question08Engine.transform_detailed_data(detailed_data)    # Transform detailed data from DF to a list of dict
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
    def get_rule(rule):
        """
        Return the corresponding rule to select target customers as a function ref
        :param rule: string, name of the rule, must match one of the keys in the map
        :return: function ref, used to select target customers
        """
        mapping = {
            'nosale': Question08Engine.get_nosale_customers,
        }
        return mapping.get(rule)

    @staticmethod
    def get_increase_purchase_customers(transaction_data, increase_percentage):
        """
        Return the user id of the customers that have had no sale for the specified number of months for each observed month,
        in a list with each element representing a month
        e.g. Current month = Oct, num_month_nosale = 5
            The 4th element in the resulting list will be customers lost in June (i.e. customers with no sales in the pass 5 months (Jan - May))
        :param transaction_data: DataFrame, transaction records
        :param num_month_observe: int, the number of months of the observed period
        :param num_month_nosale: int, the number of months for which there are no sale
        :return: list of series of int, user id of the customers with no sales, with each series representing a month
        """
        results = []
        # Get the user IDs for each month
        for month_observe in range(1, 13):
            transaction_startdate = Question08Engine.get_start_date(month_observe + 6)
            transaction_enddate = Question08Engine.get_start_date(month_observe).replace(day=1)

            before_transaction = transaction_data[transaction_data['Transaction_Date'] < transaction_startdate].groupby(['User_ID'])['Transaction_Quantity'].sum()
            after_transaction = \
            transaction_data[transaction_data['Transaction_Date'] < transaction_enddate].groupby(['User_ID'])[
                'Transaction_Quantity'].sum()

            results.append(before_transaction[(after_transaction - before_transaction) / before_transaction > 0.05].reset_index().loc[:, 'User_ID'].astype(str))

        return results

    @staticmethod
    def merge_increase_purchase_data(transaction_data, customer_data, observed_target_customers):
        """
        Merge the transaction and customer records for the supplied customer IDs and return a DataFrame with the relevant columns
        :param transaction_data: DataFrame, transaction records
        :param customer_data: DataFrame, customer records
        :param observed_target_customers: list of int, customer IDs to return
        :return: DataFrame, merged records
        """
        total_transaction = \
        transaction_data[transaction_data['User_ID'].isin(observed_target_customers)].groupby(['User_ID'])[
            'Transaction_Quantity'].sum().reset_index()
        total_transaction = total_transaction.merge(
            transaction_data.groupby(['User_ID'])['Transaction_Date'].max().reset_index(), on='User_ID')
        total_transaction = total_transaction.rename(index=str, columns={'Transaction_Quantity': 'Total_Quantity',
                                                                         'Transaction_Date': 'Last_Transaction_Date'})

        target_customers_data = customer_data[customer_data['User_ID'].isin(observed_target_customers)].copy()

        return total_transaction.merge(target_customers_data, left_on='User_ID', right_on='User_ID') \
            [['User_ID', 'Display_Name', 'Age', 'Gender', 'Country', 'Total_Quantity', 'Last_Transaction_Date']]

    @staticmethod
    def get_detailed_data(total_transaction, target_customers_data):
        """
        Merge the transaction and targeted customers records with only the relevant columns
        :param total_transaction:  DataFrame, transaction records that has been aggregated for Total_Quantity and Last_Transaction_Date per customer
        :param target_customers_data: DataFrame, targeted customer records
        :return: DataFrame: merged records with only the relevant columns
        """
        return total_transaction.merge(target_customers_data, left_on='User_ID', right_on='ID') \
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
            stats = detailed_data.groupby(pd.cut(detailed_data[characteristic], Question08Engine.AGE_BINS)).size().reset_index()
            stats[characteristic] = stats[characteristic].astype(str).replace(Question08Engine.AGE_MAPPING)
        else:
            stats = detailed_data.groupby(detailed_data[characteristic]).size().reset_index()
        stats = stats.rename(columns={0: 'Count'})

        # Total count
        results = [
            {
                "key": "Total Customers Lost",
                "value": stats['Count'].sum()
            }
        ]
        # Count for each group
        for index, row in stats.iterrows():
            results.append({"key": 'Total {0} Customers Lost'.format(row[characteristic]), "value": row['Count']})

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
            stats = detailed_data.groupby(pd.cut(detailed_data[characteristic], Question08Engine.AGE_BINS)).mean()['Total_Quantity'].reset_index()
            stats[characteristic] = stats[characteristic].astype(str).replace(Question08Engine.AGE_MAPPING)
            stats['Total_Quantity'] = stats['Total_Quantity'].fillna(value=0).astype(int)
        else:
            stats = detailed_data.groupby(detailed_data[characteristic]).mean()['Total_Quantity'].reset_index()

        # Overall average
        results = [
            {
                "key": 'Average Transaction Quantity per Customer Lost',
                "value": detailed_data['Total_Quantity'].mean(),
                "isFullWIDth": True
            }
        ]
        # Average per group
        for index, row in stats.iterrows():
            results.append({"key": 'Average Transaction Quantity per {0} Customers Lost'.format(row[characteristic]), "value": row['Total_Quantity']})

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
                "key": "Involved Dataset (Transaction)",
                "value": len(transaction_data)
            },
            {
                "key": "Involved Dataset (Customer)",
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
                stats = stats.groupby(pd.cut(stats[characteristic], Question08Engine.AGE_BINS)).size().reset_index()
                stats[characteristic] = stats[characteristic].astype(str).replace(Question08Engine.AGE_MAPPING)
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
                    "data": record[1],
                    "fill": False
                }
            )

        # Construct the chart with the data, labels and other meta fields
        results = {
            "labels": labels,
            "datasets": datasets,
            "x_label": 'Month',
            "y_label": 'Number of Improved Customers',
            "x_stacked": True,
            "y_stacked": True
        }

        return results
