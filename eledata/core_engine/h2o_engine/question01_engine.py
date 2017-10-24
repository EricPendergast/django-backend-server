from .h2o_engine import H2OEngine
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from eledata.models.entity import Entity
from h2o.estimators.random_forest import H2ORandomForestEstimator
from project.settings import CONSTANTS
from eledata.verifiers.event import QuestionVerifier
from eledata.serializers.event import GeneralEventSerializer
from bson import objectid


class Question01Engine(H2OEngine):
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

        turning_date and end_date and match_obj.update({
            "data.Transaction_Date": {
                "$gte": turning_date,
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

    def get_back_test_accuracy(self, updated_training_frame):
        _allowance = 0.1
        return (
            ((abs(updated_training_frame['clv'] - updated_training_frame['predict_clv'])
              < updated_training_frame['clv'] * _allowance) |
             (abs(updated_training_frame['clv'] - updated_training_frame['predict_clv'])
              < 2 * updated_training_frame['std_monetary_amount']) |
             (abs(updated_training_frame['clv'] - updated_training_frame['predict_clv'])
              < 10)).sum() / len(updated_training_frame)
        )

    def execute(self):
        h2o = self.get_h2o_client()
        self.response = {}

        # Prepare Background Entity Resource, from transaction / customer records depends
        user_list = self.get_user_list()
        time_range_response = self.get_total_time_window()
        last_date, _id, first_date = [time_range_response[x] for x in list(time_range_response)]

        # Prepare Time Based Resource, derived from first_date and last_date
        total_month_diff = self.get_month_diff(first_date, last_date)
        time_shift = self.get_supervising_time_window(total_month_diff)
        training_month_diff = total_month_diff - time_shift
        turning_date = last_date - relativedelta(months=time_shift)
        second_date = first_date + relativedelta(months=time_shift)

        '''
        Prepare training data list
        '''
        loop_range = (training_month_diff + 1) / time_shift \
            if time_shift > 1 else training_month_diff

        historical_date_list = [last_date - relativedelta(months=i * time_shift) for i in range(loop_range + 1)]
        historical_date_list.append(first_date)
        self.response['historical_date_list'] = historical_date_list[::-1]
        self.response['time_shift'] = time_shift

        '''
        Prepare Label
        '''
        class_attr = self.get_class_attributes(user_list=user_list, start_date=first_date,
                                               turning_date=turning_date, end_date=last_date,
                                               supervising_window_length=time_shift)

        training = self.get_descriptive_attributes(user_list=user_list, start_date=first_date,
                                                   end_date=turning_date,
                                                   total_window_length=training_month_diff,
                                                   supervising_window_length=time_shift)

        for_prediction = self.get_descriptive_attributes(user_list=user_list, start_date=second_date,
                                                         end_date=last_date,
                                                         total_window_length=training_month_diff,
                                                         supervising_window_length=time_shift)

        '''
        Prepare for CV and Training
        '''
        training_frame = h2o.H2OFrame(python_obj=pd.merge(training, class_attr, how='outer', on='user_id'))
        # training_frame, testing_frame = training_frame1.split_frame(
        #     ratios=[0.9],
        #     seed=123461
        # )
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

        '''
        Prediction and Accuracy Testing
        '''
        prediction_result = model.predict(prediction_frame)
        prediction_frame['predict_clv'] = prediction_result['predict']
        training_frame['predict_clv'] = prediction_result['predict']

        self.response['r2'] = model.r2()
        self.response['prediction_frame'] = prediction_frame.as_data_frame().select(
            lambda col: col in ['user_id', 'predict_clv'], axis=1)
        self.response['accuracy'] = self.get_back_test_accuracy(updated_training_frame=training_frame)

        map(lambda _x: h2o.remove(_x), self.gc_list)

    def event_init(self):
        """
        EntityStatsEngine Does not init event (For the time beings?)
        :return:
        """
        '''
        Retrieving Intermediate Response 
        '''
        date_list = self.response.get('historical_date_list')
        time_shift = self.response.get('time_shift')
        prediction_frame = self.response.get('prediction_frame')

        '''
        Calculating historical profile
        '''
        branches = [
            {"case": {"$and": [
                {"$gte": [date_list[i + 2], "$data.Transaction_Date"]},
                {"$lt": [date_list[i + 1], "$data.Transaction_Date"]},
            ]}, "then": i} for i in range(len(date_list) - 2)
        ]
        branches.insert(0, {"case": {"$and": [
            {"$gte": [date_list[1], "$data.Transaction_Date"]},
            {"$lte": [date_list[0], "$data.Transaction_Date"]},
        ]}, "then": -1})
        pipeline = [
            {"$unwind": "$data"},
            {"$match": {
                "data.Transaction_Date": {
                    "$gte": date_list[0],
                    "$lte": date_list[-1]
                }
            }},
            {"$project": {
                "user_id": "$data.User_ID",
                "monetary_amount": {"$sum": "$data.Transaction_Value"},
                "recency": {"$max": "$data.Transaction_Date"},
                "monetary_quantity": {"$sum": "$data.Transaction_Quantity"},
                "transaction_date_group": {
                    "$switch": {
                        "branches": branches,
                        "default": -2
                    }
                }
            }},
            {
                "$group": {
                    "_id": {
                        "user_id": "$user_id",
                        "transaction_date_group": "$transaction_date_group"
                    },
                    "monetary_amount": {"$sum": "$monetary_amount"},
                    "frequency": {"$sum": 1},
                    "monetary_quantity": {"$sum": "$monetary_quantity"}
                }
            }
        ]

        '''
        Grouping historical data by month group, calculating sum and merging
        '''
        historical_data = list(Entity.objects(group=self.group, type='transaction').aggregate(*pipeline))
        historical_data = pd.DataFrame(historical_data)
        historical_profile = []
        for i in range(len(date_list) - 1):
            historical_data_subgroup = historical_data[historical_data['_id'].apply(
                lambda x: x[u'transaction_date_group']) == (i - 1)]
            historical_data_subgroup['user_id'] = historical_data_subgroup[u'_id'].apply(lambda x: x[u'user_id'])
            historical_data_subgroup['transaction_date_group'] = historical_data_subgroup[u'_id'].apply(
                lambda x: x[u'transaction_date_group'])
            del historical_data_subgroup[u'_id']

            # TODO: can we use pandas aggregation directly?
            historical_data_subgroup = historical_data_subgroup.groupby('user_id')
            t_profile = {
                'monetary_amount': historical_data_subgroup['monetary_amount'].sum() / time_shift,
                'frequency': historical_data_subgroup['frequency'].sum(),
                'monetary_quantity': historical_data_subgroup['monetary_quantity'].sum() / time_shift,
            }
            t_profile = pd.DataFrame(t_profile)
            t_profile.reset_index(level=0, inplace=True)
            t_profile['user_id'] = t_profile['user_id'].astype(str)
            t_profile = pd.merge(prediction_frame, t_profile, how='outer', on='user_id')
            t_profile = t_profile.fillna(value=0)
            historical_profile.append(t_profile)

        """
        calculate expiry date
        """
        d1 = datetime.date.today()
        d1 += relativedelta(days=(time_shift * 15))
        expiry_date = d1

        def get_event_value():
            return dict(key="predicted_revenue", value="{:,.2f}".format(prediction_frame['predict_clv'].sum()))

        def get_event_desc():
            predicted_revenue = prediction_frame['predict_clv'].sum()
            captured_user = prediction_frame.shape[0]

            returning_dict = [
                {
                    'key': 'predicted_revenue',
                    'value': "{:,.2f}".format(predicted_revenue)
                },
                {
                    'key': 'captured_user',
                    'value': "{:,}".format(captured_user)
                },
                {
                    'key': 'expiry_date',
                    'value': str(expiry_date)
                },
            ]
            return returning_dict

        def get_detail_desc():
            average_predicted_revenue = prediction_frame['predict_clv'].mean()
            average_historical_revenue = historical_profile[-1]['monetary_amount'].sum() / prediction_frame.shape[0]

            returning_dict = [
                {
                    'key': 'average_predicted_revenue',
                    'value': "{:,.2f}".format(average_predicted_revenue)
                },
                {
                    'key': 'average_historical_revenue',
                    'value': "{:,.2f}".format(average_historical_revenue)
                },
            ]
            return returning_dict

        def get_analysis_desc():
            accuracy = self.response.get('accuracy')
            # r2 = self.response.get('r2')
            training_customer_size = prediction_frame.shape[0]
            testing_customer_size = prediction_frame.shape[0] * 0.2
            training_transaction_size = sum([x['frequency'].sum() for x in historical_profile[:-1]])
            testing_transaction_size = sum([x['frequency'].sum() for x in historical_profile[:-1]]) * 0.2

            returning_dict = [
                {
                    'key': 'accuracy',
                    'value': "{:,.2f}".format(accuracy),
                    'isFullWidth': True
                },
                {
                    'key': 'testing_customer_size',
                    'value': "{:,}".format(training_customer_size)
                },
                {
                    'key': 'testing_transaction_size',
                    'value': "{:,}".format(testing_customer_size)
                },
                {
                    'key': 'training_customer_size',
                    'value': "{:,}".format(training_transaction_size)
                },
                {
                    'key': 'training_transaction_size',
                    'value': "{:,}".format(testing_transaction_size)
                }
            ]
            return returning_dict

        def get_chart():
            label_start_date = (date_list[1] - date_list[0]) / 2 + date_list[0]
            label_list = [label_start_date + relativedelta(months=(x * time_shift)) for x in range(len(date_list))]

            actual = {'data': [], 'border': False, 'label': 'actual '}
            prediction = {'data': [], 'border': True, 'label': 'prediction '}
            lower = {'data': [], 'border': False, 'label': 'lower '}
            higher = {'data': [], 'border': False, 'label': 'higher '}

            for x in historical_profile:
                _shape = x.shape[0]
                actual['data'] += [x['monetary_amount'].sum(), ]
                prediction['data'] += [None, ]
                lower['data'] += [x['monetary_amount'].quantile(.25) * _shape, ]
                higher['data'] += [x['monetary_amount'].quantile(.75) * _shape, ]

            prediction['data'][-1] = actual['data'][-1]
            actual['data'] += [None, ]
            prediction['data'] += [prediction_frame['predict_clv'].sum(), ]
            lower['data'] += [None, ]
            higher['data'] += [None, ]
            chart = {
                'labels': label_list,
                'y_label': 'totalRevenue',
                'x_label': 'transactionTime',
                'datasets': [actual, prediction, lower, higher],
                "x_stacked": False,
                "y_stacked": False
            }
            return chart

        event_dict = dict(
            event_id=objectid.ObjectId(),
            event_category=CONSTANTS.EVENT.CATEGORY.get('INSIGHT'),
            event_type='question_01',
            event_value=get_event_value(),
            event_desc=get_event_desc(),
            detailed_desc=get_detail_desc(),
            analysis_desc=get_analysis_desc(),
            chart_type='Line',
            chart=get_chart(),
            tabs={},
            selected_tab={},
            detailed_data=dict(
                data=[],
                columns=[]
            ),
            expiry_date=expiry_date,
            event_status=CONSTANTS.EVENT.STATUS.get('PENDING')
        )

        verifier = QuestionVerifier()
        serializer = GeneralEventSerializer(data=event_dict)
        verifier.verify(0, self.group)
        verifier.verify(1, serializer)
        event = serializer.create(serializer.validated_data)

        event.group = self.group
        event.save()
        return event_dict
