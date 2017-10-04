from .h2o_engine import H2OEngine
from dateutil.relativedelta import relativedelta
import pandas as pd
from eledata.models.entity import Entity
from h2o.estimators.random_forest import H2ORandomForestEstimator
from h2o.estimators.gbm import H2OGradientBoostingEstimator
import uuid
from project.settings import CONSTANTS


class ClvH2OEngine(H2OEngine):
    def get_user_acceptance_level(self):
        # TODO: Handle default
        # TODO: Handle percentage allowance fetching
        return

    def get_class_attributes(self, user_list, start_date, turning_date, end_date, supervising_window_length):
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
        response['clv'] = response['clv'] / supervising_window_length
        user_frame = pd.DataFrame(user_list, columns=['user_id'])
        response = pd.merge(user_frame, response.rename(columns={'_id': 'user_id'}), how='outer', on='user_id')

        for col in response:
            response[col].fillna(0, inplace=True)

        return response

    def get_descriptive_attributes(self, user_list, start_date, end_date, total_window_length,
                                   supervising_window_length):
        # Prepare Features
        rmf_list = self.get_dynamic_rmf_in_window(user_list=user_list, start_date=start_date, end_date=end_date,
                                                  supervising_window_length=supervising_window_length,
                                                  total_window_length=total_window_length)

        # Prepare Allowance
        allowance_list = self.get_allowance_in_window(user_list=user_list, start_date=start_date, end_date=end_date)
        allowance_list['allowance'] = allowance_list['std_monetary_amount']

        # TODO: Add Mean-Shift / Normalize Here
        # Final Processing For Training Set
        combined_rmf = None
        for index, item in enumerate(rmf_list):
            if index == 0:
                combined_rmf = item
            else:
                combined_rmf = self.dynamic_rmf_merger(combined_rmf, item, index)

        combined_rmf = pd.merge(combined_rmf, allowance_list, on='user_id')
        del combined_rmf['allowance']

        user_frame = pd.DataFrame(user_list, columns=['user_id'])
        combined_rmf = pd.merge(user_frame, combined_rmf, how='outer', on='user_id')

        for col in combined_rmf:
            if "recency" in col:  # Fill missing Recency by it the upper limit within date group
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

    def get_back_test_accuracy(self):
        pass

    def execute(self):
        h2o = self.get_h2o_client()

        # Prepare Background Entity Resource, from transaction / customer records depends
        user_list = self.get_user_list()
        time_range_response = self.get_total_time_window()
        last_date, _id, first_date = [time_range_response[x] for x in list(time_range_response)]

        # Prepare Time Based Resource, derived from first_date and last_date
        total_month_diff = self.get_month_diff(first_date, last_date)
        time_shift = self.get_supervising_time_window(total_month_diff)
        training_month_diff = total_month_diff - time_shift
        prediction_month_diff = time_shift
        turning_date = last_date - relativedelta(months=time_shift)
        second_date = first_date + relativedelta(months=time_shift)

        # Prepare Label
        class_attr = self.get_class_attributes(user_list=user_list, start_date=first_date,
                                               turning_date=turning_date, end_date=last_date,
                                               supervising_window_length=prediction_month_diff)

        training = self.get_descriptive_attributes(user_list=user_list, start_date=first_date,
                                                   end_date=turning_date,
                                                   total_window_length=training_month_diff,
                                                   supervising_window_length=time_shift)

        for_prediction = self.get_descriptive_attributes(user_list=user_list, start_date=second_date,
                                                         end_date=last_date,
                                                         total_window_length=training_month_diff,
                                                         supervising_window_length=time_shift)

        training_frame1 = h2o.H2OFrame(python_obj=pd.merge(training, class_attr, how='outer', on='user_id'))
        training_frame, testing_frame = training_frame1.split_frame(
            ratios=[0.9],
            seed=123461
        )
        self.gc_list += [training_frame, ]

        prediction_frame = h2o.H2OFrame(python_obj=for_prediction)
        self.gc_list += [prediction_frame, ]

        model = H2ORandomForestEstimator(
            model_id="rf_covType_v2",
            ntrees=50,
            max_depth=30,
            col_sample_rate_per_tree=0.95,
            stopping_rounds=10,
            stopping_tolerance=0.01,
            score_each_iteration=True,
            nfolds=5,
            seed=3000000)

        model.train(x=training_frame.columns, y='clv', training_frame=training_frame)
        self.gc_list += [model, ]
        prediction_result = model.predict(prediction_frame)
        prediction_frame['predict_clv'] = prediction_result['predict']
        # training_frame['predict_clv'] = prediction_result['predict']
        _allowance = 0.1

        # median = training_frame["clv"].median()[0]
        # low_med = training_frame[training_frame["clv"] <= median, "clv"].median()[0]
        # high_med = training_frame[training_frame["clv"] > median, "clv"].median()[0]

        # print("Score 1:")
        # print(
        #          (training_frame['clv'] > high_med) & (training_frame['predict_clv'] > high_med) |
        #          ((high_med >= training_frame['clv']) & (training_frame['clv'] > median)) & ((
        #              high_med >= training_frame['predict_clv']) & (training_frame['predict_clv'] > median)) |
        #          ((median >= training_frame['clv']) & (training_frame['clv'] > low_med)) & (
        #              (median >= training_frame['predict_clv']) & (training_frame['predict_clv'] > low_med)) |
        #          (training_frame['clv'] <= low_med) & (training_frame['predict_clv'] <= low_med)).sum() / len(
        #     training_frame)
        #
        # print("Score 2:")
        # print(
        #     (abs(training_frame['clv'] - training_frame['predict_clv']) < training_frame['clv'] * _allowance) |
        #     (abs(training_frame['clv'] - training_frame['predict_clv']) < training_frame['std_monetary_amount']) |
        #     (abs(training_frame['clv'] - training_frame['predict_clv']) < 10)
        # ).sum() / len(training_frame)
        # print(model)

        # Set response to the list of leavers' user_id
        self.response = prediction_frame[prediction_result['predict'] == '0'].as_data_frame()['user_id'].tolist()
        map(lambda _x: h2o.remove(_x), self.gc_list)

    def event_init(self):
        """
        EntityStatsEngine Does not init event (For the time beings?)
        :return:
        """
        spec = CONSTANTS.JOB.EVENT_SPEC.get('H2O.Leaving')

        leaving_user_list = self.response
        # print(leaving_user_list)

        pipeline = [
            {"$unwind": "$data"},
            {"$match": {
                "data.User_ID": {"$in": leaving_user_list}
            }},
            {
                "$group": {
                    "_id": "$data.User_ID",
                    "monetary_amount": {"$sum": "$data.Transaction_Value"},
                    "frequency": {"$sum": 1},
                    "first_purchase_date": {"$min": "$data.Transaction_Date"},
                    "last_purchase_date": {"$max": "$data.Transaction_Date"},
                }
            }
        ]

        # base_leaving_user_profile = Entity.objects(group=self.group, type='transaction').aggregate(*pipeline)


        def get_event_value():
            captured_user = len(leaving_user_list)

            """
            :return: VAO
            """
            pass

        def get_event_desc():
            """
            Retrieving corresponding value in event_desc/ detailed_event_desc
            :return:
            """

        def get_analysis_desc():
            """
            Like getting model feedback
            :return:
            """

        def get_chart():
            """

            :return:
            """

        # "event_value": "vao",
        # "event_desc": [
        #                   "captured_user", "average_value_change_per_user", "expiry_date"
        #               ],
        # "detailed_event_desc": [
        #                            "average_transaction_value_per_user", "average_transaction_quantity_per_user",
        #                            "most_popular_product"
        #                        ],
        # "analysis_desc": [
        #                      "back_test_accuracy", "training_set_customer", "testing_set_customer",
        #                      "training_set_transaction",
        #                      "testing_set_transaction"
        #                  ],
        # "chart_type": "Line",
        # "chart": "H2O.Leaving"
        return
