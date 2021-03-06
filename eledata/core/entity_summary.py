import pandas as pd
import datetime


def calculate_transaction_data(data, create_date=None, last_update=None):
    data['Transaction_Date'] = pd.to_datetime(data['Transaction_Date'], format='%d/%m/%Y')

    return {
        'Transaction Records': data.count(),
        'First Conversion Start Date': data['Transaction_Date'].min().strftime('%Y-%m-%d'),
        'Last Conversion End Date': data['Transaction_Date'].max().strftime('%Y-%m-%d'),
        'Involved User': data.groupby(['User_ID']).count(),
        'Average Transaction Value': data['Transaction_Value'].mean(),
        'Average Transaction Quantity': data['Transaction_Quantity'].mean(),
        'Create Date': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Last Update': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }


def calculate_customer_data(data, create_date=None, last_update=None):
    data['Create_Date'] = pd.to_datetime(data['Create_Date'], format='%d/%m/%Y')

    return {
        'Customer Records': data.count(),
        'First Customer Join Date': data['Create_Date'].min().strftime('%Y-%m-%d'),
        'Latest Customer Join Date': data['Create_Date'].max().strftime('%Y-%m-%d'),
        'Involved Countries': data.groupby(['Country']).count(),
        'Customer Age Range': str(data['Age'].min()) + ' - ' + str(data['Age'].max()),
        'Create Date': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Last Update': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }


def calculate_conversion_data(data, create_date=None, last_update=None):
    data['Start_Date'] = pd.to_datetime(data['Start_Date'], format='%d/%m/%Y')
    data['End_Date'] = pd.to_datetime(data['End_Date'], format='%d/%m/%Y')

    conversion_record = data['Conversion_ID'].count()
    grouped = data.groupby(['User_ID']).count()
    test = data[(data.Response == 'Completed')].count()
    completed_rate = format(float(test['Conversion_ID']) / float(conversion_record), '.2f')

    return {
        'Involved User': grouped['Campaign_ID'].count(),
        'Conversion Records': conversion_record,
        'Completed Rate': completed_rate,
        'First Record Start Date': data['Start_Date'].min().strftime('%Y-%m-%d'),
        'Last Record End Date': data['End_Date'].max().strftime('%Y-%m-%d'),
        'Create Date': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Last Update': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }


def calculate_offline_event_data(data, create_date=None, last_update=None):
    data['Start Date'] = pd.to_datetime(data['Start Date'], format='%d/%m/%Y')
    data['End Date'] = pd.to_datetime(data['End Date'], format='%d/%m/%Y')
    data['Event Period'] = data['End Date'].sub(data['Start Date'], axis=0)

    return {
        'Event Record Count': data['No.'].count(),
        'First Event Start Date': data['Start Date'].min().strftime('%Y-%m-%d'),
        'Last Event End Date': data['End Date'].max().strftime('%Y-%m-%d'),
        'Average Event Period': str(data['Event Period'].mean().days) + ' Days',
        'Create Date': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Last Update': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }


def calculate_subscription_data(data, create_date=None, last_update=None):
    data['Timestamp'] = pd.to_datetime(data['Timestamp'], format='%d/%m/%Y %H:%M')
    data['Date'] = data['Timestamp'].dt.date

    grouped = data[(data.Action == 'Subscribe')].count()
    grouped_by_day = data.groupby(['Date', 'Action']).count().reset_index()
    return {
        'Total Subscription': grouped['Subscription'],
        'Average Subscription per Day': format(
            grouped_by_day.loc[grouped_by_day['Action'] == 'Subscribe', 'Subscription'].mean(), '.1f'),
        'First Record Start Date': data['Timestamp'].min().strftime('%Y-%m-%d'),
        'Last Record End Date': data['Timestamp'].max().strftime('%Y-%m-%d'),
        'Create Date': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Last Update': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }


def calculate_people_counter_data(data, create_date=None, last_update=None):
    data['Timestamp'] = pd.to_datetime(data['Timestamp'], format='%d/%m/%Y %H:%M:%S')
    data['Date'] = data['Timestamp'].dt.date

    grouped = data.groupby(['Date']).sum()
    average_visitor_counter_day = grouped['PeopleInflow'].mean()

    return {
        'Total Head Count': data['PeopleInflow'].sum(),
        'First Record Start Date': data['Date'].min().strftime('%Y-%m-%d'),
        'Last Record End Date': data['Date'].max().strftime('%Y-%m-%d'),
        'Average Visitor Count per Day': format(average_visitor_counter_day, '.1f'),
        'Maximum Visitor Count by Day': grouped['PeopleInflow'].max(),
        'Maximum Visitor Day': grouped.sort_values('PeopleInflow', ascending=0).index[0].strftime('%Y-%m-%d'),
        'Create Date': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Last Update': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }


def calculate_service_logs_data(data, create_date=None, last_update=None):
    data['Timestamp'] = pd.to_datetime(data['Timestamp'], format='%d/%m/%Y')
    return {
        'Total Record': data['Transaction ID'].count(),
        'First Record Start Date': data['Timestamp'].min(),
        'Last Record End Date': data['Timestamp'].max(),
        'Create Date': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Last Update': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }


def calculate_my_facebook_data(data, create_date=None, last_update=None):
    return {
        'TotalViews': data['Views'].max(),
        'TotalLikes': data['Likes'].max(),
        'TotalFollowers': data['Followers'].max(),
        'First Record Start Date': data['Timestamp'].min(),
        'Last Record End Date': data['Timestamp'].max(),
        'Create Date': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Last Update': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }


def calculate_ga_data(data, create_date=None, last_update=None):
    grouped = data[(data.TypeofVisitor == 'Returning  visitor')].count()
    return {
        'Total Visitor': data['Users City'].count(),
        'Returning Visitor': grouped['TypeofVisitor'].count(),
        'Create Date': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Last Update': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }


def get_single_data_summary(data, data_type, create_date=None, last_update=None):
    mapping = {
        'transaction': calculate_transaction_data,
        'customer': calculate_customer_data,
        'conversion': calculate_conversion_data,
        'offlineEvent': calculate_offline_event_data,
        'googleAnalytics': calculate_my_facebook_data,
        'serviceLogs': calculate_service_logs_data,
        'subscription': calculate_subscription_data,
        'peopleCounterData': calculate_people_counter_data,
        # 'openDataWeather':
        # 'openDataHolidays':
        # 'openDataHumanTraffic':
        # 'competitorFacebook':
    }
    return mapping[data_type](data, create_date, last_update)
