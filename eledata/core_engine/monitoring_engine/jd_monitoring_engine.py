# coding:utf-8
import re
import urllib2
from bs4 import BeautifulSoup
import uuid
from selenium import webdriver
import time
from .monitoring_engine import MonitoringEngine
from datetime import datetime


class JDMonitoringEngine(MonitoringEngine):
    keyword = None
    url = None
    results = []
    param_dict = {}
    url_list =[]
    request_page = None
    limit_current = None
    limit_total = None
    # TODO add class variable locations (array of string)
    # 深圳　北京　上海　廣州　杭州　南京　武漢　廈門　天津　蘇州
    supported_locations = [
        {'name': 'ShenZhen', 'id': '19_1607_3638_0'},
        {'name': 'BeiJing', 'id': '1_72_2839_0'},
        {'name': 'ShangHai', 'id': '2_2813_51976_0'},
        {'name': 'GuangZhou', 'id': '19_1601_3634_0'},
        {'name': 'HangZhou', 'id': '15_1213_3408_0'},
        {'name': 'NanJing', 'id': '12_904_3376_0'},
        {'name': 'WuHan', 'id': '17_1381_50718_0'},
        {'name': 'XiaMen', 'id': '16_1315_1316_53522'},
        {'name': 'TianJin', 'id': '3_51040_2986_0'},
        {'name': 'Suzhou', 'id': '12_988_4346_0'},
    ]
    locations = []

    """
    Overriding abstract functions for initialization
    """

    def set_searching_url(self, keyword, _page):
        _url = 'https://search.jd.com/Search?keyword=CHANGEME&enc=utf-8'
        self.url = _url.replace('CHANGEME', keyword)
        for num in range(1, _page * 2 + 1, 2):
            self.url_list.append('https://search.jd.com/Search?keyword='+keyword+'&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&bs=1&wq=dell&page='+str(num)+'&s=1&click=0')

    def set_location(self, location):
        if location:
            self.locations = [item for item in self.supported_locations for y in location if item.get('name') == y]
        else:
            self.locations = self.supported_locations

    def set_cookie(self, _key_1, _key_2):
        """
        We do nothing here.
        """
        return

    """
    Engine/ Platform depending functions
    """

    def get_soup(self, _url=None, is_scroll=False):
        if not is_scroll:
            request = urllib2.Request(self.url)
            response = urllib2.urlopen(request, timeout=20)
            content = response.read()
            this_soup = BeautifulSoup(content, 'html.parser')
            return this_soup

        else:
            driver = webdriver.Chrome()
            driver.get(_url)

            def execute_times(times):
                for i in range(times + 1):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)

            execute_times(3)
            html = driver.page_source
            _soup = BeautifulSoup(html, 'html.parser')
            return _soup

    @staticmethod
    def read_url_detail(_http, _format):
        req_this = urllib2.Request(_http)
        this_html = urllib2.urlopen(req_this)
        this_content = this_html.read()
        this_soup = BeautifulSoup(this_content, _format)
        return this_soup

    def get_basic_info(self, soup):
        # get limit info
        limit_item = soup.find("div", class_='f-pager')
        self.limit_current = limit_item.find('b').text
        self.limit_total = limit_item.find('i').text
        # get details
        product_list = []
        lis = soup.find_all("li", class_='gl-item')

        for li in lis:
            stock_list = []
            img_list = []

            # get sku_id
            _data_pid = li.get("data-sku")

            # get final price in the list
            price_item = li.find('div', class_="p-price")
            final_price = price_item.strong.i.string

            # get seller name
            seller_item = li.find('div', class_="p-shop")
            seller_name = seller_item.find('a')['title']

            # get commit count
            commit_item = li.find('div', class_="p-commit")
            _commit_count = commit_item.strong.a.string

            # get img in list
            img_item = li.find('div', class_="p-img")
            img_div = img_item.find('a').find('img')
            img_src = img_div.get('src', False) or img_div.get('data-lazy-img', False)
            img_src = 'http:' + img_src

            file_name = str(uuid.uuid4())
            img_list.append(file_name)

            self.save_image(img_src, self.img_pth, file_name)

            _http = "http:" + '//item.jd.com/' + _data_pid + '.html'
            # get product name in list
            name_item = li.find('div', class_="p-name")
            product_name = name_item.find('a').find('em').text

            # get details form this line
            this_soup = self.read_url_detail(_http, 'html.parser')

            # save detail images to file
            detail_images = this_soup.find("ul", class_='lh')
            detail_image = detail_images.find_all('li')
            for detail_i in detail_image:
                img_detail_src = str(detail_i.find('img').get('src') or detail_i.find('img').get('data-lazy-img'))
                img_detail_src = 'http:' + img_detail_src

                detail_save_path = self.img_pth
                detail_file_name = str(uuid.uuid4())
                img_list.append(detail_file_name)
                self.save_image(img_detail_src, detail_save_path, detail_file_name)

            # get information from js
            ss = this_soup.find_all('script')[0:1]
            m = re.search(r"(?s)var\s+pageConfig\s*=\s*(\{.*?\});", str(ss))
            json_str = m.group(1)

            # get cat
            _a = re.search(r"cat: ([\[\d,\]]+),", json_str)
            _a_str = _a.group(1)[1:-1]

            # get vender id
            _ven = re.search(r"venderId:(\d+)", json_str)
            _vender_id = _ven.group(1)

            # get brand id
            _brand = re.search(r"brand: (\d+)", json_str)
            _brand_id = _brand.group(1)  # Better

            # shop_id
            _shop = re.search(r"shopId:\'(\d+)\'", json_str)
            _shop_id = _shop.group(1)

            # support
            _call_support = 'http://cd.jd.com/yanbao/v3?skuId=' + _data_pid + '&cat=' + _a_str + '&area=' + \
                            self.locations[0]['id'] + '&brandId=' + _brand_id
            yan_bao_info = self.auto_recovered_fetch_json(_call_support)
            support = []
            if yan_bao_info == {}:
                support = []
            else:
                yanbaolist = yan_bao_info[_data_pid]
                for item in yanbaolist:
                    for item_detail in item['details']:
                        support.append({
                            'support_name': item_detail['bindSkuName'],
                            'support_price': item_detail['price'],
                        })


            # suit
            _call_suit = 'http://c.3.cn/recommend?sku=' + _data_pid + '&cat=' + _a_str + '&area=' + \
                         self.locations[0]['id'] + '&methods=suitv2'
            suit_info = self.auto_recovered_fetch_json(_call_suit)
            suit_list = []
            suit_list_data = suit_info['suit']['data']

            if 'packList' in suit_list_data:
                src_suit_list = suit_info['suit']['data']['packList']

                for item in src_suit_list:
                    suit_name = item['packName']
                    suit_origin_price = item['packOriginalPrice']
                    suit_promo_price = item['packPromotionPrice']
                    suit_id = item['packId']
                    suit = {
                        'suit_name': suit_name,
                        'suit_origin_price': suit_origin_price,
                        'suit_promo_price': suit_promo_price,
                        'suit_id': suit_id,
                    }
                    suit_list.append(suit)

            # advertisements
            _call_ad = 'http://cd.jd.com/promotion/v2?skuId=' + _data_pid + '&area=' + self.locations[0]['id'] + '&shopId=' + _shop_id + '&venderId=' + _vender_id + '&cat=' + _a_str
            ad_info = self.auto_recovered_fetch_json(_call_ad)
            ad_info_text = []
            for g in ad_info['ads']:
                ad_info_text.append(g['ad'])
            # tips = []
            # for g in ad_info['tags']:
            #     tips.append(g['content'])

            # get stock value from locations
            for item in self.locations:
                tl = item['id']
                _call = 'http://c0.3.cn/stock?skuId=' + _data_pid + '&venderId=' + _vender_id + '&cat=' + _a_str + '&area=' + tl + '&buyNum=1&extraParam={%22originid%22:%221%22}'
                stock_info = self.auto_recovered_fetch_json(_call)
                stock = stock_info[u'stock'][u'stockDesc'].replace('<strong>', '').replace('</strong>', '')
                the_stock_value = {
                    'tn': item['name'],
                    'stock': stock
                }
                stock_list.append(the_stock_value)
            # create dic
            # TODO create a item that called suit can get suit information
            the_basic_info = {
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'platform': 'JD',
                'product_name': product_name,
                'seller_name': seller_name,
                'sku_id': _data_pid,
                'default_price': final_price,
                'final_price': 'No discount now',
                'item_url': _http,
                'comments_count': _commit_count,
                'img_pth': self.img_pth,
                'images': img_list,
                # 'cat': _astr,
                # 'vid': _vender_id,
                'current_stock': stock_list,
                'support': support,
                'advertisements': ad_info_text,
                # 'tips': tips
            }
            product_list.append(the_basic_info)
        self.results = product_list
        return product_list

    def out(self, _list):
        # print _list
        for i in _list:
            print "Title:", i['product_name']
            print "Product Id:", i['sku_id']
            print "Http:", i['item_url']
            print "Price:", i['default_price']
            print "Commit Count:", i['comments_count']
            for t in i['images']:
                print t + '.img'
            for y in i['current_stock']:
                print y['tn'], ":", y['stock']
            print '延保服务：'
            for item in i['support']:
                print '延保名称：', item['support_name'], '延保价格：', item['support_price']
            # maybe have some problems
            print '广告：'
            for g in i['advertisements']:
                print g
            # print 'tips:'
            print '\n'

    def get_multi_page(self):
        for item in self.url_list:
            _url = item
            soup = self.get_soup(_url=_url, is_scroll=True)
            t_list = self.get_basic_info(soup)
            # print self.limit_current, self.limit_total
            self.out(t_list)
            if self.limit_current == self.limit_total:
                break
            # self.put_db(t_list)