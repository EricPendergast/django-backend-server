import pandas as pd
from eledata.models.entity import *
import entity_summary


# TODO: To be renamed most likely
class EntityFrame(object):
    data_frame = {}
    """
    - Class constructor function with different type of input:
    1. list for dict / csv
    2. Mongo Object from database

    """

    @classmethod
    def frame_from_file(cls, entity, entity_type):
        # TODO: verify if entity type is missing
        # TODO: verify if data header has been set properly
        cls.data_frame.update({entity_type: pd.DataFrame(entity)})
        return cls

    @classmethod
    def frame_from_group(cls, user):
        # think of it later....
        entity_object = Entity.objects(group=user.group)
        for key in entity_object:
            cls.data_frame.update({key: entity_object[key]['data']})
        return cls

    def get_summary(self, entity_type):
        # if data_frame has more than 1 item, use entity_type to help
        key = self.data_frame.keys()[0] if self.data_frame.keys() == 1 else entity_type

        return entity_summary.get_single_data_summary(
            data=self.data_frame[key],
            data_type=key,
        )
