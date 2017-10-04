# coding:utf-8
from eledata.core_engine.base_engine import BaseEngine
import os
import requests
from abc import abstractmethod
import json
from eledata.util import EngineExecutingError


class MonitoringEngine(BaseEngine):
    img_pth = 'temp/img'
    locations = []
    # 深圳　北京　上海　廣州　杭州　南京　武漢　廈門　天津　蘇州
    # TODO: move the location dictionary to constant file
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

    def __init__(self, group, params, keyword=None, location=None, _u_key='CHANGE_ME', _p_key='CHANGE_ME',
                 _page_limit=None):
        # if not keyword:
        #     keyword = get_keyword_from_group_param
        super(MonitoringEngine, self).__init__(group, params)
        self.keyword = keyword
        self.page_limit = _page_limit
        self.set_searching_url(keyword, _page_limit)
        self.set_location(location)
        self.set_cookie(_u_key, _p_key)

    def set_keyword(self):
        keyword_param = filter(lambda _x: _x.label == "keywords", self.params)[0]
        if not keyword_param.choice_input:
            raise EngineExecutingError("Invalid keyword user parameter is retrieved")
        self.keyword = keyword_param.choice_input.split(",")
        return

    def set_page_limit(self):
        leaving_param = filter(lambda _x: _x.label == "page_limit", self.params)[0]
        user_input = leaving_param.choice_input \
            if leaving_param.choice_index is 1 else 3  # by default 3 pages
        self.page_limit = user_input

        return

    def set_location(self):
        location_param = filter(lambda _x: _x.label == "location_limit", self.params)[0]
        user_input = location_param.choice_input \
            if location_param.choice_index is 1 else 20  # by default 3 pages
        self.locations = self.supported_locations[:user_input]
        pass

    @abstractmethod
    def set_searching_url(self, _keyword, _page):
        """
        update self.url from _keyword, for all sub-engines
        """

    @abstractmethod
    def set_location(self, _location):
        """
        update self.location from _location (and self.supported_locations,for engines with location dependency)
        """

    @abstractmethod
    def set_cookie(self, _key_1, _key_2):
        """
        update self.cookie based on _key_1, _key_2 on selenium (for engines with login dependency most likely)
        """

    @abstractmethod
    def get_multi_page(self):
        """

        """

    def execute(self):
        """

        :return:
        """
        soup = self.get_soup(None)
        self.response = self.get_basic_info(soup)
        self.out(self.response)

    def event_init(self):
        return

    def get_soup(self, _url=None):
        """
        Open self.url from beautiful_soup to get soup string
        :return:
        """
        return

    def get_basic_info(self, soup_string):
        """
        Extract Item Information from soup_string
        :param soup_string:
        :return: [{...item_information},]
        """
        return

    @staticmethod
    def auto_recovered_fetch_json(_url, _http_header=None):
        while True:
            try:
                sess = requests.Session()
                resp = sess.get(_url, headers=_http_header)
                resp.encoding = 'gbk'
                _info = json.loads(resp.text)
                break
            except ValueError:
                continue
        return _info

    def save_image(self, _url, _save_path, _filename):
        if not os.path.exists(_save_path):
            os.makedirs(_save_path)
        img_data = requests.get(_url).content
        path = _save_path + "/" + _filename + '.jpg'
        with open(path, 'wb') as handler:
            handler.write(img_data)
        self.img_pth = _save_path

    def out(self, data):
        return
