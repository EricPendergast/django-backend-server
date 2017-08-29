import pandas as pd
from eledata.models.entity import *
from dateutil.relativedelta import relativedelta


# from h2o.estimators.random_forest import H2ORandomForestEstimator


class EntityH2OEngine(object):
    group = None
    time_window = None

    def __init__(self, group):
        self.group = group

    def get_status(self):
        return self.group.name

    def get_time_window(self):
        # TODO for performance study: -
        # https://stackoverflow.com/questions/32076382/mongodb-how-to-get-max-value-from-collections
        pipeline = [
            {"$unwind": "$data"},
            {
                "$group": {
                    "_id": None,
                    "last_date": {"$max": "$data.Transaction_Date"},
                    "first_date": {"$min": "$data.Transaction_Date"}
                }
            }
        ]
        response = list(Entity.objects(group=self.group, type='transaction').aggregate(*pipeline))
        return response[0]

    def get_transaction_based_user_list(self):
        pipeline = [
            {"$unwind": "$data"},
            {
                "$group": {
                    "_id": "$data.User_ID",
                }
            }
        ]
        response = list(Entity.objects(group=self.group, type='transaction').aggregate(*pipeline))
        return pd.DataFrame(response)

    def get_customer_based_user_list(self):
        pipeline = [
            {"$unwind": "$data"},
            {
                "$group": {
                    "_id": "$data.User_ID",
                }
            }
        ]
        response = list(Entity.objects(group=self.group, type='customer').aggregate(*pipeline))
        return pd.DataFrame(response)

    def get_clv_in_window(self, user_list=None, start_date=None, end_date=None):
        month_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1 if (
            start_date and end_date) else 3

        pipeline = [
            {"$unwind": "$data"},
            {"$match": {}},
            {
                "$group": {
                    "_id": "$data.User_ID",
                    "clv": {"$sum": "$data.Transaction_Value"},
                }
            }
        ]
        match_obj = pipeline[1]["$match"]

        user_list and match_obj.update({
            "data.User_ID": {"$in": user_list}
        })
        start_date and end_date and match_obj.update({
            "data.Transaction_Date": {
                "$gte": start_date,
                "$lte": end_date
            }
        })

        response = list(Entity.objects(group=self.group, type='transaction').aggregate(*pipeline))
        response = pd.DataFrame(response)
        # post handling month base amount
        response['clv'] = response['clv'] / month_diff
        return response

    def get_rmf_in_window(self, user_list=None, start_date=None, end_date=None):
        month_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1 if (
            start_date and end_date) else 3

        pipeline = [
            {"$unwind": "$data"},
            {"$match": {}},
            {
                "$group": {
                    "_id": "$data.User_ID",
                    "monetary_amount": {"$sum": "$data.Transaction_Value"},
                    "frequency": {"$sum": 1},
                    "recency": {"$max": "$data.Transaction_Date"},
                    "monetary_quantity": {"$sum": "$data.Transaction_Quantity"}
                }
            }
        ]
        match_obj = pipeline[1]["$match"]

        user_list and match_obj.update({
            "data.User_ID": {"$in": user_list}
        })
        start_date and end_date and match_obj.update({
            "data.Transaction_Date": {
                "$gte": start_date,
                "$lte": end_date
            }
        })

        response = list(Entity.objects(group=self.group, type='transaction').aggregate(*pipeline))
        response = pd.DataFrame(response).sort_values(['_id'], ascending=[1])
        # post handling month base amount
        response['monetary_amount'] = response['monetary_amount'] / month_diff
        response['monetary_quantity'] = response['monetary_quantity'] / month_diff
        response['recency'] = end_date and (
            map(lambda x: (end_date - x).days, response['recency'])) or (
                                  map(lambda x: (datetime.datetime.now() - x).days, response['recency']))
        return response

    def get_allowance_in_window(self, user_list=None, start_date=None, end_date=None):
        pipeline = [
            {"$unwind": "$data"},
            {"$match": {}},
            {
                "$group": {
                    "_id": {
                        "user_id": "$data.User_ID",
                        "transaction_date": {
                            "year": {"$year": "$data.Transaction_Date"},
                            "month": {"$month": "$data.Transaction_Date"},
                            "day": {"$dayOfMonth": "$data.Transaction_Date"}
                        }
                    },
                    "monetary_amount": {"$sum": "$data.Transaction_Value"},
                },
            },
            {
                "$group": {
                    "_id": "$_id.user_id",
                    "std_monetary_amount": {"$stdDevPop": "$monetary_amount"},
                }
            }
        ]
        match_obj = pipeline[1]["$match"]

        user_list and match_obj.update({
            "data.User_ID": {"$in": user_list}
        })
        start_date and end_date and match_obj.update({
            "data.Transaction_Date": {
                "$gte": start_date,
                "$lte": end_date
            }
        })

        response = list(Entity.objects(group=self.group, type='transaction').aggregate(*pipeline))
        response = pd.DataFrame(response)
        return response

    @staticmethod
    def mean_shift_standardize(data):
        for y in data.columns[1:]:
            data[y] = abs(data[y] - data[y].mean()[0]) / data[y].sd()[0]
        return data

    def get_dynamic_rmf_in_window(self, user_list=None, start_date=None, end_date=None, window_length=3):
        month_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1 if (
            start_date and end_date) else 3
        date_list = [end_date - relativedelta(months=i * window_length) for i in range(month_diff / window_length)]
        date_list.append(start_date)
        date_list = date_list[::-1]
        branches = [
            {"case": {"$and": [
                {"$gte": [date_list[i + 1], "$data.Transaction_Date"]},
                {"$lt": [date_list[i], "$data.Transaction_Date"]},
            ]}, "then": i} for i in range(len(date_list) - 1)
        ]
        branches.insert(0,
                        {"case": {
                            "$gte": [start_date, "$data.Transaction_Date"]
                        }, "then": -1})
        branches.append({"case": {
            "lt": [end_date, "$data.Transaction_Date"]
        }, "then": len(date_list) - 2})

        pipeline = [
            {"$unwind": "$data"},
            {"$match": {}},
            {
                "$project": {
                    "user_id": "$data.User_ID",
                    "monetary_amount": {"$sum": "$data.Transaction_Value"},
                    "recency": {"$max": "$data.Transaction_Date"},
                    "monetary_quantity": {"$sum": "$data.Transaction_Quantity"},
                    "transaction_date_group": {
                        "$switch": {
                            "branches": branches
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "user_id": "$user_id",
                        "transaction_date_group": "$transaction_date_group"
                    },
                    "monetary_amount": {"$sum": "$monetary_amount"},
                    "frequency": {"$sum": 1},
                    "recency": {"$max": "$recency"},
                    "monetary_quantity": {"$sum": "$monetary_quantity"}
                }
            }
        ]
        match_obj = pipeline[1]["$match"]

        user_list and match_obj.update({
            "data.User_ID": {"$in": user_list}
        })
        start_date and end_date and match_obj.update({
            "data.Transaction_Date": {
                "$gte": start_date,
                "$lte": end_date
            }
        })
        response = list(Entity.objects(group=self.group, type='transaction').aggregate(*pipeline))
        response = pd.DataFrame(response)
        # print(map(lambda x: x['transaction_date_group'], response['_id']))
        # print(map(lambda x: x['user_id'], response['_id']))
        # print([x[u'Transaction_Date'] for x in Entity.objects(group=self.group, type='transaction').as_pymongo()[0][u'data']])
        # print([x[u'User_ID'] for x in Entity.objects(group=self.group, type='transaction').as_pymongo()[0][u'data']])
        # post handling month base amount
        # response['monetary_amount'] = response['monetary_amount'] / month_diff
        # response['monetary_quantity'] = response['monetary_quantity'] / month_diff
        # response['recency'] = end_date and (
        #     map(lambda x: (end_date - x).days, response['recency'])) or (
        #                           map(lambda x: (datetime.datetime.now() - x).days, response['recency']))
        return response
