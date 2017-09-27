from abc import abstractmethod
from eledata.core_engine.base_engine import BaseEngine
import pandas as pd


class H2OEngine(BaseEngine):

    def __init__(self, group, params):
        super(H2OEngine, self).__init__(group, params)

    def execute(self):
        """
        No idea right now
        :return:
        """
        return

    def event_init(self):
        """
        EntityStatsEngine Does not init event (For the time beings?)
        :return:
        """
        return
