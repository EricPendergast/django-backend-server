from eledata.core_engine.base_engine import BaseEngine
from eledata.models.watcher import Watcher
import pandas as pd
from project.settings import CONSTANTS
from dateutil.relativedelta import relativedelta
import datetime
import statistics
from eledata.serializers.watcher import GeneralWatcherSerializer



class Question34Engine(BaseEngine):
    """
    mine = [mine searchkeyword]
    competitors = [competitors]
    category = [seach what for mine and competitors]
    mine_sku_list = [a list of sku_id for mine]
    competitors_sku_list = [ a list of competitors sku_id]
    platform = [a list of platform]
    """
    mine = None
    competitors = None
    category = None
    mine_sku_list = None
    competitors_sku_list = None
    platform = None

    def __init__(self, group, params, mine, competitors, category):
        super(Question34Engine, self).__init__(group, params)
        self.mine = mine
        self.competitors = competitors
        self.category = category
        self.platform = ['JD','Tao']

    # return mine sku_list
    def get_mine(self):
        mine_sku_list = Watcher.objects(search_keyword__in=self.mine).fields(sku_id=1)
        self.mine_sku_list = sorted(set([x['sku_id'] for x in mine_sku_list]))

    # return competitors sku_list
    def get_competitors(self):

        competitors_sku_list = Watcher.objects(search_keyword__in=self.competitors).fields(sku_id=1)
        self.competitors_sku_list = sorted(set([x['sku_id'] for x in competitors_sku_list]))

    #  return serch_order list by platform
    def get_orderlsit(self,selected_platform):
        if selected_platform == "JD":
            return ['default', 'integrated', 'price', 'sales', 'hot', 'new', ]
        if selected_platform == 'Tao':
            return ['default', 'integrated', 'price', 'sales', 'hot', 'credit']





    def execute(self):
        # 1. get the first page of platform
        self.get_mine()
        self.get_competitors()

    def check_list(self,list):
        if not list:
            return [-1]
        else:
            return list

    def do_data(self, list):
        """
        :param list: the list that 60 product detailed items
        :return:  the desc of the 60 product items
        """
        product_data = pd.DataFrame(list)
        #1. captured products
        mine_list_l = []
        competitors_list_l = []
        price_list_l = []
        comment_list_l = []
        price_list_mine= []
        comments_list_mine = []
        price_list_competitors = []
        comments_list_copetitors = []
        for item in list:
            comment_list_l.append(item["comments_count"])
            price_list_l.append(item['default_price'])
            if "relationship" in item and item["relationship"] == "mine":
                mine_list_l.append(item["search_rank"])
                price_list_mine.append(item["default_price"])
                comments_list_mine.append(item["comments_count"])
            if "relationship" in item and item["relationship"] == "competitor":
                competitors_list_l.append(item["search_rank"])
                price_list_competitors.append(item["default_price"])
                comments_list_copetitors.append(item["comments_count"])
        mine_list_l = self.check_list(mine_list_l)
        competitors_list_l = self.check_list(competitors_list_l)
        price_list_l = self.check_list(price_list_l)
        comment_list_l = self.check_list(comment_list_l)
        price_list_mine = self.check_list(price_list_mine)
        comments_list_mine = self.check_list(comments_list_mine)
        price_list_competitors = self.check_list(price_list_competitors)
        comments_list_copetitors = self.check_list(comments_list_copetitors)
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
        firstpage_status_all = {
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
            "max_comments": max(comments_list_copetitors),
            "min_comments": min(comments_list_copetitors),
            "mean_comments": statistics.mean(comments_list_copetitors)
        }

        firstpage_status_mine = {
            "price":price_status_mine,
            "comments":comments_status_mine
        }
        firstpage_status_competitors = {
            "price":price_status_competitors,
            "comments":comments_status_competitors
        }
        detailed = {
            "firstpage_status_all":firstpage_status_all,
            "firstpage_status_mine":firstpage_status_mine,
            "firstpage_status_competitors":firstpage_status_competitors
        }
        desc_order_platform = {
            "detailed": detailed,
            "captured_products": captured_products
        }
        return desc_order_platform


    def event_init(self):
        for selected_platform in self.platform:
            _order_list = self.get_orderlsit(selected_platform)
            for order in _order_list:
                category_list = Watcher.objects(search_order=order, search_keyword__in=self.category, platform=selected_platform).order_by('-last_crawling_timestamp').limit(60)
                serializer = GeneralWatcherSerializer(category_list, many=True)
                if serializer.data:
                    for item in serializer.data:
                        if item["sku_id"] in self.mine_sku_list:
                            item["relationship"] = "mine"
                        elif item["sku_id"] in self.competitors_sku_list:
                            item["relationship"] = "competitor"
                        else:
                            item["relationship"] = ""
                    data = self.do_data(serializer.data)
                    desc_data = {
                        "platform": selected_platform,
                        "order": order,
                        "data": data
                    }

                    DESC =  {
                            "event_category": CONSTANTS.EVENT.CATEGORY.get("INSIGHT"),
                            "event_type": "question_34",
                            "event_value": desc_data["data"]["captured_products"],
                            "event_desc": len(desc_data["data"]["captured_products"]["mine"]),
                            "detailed_desc":  desc_data["data"]["detailed"],
                            "analysis_desc": "",
                            "chart_type": "Table",  # For the time being
                            "chart": {},
                            "tabs": {
                                "keyword": _order_list,
                            },
                            "selected_tab": {
                                "keyword": desc_data["order"],
                            },
                            "detailed_data": serializer.data,
                            "event_status": CONSTANTS.EVENT.STATUS.get('PENDING'),
                        }
                    serializer = GeneralWatcherSerializer(data=DESC, many=True)
                    if serializer.is_valid():
                        # for _data in serializer.validated_data:
                        _data = serializer.create(serializer.validated_data)
                        for data in _data:
                            data.group = self.group
                            data.save()
                    else:
                        # TODO: report errors
                        print(serializer.errors)






