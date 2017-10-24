from eledata.core_engine.base_engine import BaseEngine
from eledata.models.watcher import Watcher
import pandas as pd
from project.settings import CONSTANTS
from dateutil.relativedelta import relativedelta
import datetime
from eledata.serializers.event import GeneralEventSerializer
from bson import objectid


class Question37Engine(BaseEngine):
    IMG_PATH = 'temp/img'
    search_key = None
    result_list = None
    platform = None

    def __init__(self, group, params, keyword_list):
        super(Question37Engine, self).__init__(group, params)
        self.search_key = keyword_list

    def execute(self):
        """
        Fetching products data by aggregation, with search_keyword in from self.search_key (list)
        :return:
        """

        # Querying from MongoDB. Grouping by sku_id, search_keyword and platform
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "sku_id": "$sku_id",
                        "search_keyword": "$search_keyword",
                        "platform": "$platform",
                        # Grouping by seller name in MongoDB or pandas
                        # "seller_name": "$seller_name",
                    },

                    # For simplicity, we extract the id content here, assumed identical
                    "sku_id": {"$first": "$sku_id"},
                    "search_keyword": {"$first": "$search_keyword"},
                    "platform": {"$first": "$platform"},

                    "count": {"$first": 1}
                    ,
                    "max_final_price": {"$max": "$default_price"},
                    "mean_final_price": {"$avg": "$default_price"},
                    "min_final_price": {"$min": "$default_price"},

                    "max_comments_count": {"$max": "$comments_count"},
                    "mean_comments_count": {"$avg": "$comments_count"},
                    "min_comments_count": {"$min": "$comments_count"},

                    # Assumed the below fields are identical
                    "product_name": {"$first": "$product_name"},
                    "item_url": {"$first": "$item_url"},
                    "seller_name": {"$first": "$seller_name"},
                    "seller_url": {"$first": "$seller_url"},
                    "images": {"$first": "$images"},
                }
            }
        ]
        self.response = list(Watcher.objects(search_keyword__in=self.search_key, group=self.group).aggregate(*pipeline))

    def event_init(self):
        responses = []
        raw_product_data = self.response
        product_data = pd.DataFrame(raw_product_data)

        event_id = objectid.ObjectId()
        for keyword in self.search_key:
            selected_product_data = product_data[product_data['search_keyword'] == keyword].copy()

            selected_product_data['images'].apply(lambda x: x[0])

            # Compressing df by seller_url in pandas in case
            selected_product_data = selected_product_data.groupby('seller_name').agg({
                "sku_id": ['first'],
                "search_keyword": ['first'],
                "platform": ['first'],
                "count": ['sum'],
                "max_final_price": ['max'],
                "mean_final_price": ['mean'],
                "min_final_price": ['min'],

                "max_comments_count": ['max'],
                "mean_comments_count": ['mean'],
                "min_comments_count": ['min'],
                # Assumed the below fields are identical
                "product_name": ['first'],
                "item_url": ['first'],
                "seller_name": ['first'],
                "seller_url": ['first'],
                "images": ['first'],
            }).reset_index()

            # Flatten hierarchical index in columns
            selected_product_data.columns = selected_product_data.columns.get_level_values(0)

            # Break event saving for empty data frame, no corresponding records in watcher.
            if selected_product_data.empty:
                # TODO: report for mission abort?
                continue

            # Get seller with lowest price
            lowest_price_seller = selected_product_data.loc[
                selected_product_data['min_final_price'] == selected_product_data['min_final_price'].min()]

            # Get seller with highest price
            highest_price_seller = selected_product_data.loc[
                selected_product_data['max_final_price'] == selected_product_data['max_final_price'].max()]

            # Get seller with most comments
            popular_seller = selected_product_data.loc[
                selected_product_data['max_comments_count'] == selected_product_data['max_comments_count'].max()]

            # Get seller with least comments
            unpopular_seller = selected_product_data.loc[
                selected_product_data['min_comments_count'] == selected_product_data['min_comments_count'].min()]

            # Construct response
            responses.append(
                {
                    "event_id": event_id,
                    "event_category": CONSTANTS.EVENT.CATEGORY.get("INSIGHT"),
                    "event_type": "question_37",
                    "event_value": self.get_event_value(selected_product_data),
                    "event_desc": self.get_event_desc(selected_product_data, lowest_price_seller),
                    "detailed_desc": self.get_detailed_desc(highest_price_seller, popular_seller, unpopular_seller),
                    "analysis_desc": self.get_analysis_desc(),
                    "chart_type": "Table",  # For the time being
                    "chart": {},
                    "tabs": {
                        "keyword": self.search_key,
                    },
                    "selected_tab": {
                        "keyword": keyword,
                    },
                    "detailed_data": self.transform_detailed_data(selected_product_data),
                    "event_status": CONSTANTS.EVENT.STATUS.get('PENDING'),
                }
            )

        serializer = GeneralEventSerializer(data=responses, many=True)
        if serializer.is_valid():
            # for _data in serializer.validated_data:
            _data = serializer.create(serializer.validated_data)
            for data in _data:
                data.group = self.group
                data.save()
        else:
            # TODO: report errors
            print(serializer.errors)

    @staticmethod
    def get_event_value(selected_product_data):
        product_count = selected_product_data['count'].sum()
        return dict(key="captured_products", value=product_count)

    @staticmethod
    def get_event_desc(selected_product_data, lowest_price_seller):
        product_count = selected_product_data['count'].sum()
        reseller_count = len(selected_product_data)
        lowest_price_seller_name = lowest_price_seller.iloc[0]['seller_name']
        lowest_price = lowest_price_seller.iloc[0]['min_final_price']
        return [
            {
                "key": "product_count",
                "value": product_count
            },
            {
                "key": "reseller_count",
                "value": reseller_count
            },
            {
                "key": "lowest_price_seller_name",
                "value": lowest_price_seller_name
            },
            {
                "key": "lowest_price",
                "value": lowest_price
            }
        ]

    @staticmethod
    def get_detailed_desc(highest_price_seller, popular_seller, unpopular_seller):

        highest_price_seller_name = highest_price_seller.iloc[0]['seller_name']
        highest_price = highest_price_seller.iloc[0]['max_final_price']

        popular_seller_name = popular_seller.iloc[0]['seller_name']
        popular_comments = popular_seller.iloc[0]['max_comments_count']

        unpopular_seller_name = unpopular_seller.iloc[0]['seller_name']
        unpopular_comments = unpopular_seller.iloc[0]['min_comments_count']
        return [
            {
                "key": "highest_price_seller_name",
                "value": highest_price_seller_name
            },
            {
                "key": "highest_price",
                "value": highest_price
            },
            {
                "key": "popular_seller_name",
                "value": popular_seller_name
            },
            {
                "key": "popular_comments",
                "value": popular_comments
            },
            {
                "key": "unpopular_seller_name",
                "value": unpopular_seller_name
            },
            {
                "key": "unpopular_comments",
                "value": unpopular_comments
            }
        ]

    @staticmethod
    def get_analysis_desc():
        next_update_time = datetime.datetime.now() + relativedelta(days=1)
        return [dict(key="next_update_time", value=next_update_time.strftime("%Y-%m-%d %H:%M:%S"))]

    @staticmethod
    def transform_detailed_data(detailed_data):
        """
        Transform the supplied DF to a python structure with fields matching the Event model
        :param detailed_data: DataFrame, targeted customer records, should be output from get_detailed_data
        :return: python structure matching the Event model, contains detailed data
        """

        results = {"data": detailed_data.to_dict(orient='records'), "columns": []}

        # Column setting
        for field in ["images", "product_name", "seller_name", "platform", "min_final_price",
                      "mean_final_price", "max_final_price", "mean_comments_count"]:
            results["columns"].append(
                {
                    "key": field,
                    "sortable": True,
                    "label": field,
                }
            )
        return results
