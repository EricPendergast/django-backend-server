import json
from operator import itemgetter
from itertools import groupby
from eledata.core_engine.base_engine import BaseEngine
from eledata.models.watcher import Watcher


class Question37Engine(BaseEngine):

    search_key = None
    result_list = None
    platform = None

    def __init__(self, group, params, keyword_list):
        super(Question37Engine, self).__init__(group, params)
        self.search_key = keyword_list

    def execute(self):
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "sku_id": "$sku_id",
                        "search_keyword": "$search_keyword",
                        "platform": "$platform",
                    },
                    "count": {"$sum": 1},
                    "max_final_price": {"$max": "$default_price"},
                    "mean_final_price": {"$avg": "$default_price"},
                    "min_final_price": {"$min": "$default_price"},

                    "max_comments_count": {"$max": "$comments_count"},
                    "mean_comments_count": {"$avg": "$comments_count"},
                    "min_comments_count": {"$min": "$comments_count"},

                    # Assumed the below fields are identical
                    "product_name": {"$first": "product_name"},
                    "item_url": {"$first": "item_url"},
                    "seller_name": {"$first": "seller_name"},
                    "seller_url": {"$first": "seller_url"},
                }
            }
        ]
        self.response = list(Watcher.objects(search_keyword__in=self.search_key).aggregate(*pipeline))
        # TODO: continue with the above response

    def event_init(self):
        pass

    def manage(self):
        before_mana_list = self.result_list
        # this level by key
        data = []
        escevent = []
        escdetailed = []
        for index, item_by_key in enumerate(before_mana_list):
            product = self.search_key[index]
            subdata = []
            '''
            seller name based grouping
            '''
            item_by_key.sort(key=itemgetter('seller_name'))
            comment_all_list = []
            for item in item_by_key:
                comment_all_list.append({
                    "sku_id": item["sku_id"],
                    "comments": item["comments_count"]
                })
            comments_sku_list = []
            comment_all_list.sort(key=itemgetter('sku_id'))
            for sku_id, items in groupby(comment_all_list, key=itemgetter('sku_id')):
                # print sku_id

                comments_list = []
                for item in items:
                    comments_list.append(item["comments"])
                high_comments = max(comments_list)
                low_comments = min(comments_list)
                # av_comments = statistics.mean(comments_list)
                comment_sku={
                    "sku_id": sku_id,
                    "high_comments": high_comments,
                    "low_comments": low_comments,
                    # "av_comments": av_comments,
                }
                comments_sku_list.append(comment_sku)
            for seller_name, items in groupby(item_by_key, key=itemgetter('seller_name')):
                """
                Shop data Dic
                """
                # product_icon = items[0]['images'][0]
                _seller_name = seller_name
                price_list = []
                time_list = []
                count = 0
                for item in items:
                    price = float(item['default_price'])
                    price_list.append(price)
                    sales = item['comments_count']
                    count = count + sales
                    time = {
                        "sku_id": item['sku_id'],
                        "time": item['last_crawling_timestamp']
                    }
                    time_list.append(time)
                price_f = min(price_list)
                price_t = max(price_list)
                # price_a = statistics.mean(price_list)

                subdata.append({
                    # "product_icon": product_icon,
                    "seller_name": _seller_name,
                    "price_from": price_f,
                    "price_to": price_t,
                    # "price_a": price_a,
                    "sales": count
                })
                """
                manage data
                """
                # best seller
                sales_list = []
                price_list = []
                price_top_list = []
                price_lower_list = []
                for item in subdata:
                    sales_list.append(item["sales"])
                    price_list.append(item["price_a"])
                    price_top_list.append(item["price_to"])
                    price_lower_list.append(item["price_from"])
                # best_sales_value = statistics.mean(sales_list)
                cheapest_value = min(price_list)
                # av_price_alltime = statistics.mean(price_list)
                top_price_alltime = max(price_top_list)
                lower_pirce_alltime = min(price_lower_list)
                for item in subdata:
                    # if item["sales"] == best_sales_value:
                    #     best_seller = item["seller_name"]
                    if item["price_a"] == cheapest_value:
                        cheapest_seller = item["seller_name"]
                eventdesc_by_key = {
                    # "best_seller": best_seller,
                    # "best_comment_value": best_sales_value,
                    "cheapest_seller": cheapest_seller,
                    "cheapest_seller_value": cheapest_value
                }
                detaileddesc_by_key={
                    # "av_price_alltime": av_price_alltime,
                    "top_price_alltime": top_price_alltime,
                    "lower_pirce_alltime": lower_pirce_alltime,
                    "comments": comments_sku_list
                }

            data.append({
                "product": product,
                "subData": subdata
            })
            escevent.append({
                "product": product,
                "esc": eventdesc_by_key
            })
            escdetailed.append({
                "product": product,
                "esc": detaileddesc_by_key
            })

            analysisdesc = [
                                {
                                    "key": "Data Processing Time",
                                    "value": "2.4 hr"
                                },
                                {
                                    "key": "Captured Product Data",
                                    "value": "5,400"
                                }
                            ],


        dic = {
            "subHeader": "Price range for products being sold by my competitors",
            "eventValue": "Distinct Products: 3",
            "eventDesc": escevent,
            "detailedEventDesc": escdetailed,
            "analysisDesc": analysisdesc,
            "chartType": "MultiTables",
            "chart": {},
            "detailedData": {
                "data": data,
                "columns": []
            }
        }

        print dic
        text_file = open("Output.csv", "w")
        text_file.write(json.dumps(dic))
        text_file.close()
