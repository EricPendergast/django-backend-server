from abc import abstractmethod
from eledata.core_engine.base_engine import BaseEngine
import pandas as pd


class EntityStatsEngine(BaseEngine):

    entity_data = None
    entity_type = None

    def __init__(self, group, params, entity_data, entity_type):
        super(EntityStatsEngine, self).__init__(None, group, params)
        # TODO: verify if entity type is missing
        # TODO: verify if data header has been set properly
        df = pd.DataFrame(entity_data)
        self.entity_data = df
        self.entity_type = entity_type

    def event_init(self):
        """
        EntityStatsEngine Does not init event (For the time beings?)
        :return:
        """
        return

    @abstractmethod
    def get_stats(self, data, data_type):
        """
        :param data: data
        :param data_type:
        :return: stats_response: dictionary of stats finding
        """

    def execute(self, entity_type=None):

        if self.entity_type:
            _entity_type = self.entity_type
        else:
            _entity_type = entity_type

        self.response = self.get_stats(data=self.entity_data, data_type=_entity_type)
