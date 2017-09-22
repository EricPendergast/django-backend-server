import pandas as pd
from eledata.models.entity import *
from dateutil.relativedelta import relativedelta
import h2o

pd.options.mode.chained_assignment = None


# from h2o.estimators.random_forest import H2ORandomForestEstimator


class EntityH2OEngine(object):
    def __init__(self, group, questions=False, params=False):
        self.group = group
        self.questions = questions
        self.params = params

    time_window = None

    # Background Entity Resource Functions,  from transaction / customer records depends
    # ==================================================================================

    # Return Engine Group Name, mainly for validation
    def get_status(self):
        return self.group.name

    # Fetch User List from Customer (then Transaction) Entity.
    def get_user_list(self):
        """
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

    # Fetch the full time window from Transaction Entity
    def get_time_window(self):
        """
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

    # Time Based Resource Functions, derived from first_date and last_date
    @staticmethod
    def get_month_diff(start_date, end_date):
        """
        :param start_date: datetime object, start of the window
        :param end_date: datetime object, end of the window
        :return: month_diff: integer (in month)
        """
        return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1 if (
            start_date and end_date) else 3

    # Comparing total time window's length and user parameter input, response with correct supervising window length
    def get_time_shift(self, month_diff):
        """
        :param month_diff: integer, total time window's length, for comparsion
        :return: time_shift: integer (in month)
        """
        prediction_window = [x for x in self.params if x.label == "prediction_window"][0]

        user_choice = prediction_window.choice_input if prediction_window.choice_index == 1 else False

        # Do month by month analysis for 2 < Month < 6
        if month_diff < 6:
            return 1

        # Do quarter by quarter analysis for 6 < month < 24
        elif month_diff < 24 and user_choice < (month_diff / 3):
            return user_choice or 3

        # Do quarter by quarter analysis for
        elif month_diff < 24:
            return 3

        elif user_choice < month_diff / 2:
            return user_choice or 12

        else:
            return 12

    # Features Resource Functions
    # ===========================
    @staticmethod
    def dynamic_rmf_solver(_left, _right, ext):
        _right.columns = [x + "-" + str(ext) if x is not "user_id" else x for x in _right.columns]
        return pd.merge(_left, _right, how='outer', on='user_id')

    def get_clv_in_window(self, user_list=None, start_date=None, end_date=None, month_diff=3):
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

        # TODO: when there is no one have clv in this window...
        # post handling month base amount
        response['clv'] = response['clv'] / month_diff
        user_frame = pd.DataFrame(user_list, columns=['user_id'])
        response = pd.merge(user_frame, response.rename(columns={'_id': 'user_id'}), how='outer', on='user_id')

        for col in response:
            response[col].fillna(0, inplace=True)

        return response

    def get_rmf_in_window(self, user_list=None, start_date=None, end_date=None, month_diff=3):

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
        response = pd.DataFrame(response).rename(columns={'_id': 'user_id'})
        return response

    def get_dynamic_rmf_in_window(self, user_list=None, start_date=None, end_date=None, window_length=3, month_diff=3):
        """
        2. - We generate date_list as the points for different time window points, so that we have
        end_date -> date_list[1] -> date_list[2] -> ... -> start_date, all different by window_length.

        3. - loop_range will be the length of the date_list

        4. - We generate the aggregation pipeline command for mongo_engine, based on the date_list

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
        loop_range = (month_diff + 1) / window_length if window_length > 1 else month_diff

        date_list = [end_date - relativedelta(months=i * window_length) for i in range(loop_range)]
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
            num_of_month = (len(date_list) - 1 - i) * window_length if i > 0 else month_diff

            # 7.
            sub_response_group = response[response['_id'].apply(lambda x: x[u'transaction_date_group']) >= i - 1]
            sub_response_group['user_id'] = sub_response_group[u'_id'].apply(lambda x: x[u'user_id'])
            sub_response_group['transaction_date_group'] = sub_response_group[u'_id'].apply(
                lambda x: x[u'transaction_date_group'])
            del sub_response_group[u'_id']

            sub_response_group = sub_response_group.groupby('user_id')
            t_response = {
                'monetary_amount': sub_response_group['monetary_amount'].sum() / num_of_month,
                'frequency': sub_response_group['frequency'].sum() / num_of_month,
                'recency': end_date and (
                    map(lambda x: (end_date - x).days, sub_response_group['recency'].max())) or (
                               map(lambda x: (datetime.datetime.now() - x).days, sub_response_group['recency'].max())),
                'monetary_quantity': sub_response_group['monetary_quantity'].sum(),
            }
            t_response = pd.DataFrame(t_response)
            t_response.reset_index(level=0, inplace=True)
            t_response['user_id'] = t_response['user_id'].astype(str)

            final_response.append(t_response)

        return final_response

    # Final Processing
    def get_final_data(self, _user_list, _start_date, _end_date, _time_shift, _month_diff):
        # Prepare Features
        rmf_list = self.get_dynamic_rmf_in_window(user_list=_user_list, start_date=_start_date, end_date=_end_date,
                                                  window_length=_time_shift, month_diff=_month_diff)

        # Prepare Allowance
        allowance_list = self.get_allowance_in_window(user_list=_user_list, start_date=_start_date, end_date=_end_date)

        allowance_param = [x for x in self.params if x.label == "clv"][0]
        if allowance_param.choice_index == 1:
            allowance_list['allowance'] = allowance_param.choice_input
        else:
            allowance_list['allowance'] = allowance_list['std_monetary_amount']

        # TODO: Add Mean-Shift / Normalize Here
        # Final Processing For Training Set

        combined_rmf = None
        for index, item in enumerate(rmf_list):
            if index == 0:
                combined_rmf = item
            else:
                combined_rmf = self.dynamic_rmf_solver(combined_rmf, item, index)

        combined_rmf = pd.merge(combined_rmf, allowance_list, on='user_id')
        del combined_rmf['allowance']

        user_frame = pd.DataFrame(_user_list, columns=['user_id'])
        combined_rmf = pd.merge(user_frame, combined_rmf, how='outer', on='user_id')

        for col in combined_rmf:
            if "recency" in col:
                combined_rmf[col].fillna(combined_rmf[col].max(), inplace=True)
            else:
                combined_rmf[col].fillna(0, inplace=True)

        try:
            combined_rmf['user_id'] = combined_rmf['user_id'].astype(int)
            combined_rmf.sort_values('user_id', ascending=1)
            combined_rmf['user_id'] = combined_rmf['user_id'].astype(str)
        except:
            combined_rmf.sort_values('user_id', ascending=1)
        return combined_rmf

    @staticmethod
    def mean_shift_standardize(data):
        for y in data.columns[1:]:
            data[y] = abs(data[y] - data[y].mean()[0]) / data[y].sd()[0]
        return data

    # TODO: draft for the whole execute whole for getting prediction
    def execute(self):
        h2o.init()
        # Prepare Background Entity Resource, from transaction / customer records depends
        user_list = self.get_user_list()
        time_range_response = self.get_time_window()
        last_date, _id, first_date = [time_range_response[x] for x in list(time_range_response)]

        # Prepare Time Based Resource, derived from first_date and last_date
        total_month_diff = self.get_month_diff(first_date, last_date)
        time_shift = self.get_time_shift(total_month_diff)
        training_month_diff = total_month_diff - time_shift
        prediction_month_diff = time_shift
        turning_date = last_date - relativedelta(month=time_shift)
        second_date = first_date + relativedelta(month=time_shift)

        # Prepare Label
        clv = self.get_clv_in_window(user_list=user_list, start_date=turning_date, end_date=last_date,
                                     month_diff=prediction_month_diff)

        training = self.get_final_data(_user_list=user_list, _start_date=first_date, _end_date=turning_date,
                                       _month_diff=training_month_diff, _time_shift=time_shift)

        for_prediction = self.get_final_data(_user_list=user_list, _start_date=second_date, _end_date=last_date,
                                             _month_diff=training_month_diff, _time_shift=time_shift)

        training_frame = h2o.H2OFrame(python_obj=pd.merge(training, clv, how='outer', on='user_id'))

        train, test = training_frame.split_frame(
            ratios=[0.9],
            seed=123461
        )

        prediction_frame = h2o.H2OFrame(python_obj=for_prediction)

        from h2o.estimators.random_forest import H2ORandomForestEstimator
        model = H2ORandomForestEstimator(
            model_id="rf_covType_v2",
            ntrees=50,
            max_depth=30,
            col_sample_rate_per_tree=0.9,
            stopping_rounds=10,
            stopping_tolerance=0.01,
            score_each_iteration=True,
            seed=3000000)

        model.train(x=training_frame.columns, y='clv', training_frame=train)
        test['predict_clv'] = model.predict(test)

        # median = training_frame["clv"].median()[0]
        # low_med = training_frame[training_frame["clv"] <= median, "clv"].median()[0]
        # high_med = training_frame[training_frame["clv"] > median, "clv"].median()[0]

        # print("----Hit Ratio----")
        # print (((test['clv'] > high_med) & (test['predict_clv'] > high_med)) |
        #        (((high_med >= test['clv']) & (test['clv'] > median)) & (
        #            (high_med >= test['predict_clv']) & (test['clv'] > median))) |
        #        (((median >= test['clv']) & (test['clv'] > low_med)) & (
        #            (median >= test['predict_clv']) & (test['clv'] > low_med))) |
        #        (((test['clv'] <= low_med) & (test['predict_clv'] <= low_med)
        #          ))).sum() / len(test)
        #
        # print("---- Dummy Accuracy----")
        # print (abs(test['clv'] - test['predict_clv']) <= test['std_monetary_amount']).sum() / len(test)
        # # print(model.auc(train=True))
        # print(model)
        # h2o.export_file(test, path='satou.csv')
