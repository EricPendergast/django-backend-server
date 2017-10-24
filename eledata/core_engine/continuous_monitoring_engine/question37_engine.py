from eledata.core_engine.base_engine import BaseEngine
from eledata.core_engine.provider import EngineProvider
from eledata.util import EngineExecutingError


class Question37Engine(BaseEngine):
    our_keyword_list = []

    def __init__(self, group, params):
        super(Question37Engine, self).__init__(group, params)

    def execute(self):
        """
        Execute monitoring engine among all platform, update database with our_keyword_list
        :return:
        """
        self.set_our_keyword_list()
        for our_keyword in self.our_keyword_list:
            # EngineProvider.provide("Monitoring.JD", group=self.group, params=None,
            #                        keyword=our_keyword, _page_limit=3).execute()
            EngineProvider.provide("Monitoring.Tao", group=self.group, params=None,
                                   keyword=our_keyword, _page_limit=3).execute()

    def event_init(self):
        """
        Execute report engine to get summary, and save to event db.
        :return:
        """
        report_engine = EngineProvider.provide("MonitoringReport.question_37",
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
            self.our_keyword_list = our_keyword_list_param[u'choice_input'].split(',')
        except (IndexError, ValueError) as e:
            raise EngineExecutingError(e)
