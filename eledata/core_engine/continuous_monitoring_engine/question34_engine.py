from eledata.core_engine.base_engine import BaseEngine
from eledata.core_engine.provider import EngineProvider
from eledata.util import EngineExecutingError


class Question34Engine(BaseEngine):
    our_keyword_list = []

    def __init__(self, event_id, group, params):
        super(Question34Engine, self).__init__(event_id, group, params)

    def execute(self):
        """
        Execute monitoring engine among all platform, update database with our_keyword_list
        :return:
        """
        # TODO: choose what and how much to be scraped by checking overall enabled question in group
        self.set_our_keyword_list()
        self.set_competitor_keyword_list()
        for our_keyword in self.our_keyword_list:
            EngineProvider.provide("Monitoring.JD", event_id=self.event_id, group=self.group, params=None,
                                   keyword=our_keyword, _page_limit=3).execute()
            EngineProvider.provide("Monitoring.Tao", event_id=self.event_id, group=self.group, params=None,
                                   keyword=our_keyword, _page_limit=3).execute()

    def event_init(self):
        """
        Execute report engine to get summary, and save to event db.
        :return:
        """
        report_engine = EngineProvider.provide("MonitoringReport.question_34",
                                               event_id=self.event_id,
                                               group=self.group,
                                               params=None,
                                               keyword_list=self.our_keyword_list)

        report_engine.execute()
        report_engine.event_init()

    def set_our_keyword_list(self):
        """
        Obtain our-product-keyword-list from user param
        :return:
        """
        try:
            our_keyword_list_param = filter(lambda _x: _x.get('label') == "our_keyword_list", self.params)[0]
            self.our_keyword_list = [x.strip() for x in our_keyword_list_param[u'choice_input'].split(',')]
        except (IndexError, ValueError) as e:
            raise EngineExecutingError(e)

    def set_competitor_keyword_list(self):
        """
        Obtain competitor-keyword-list from user param
        :return:
        """
        try:
            our_keyword_list_param = filter(lambda _x: _x.get('label') == "competitor_keyword_list", self.params)[0]
            self.our_keyword_list = [x.strip() for x in our_keyword_list_param[u'choice_input'].split(',')]
        except (IndexError, ValueError) as e:
            raise EngineExecutingError(e)
