# coding:utf-8
from .monitoring_engine import MonitoringEngine
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re
from bs4 import BeautifulSoup
import requests
from eledata.serializers.watcher import GeneralWatcherSerializer
from datetime import datetime


class TaoMonitoringEngine(MonitoringEngine):
    # TODO: Auto Updating Proxy Url
    keyword = None
    url = None
    results = []
    param_dict = {}
    url_list = []
    order_list = []
    cookies = None
    _u_key = None
    _p_key = None

    ORDER_MAPPING = {
        'integrated': '&sort=default',
        'price': '&sort=price-asc',
        'sales': '&sort=sale-desc',
        'hot': '&sort=renqi-desc',
        # 'new': '&psort=5',
        'credit': '&sort=credit-desc',
    }

    """
    Overriding Environment Setting Functions
    """
    def set_cookie(self, _key_1, _key_2):
        self._u_key = _key_1
        self._p_key = _key_2

        # PhantomJS with proxy
        # service_args = [
        #     '--proxy=217.156.252.118:8080',
        #     '--proxy-type=https',
        # ]
        # driver = webdriver.PhantomJS(service_args=service_args)

        # Firefox with proxy
        # profile = webdriver.FirefoxProfile()
        # profile.set_preference("network.proxy.type", 1)
        # profile.set_preference("network.proxy.http", "116.48.136.128")
        # profile.set_preference("network.proxy.http_port", 8080)
        # profile.update_preferences()　
        # driver = webdriver.Firefox(executable_path=r'constants/geckodriver', firefox_profile=profile)

        # Plain PhantomJS
        driver = webdriver.PhantomJS(executable_path=r'constants/phantomjs')

        driver.get("https://login.taobao.com/member/login.jhtml")
        time.sleep(2)
        # 用户名 密码
        elem_user = driver.find_element_by_name("TPL_username")
        elem_user.send_keys(self._u_key)
        elem_pwd = driver.find_element_by_name("TPL_password")
        elem_pwd.send_keys(self._p_key)
        submit_btn = driver.find_element_by_id("J_SubmitStatic")
        submit_btn.send_keys(Keys.ENTER)
        time.sleep(2)
        cookies = driver.get_cookies()
        self.driver = driver
        self.cookies = cookies

    def set_searching_url(self, _keyword, _page_limit, _order):
        _url = 'https://s.taobao.com/search?q=CHANGEME&bcoffset=0&ntoffset=0&s=0'
        self.url = _url.replace('CHANGEME', _keyword)
        for num in range(0, _page_limit):
            if not _order:
                self.order_list.append('default')
                self.url_list.append("https://s.taobao.com/search?" + "q=" + _keyword + "&s=" + str(num * 44))
            else:
                for order in _order:
                    self.url_list.append("https://s.taobao.com/search?" + "q=" + _keyword + "&s=" + str(num * 44)
                                         + self.ORDER_MAPPING.get(order))
                    self.order_list.append(order)

    """
    Overriding Monitoring Core Functions
    """
    def get_soup(self, _url):
        driver = self.driver
        driver.get(_url)
        html = driver.page_source
        _soup = BeautifulSoup(html, 'html.parser')
        return _soup

    def get_basic_info(self, soup_string, _current_order=None):
        product_list = []
        items_ad = soup_string.find_all('div', {'class': 'item J_MouserOnverReq item-ad '})
        items_n = soup_string.find_all('div', {'class': 'item J_MouserOnverReq '})
        items = items_ad + items_n
        rank = 0
        for item in items:
            rank = rank + 1
            '''
            product_name  sku_id item_url
            '''
            product_name_item = item.find('div', {'class': 'row row-2 title'})
            product_name = product_name_item.text.strip()
            sku_id = product_name_item.find('a', {'class': 'J_ClickStat'})['data-nid']
            item_url = 'http:' + product_name_item.find('a', {'class': 'J_ClickStat'})['href']
            img_save_path = self.img_pth

            '''
            thumbnail
            '''
            try:
                img_src = 'http:' + str(item.find('div', {'class': 'pic'}).find('a').find("img")['src'])
            except KeyError:
                img_src = 'http:' + str(item.find('div', {'class': 'pic'}).find('a').find("img")['data-ks-lazyload'])
            # img_name = self.save_image(img_src, img_save_path)
            '''
            seller   include seller_name seller_url  seller_location
            '''
            seller_item = item.find("div", class_="row row-3 g-clearfix")
            seller_name = seller_item.find_all("span")[-1].text
            seller_url = 'http:' + seller_item.find('a')['href']
            seller_location = seller_item.find('div', class_='location').text.strip()
            '''
            price and sales
            '''
            sales_item = item.find("div", class_="row row-1 g-clearfix")
            default_price_item = sales_item.find('div', class_='price g_price g_price-highlight').text.strip()
            default_price = int(re.search(r'\d+', default_price_item).group())
            sales_count_text = sales_item.find('div', class_='deal-cnt').text.strip()
            sales_count = int(re.search(r'\d+', sales_count_text).group())
            '''
            comment_count
            '''
            try:
                _call_ad = "https://rate.taobao.com/detailCount.do?itemId=" + sku_id
                sess_g = requests.Session()
                rep_g = sess_g.get(_call_ad)
                rep_g.encoding = 'UTF-8'
                comment_item = rep_g.text
                comments_count = int(re.search(r"(\d+)", comment_item).group(1))
            except:
                comments_count = 1

            the_basic_info = {
                "platform": "TB",
                'search_keyword': self.keyword,
                'last_crawling_timestamp': datetime.now(),
                'seller_location': seller_location,
                'product_name': product_name,
                'seller_name': seller_name,
                'sku_id': sku_id,
                'default_price': float(default_price),
                'final_price': 0,
                'item_url': item_url,
                'images': [img_src],
                'sales_count': float(sales_count),
                'img_pth': self.img_pth,
                'search_rank': rank,
                'search_order': _current_order,
                'seller_url': seller_url,
                'comments_count': comments_count
            }
            product_list.append(the_basic_info)
        return product_list

    def out(self, _list):
        serializer = GeneralWatcherSerializer(data=_list, many=True)
        if serializer.is_valid():
            # for _data in serializer.validated_data:
            _data = serializer.create(serializer.validated_data)
            for data in _data:
                data.group = self.group
                data.save()
        else:
            # TODO: report errors
            print(serializer.errors)
