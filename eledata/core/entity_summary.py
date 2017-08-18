import pandas as pd
import datetime


def calculate_transaction_data(data, create_date=None, last_update=None):
    data['Transaction_Date'] = pd.to_datetime(data['Transaction_Date'], format='%d/%m/%Y')

    return [
        {'key': 'Transaction Records', 'value': len(data.index)},
        {'key': 'Involved User', 'value': len(data.groupby(['User_ID']).count().index)},
        {'key': 'First Transaction Start Date', 'value': data['Transaction_Date'].min().strftime('%Y-%m-%d')},
        {'key': 'Last Transaction End Date', 'value': data['Transaction_Date'].max().strftime('%Y-%m-%d')},
        {'key': 'Average Transaction Value', 'value': format(data['Transaction_Value'].mean(), '.2f')},
        {'key': 'Average Transaction Quantity', 'value': format(data['Transaction_Quantity'].mean(), '.1f')},
        {'key': 'Create Date', 'value': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        {'key': 'Last Update', 'value': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    ]


def calculate_customer_data(data, create_date=None, last_update=None):
    data['Create_Date'] = pd.to_datetime(data['Create_Date'], format='%d/%m/%Y')

    return [
        {'key': 'Customer Records', 'value': len(data.index)},
        {'key': 'First Customer Join Date', 'value': data['Create_Date'].min().strftime('%Y-%m-%d')},
        {'key': 'Latest Customer Join Date', 'value': data['Create_Date'].max().strftime('%Y-%m-%d')},
        {'key': 'Involved Countries', 'value': len(data.groupby(['Country']).count().index)},
        {'key': 'Customer Age Range', 'value': str(data['Age'].min()) + ' - ' + str(data['Age'].max())},
        {'key': 'Create Date', 'value': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        {'key': 'Last Update', 'value': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
    ]


def calculate_conversion_data(data, create_date=None, last_update=None):
    data['Start_Date'] = pd.to_datetime(data['Start_Date'], format='%d/%m/%Y')
    data['End_Date'] = pd.to_datetime(data['End_Date'], format='%d/%m/%Y')

    conversion_record = data['Conversion_ID'].count()
    grouped = data.groupby(['User_ID']).count()
    test = data[(data.Response == 'Completed')].count()
    completed_rate = format(float(test['Conversion_ID']) / float(conversion_record), '.2f')

    return [
        {'key': 'Involved Campaigns', 'value': len(data.groupby(['Campaign_ID']).count().index)},
        {'key': 'Involved Users', 'value': grouped['Campaign_ID'].count()},
        {'key': 'Conversion Records', 'value': conversion_record},
        {'key': 'Completed Rate', 'value': completed_rate},
        {'key': 'First Record Start Date', 'value': data['Start_Date'].min().strftime('%Y-%m-%d')},
        {'key': 'Last Record End Date', 'value': data['End_Date'].max().strftime('%Y-%m-%d')},
        {'key': 'Create Date', 'value': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        {'key': 'Last Update', 'value': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
    ]


def calculate_offline_event_data(data, create_date=None, last_update=None):
    data['Start Date'] = pd.to_datetime(data['Start Date'], format='%d/%m/%Y')
    data['End Date'] = pd.to_datetime(data['End Date'], format='%d/%m/%Y')
    data['Event Period'] = data['End Date'].sub(data['Start Date'], axis=0)

    return [
        {'key': 'Event Record Count', 'value': data['No.'].count()},
        {'key': 'First Event Start Date', 'value': data['Start Date'].min().strftime('%Y-%m-%d')},
        {'key': 'Last Event End Date', 'value': data['End Date'].max().strftime('%Y-%m-%d')},
        {'key': 'Average Event Period', 'value': str(data['Event Period'].mean().days) + ' Days'},
        {'key': 'Create Date', 'value': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        {'key': 'Last Update', 'value': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
    ]


def calculate_subscription_data(data, create_date=None, last_update=None):
    data['Timestamp'] = pd.to_datetime(data['Timestamp'], format='%d/%m/%Y %H:%M')
    data['Date'] = data['Timestamp'].dt.date

    grouped = data[(data.Action == 'Subscribe')].count()
    grouped_by_day = data.groupby(['Date', 'Action']).count().reset_index()
    return [
        {'key': 'Total Subscription', 'value': grouped['Subscription']},
        {'key': 'Average Subscription per Day', 'value': format(
            grouped_by_day.loc[grouped_by_day['Action'] == 'Subscribe', 'Subscription'].mean(), '.1f')},
        {'key': 'First Record Start Date', 'value': data['Timestamp'].min().strftime('%Y-%m-%d')},
        {'key': 'Last Record End Date', 'value': data['Timestamp'].max().strftime('%Y-%m-%d')},
        {'key': 'Create Date', 'value': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        {'key': 'Last Update', 'value': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
    ]


def calculate_people_counter_data(data, create_date=None, last_update=None):
    data['Timestamp'] = pd.to_datetime(data['Timestamp'], format='%d/%m/%Y %H:%M:%S')
    data['Date'] = data['Timestamp'].dt.date

    grouped = data.groupby(['Date']).sum()
    average_visitor_counter_day = grouped['PeopleInflow'].mean()

    return [
        {'key': 'Total Head Count', 'value': data['PeopleInflow'].sum()},
        {'key': 'First Record Start Date', 'value': data['Date'].min().strftime('%Y-%m-%d')},
        {'key': 'Last Record End Date', 'value': data['Date'].max().strftime('%Y-%m-%d')},
        {'key': 'Average Visitor Count per Day', 'value': format(average_visitor_counter_day, '.1f')},
        {'key': 'Maximum Visitor Count by Day', 'value': grouped['PeopleInflow'].max()},
        {'key': 'Maximum Visitor Day',
         'value': grouped.sort_values('PeopleInflow', ascending=0).index[0].strftime('%Y-%m-%d')},
        {'key': 'Create Date', 'value': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        {'key': 'Last Update', 'value': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
    ]


def calculate_service_logs_data(data, create_date=None, last_update=None):
    data['Timestamp'] = pd.to_datetime(data['Timestamp'], format='%d/%m/%Y')
    return [
        {'key': 'Total Record', 'value': data['Transaction ID'].count()},
        {'key': 'First Record Start Date', 'value': data['Timestamp'].min()},
        {'key': 'Last Record End Date', 'value': data['Timestamp'].max()},
        {'key': 'Create Date', 'value': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        {'key': 'Last Update', 'value': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
    ]


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


def calculate_ga_data(data, create_date=None, last_update=None):
    grouped = data[(data.TypeofVisitor == 'Returning  visitor')].count()
    return [
        {'key': 'Total Visitor', 'value': data['Users City'].count()},
        {'key': 'Returning Visitor', 'value': grouped['TypeofVisitor'].count()},
        {'key': 'Create Date', 'value': create_date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        {'key': 'Last Update', 'value': last_update or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
    ]


def get_single_data_summary(data, data_type, create_date=None, last_update=None):
    mapping = {
        'transaction': calculate_transaction_data,
        'customer': calculate_customer_data,
        'conversion': calculate_conversion_data,
        'offlineEvent': calculate_offline_event_data,
        'googleAnalytics': calculate_ga_data,
        'serviceLogs': calculate_service_logs_data,
        'subscription': calculate_subscription_data,
        'peopleCounterData': calculate_people_counter_data,
        'myFacebook': calculate_my_facebook_data,
        # 'openDataWeather':
        # 'openDataHolidays':
        # 'openDataHumanTraffic':
        # 'competitorFacebook':
    }
    return mapping[data_type](data, create_date, last_update)
