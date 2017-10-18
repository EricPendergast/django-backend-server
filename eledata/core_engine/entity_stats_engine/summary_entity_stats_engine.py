from .entity_stats_engine import EntityStatsEngine
import pandas as pd
import datetime


class SummaryEntityStatsEngine(EntityStatsEngine):

    def get_stats(self, data, data_type):
        mapping = {
            'transaction': self.calculate_transaction_data,
            'customer': self.calculate_customer_data,
            'conversion': self.calculate_conversion_data,
            'offlineEvent': self.calculate_offline_event_data,
            'googleAnalytics': self.calculate_ga_data,
            'serviceLogs': self.calculate_service_logs_data,
            'subscription': self.calculate_subscription_data,
            'peopleCounterData': self.calculate_people_counter_data,
            'myFacebook': self.calculate_my_facebook_data,
            # 'openDataWeather':
            # 'openDataHolidays':
            # 'openDataHumanTraffic':
            # 'competitorFacebook':
        }
        return mapping.get(data_type)(data.copy())

    @staticmethod
    def calculate_transaction_data(data, create_date=None, last_update=None):
        # TODO: Use datetime util dynamic loading reduce complexity, but slower time
        # data['Temp_Transaction_Date'] = pd.to_datetime(data['Transaction_Date'], dayfirst=True)
        data['Temp_Transaction_Date'] = pd.to_datetime(data['Transaction_Date'], format='%d/%m/%Y')

        response = [
            {'key': 'Transaction Records', 'value': len(data.index)},
            {'key': 'Involved User', 'value': len(data.groupby(['User_ID']).count().index)},
            {'key': 'First Transaction Start Date', 'value': data['Temp_Transaction_Date'].min().strftime('%Y-%m-%d')},
            {'key': 'Last Transaction End Date', 'value': data['Temp_Transaction_Date'].max().strftime('%Y-%m-%d')},
            {'key': 'Average Transaction Value', 'value': format(data['Transaction_Value'].mean(), '.2f')},
            {'key': 'Average Transaction Quantity', 'value': format(data['Transaction_Quantity'].mean(), '.1f')},
            {'key': 'Create Date', 'value': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'key': 'Last Update', 'value': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        ]
        del data['Temp_Transaction_Date']
        return response

    @staticmethod
    def calculate_customer_data(data, create_date=None, last_update=None):
        data['Temp_Create_Date'] = pd.to_datetime(data['Create_Date'], format='%d/%m/%Y')

        response = [
            {'key': 'Customer Records', 'value': len(data.index)},
            {'key': 'First Customer Join Date', 'value': data['Temp_Create_Date'].min().strftime('%Y-%m-%d')},
            {'key': 'Latest Customer Join Date', 'value': data['Temp_Create_Date'].max().strftime('%Y-%m-%d')}
        ]
        if 'Country' in data.columns:
            response.append(
                {'key': 'Involved Countries', 'value': len(data.groupby(['Country']).count().index)}
            )
        if 'Age' in data.columns:
            response.append(
                {'key': 'Customer Age Range', 'value': str(data['Age'].min()) + ' - ' + str(data['Age'].max())}
            )
        response += [
            {'key': 'Create Date', 'value': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'key': 'Last Update', 'value': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        ]

        del data['Temp_Create_Date']
        return response

    @staticmethod
    def calculate_conversion_data(data, create_date=None, last_update=None):
        data['Temp_Start_Date'] = pd.to_datetime(data['Start_Date'], format='%d/%m/%Y')
        data['Temp_End_Date'] = pd.to_datetime(data['End_Date'], format='%d/%m/%Y')

        conversion_record = data['Conversion_ID'].count()
        grouped = data.groupby(['User_ID']).count()
        test = data[(data.Response == 'Completed')].count()
        completed_rate = format(float(test['Conversion_ID']) / float(conversion_record), '.2f')

        response = [
            {'key': 'Involved Campaigns', 'value': len(data.groupby(['Campaign_ID']).count().index)},
            {'key': 'Involved Users', 'value': grouped['Campaign_ID'].count()},
            {'key': 'Conversion Records', 'value': conversion_record},
            {'key': 'Completed Rate', 'value': completed_rate},
            {'key': 'First Record Start Date', 'value': data['Temp_Start_Date'].min().strftime('%Y-%m-%d')},
            {'key': 'Last Record End Date', 'value': data['Temp_End_Date'].max().strftime('%Y-%m-%d')},
            {'key': 'Create Date', 'value': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'key': 'Last Update', 'value': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        ]
        del data['Temp_Start_Date']
        del data['Temp_End_Date']
        return response

    @staticmethod
    def calculate_offline_event_data(data, create_date=None, last_update=None):
        data['Temp_Start_Date'] = pd.to_datetime(data['Start_Date'], format='%d/%m/%Y')
        data['Temp_End_Date'] = pd.to_datetime(data['End_Date'], format='%d/%m/%Y')
        data['Event_Period'] = data['Temp_End_Date'].sub(data['Temp_Start_Date'], axis=0)

        response = [
            {'key': 'Event Record Count', 'value': data['Event_ID'].count()},
            {'key': 'First Event Start Date', 'value': data['Temp_Start_Date'].min().strftime('%Y-%m-%d')},
            {'key': 'Last Event End Date', 'value': data['Temp_End_Date'].max().strftime('%Y-%m-%d')},
            {'key': 'Average Event Period', 'value': str(data['Event_Period'].mean().days) + ' Days'},
            {'key': 'Create Date', 'value': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'key': 'Last Update', 'value': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        ]
        del data['Event_Period']
        del data['Temp_Start_Date']
        del data['Temp_End_Date']
        return response

    @staticmethod
    def calculate_subscription_data(data, create_date=None, last_update=None):
        data['Temp_Timestamp'] = pd.to_datetime(data['Timestamp'], format='%d/%m/%Y %H:%M')
        data['Temp_Date'] = data['Temp_Timestamp'].dt.date

        grouped = data[(data.Action == 'Subscribe')].count()
        grouped_by_day = data.groupby(['Temp_Date', 'Action']).count().reset_index()

        response = [
            {'key': 'Total Subscription', 'value': grouped['Subscription']},
            {'key': 'Average Subscription per Day', 'value': format(
                grouped_by_day.loc[grouped_by_day['Action'] == 'Subscribe', 'Subscription'].mean(), '.1f')},
            {'key': 'First Record Start Date', 'value': data['Temp_Timestamp'].min().strftime('%Y-%m-%d')},
            {'key': 'Last Record End Date', 'value': data['Temp_Timestamp'].max().strftime('%Y-%m-%d')},
            {'key': 'Create Date', 'value': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'key': 'Last Update', 'value': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        ]
        del data['Temp_Timestamp']
        del data['Temp_Date']
        return response

    @staticmethod
    def calculate_people_counter_data(data, create_date=None, last_update=None):
        data['Temp_Timestamp'] = pd.to_datetime(data['Timestamp'], format='%d/%m/%Y %H:%M:%S')
        data['Temp_Date'] = data['Temp_Timestamp'].dt.date

        grouped = data.groupby(['Temp_Date']).sum()
        average_visitor_counter_day = grouped['Number_People_In'].mean()

        response = [
            {'key': 'Total Head Count', 'value': data['Number_People_In'].sum()},
            {'key': 'First Record Start Date', 'value': data['Temp_Date'].min().strftime('%Y-%m-%d')},
            {'key': 'Last Record End Date', 'value': data['Temp_Date'].max().strftime('%Y-%m-%d')},
            {'key': 'Average Visitor Count per Day', 'value': format(average_visitor_counter_day, '.1f')},
            {'key': 'Maximum Visitor Count by Day', 'value': grouped['Number_People_In'].max()},
            {'key': 'Maximum Visitor Day',
             'value': grouped.sort_values('Number_People_In', ascending=0).index[0].strftime('%Y-%m-%d')},
            {'key': 'Create Date', 'value': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'key': 'Last Update', 'value': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        ]
        del data['Temp_Timestamp']
        del data['Temp_Date']
        return response

    @staticmethod
    def calculate_service_logs_data(data, create_date=None, last_update=None):
        data['Temp_Timestamp'] = pd.to_datetime(data['Timestamp'], format='%d/%m/%Y')

        response = [
            {'key': 'Total Record', 'value': data['Transaction ID'].count()},
            {'key': 'First Record Start Date', 'value': data['Temp_Timestamp'].min()},
            {'key': 'Last Record End Date', 'value': data['Temp_Timestamp'].max()},
            {'key': 'Create Date', 'value': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'key': 'Last Update', 'value': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        ]
        del data['Temp_Timestamp']
        return response

    @staticmethod
    def calculate_my_facebook_data(data, create_date=None, last_update=None):
        return [
            {'key': 'TotalViews', 'value': data['Views'].max()},
            {'key': 'TotalLikes', 'value': data['Likes'].max()},
            {'key': 'TotalFollowers', 'value': data['Followers'].max()},
            {'key': 'First Record Start Date', 'value': data['Timestamp'].min()},
            {'key': 'Last Record End Date', 'value': data['Timestamp'].max()},
            {'key': 'Create Date', 'value': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'key': 'Last Update', 'value': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        ]

    @staticmethod
    def calculate_ga_data(data, create_date=None, last_update=None):
        grouped = data[(data.TypeofVisitor == 'Returning  visitor')].count()
        return [
            {'key': 'Total Visitor', 'value': data['Users City'].count()},
            {'key': 'Returning Visitor', 'value': grouped['TypeofVisitor'].count()},
            {'key': 'Create Date', 'value': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'key': 'Last Update', 'value': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        ]
