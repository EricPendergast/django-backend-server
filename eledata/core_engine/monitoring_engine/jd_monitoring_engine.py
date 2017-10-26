# coding:utf-8
import re
import urllib2

from bs4 import BeautifulSoup
from selenium import webdriver
import time
from .monitoring_engine import MonitoringEngine
from datetime import datetime
from eledata.serializers.watcher import GeneralWatcherSerializer


class JDMonitoringEngine(MonitoringEngine):
    keyword = None
    url = None
    results = []
    param_dict = {}
    url_list = []
    order_list = []

    ORDER_MAPPING = {
        'integrated': '&psort=1',
        'price': '&psort=2',
        'sales': '&psort=3',
        'hot': '&psort=4',
        'new': '&psort=5',
    }
    # 深圳　北京　上海　廣州　杭州　南京　武漢　廈門　天津　蘇州
    SUPPORTED_LOCATIONS = [
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
    # TODO add class variable locations (array of string)

    """
    Overriding Environment Setting Functions
    """
    def set_searching_url(self, _keyword, _page_limit, _order):
        _url = 'https://search.jd.com/Search?keyword=CHANGEME&enc=utf-8'
        self.url = _url.replace('CHANGEME', _keyword)
        for num in range(1, _page_limit * 2 + 1, 2):
            if not _order:
                self.url_list.append('https://search.jd.com/Search?keyword=' + _keyword +
                                     '&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&bs=1&wq=dell&page=' +
                                     str(num) + '&s=1&click=0')
                self.order_list.append('default')
            else:
                for order in _order:
                    self.url_list.append('https://search.jd.com/Search?keyword=' + _keyword +
                                         '&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&bs=1&wq=dell&page=' + str(num) +
                                         '&s=1&click=0' + self.ORDER_MAPPING.get(order))
                    self.order_list.append(order)

    def set_location(self, _location=None):
        """
        Choosing what locations to be monitored. Monitoring all 10 supported by default.
        :param _location: list, locations params to be monitored
        :return:
        """
        if _location:
            self.locations = [item for item in self.SUPPORTED_LOCATIONS for y in _location if item.get('name') == y]
        else:
            self.locations = self.SUPPORTED_LOCATIONS
        pass

    def set_cookie(self, _key_1, _key_2):
        self.driver = webdriver.PhantomJS(executable_path=r'constants/phantomjs')  # Prefer phantom over chrome in production
        return

    """
    Overriding Monitoring Core Functions
    """
    def get_soup(self, _url):
        self.driver = webdriver.Chrome()
        driver = self.driver
        driver.get(_url)

        def execute_times(times):
            for i in range(times + 1):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

        execute_times(3)
        html = driver.page_source
        _soup = BeautifulSoup(html, 'html.parser')
        return _soup

    def read_url_detail(self, _http, _format):
        # Direct urllib fetching
        req_this = urllib2.Request(_http)
        this_html = urllib2.urlopen(req_this)
        this_content = this_html.read()
        # # Selenium
        # driver = self.driver
        # driver.get(_http)
        # time.sleep(30)
        # this_content = driver.page_source　
        this_soup = BeautifulSoup(this_content, _format)
        return this_soup

    @staticmethod
    def comment_quantity_change(before_quantity):
        """
        Converting 1万 or 1.0万 to 10000.
        :param before_quantity:
        :return:
        """
        before_quantity = before_quantity.replace("+", "")
        if u'万' in before_quantity:
            if '.' in before_quantity:
                before_quantity = before_quantity.replace(".", "")
                before_quantity = before_quantity.replace(u'万', "000")
            else:
                before_quantity = before_quantity.replace(u'万', "0000")
        return int(before_quantity)

    def get_basic_info(self, soup, _current_order=None):
        product_list = []
        limit_item = soup.find("div", class_='f-pager')

        # Get limit (page number) from web page.
        self.limit_current = limit_item.find('span').find('b').text
        self.limit_total = limit_item.find('i').text

        # Get products
        ul = soup.find(lambda tag: tag.name == 'ul' and tag.get('class') == ['gl-warp', 'clearfix'])
        lis = ul.find_all("li", class_='gl-item')
        rank = 0

        for li in lis:
            try:
                rank = rank + 1
                stock_list = []
                img_list = []

                # Get product sku_id
                _data_pid = li.get("data-sku")

                # Get final price in the list
                price_item = li.find('div', class_="p-price")
                final_price = price_item.strong.i.string

                # Get seller name
                seller_item = li.find('div', class_="p-shop")
                # TODO: we can enhance it if have time
                try:
                    seller_name = seller_item.find('a').get('title', '')
                except:
                    seller_name = 'JD'
                try:
                    seller_url = 'http:' + seller_item.find('a').get('href', '')
                except:
                    seller_url = 'http://www.jd.com'

                # Get comment count
                comment_item = li.find('div', class_="p-commit")
                _comment_count = comment_item.strong.a.string
                comment_count = self.comment_quantity_change(_comment_count)

                # Get and save img in list
                img_item = li.find('div', class_="p-img")
                try:
                    img_src = 'http:' + str(img_item.find("a").find("img")['src'])
                except:
                    img_src = 'http:' + str(img_item.find("a").find("img")['data-lazy-img'])
                save_path = self.img_pth
                # file_name = self.save_image(img_src, save_path)
                img_list.append(img_src)
                _http = "http:" + '//item.jd.com/' + _data_pid + '.html'

                # Get product name in list
                name_item = li.find('div', class_="p-name")
                product_name = name_item.find('a').find('em').text

                # Get details form this line
                this_soup = self.read_url_detail(_http, 'html.parser')

                # Save and save detail images to file
                detail_imgs = this_soup.find("ul", class_='lh')

                if detail_imgs:
                    detail_img = detail_imgs.find_all('li')
                    for detail_i in detail_img:
                        try:
                            img_detail_src = 'http:' + str(detail_i.find('img')['src'])
                        except:
                            img_detail_src = 'http:' + str(detail_i.find('img')['data-lazy-img'])
                        detail_save_path = self.img_pth
                        # detail_file_name = self.save_image(img_detail_src, detail_save_path)
                        img_list.append(img_detail_src)

                # get information from js
                ss = this_soup.find_all('script')[0:1]
                strss = str(ss)
                m = re.search(r"(?s)var\s+pageConfig\s*=\s*(\{.*?\});", strss)
                jsonstr = m.group(1)
                # cat
                _a = re.search(r"cat: ([\[\d,\]]+),", jsonstr)
                _astr = _a.group(1)[1:-1]
                # venderid
                _ven = re.search(r"venderId:(\d+)", jsonstr)
                _venderid = _ven.group(1)
                # brandid
                _brand = re.search(r"brand: (\d+)", jsonstr)
                _brandid = _brand.group(1)
                # shopid
                _shop = re.search(r"shopId:\'(\d+)\'", jsonstr)
                _shopid = _shop.group(1)

                # support
                support = []
                jsoncall_yan = 'http://cd.jd.com/yanbao/v3?skuId=' + _data_pid + '&cat=' + _astr + '&area=' + \
                               self.locations[0]['id'] + '&brandId=' + _brandid
                try:
                    yanbao_info = self.auto_recovered_fetch_json(_url=jsoncall_yan)
                    if yanbao_info == {}:
                        support.append({
                            'support_name': '',
                            'support_price': ''
                        })
                    else:
                        yanbaolist = yanbao_info[_data_pid]
                        for item in yanbaolist:
                            for item_detail in item['details']:
                                support.append({
                                    'support_name': item_detail['bindSkuName'],
                                    'support_price': item_detail['price'],
                                })
                except:
                    support.append({
                        'support_name': '',
                        'support_price': ''
                    })

                # Get suit
                jsoncall_suit = 'http://c.3.cn/recommend?sku=' + _data_pid + '&cat=' + _astr + '&area=' + self.locations[0][
                    'id'] + '&methods=suitv2'
                suit_list = []
                try:
                    suit_info = self.auto_recovered_fetch_json(_url=jsoncall_suit)
                    suitlist_data = suit_info['suit']['data']
                    if 'packList' not in suitlist_data:
                        suit_list = []
                    else:
                        suits = suit_info['suit']['data']['packList']
                        for item in suits:
                            suit = {
                                'suitname': item['packName'],
                                'suitOriginPrice': item['packOriginalPrice'],
                                'suitPromoPrice': item['packPromotionPrice'],
                                'suitid': item['packId'],
                            }
                            suit_list.append(suit)
                except:
                    suit_list.append({
                        'suitname': '',
                        'suitOriginPrice': '',
                        'suitPromoPrice': '',
                        'suitid': ''
                    })

                # Get advertisements
                _call_ad = 'http://cd.jd.com/promotion/v2?skuId=' + _data_pid + '&area=' + self.locations[0][
                    'id'] + '&shopId=' + _shopid + '&venderId=' + _venderid + '&cat=' + _astr
                ad_info = self.auto_recovered_fetch_json(_url=_call_ad)
                ad_info_text = []
                for g in ad_info['ads']:
                    ad_info_text.append(g['ad'])

                # getGmodel
                _call_model = 'https://c.3.cn/recommend?methods=accessories&sku=' + _data_pid + '&cat=' + _astr
                model_info = self.auto_recovered_fetch_json(_url=_call_model)
                accessories_info = model_info.get('accessories', None)
                model_dic = {}
                if accessories_info and ('data' in accessories_info):
                    if 'model' in model_info['accessories']['data']:
                        model_dic['model'] = model_info['accessories']['data']['model']
                    if 'chBrand' in model_info['accessories']['data']:
                        model_dic['brand'] = model_info['accessories']['data']['chBrand']
                    if 'wName' in model_info['accessories']['data']:
                        model_dic['wName'] = model_info['accessories']['data']['wName']
                else:
                    model_dic = {
                        'model': '',
                        'brand': '',
                        'wName': ''
                    }

                # Get stock value from locations
                for item in self.locations:
                    tl = item['id']
                    jsoncall = 'http://c0.3.cn/stock?skuId=' + _data_pid + '&venderId=' + _venderid + '&cat=' + _astr + '&area=' + tl + '&buyNum=1&extraParam={%22originid%22:%221%22}'
                    try:
                        stock_info = self.auto_recovered_fetch_json(_url=jsoncall)
                        if stock_info is not {}:
                            # print stock_info
                            stock = stock_info[u'stock'][u'stockDesc'].replace('<strong>', '').replace('</strong>', '')
                            the_stock_value = {
                                'tn': item['name'],
                                'stock': stock
                            }
                            stock_list.append(the_stock_value)
                        else:
                            print 'no stock info '
                    except:
                        stock_list.append({
                            'tn': item['name'],
                            'stock': ''
                        })
                # get tab from details
                detail_list = []
                detail = this_soup.find('div', class_='detail')
                tab = detail.find('div', class_='tab-con')
                tab_item = tab.find_all("div", {"data-tab": "item"})
                for item in tab_item[:1]:
                    ul_list = item.find_all('ul')
                    for ul in ul_list:
                        li_list = ul.find_all('li')
                        for li in li_list:
                            li_txt = li.text.strip().encode("utf-8")
                            if '：' in li_txt:
                                words = li_txt.split('：')
                                key = words[0].strip()
                                value = words[1].strip()
                                detail_list.append({
                                    'key': key,
                                    'value': value
                                })

                if not _current_order:
                    _current_order = ''

                the_basic_info = {
                    'search_keyword': self.keyword,
                    'last_crawling_timestamp': datetime.now(),
                    'platform': 'JD',
                    'product_name': product_name,
                    'seller_name': seller_name,
                    'sku_id': _data_pid,
                    'default_price': float(final_price),
                    'final_price': 0,
                    'item_url': _http,
                    'comments_count': comment_count,
                    'images': [img_list[0]],
                    'current_stock': stock_list,
                    'support': support,
                    'advertisements': ad_info_text,
                    'bundle': suit_list,
                    'model': model_dic,
                    'detail': detail_list,
                    'search_rank': rank,
                    'search_order': _current_order,
                    'seller_url': seller_url
                }
                product_list.append(the_basic_info)
            except (AttributeError, KeyError, ValueError) as e:
                print(e)
        self.results = product_list
        return product_list

    def out(self, _list):
        serializer = GeneralWatcherSerializer(data=_list, many=True)
        if serializer.is_valid():
            _data = serializer.create(serializer.validated_data)
            for data in _data:
                data.group = self.group
                data.save()
        else:
            # TODO: report errors
            print(serializer.errors)
