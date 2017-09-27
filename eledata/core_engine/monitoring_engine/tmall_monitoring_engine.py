# coding:utf-8
from selenium import webdriver
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.keys import Keys
import time
import re
from bs4 import BeautifulSoup
import urllib2
import requests
import json
import uuid
from .monitoring_engine import MonitoringEngine
from datetime import datetime


class TMallScrap(MonitoringEngine):
    key = ''
    url = ''
    cookie = ''
    request_page = ''
    total_page = ''
    url_list = []
    results = []

    """
    Overriding abstract functions for initialization
    """

    def set_searching_url(self, keyword, _page):
        _url = 'https://list.tmall.com/search_product.htm?q=CHANGEME' \
               '&type=p&vmarket=&spm=875.7931836%2FB.a2227oh.d100&from=mallfp..pc_1_searchbutton'
        self.url = _url.replace('CHANGEME', keyword)
        self.request_page = _page
        self.get_url_list()

    def get_url_list(self):
        t_url = self.url
        url_list = []
        t_soup = self.get_soup(self.url)
        total_page = int(t_soup.find("input", {"name": "totalPage"}).get("value"))
        self.total_page = min(total_page, self.request_page)
        # self.total_page = total_page
        for i in range(1, total_page - 1):
            soure_Url = t_url.replace('q=', 's=' + str(i * 60) + '&q=')
            url_list.append(soure_Url)
        self.url_list = url_list

    def set_location(self, _location):
        """
        We do nothing here.
        """
        return

    def set_cookie(self, _u_key, _p_key):
        def human_type(element, text):
            element.click()
            for char in text:
                time.sleep(float(random.randint(1, 100) /60))  # fixed a . instead of a ,
                element.send_keys(char)
            time.sleep(float(random.randint(1, 100) /60))

        driver = webdriver.Chrome()
        # driver = webdriver.PhantomJS()
        driver.get("https://login.taobao.com/member/login.jhtml")
        elem_user = driver.find_element_by_name("TPL_username")
        human_type(elem_user, _u_key)
        elem_pwd = driver.find_element_by_name("TPL_password")
        human_type(elem_pwd, _p_key)
        # drag = driver.find_elements_by_class_name("btn_slide")[0]
        #
        # def slide_to_unlock(_drag):
        #     action = ActionChains(driver)
        #     action.click_and_hold(_drag).perform()  # 鼠标左键按下不放
        #     for index in range(200):
        #         try:
        #             action.move_by_offset(2, 0).perform()  # 平行移动鼠标
        #         except UnexpectedAlertPresentException:
        #             break
        #         action.reset_actions()
        #         time.sleep(0.1)  # 等待停顿时间
        #
        # if drag:
        #     slide_to_unlock(drag)

        submit_btn = driver.find_element_by_id("J_SubmitStatic")
        time.sleep(3)
        submit_btn.send_keys(Keys.ENTER)
        cookies = driver.get_cookies()
        self.cookie = "; ".join([item["name"] + "=" + item["value"] for item in cookies])
        driver.delete_all_cookies()
        print(self.cookie)

    """
    Engine/ Platform depending functions
    """

    def get_soup(self, _url=None):
        url = _url or self.url
        headers = {
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/60.0.3112.101 Safari/537.36",
            "cookie": self.cookie,
            "referer": url
        }

        response = requests.get(url, headers=headers)
        contents = response.content

        soup = BeautifulSoup(contents, 'html.parser')
        return soup

    @staticmethod
    def generate_ip():
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36'}
        url = 'http://www.xicidaili.com/nn/1'
        s = requests.get(url, headers=headers)
        soup = BeautifulSoup(s.text, 'html.parser')
        ips = soup.select('#ip_list tr')
        ip_list = []
        for i in ips:
            try:
                ipp = i.select('td')
                ip = ipp[1].text
                host = ipp[2].text
                ip_list.append(ip + ':' + host)
            except:
                print '121.232.144.76:9000'
        return ip_list

    def get_basic_info(self, soup):
        print soup
        product_list = []
        product_title = soup.find("div", {"id": "J_ItemList"})

        # Previous Product Ad Handling:
        # product_title = [x for x in product_title if x.get('class', []) == ['product', 'item-1111', '']]
        product_item = product_title.find_all("div", {"class": "product "})
        for index, item in enumerate(product_item):
            product_img = []
            sku_id = item['data-id']
            seller_name = item.find("div", class_='productShop').find("a", class_='productShop-name').text
            shop_price = item.find("p", class_='productPrice').find("em").text
            shop_title = item.find("div", class_='productTitle').find_all("a")
            product_name = ''
            for item_title in shop_title:
                product_name += item_title.text.strip()
            sales_count_a = item.find("p", class_='productStatus') and item.find("p", class_='productStatus').text
            sales_count = sales_count_a and sales_count_a.strip() or "No Shop Status"
            item_url = 'http:' + item.find("div", class_='productImg-wrap').find("a")['href']

            url_item = item.find("div", class_='productImg-wrap').find("a").find("img")
            url_img = url_item.get('src', False) or url_item.get('data-ks-lazyload', False)
            url_img = 'http:' + url_img

            save_path = self.img_pth
            file_name = str(uuid.uuid4())
            product_img.append(file_name)
            self.save_image(url_img, save_path, file_name)

            _soup = self.get_soup(item_url)
            # get price info

            headers2 = {'Referer': item_url, 'cookie': self.cookie}
            url3 = "https://mdskip.taobao.com/core/initItemDetail.htm?itemId=" + sku_id
            proxy = urllib2.ProxyHandler({'http': "121.232.144.76:9000"})
            opener = urllib2.build_opener(proxy)
            urllib2.install_opener(opener)
            ws3 = urllib2.urlopen(urllib2.Request(url3, headers=headers2)).read()
            ws2 = ws3.decode('unicode_escape').encode('utf-8')
            # print ws2
            recall_info = json.loads(ws2)
            price_info = recall_info['defaultModel']['itemPriceResultDO']['priceInfo']
            suit_final_price_list = []
            for i in price_info:
                try:
                    final_price = price_info[i].get('promotionList', False)[0].get('price', False)
                except TypeError or IndexError:
                    final_price = "No Discount"

                suit_final_price = {'skuid': i, 'final price': final_price}
                suit_final_price_list.append(suit_final_price)
            try:
                ul_image_list = _soup.find('ul', {"id": "J_UlThumb"})
                img_list = ul_image_list.find_all('li')
                for index2, img in enumerate(img_list):
                    detail_src = 'http:' + img.find('a').find('img')['src']
                    detail_file_path = self.img_pth
                    detail_file_name = str(uuid.uuid4())
                    self.save_image(detail_src, detail_file_path, detail_file_name)
                    product_img.append(detail_file_name)

            # TODO: fix the try except that can re-get the iamge
            except TypeError or ValueError or IndexError:
                print 'error when get image'

            # get support
            support_list = []
            try:
                support_ul = _soup.find('ul', class_='tb-serPromise')
                support_ul_li = support_ul.find_all('li')
                for li in support_ul_li:
                    support_list.append(li.find('a').text.strip())
                    print("OK when get support")
            except TypeError or ValueError or IndexError:
                # 2. There is no such data
                support_list.append('')
                print 'error when get support', item_url

            final_price_list = []  # Please update all this simple typo before commit and push
            sss = _soup.find("div", {"id": "J_DetailMeta"})
            # TODO make the final_price_list better
            try:
                map_list = []
                m = re.search(r"\"(skuList)\":\[(.*?)\]", str(sss))
                pro_json = json.loads('{' + (m.group(0)) + '}')
                pro_list = pro_json['skuList']
                y = re.findall(r"\"(priceCent)\":(\d+),\"(skuId)\":\"(\d+)\",\"(stock)\":(\d+)", str(sss))
                for item_y in y:
                    map_json = {item_y[0]: item_y[1],
                                item_y[2]: item_y[3],
                                item_y[4]: item_y[5]
                                }
                    map_list.append(map_json)
                list_n = []
                for i in map_list:
                    for y in pro_list:
                        if i['skuId'] == y[u'skuId']:
                            map_json = {
                                'default_price': i['priceCent'],
                                'sku_id': i['skuId'],
                                'product name': y[u'names'],
                                'stock': i['stock']
                            }
                            list_n.append(map_json)
                for i in list_n:
                    for y in suit_final_price_list:
                        if i['sku_id'] == y['skuid']:
                            final_price_dic = {
                                'default_price': round(int(i['default_price']) / 100, 2),
                                'sku_id': i['sku_id'],
                                'product name': i['product name'],
                                'stock': i['stock'],
                                'final_price': y['final price']
                            }
                            final_price_list.append(final_price_dic)
                print("OK when get suit")

            except TypeError or ValueError or IndexError:
                final_price_list.append({
                    'default_price': '',
                    'sku_id': '',
                    'product name': '',
                    'stock': '',
                    'final_price': ''
                })
                print 'this product no suits'

            detail = {
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'platform': 'TMall',
                'product_name': product_name,
                'seller_name': seller_name.strip(),
                "sku_id": sku_id,
                'default_price': shop_price.strip(),
                'final_price': '',
                'item_url': item_url,
                'sales_count': sales_count,
                'img_pth': self.img_pth,
                'images': product_img,
                'current_stock': '',
                'support': support_list,
                "suit": final_price_list
            }
            product_list.append(detail)
            # break
        self.results = product_list
        return product_list

    def out(self, _list):
        # print _list
        # pass
        for item in _list:
            print "Sku id:", item['sku_id']
            print "Shop Name:", item['seller_name']
            print "Product Price:", item['default_price']
            print "Product Name:", item['product_name']
            for p in item['images']:
                print p + '.img'
            print "sales_count:", item['sales_count']
            print "item_url:", item['item_url']
            for i in item['support']:
                print i
            try:
                for i in item['suit']:
                    print 'Product Name:', i['product name'], '  SkuId:', i['sku_id'], '  Stock Value:', i[
                        'stock'], 'Default price:', i['default_price'], 'Final price:', i['final_price'] + '\n',
            except:
                print 'print suit error'

    def get_multi_page(self):
        _url_list = self.url_list
        for item in _url_list:
            _soup = self.get_soup(item)
            t_list = self.get_basic_info(_soup)
            self.out(t_list)
            # self.put_db(t_list)