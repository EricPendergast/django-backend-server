import datetime
from dateutil.relativedelta import relativedelta

from eledata.core_engine.base_engine import BaseEngine
from eledata.models.watcher import Watcher
import pandas as pd

from eledata.serializers.event import GeneralEventSerializer
from project.settings import CONSTANTS
import statistics
from eledata.serializers.watcher import GeneralWatcherSerializer


class Question34Engine(BaseEngine):
    """
    :param = [mine searchkeyword]
    competitors = [competitors]
    category = [seach what for mine and competitors]
    mine_sku_list = [a list of sku_id for mine]
    competitors_sku_list = [ a list of competitors sku_id]
    platform = [a list of platform]
    """
    our_keyword_list = None
    competitor_keyword_list = None
    first_page_keyword_list = None
    our_sku_id_list = None
    competitor_sku_id_list = None
    platform = ['JD', 'TB']
    order_list = {
        "JD": ['integrated', 'price', 'sales', 'hot'],
        'TB': ['integrated', 'price', 'sales', 'hot']
    }

    def __init__(self, event_id, group, params, our_keyword_list, competitor_keyword_list, first_page_keyword_list):
        super(Question34Engine, self).__init__(event_id, group, params)
        self.our_keyword_list = our_keyword_list
        self.competitor_keyword_list = competitor_keyword_list
        self.first_page_keyword_list = first_page_keyword_list

    def set_our_sku_id_list(self):
        """
        Set our_sku_id_list by querying with our_keyword_list
        :return:
        """
        mine_sku_list = Watcher.objects(search_keyword__in=self.our_keyword_list).fields(sku_id=1)
        self.our_sku_id_list = sorted(set([x['sku_id'] for x in mine_sku_list]))

    def set_competitor_sku_id_list(self):
        """
        Set competitor_sku_id_list by querying with competitor_keyword_list
        :return:
        """
        competitors_sku_list = Watcher.objects(search_keyword__in=self.competitor_keyword_list).fields(sku_id=1)
        self.competitor_sku_id_list = sorted(set([x['sku_id'] for x in competitors_sku_list]))

    def execute(self):
        self.set_our_sku_id_list()
        self.set_competitor_sku_id_list()

    def check_list(self, _list):
        if not _list:
            return [-1]
        else:
            return _list

    def do_data(self, _list):
        """
        :param _list: the list that 60 product detailed items
        :return:  the desc of the 60 product items
        """
        # 1. captured products
        mine_list_l = []
        competitors_list_l = []
        price_list_l = []
        comment_list_l = []
        price_list_mine = []
        comments_list_mine = []
        price_list_competitors = []
        comments_list_competitors = []
        for item in _list:
            comment_list_l.append(item["comments_count"])
            price_list_l.append(item['default_price'])
            if "relationship" in item and item["relationship"] == "mine":
                mine_list_l.append(item["search_rank"])
                price_list_mine.append(item["default_price"])
                comments_list_mine.append(item["comments_count"])
            if "relationship" in item and item["relationship"] == "competitor":
                competitors_list_l.append(item["search_rank"])
                price_list_competitors.append(item["default_price"])
                comments_list_competitors.append(item["comments_count"])

        mine_list_l = self.check_list(mine_list_l)
        competitors_list_l = self.check_list(competitors_list_l)
        price_list_l = self.check_list(price_list_l)
        comment_list_l = self.check_list(comment_list_l)
        price_list_mine = self.check_list(price_list_mine)
        comments_list_mine = self.check_list(comments_list_mine)
        price_list_competitors = self.check_list(price_list_competitors)
        comments_list_competitors = self.check_list(comments_list_competitors)

        captured_products = {
            "mine": mine_list_l,
            "competitors": competitors_list_l
        }
        comments_status = {
            "max_comments": max(comment_list_l),
            "min_comments": min(comment_list_l),
            "mean_comments": statistics.mean(comment_list_l)
        }
        price_status = {
            "max_price": max(price_list_l),
            "min_price": min(price_list_l),
            "mean_price": statistics.mean(price_list_l)
        }
        first_page_status_all = {
            "price": price_status,
            "comments": comments_status
        }
        price_status_mine = {
            "max_price": max(price_list_mine),
            "min_price": min(price_list_mine),
            "mean_price": statistics.mean(price_list_mine)
        }
        comments_status_mine = {
            "max_comments": max(comments_list_mine),
            "min_comments": min(comments_list_mine),
            "mean_comments": statistics.mean(comments_list_mine)
        }
        price_status_competitors = {
            "max_price": max(price_list_competitors),
            "min_price": min(price_list_competitors),
            "mean_price": statistics.mean(price_list_competitors)
        }
        comments_status_competitors = {
            "max_comments": max(comments_list_competitors),
            "min_comments": min(comments_list_competitors),
            "mean_comments": statistics.mean(comments_list_competitors)
        }

        first_page_status_mine = {
            "price": price_status_mine,
            "comments": comments_status_mine
        }
        first_page_status_competitors = {
            "price": price_status_competitors,
            "comments": comments_status_competitors
        }
        detailed = {
            "first_page_status_all": first_page_status_all,
            "first_page_status_mine": first_page_status_mine,
            "first_page_status_competitors": first_page_status_competitors
        }
        desc_order_platform = {
            "detailed": detailed,
            "captured_products": captured_products
        }
        return desc_order_platform

    def event_init(self):
        final_data = []
        for selected_platform in self.platform:
            _order_list = self.order_list[selected_platform]
            for order in _order_list:
                our_rank_list = []
                competitor_rank_list = []
                category_list = Watcher.objects(search_order=order, search_keyword__in=self.first_page_keyword_list,
                                                platform=selected_platform).order_by('-last_crawling_timestamp').limit(
                    60)

                serializer = GeneralWatcherSerializer(category_list, many=True)
                if serializer.data:
                    for item in serializer.data:
                        if item["sku_id"] in self.our_sku_id_list:
                            item["relationship"] = "mine"
                            our_rank_list.append(item["search_rank"])
                        elif item["sku_id"] in self.competitor_sku_id_list:
                            item["relationship"] = "competitor"
                            competitor_rank_list.append(item["search_rank"])
                        else:
                            item["relationship"] = ""

                    product_data = serializer.data
                    event = {
                        "event_id": self.event_id,
                        "event_category": CONSTANTS.EVENT.CATEGORY.get("INSIGHT"),
                        "event_type": "question_34",
                        "event_value": dict(key="mine", value=', '.join(
                            map(lambda x: str(x), sorted(our_rank_list))) if our_rank_list else "---"),
                        "event_desc": self.get_event_desc(our_rank_list, competitor_rank_list),
                        "detailed_desc": self.get_detailed_desc(product_data),
                        "analysis_desc": self.get_analysis_desc(),
                        "chart_type": "Table",  # For the time being
                        "chart": {},
                        "tabs": {
                            "search_order": _order_list,
                            "platform": self.platform,
                        },
                        "selected_tab": {
                            "search_order": order,
                            "platform": selected_platform,
                        },
                        "detailed_data": self.transform_detailed_data(pd.DataFrame(product_data)),
                        "event_status": CONSTANTS.EVENT.STATUS.get('PENDING'),
                        "scheduled_at": datetime.datetime.now() + relativedelta(hours=12)
                    }
                    final_data.append(event)
                else:
                    # TODO: error report
                    pass
        serializer = GeneralEventSerializer(data=final_data, many=True)
        if serializer.is_valid():
            # for _data in serializer.validated_data:
            _data = serializer.create(serializer.validated_data)
            for data in _data:
                data.group = self.group
                data.save()
        else:
            # TODO: report errors
            print(serializer.errors)

    def get_event_desc(self, our_rank_list, competitor_rank_list, ):
        return [
            dict(key="mine", value=', '.join(
                map(lambda x: str(x), sorted(our_rank_list))) if our_rank_list else "---"),
            dict(key="competitors", value=', '.join(
                map(lambda x: str(x), sorted(competitor_rank_list))) if our_rank_list else "---"),
            dict(key="mine_count", value=len(our_rank_list)),
            dict(key="competitors_count", value=len(competitor_rank_list)),
        ]

    def get_detailed_desc(self, _list):
        price_list_l = []
        comment_list_l = []
        price_list_mine = []
        comments_list_mine = []
        price_list_competitors = []
        comments_list_competitors = []
        for item in _list:
            comment_list_l.append(item["comments_count"])
            price_list_l.append(item['default_price'])
            if "relationship" in item and item["relationship"] == "mine":
                price_list_mine.append(item["default_price"])
                comments_list_mine.append(item["comments_count"])
            if "relationship" in item and item["relationship"] == "competitor":
                price_list_competitors.append(item["default_price"])
                comments_list_competitors.append(item["comments_count"])

        detailed = [
            dict(key="comments_status_max_comments",
                 value=str(max(comment_list_l)) if comment_list_l else "---"),
            dict(key="comments_status_min_comments",
                 value=str(min(comment_list_l)) if comment_list_l else "---"),
            dict(key="comments_status_mean_comments",
                 value=str(statistics.mean(comment_list_l)) if comment_list_l else "---"),
            dict(key="price_status_max_price",
                 value=str(max(price_list_l)) if price_list_l else "---"),
            dict(key="price_status_min_price",
                 value=str(min(price_list_l)) if price_list_l else "---"),
            dict(key="price_status_mean_price",
                 value=str(statistics.mean(price_list_l)) if price_list_l else "---"),
            dict(key="price_status_mine_max_price",
                 value=str(max(price_list_mine)) if price_list_mine else "---"),
            dict(key="price_status_mine_min_price",
                 value=str(min(price_list_mine)) if price_list_mine else "---"),
            dict(key="price_status_mine_mean_price",
                 value=str(statistics.mean(price_list_mine)) if price_list_mine else "---"),
            dict(key="comments_status_mine_max_comments",
                 value=str(max(comments_list_mine)) if comments_list_mine else "---"),
            dict(key="comments_status_mine_min_comments",
                 value=str(min(comments_list_mine)) if comments_list_mine else "---"),
            dict(key="comments_status_mine_mean_comments",
                 value=str(statistics.mean(comments_list_mine)) if comments_list_mine else "---"),
            dict(key="price_status_competitors_max_price",
                 value=str(max(price_list_competitors)) if price_list_competitors else "---"),
            dict(key="price_status_competitors_min_price",
                 value=str(min(price_list_competitors)) if price_list_competitors else "---"),
            dict(key="price_status_competitors_mean_price",
                 value=str(statistics.mean(price_list_competitors)) if price_list_competitors else "---"),
            dict(key="comments_status_competitors_max_comments",
                 value=str(max(comments_list_competitors)) if comments_list_competitors else "---"),
            dict(key="comments_status_competitors_min_comments",
                 value=str(min(comments_list_competitors)) if comments_list_competitors else "---"),
            dict(key="comments_status_competitors_mean_comments",
                 value=str(statistics.mean(comments_list_competitors)) if comments_list_competitors else "---"),
        ]
        return detailed

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
        present_data = detailed_data.copy()
        del present_data['detail']
        del present_data['current_stock']
        del present_data['model']
        del present_data['sku_id']
        present_data['last_crawling_timestamp'].apply(lambda x: x.replace('T', ' ')[0: -7])

        results = {"data": present_data.sort_values('search_rank').to_dict(orient='records'), "columns": []}

        # Column setting
        for field in ['product_name', 'seller_name', 'default_price', 'search_rank',
                      'last_crawling_timestamp', 'comments_count', 'sales_count']:
            results["columns"].append(
                {
                    "key": field,
                    "sortable": True,
                    "label": field,
                }
            )
        return results
