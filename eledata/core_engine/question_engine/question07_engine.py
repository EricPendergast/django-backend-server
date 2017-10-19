from eledata.core_engine.base_engine import BaseEngine
import pandas as pd
import datetime
from collections import defaultdict


class Question07Engine(BaseEngine):

    transaction_data = None
    customer_data = None
    AGE_BINS = [0, 14, 34, 54, 110]
    AGE_MAPPING = {
        '(0, 14]': '< 15 Years Old',
        '(14, 34]': '15 - 34 Years Old',
        '(34, 54]': '35 - 54 Years Old',
        '(54, 110]': '> 54 Years Old'
    }

    def __init__(self, group, params, transaction_data, customer_data):
        super(Question07Engine, self).__init__(group, params)
        # TODO: verify if question type is missing
        # TODO: verify if data header has been set properly

        self.transaction_data = pd.DataFrame(transaction_data)
        self.customer_data = pd.DataFrame(customer_data)

    def event_init(self):
        """
        EntityStatsEngine Does not init event (For the time beings?)
        :return:
        """
        verifier.verify(1, request_data)
        # The dir that the uploaded data file will be saved to.
        # Appending the original filename to the end so that the new
        # filename has the same extension, while also making the filename
        # more recognizable.
        filename = "temp/" + str(uuid.uuid4()) + "." + str(request_file)

        with open(filename, "w") as fi:
            fi.write(request_file.read())
        # Parsing the entity JSON passed in into a dictionary
        entity_dict = util.from_json(request_data["entity"])

        entity_dict["source"] = {
            "file": {"filename": filename,
                     "is_header_included": request_data["isHeaderIncluded"]}}

        entity_dict['state'] = 1
        verifier.verify(2, entity_dict)

        # TODO: calculate draft of data summary here?
        entity_data = util.file_to_list_of_dictionaries(
            open(entity_dict["source"]["file"]["filename"]),
            numLines=100,
            is_header_included=util.string_caster["bool"](
                entity_dict["source"]["file"]["is_header_included"]))

        serializer = EntityDetailedSerializer(data=entity_dict)
        verifier.verify(3, serializer)

        entity = serializer.create(serializer.validated_data)
        entity.group = group
        entity.save()

        response_data = {
            'entity_id': str(entity.id),
            'data': entity_data,
            'header_option': CONSTANTS.ENTITY.HEADER_OPTION.get(entity_dict["type"].upper())
        }
        # Saving the serializer while also adding its id to the response
        # Loading the first 100 lines of data from the request file
        # Passing header option from constants file

        return response_data

        return

    def get_processed(self, transaction_data, customer_data, params):
        """
        :param data: data
        :param data_type:
        :return: stats_response: dictionary of stats finding
        """
        num_month_observe_list = range(1, 13)
        characteristics = ['Age', 'Gender', 'Country']
        insights = []

        for num_month_observe in num_month_observe_list:
            for characteristic in characteristics:
                rule = Question07Engine.get_rule(params['rule'])
                target_customers = rule(transaction_data, num_month_observe, params['rule_param'])
                target_customers_data = customer_data[customer_data['ID'].isin(target_customers)].copy()

                total_transaction = transaction_data[transaction_data['User_ID'].isin(target_customers)].groupby(['User_ID'])['Transaction_Quantity'].sum().reset_index()
                total_transaction = total_transaction.merge(transaction_data.groupby(['User_ID'])['Transaction_Date'].max().reset_index(), on='User_ID')
                total_transaction = total_transaction.rename(index=str, columns={'Transaction_Quantity': 'Total_Quantity', 'Transaction_Date': 'Last_Transaction_Date'})

                detailed_data = Question07Engine.get_detailed_data(total_transaction, target_customers_data)

                insights.append(
                    {
                        "subHeader": "Customers that stopped buying in the past 6 months",
                        "eventValue": "Total Customers Lost: {0}".format(len(target_customers)),
                        "tab": {
                            "Month": num_month_observe_list,
                            "Characteristics": characteristics
                        },
                        "selected": {
                            "Month": num_month_observe,
                            "Characteristics": characteristic
                        },
                        "eventDesc": Question07Engine.get_event_desc(detailed_data, characteristic),
                        "detailedEventDesc": Question07Engine.get_detailed_event_desc(detailed_data, characteristic),
                        "analysisDesc": Question07Engine.get_analysis_desc(transaction_data, customer_data),
                        "chartType": "bar",
                        "chart": Question07Engine.get_chart(detailed_data, characteristic, num_month_observe, params['rule_param']),
                        "detailedData": detailed_data.to_dict(orient='records')
                    }
                )

        response = {
            "insight": insights
        }

        return response

    def execute(self):
        self.response = self.get_processed(self.transaction_data, self.customer_data, self.params)

    @staticmethod
    def get_start_date(num_month, end_date=datetime.date.today()):
        start_date = end_date.replace(day=1)
        for i in range(num_month):
            start_date = (start_date - datetime.timedelta(days=1)).replace(day=1)
        return start_date

    @staticmethod
    def get_rule(rule):
        mapping = {
            'nosale': Question07Engine.get_nosale_customers,
        }
        return mapping.get(rule)

    @staticmethod
    def get_nosale_customers(transaction_data, num_month_observe, num_month_nosale):
        transaction_startdate = Question07Engine.get_start_date(num_month_observe+num_month_nosale)
        transaction_enddate = Question07Engine.get_start_date(num_month_nosale)

        last_transactions = transaction_data.groupby(['User_ID'])['Transaction_Date'].max().reset_index()
        last_transactions['Transaction_Date'] = pd.to_datetime(last_transactions['Transaction_Date'])

        return last_transactions.loc[(last_transactions['Transaction_Date'] >= transaction_startdate) & (last_transactions['Transaction_Date'] < transaction_enddate), 'User_ID'].astype(str)

    @staticmethod
    def get_detailed_data(total_transaction, target_customers_data):
        return total_transaction.merge(target_customers_data, left_on='User_ID', right_on='ID') \
            [['User_ID', 'Display_Name', 'Age', 'Gender', 'Country', 'Total_Quantity', 'Last_Transaction_Date']]

    @staticmethod
    def get_event_desc(detailed_data, characteristic):
        if characteristic == 'Age':
            stats = detailed_data.groupby(pd.cut(detailed_data[characteristic], Question07Engine.AGE_BINS)).size().reset_index()
            stats[characteristic] = stats[characteristic].astype(str).replace(Question07Engine.AGE_MAPPING)
        else:
            stats = detailed_data.groupby(detailed_data[characteristic]).size().reset_index()
        # bins = range(10, 75, 10) if characteristic == 'Age' else None
        # stats = detailed_data[characteristic].value_counts(bins=bins).reset_index()
        stats = stats.rename(columns={0: 'Count'})

        results = [
            {
                "key": "Total Customers Lost",
                "value": stats['Count'].sum()
            },
            {
                "key": "Report Date",
                "value": (datetime.date.today().replace(day=1) - datetime.timedelta(days=1))
            }
        ]
        for index, row in stats.iterrows():
            results.append({"key": 'Total {0} Customers Lost'.format(row[characteristic]), "value": row['Count']})

        return results

    @staticmethod
    def get_detailed_event_desc(detailed_data, characteristic):
        if characteristic == 'Age':
            stats = detailed_data.groupby(pd.cut(detailed_data[characteristic], Question07Engine.AGE_BINS)).mean()['Total_Quantity'].reset_index()
            stats[characteristic] = stats[characteristic].astype(str).replace(Question07Engine.AGE_MAPPING)
            stats['Total_Quantity'] = stats['Total_Quantity'].fillna(value=0).astype(int)
        else:
            stats = detailed_data.groupby(detailed_data[characteristic]).mean()['Total_Quantity'].reset_index()

        results = [
            {
                "key": 'Average Transaction Quantity per Customer Lost',
                "value": detailed_data['Total_Quantity'].mean(),
                "isFullWIDth": True
            }
        ]
        for index, row in stats.iterrows():
            results.append({"key": 'Average Transaction Quantity per {0} Customers Lost'.format(row[characteristic]), "value": row['Total_Quantity']})

        return results

    @staticmethod
    def get_analysis_desc(transaction_data, customer_data):
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
    def get_chart(detailed_data, characteristic, num_month_observe, num_month_rule):
        labels = []
        start_date = datetime.date.today().replace(day=1)
        chart_stats = []
        for i in range(num_month_observe):
            end_date = start_date
            start_date = (start_date - datetime.timedelta(days=1)).replace(day=1)
            labels.append('{0}-{1}'.format(start_date.year, start_date.month))

            transaction_start_date = start_date
            transaction_end_date = end_date
            for j in range(num_month_rule):
                transaction_start_date = (transaction_start_date - datetime.timedelta(days=1)).replace(day=1)
                transaction_end_date = (transaction_end_date - datetime.timedelta(days=1)).replace(day=1)
            detailed_data['Last_Transaction_Date'] = pd.to_datetime(detailed_data['Last_Transaction_Date'])
            stats = detailed_data[(detailed_data['Last_Transaction_Date'] < transaction_end_date) & (detailed_data['Last_Transaction_Date'] >= transaction_start_date)]
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

        datasets = []
        for record in chart_stats:
            datasets.append(
                {
                    "label": record[0],
                    "data": record[1],
                    "fill": False
                }
            )

        results = {
            "labels": labels,
            "datasets": datasets,
            "xLabel": 'Month',
            "yLabel": 'Number of Improved Customers',
            "xStacked": True,
            "yStacked": True
        }

        return results
