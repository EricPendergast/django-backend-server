import pandas as pd
import datetime


def calculate_transaction_chart_data(data):
    number_of_group = 20 if len(data.index) >= 2000 else 10
    data['groups'] = pd.cut(data['Transaction_Value'], number_of_group)
    return {
        'datasets': data.groupby(['groups'])['Transaction_Value'].count().tolist(),
        'labels': [''] * number_of_group
    }


def calculate_customer_chart_data(data):
    number_of_group = 20 if len(data.index) >= 2000 else 10

    data['Create_Date'] = pd.to_datetime(data['Create_Date'], format='%d/%m/%Y')
    today = datetime.date.today()

    data['days'] = map(lambda x: x.days, data['Create_Date'] - today)

    data['groups'] = pd.cut(data['days'], number_of_group)
    return {
        'datasets': data.groupby(['groups'])['days'].count().cumsum().tolist(),
        'labels': [''] * number_of_group
    }


def calculate_conversion_chart_data(data):
    number_of_group = 20 if len(data.index) >= 2000 else 10
    data['groups'] = pd.cut(data['Transaction_Value'], number_of_group)
    return {
        'datasets': data.groupby(['groups'])['Transaction_Value'].count().cumsum().tolist(),
        'labels': [''] * number_of_group
    }


def calculate_offline_event_chart_data(data):
    number_of_group = 20 if len(data.index) >= 2000 else 10
    data['groups'] = pd.cut(data['Transaction_Value'], number_of_group)
    return {
        'datasets': data.groupby(['groups'])['Transaction_Value'].count().cumsum().tolist(),
        'labels': [''] * number_of_group
    }


def calculate_subscription_chart_data(data):
    number_of_group = 20 if len(data.index) >= 2000 else 10
    data['groups'] = pd.cut(data['Transaction_Value'], number_of_group)
    return {
        'datasets': data.groupby(['groups'])['Transaction_Value'].count().cumsum().tolist(),
        'labels': [''] * number_of_group
    }


def calculate_people_counter_chart_data(data):
    number_of_group = 20 if len(data.index) >= 2000 else 10
    data['groups'] = pd.cut(data['Transaction_Value'], number_of_group)
    return {
        'datasets': data.groupby(['groups'])['Transaction_Value'].count().cumsum().tolist(),
        'labels': [''] * number_of_group
    }


def calculate_service_logs_chart_data(data):
    number_of_group = 20 if len(data.index) >= 2000 else 10
    data['groups'] = pd.cut(data['Transaction_Value'], number_of_group)
    return {
        'datasets': data.groupby(['groups'])['Transaction_Value'].count().cumsum().tolist(),
        'labels': [''] * number_of_group
    }


def calculate_my_facebook_chart_data(data):
    number_of_group = 20 if len(data.index) >= 2000 else 10
    data['groups'] = pd.cut(data['Transaction_Value'], number_of_group)
    return {
        'datasets': data.groupby(['groups'])['Transaction_Value'].count().cumsum().tolist(),
        'labels': [''] * number_of_group
    }


def calculate_ga_chart_data(data):
    number_of_group = 20 if len(data.index) >= 2000 else 10
    data['groups'] = pd.cut(data['Transaction_Value'], number_of_group)
    return {
        'datasets': data.groupby(['groups'])['Transaction_Value'].count().cumsum().tolist(),
        'labels': [''] * number_of_group
    }


def get_single_data_summary_chart(data, data_type):
    mapping = {
        'transaction': calculate_transaction_chart_data,
        'customer': calculate_customer_chart_data,
        'conversion': calculate_conversion_chart_data,
        'offlineEvent': calculate_offline_event_chart_data,
        'googleAnalytics': calculate_ga_chart_data,
        'serviceLogs': calculate_service_logs_chart_data,
        'subscription': calculate_subscription_chart_data,
        'peopleCounterData': calculate_people_counter_chart_data,
        'myFacebook': calculate_my_facebook_chart_data,
        # 'openDataWeather':
        # 'openDataHolidays':
        # 'openDataHumanTraffic':
        # 'competitorFacebook':
    }
    return mapping[data_type](data)
