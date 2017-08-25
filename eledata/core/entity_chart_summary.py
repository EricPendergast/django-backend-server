import pandas as pd
import datetime


def calculate_transaction_chart_data(data):
    number_of_group = 20 if len(data.index) >= 2000 else 10
    data['groups'] = pd.cut(data['Transaction_Value'], number_of_group)
    response = {
        'datasets': data.groupby(['groups'])['Transaction_Value'].count().tolist(),
        'labels': [''] * number_of_group
    }
    del data['groups']

    return response


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


def calculate_conversion_chart_data(data):
    grouped = data.groupby(['Campaign_Name'])['Campaign_Name'].count()
    response = {
        'datasets': data.groupby(['Campaign_Name'])['Campaign_Name'].count().tolist(),
        'labels': grouped.keys().tolist()
    }

    return response


def calculate_ga_chart_data(data):
    data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%Y')
    data['Date'] = pd.DatetimeIndex(data['Date']).year.astype(str).str.cat(
        pd.DatetimeIndex(data['Date']).month.astype(str), sep='-')
    data = data.groupby(['Date', 'User_Type'])['Date'].count()
    data = data.unstack(level=-1)
    data['Total visitor'] = data['New visitor'] + data['Returning  visitor']

    response = {
        'datasets': {
            'returning_visitor': data['New visitor'].tolist(),
            'total_visitor': data['Total visitor'].tolist()
        },
        'labels': data.index.get_level_values('Date').unique().tolist()
    }

    del data['Total visitor']
    return response


# def calculate_offline_event_chart_data(data):
#     number_of_group = 20 if len(data.index) >= 2000 else 10
#     data['groups'] = pd.cut(data['Transaction_Value'], number_of_group)
#     response = {
#         'datasets': data.groupby(['groups'])['Transaction_Value'].count().cumsum().tolist(),
#         'labels': [''] * number_of_group
#     }
#
#     del data['groups']
#     return response
#
#
# def calculate_subscription_chart_data(data):
#     number_of_group = 20 if len(data.index) >= 2000 else 10
#     data['groups'] = pd.cut(data['Transaction_Value'], number_of_group)
#     response = {
#         'datasets': data.groupby(['groups'])['Transaction_Value'].count().cumsum().tolist(),
#         'labels': [''] * number_of_group
#     }
#
#     del data['groups']
#     return response
#
#
# def calculate_people_counter_chart_data(data):
#     number_of_group = 20 if len(data.index) >= 2000 else 10
#     data['groups'] = pd.cut(data['Transaction_Value'], number_of_group)
#     response = {
#         'datasets': data.groupby(['groups'])['Transaction_Value'].count().cumsum().tolist(),
#         'labels': [''] * number_of_group
#     }
#
#     del data['groups']
#     return response
#
#
# def calculate_service_logs_chart_data(data):
#     number_of_group = 20 if len(data.index) >= 2000 else 10
#     data['groups'] = pd.cut(data['Transaction_Value'], number_of_group)
#     return {
#         'datasets': data.groupby(['groups'])['Transaction_Value'].count().cumsum().tolist(),
#         'labels': [''] * number_of_group
#     }
#
#
# def calculate_my_facebook_chart_data(data):
#     number_of_group = 20 if len(data.index) >= 2000 else 10
#     data['groups'] = pd.cut(data['Transaction_Value'], number_of_group)
#     return {
#         'datasets': data.groupby(['groups'])['Transaction_Value'].count().cumsum().tolist(),
#         'labels': [''] * number_of_group
#     }


def get_single_data_summary_chart(data, data_type):
    mapping = {
        'transaction': calculate_transaction_chart_data,
        'customer': calculate_customer_chart_data,
        'conversion': calculate_conversion_chart_data,
        # 'offlineEvent': calculate_offline_event_chart_data,
        # 'googleAnalytics': calculate_ga_chart_data,
        # 'serviceLogs': calculate_service_logs_chart_data,
        # 'subscription': calculate_subscription_chart_data,
        # 'peopleCounterData': calculate_people_counter_chart_data,
        # 'myFacebook': calculate_my_facebook_chart_data,
        # 'openDataWeather':
        # 'openDataHolidays':
        # 'openDataHumanTraffic':
        # 'competitorFacebook':
    }
    response = mapping[data_type](data)
    return response
