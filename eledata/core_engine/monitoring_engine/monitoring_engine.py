# coding:utf-8
from eledata.core_engine.base_engine import BaseEngine
import os
import requests
from abc import abstractmethod
import json
from eledata.util import EngineExecutingError
import time
import uuid


class MonitoringEngine(BaseEngine):
    driver = None
    keyword = None
    page_limit = 0
    order = None
    img_pth = 'temp/img'
    locations = []
    url_list = []
    order_list = []

    # This pair of limit variable is to be updated for JD only.
    limit_current = -1
    limit_total = 0

    """
    Environment Setting Functions
    """
    def __init__(self, event_id, group, params, keyword=None, location=None, _u_key='CHANGE_ME', _p_key='CHANGE_ME',
                 _page_limit=None, order=None):
        # TODO: get keywords, locations from params
        # TODO: get page, order from params??
        # if not keyword:
        #     keyword = get_keyword_from_group_param
        super(MonitoringEngine, self).__init__(event_id, group, params)
        self.keyword = keyword
        self.page_limit = _page_limit
        self.set_location(location)
        self.order = order
        self.set_cookie(_u_key, _p_key)
        self.set_searching_url(self.keyword, self.page_limit, self.order)

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

    def set_order(self):
        # TODO: update to sync order param
        location_param = filter(lambda _x: _x.label == "location_limit", self.params)[0]
        user_input = location_param.choice_input \
            if location_param.choice_index is 1 else 20  # by default 3 pages
        self.locations = self.supported_locations[:user_input]
        pass

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
    def set_searching_url(self, _keyword, _page, _order):
        """
        Update self.url from _keyword, for all sub-engines.
        :param _keyword: string, Searching keywords from params.
        :param _page: int, Number of page to be monitored.
        :param _order: string, Type of product ordering to be monitored.
        :return: list of string, Contains the url(s) to be monitored.
        """

    """
    Monitoring Core Functions
    """
    def execute(self):
        """
        Core Function.
        :return:
        """
        import signal

        class TimeoutException(Exception):  # Custom exception class
            pass

        def timeout_handler(signum, frame):  # Custom signal handler
            raise TimeoutException

        # Change the behavior of SIGALRM
        signal.signal(signal.SIGALRM, timeout_handler)

        for _index, url in enumerate(self.url_list):

            # TODO: make it try again in case dead
            signal.alarm(60)
            try:
                soup = self.get_soup(_url=url)
            except TimeoutException:
                continue
            else:
                signal.alarm(0)

            response = self.get_basic_info(soup, self.order_list[_index])
            self.out(response)
            if self.limit_current == self.limit_total:
                break
        self.driver.close()

    def event_init(self):
        """
        There is no event to be reported by low level monitoring engines.
        :return: None
        """
        return

    @abstractmethod
    def get_soup(self, _url):
        """
        Open self.url from beautiful_soup to get soup string
        :param: _url: string, Trivially url.
        :return:
        """
        pass

    @abstractmethod
    def get_basic_info(self, soup_string, _current_order=None):
        """
        Extract product information from soup_string
        :param soup_string: string, Html soup.
        :param _current_order: string, optional, Current order string for reference.
        :return: [{...item_information},]
        """
        return

    @abstractmethod
    def out(self, data):
        """
        Save product information
        :param data: list, List of product information object.
        :return:
        """
        return

    """
    Monitoring Utils Functions
    """
    @staticmethod
    def auto_recovered_fetch_json(_url, _http_header=None):
        """
        :param _url: string,
        :param _http_header:　
        :return:
        """
        _info = None
        count = 5
        while count >= 0:
            try:
                sess = requests.Session()
                resp = sess.get(_url, headers=_http_header)
                resp.encoding = 'gbk'
                _info = json.loads(resp.text)
                break
            except ValueError:
                time.sleep(5)
                count -= 1
                continue
        return _info

    @staticmethod
    def save_image(_url, _save_path):
        _filename = str(uuid.uuid4())
        if not os.path.exists(_save_path):
            os.makedirs(_save_path)
        img_data = requests.get(_url).content
        path = _save_path + "/" + _filename + '.jpg'
        with open(path, 'wb') as handler:
            handler.write(img_data)
        return path
