# coding:utf-8
from eledata.core_engine.base_engine import BaseEngine
from eledata.models.watcher import Watcher
import pandas as pd
from project.settings import CONSTANTS
from dateutil.relativedelta import relativedelta
import datetime
from eledata.serializers.event import GeneralEventSerializer
from bson import objectid


class Question36Engine(BaseEngine):
    """
    get dictionary=[
    {"mine":["HTC VIVE"],
     "competitors":["SAMSUNG Gear VR 5","SAMSUNG Gear VR 4"]
    },
    {"mine":["暴风魔镜"],
     "competitors":[“小米VR PLAY2”,"小米VR眼镜"]
    }]
    """
    mine_keylist = None
    dic = [
    {"mine": u"HTC VIVE",
     "competitors": ["SAMSUNG Gear VR 5", "SAMSUNG Gear VR 4"]
    },
    {"mine": u"暴风魔镜S1",
     "competitors": ["小米VR PLAY2", "小米VR眼镜"]
    }]
    competitors_keylist = []
    excute_results = []

    def __init__(self, group, params, mine_keylist):
        super(Question36Engine, self).__init__(group, params)
        self.mine_keylist = mine_keylist
        for item in self.dic:
            if item["mine"] in mine_keylist:
                self.competitors_keylist.append(item["competitors"])

    def execute(self):
        """
        Get products from db, and search_keyword in competitors_keylist , two layer [[the first line in dashboard],[the sencond line in dashboard]]
        :return:
        """
        pipeline = [
            {"$sort": {"last_crawling_timestamp": -1}},
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

                    # Showing latest time in table instead
                    "latest_updated_price": {"$first": "$default_price"},
                    "latest_comment_count": {"$first": "$comments_count"},
                    "latest_updated_time": {"$first": "$last_crawling_timestamp"},

                    # TODO: get mini chart from price_trend pushed column
                    # "price_trend": {
                    #     "$push": {
                    #         "price": "$default_price",
                    #         "time": "$last_crawling_timestamp"
                    #     }
                    # },
                    # We keep summary stats for more detailed presentation
                    "max_final_price": {"$max": "$default_price"},
                    # "mean_final_price": {"$avg": "$default_price"},  DEPRECATED
                    "min_final_price": {"$min": "$default_price"},

                    "max_comments_count": {"$max": "$comments_count"},
                    # "mean_comments_count": {"$avg": "$comments_count"},  DEPRECATED
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

        for item in self.competitors_keylist:
            competitors_list = list(Watcher.objects(search_keyword__in=item).aggregate(*pipeline))
            self.excute_results.append(competitors_list)

