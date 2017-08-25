import pandas as pd
from eledata.models.entity import *


class EntityH2OEngine(object):
    group = None
    time_window = None

    """  
    """

    @classmethod
    def init_engine(cls, group):
        cls.group = group
        return cls

    @classmethod
    def get_time_window(cls):
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
        response = list(Entity.objects(group=cls.group, type='transaction').aggregate(*pipeline))
        return response[0]

    @classmethod
    def get_user_list(cls):
        pipeline = [
            {"$unwind": "$data"},
            {
                "$group": {
                    "_id": "$data.User_ID",
                }
            }
        ]
        response = list(Entity.objects(group=cls.group, type='customer').aggregate(*pipeline))
        return pd.DataFrame(response)

    @classmethod
    def get_clv_in_window(cls, user_list=None, start_date=None, end_date=None):
        month_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1 if (
            start_date and end_date) else 3

        pipeline = [
            {"$unwind": "$data"},
            {"$match": {}},
            {
                "$group": {
                    "_id": "$data.User_ID",
                    "sum_purchase_amount": {"$sum": "$data.Transaction_Value"},
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

        response = list(Entity.objects(group=cls.group, type='transaction').aggregate(*pipeline))
        response = pd.DataFrame(response)
        # post handling month base amount
        response['sum_purchase_amount'] = response['sum_purchase_amount'] / month_diff
        return response

    # TODO: get_rmf_in_window

    # TODO: get_allowance_in_window (or from settings)