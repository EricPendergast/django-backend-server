from abc import abstractmethod
from eledata.core_engine.base_engine import BaseEngine
from eledata.models.entity import Entity
import pandas as pd
from dateutil.relativedelta import relativedelta
import datetime
import h2o


# TODO: do something when all instance is closed. Is it possible?
class H2OEngine(BaseEngine):
    gc_list = []

    def __init__(self, event_id, group, params):
        super(H2OEngine, self).__init__(event_id, group, params)

    """
    Workflow functions
    """

    @abstractmethod
    def get_class_attributes(self, user_list, start_date, turning_date, end_date, supervising_window_length):
        """
        Obviously different sub_engine build different model with different label
        """
        pass

    @abstractmethod
    def get_descriptive_attributes(self, user_list, start_date, end_date, month_diff, supervising_window_length):
        """
        Obviously different sub_engine build different model with different label
        """
        pass

    def execute(self):
        """
        No idea right now
        :return:
        """
        return

    def event_init(self):
        """
        EntityStatsEngine Does not init event (For the time beings?)
        :return:
        """
        return

    """
    Attribute handling functions
    """

    def get_user_list(self):
        """
        Fetch User List from Customer (then Transaction) Entity.
        :return: [ list of user_id ]
        """
        pipeline = [
            {"$unwind": "$data"},
            {
                "$group": {
                    "_id": "$data.User_ID",
                }
            }
        ]
        if Entity.objects(group=self.group, type='customer'):
            response = list(Entity.objects(group=self.group, type='customer').aggregate(*pipeline))
        else:
            response = list(Entity.objects(group=self.group, type='transaction').aggregate(*pipeline))
        return [r[u'_id'] for r in response]

    def get_total_time_window(self):
        """
        Fetch the full time window from Transaction Entity
        :return: { "last_date": xxx, "_id": xxx, "first_date": xxx }
        """
        # TODO: for performance study: -
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

    def get_supervising_time_window(self, month_diff):
        """
        Comparing total time window's length and user parameter input, response with correct supervising window length
        :param month_diff: integer, total time window's length, for comparison
        :return: time_shift: integer (in month)
        """

        prediction_window_params = filter(lambda _x: _x.get('label') == "prediction_window", self.params)
        if prediction_window_params:
            if prediction_window_params[0][u'choice_index'] == 1:
                user_choice = 1
            elif prediction_window_params[0][u'choice_index'] == 2:
                user_choice = 3
            elif prediction_window_params[0][u'choice_index'] == 3:
                user_choice = 12
            elif prediction_window_params[0][u'choice_index'] == 4:
                user_choice = prediction_window_params[0][u'choice_input']
            else:
                user_choice = False
        else:
            user_choice = False

        # Do month by month analysis for 2 < Month < 6
        if month_diff < 6:
            return 1

        # Do quarter by quarter analysis for 6 < month < 24
        elif month_diff < 24 and user_choice and user_choice < (month_diff / 3):
            return user_choice

        # Do quarter by quarter analysis for
        elif month_diff < 24:
            return 3

        elif user_choice and user_choice < month_diff / 2:
            return user_choice

        else:
            return 12

    def get_rmf_in_window(self, user_list, start_date, end_date, supervising_window_length):
        """
        :param user_list:
        :param start_date:
        :param end_date:
        :param supervising_window_length:
        :return: df(Recency, Monetary (Amount, Quantity), Frequency)
        """
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
        response = pd.DataFrame(response).sort_values([u'_id'], ascending=[1])
        response['user_id'] = response['_id']
        del response['_id']

        # post handling month base amount
        response['monetary_amount'] = response['monetary_amount'] / supervising_window_length
        response['monetary_quantity'] = response['monetary_quantity'] / supervising_window_length
        response['recency'] = end_date and (
            map(lambda x: (end_date - x).days, response['recency'])
        ) or (
            map(lambda x: (datetime.datetime.now() - x).days, response['recency'])
        )
        return response

    def get_dynamic_rmf_in_window(self, user_list=None, start_date=None, end_date=None,
                                  supervising_window_length=3, total_window_length=3):
        """
        2. - We generate date_list as the points for different time window points, so that we have
        end_date -> date_list[1] -> date_list[2] -> ... -> start_date, all different by window_length.

        3. - loop_range will be the length of the date_list

        4. - Aggregation on entity.data, retrieving Recency, Monetary (Amount, Quantity), Frequency

        5. - Get response from querying

        6. - Response should be list of grouped rmf aggregations from range:
            from date_list[1] to end_date
            from date_list[2] to date_list[1]
            ....
            from start_date to date_list[0]

           - We further combined the group to form rmf aggregations from end_date to different date_list[i] (time point)

        7. - We use transaction_date_group as the identifier
           - transaction_date_group with smaller value indicates they are more far away from end_date
        """

        # 2, 3.
        loop_range = (total_window_length + 1) / supervising_window_length \
            if supervising_window_length > 1 else total_window_length

        date_list = [end_date - relativedelta(months=i * supervising_window_length) for i in range(loop_range)]
        date_list.append(start_date)
        date_list = date_list[::-1]

        # 4.
        branches = [
            {"case": {"$and": [
                {"$gte": [date_list[i + 2], "$data.Transaction_Date"]},
                {"$lt": [date_list[i + 1], "$data.Transaction_Date"]},
            ]}, "then": i} for i in range(len(date_list) - 2)
        ]
        branches.insert(0,
                        {"case": {"$and": [
                            {"$gte": [date_list[1], "$data.Transaction_Date"]},
                            {"$lte": [start_date, "$data.Transaction_Date"]},
                        ]}, "then": -1})

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
                            "branches": branches,
                            "default": -1
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

        # 5.
        response = list(Entity.objects(group=self.group, type='transaction').aggregate(*pipeline))
        response = pd.DataFrame(response)

        final_response = []

        # 6.
        for i in range(len(date_list) - 1):
            num_of_month = (len(date_list) - 1 - i) * supervising_window_length if i > 0 else total_window_length

            # 7.
            sub_response_group = response[response['_id'].apply(lambda x: x[u'transaction_date_group']) >= i - 1]
            sub_response_group['user_id'] = sub_response_group[u'_id'].apply(lambda x: x[u'user_id'])
            sub_response_group['transaction_date_group'] = sub_response_group[u'_id'].apply(
                lambda x: x[u'transaction_date_group'])
            del sub_response_group[u'_id']

            _hint_text = "_last_" + str(num_of_month) + "_month"
            sub_response_group = sub_response_group.groupby('user_id')
            t_response = {
                'monetary_amount' + _hint_text: sub_response_group['monetary_amount'].sum() / num_of_month,
                'frequency' + _hint_text: sub_response_group['frequency'].sum() / num_of_month,
                'recency' + _hint_text: end_date and (
                    map(lambda x: (end_date - x).days, sub_response_group['recency'].max())) or (
                               map(lambda x: (datetime.datetime.now() - x).days, sub_response_group['recency'].max())),
                'monetary_quantity': sub_response_group['monetary_quantity'].sum(),
            }
            t_response = pd.DataFrame(t_response)
            t_response.reset_index(level=0, inplace=True)
            t_response['user_id'] = t_response['user_id'].astype(str)

            final_response.append(t_response)

        return final_response

    def get_allowance_in_window(self, user_list=None, start_date=None, end_date=None):

        # TODO: complete allowance from user param flow
        # allowance_param = filter(lambda _x: _x.label == "allowance", self.params)[0]
        #
        # user_choice = allowance_param.choice_input \
        #     if allowance_param.choice_index == 1 else False
        #
        # if user_choice:
        #     pipeline = [...pipeline_getting_clv_mean]
        # allowance = mean * user_choice

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
        response = pd.DataFrame(response).rename(columns={'_id': 'user_id'})
        return response

    @abstractmethod
    def get_back_test_accuracy(self, updated_training_frame):
        pass

    """
    Utility static methods below:
    """

    @staticmethod
    def get_h2o_client():
        if not h2o.cluster():
            h2o.init()
            return h2o

    @staticmethod
    def get_month_diff(start_date, end_date):
        """
        Time Based Resource Functions, derived from first_date and last_date
        :param start_date: datetime object, start of the window
        :param end_date: datetime object, end of the window
        :return: month_diff: integer (in month)
        """
        return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1

    @staticmethod
    def mean_shift_standardize(data, omitted_list):
        for y in data.columns:
            if y not in omitted_list:
                data[y] = abs(data[y] - data[y].mean()[0]) / data[y].sd()[0]
        return data

    @staticmethod
    def dynamic_rmf_merger(_left, _right, ext):
        _right.columns = [x + '-' + str(ext) if x is not 'user_id' else x for x in _right.columns]
        return pd.merge(_left, _right, how='outer', on='user_id')

    @classmethod
    def overall_gc(cls):
        h2o_client = cls.get_h2o_client()
        h2o_client.remove_all()
        return
