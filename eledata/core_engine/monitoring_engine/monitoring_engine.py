from eledata.core_engine.base_engine import BaseEngine
import os
import requests
from abc import abstractmethod
import json


class MonitoringEngine(BaseEngine):
    img_pth = 'temp/img'

    def __init__(self, group, keyword=None, location=None, _u_key='CHANGE_ME', _p_key='CHANGE_ME'):
        # if not keyword:
        #     keyword = get_keyword_from_group_param
        super(MonitoringEngine, self).__init__(group)
        self.keyword = keyword
        self.set_searching_url(keyword)
        self.set_location(location)
        self.set_cookie(_u_key, _p_key)

    @abstractmethod
    def set_searching_url(self, _keyword):
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
