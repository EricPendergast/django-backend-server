from .entity_stats_engine import EntityStatsEngine
import pandas as pd
import datetime


class ChartEntityStatsEngine(EntityStatsEngine):

    def get_stats(self, data, data_type):
        mapping = {
            'transaction': self.calculate_transaction_chart_data,
            'customer': self.calculate_customer_chart_data,
            'conversion': self.calculate_conversion_chart_data,
            'offlineEvent': self.calculate_offline_event_chart_data,
            'googleAnalytics': self.calculate_ga_chart_data,
            # 'serviceLogs': self.calculate_service_logs_data,
            'subscription': self.calculate_subscription_chart_data,
            'peopleCounterData': self.calculate_people_counter_chart_data,
            # 'myFacebook': self.calculate_my_facebook_data,
            # 'openDataWeather':
            # 'openDataHolidays':
            # 'openDataHumanTraffic':
            # 'competitorFacebook':
        }
        return mapping.get(data_type)(data.copy())

    @staticmethod
    def calculate_transaction_chart_data(data):
        number_of_group = 20 if len(data.index) >= 2000 else 10
        data['groups'] = pd.cut(data['Transaction_Value'], number_of_group)
        response = {
            'datasets': data.groupby(['groups'])['Transaction_Value'].count().tolist(),
            'labels': [''] * number_of_group
        }
        del data['groups']

        return response

    @staticmethod
    def calculate_customer_chart_data(data):
        number_of_group = 20 if len(data.index) >= 2000 else 10

        data['Temp_Create_Date'] = pd.to_datetime(data['Create_Date'], format='%d/%m/%Y')
        today = datetime.date.today()

        data['days'] = map(lambda x: x.days, data['Temp_Create_Date'] - today)

        data['groups'] = pd.cut(data['days'], number_of_group)
        response = {
            'datasets': data.groupby(['groups'])['days'].count().cumsum().tolist(),
            'labels': [''] * number_of_group
        }

        del data['Temp_Create_Date']
        del data['days']
        del data['groups']
        return response

    @staticmethod
    def calculate_conversion_chart_data(data):
        grouped = data.groupby(['Campaign_Name'])['Campaign_Name'].count()
        response = {
            'datasets': data.groupby(['Campaign_Name'])['Campaign_Name'].count().tolist(),
            'labels': grouped.keys().tolist()
        }
        del grouped
        return response

    @staticmethod
    def calculate_ga_chart_data(data):
        data['Temp_Date'] = pd.to_datetime(data['Date'], format='%d/%m/%Y')
        data['Temp_Date'] = pd.DatetimeIndex(data['Temp_Date']).year.astype(str).str.cat(
            pd.DatetimeIndex(data['Temp_Date']).month.astype(str), sep='-')
        gdata = data.groupby(['Temp_Date', 'User_Type'])['Temp_Date'].count()
        tdata = gdata.unstack(level=-1)
        tdata['Total visitor'] = tdata['New visitor'] + tdata['Returning  visitor']
        response = {
            'datasets': {
                'returning_visitor': tdata['New visitor'].tolist(),
                'total_visitor': tdata['Total visitor'].tolist()
            },
            'labels': tdata.index.get_level_values('Temp_Date').unique().tolist()
        }
        del data['Temp_Date']
        del tdata, gdata
        return response

    # TODO: simple offline event chart like this for large data set may not work :o)
    @staticmethod
    def calculate_offline_event_chart_data(df):
        return {
            'datasets': {
                'start_date': df['Start_Date'].tolist(),
                'end_date': df['End_Date'].tolist(),
            },
            'labels': df['Event_Type'].tolist()
        }

    @staticmethod
    def calculate_subscription_chart_data(df):
        df['Temp_Timestamp'] = df['Timestamp'].apply(lambda x: x.split()[0])
        df['Temp_Timestamp'] = pd.to_datetime(df['Temp_Timestamp'], format='%d/%m/%Y')
        gdf = df.groupby(['Temp_Timestamp', 'Action'])['Subscription'].count()
        tdf = gdf.unstack(level=-1)
        del gdf
        del df['Temp_Timestamp']
        return {
            'datasets': {
                'subscribe_count': tdf['Subscribe'].tolist(),
                'unsubscribe_count': tdf['Unsubscribe'].tolist(),
            },
            'labels': tdf.index.tolist()
        }

    @staticmethod
    def calculate_people_counter_chart_data(df):
        df['Temp_Timestamp'] = df['Timestamp'].apply(lambda x: x.split()[0])
        df['Temp_Timestamp'] = pd.to_datetime(df['Temp_Timestamp'], format='%d/%m/%Y')
        grouped = df.groupby(['Temp_Timestamp']).sum()
        del df['Temp_Timestamp']
        return {
            'datasets': {
                'datasets_inflow': grouped['Number_People_In'].tolist(),
                'datasets_outflow': grouped['Number_People_Out'].tolist(),
            },
            'labels': grouped.index.tolist()
        }
