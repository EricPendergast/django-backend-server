import pandas as pd
import entity_summary
import entity_chart_summary


class EntityFrame(object):
    entity_data = None
    entity_type = None
    """
    - Class constructor function with different type of input:
    1. list for dict / csv
    2. Mongo Object from database

    """

    @classmethod
    def frame_from_file(cls, entity_data, entity_type):
        # TODO: verify if entity type is missing
        # TODO: verify if data header has been set properly
        df = pd.DataFrame(entity_data)
        cls.entity_data = df
        cls.entity_type = entity_type
        return cls

    @classmethod
    def get_summary(cls, entity_type=None):
        # if data_frame has more than 1 item, use entity_type to help
        key = cls.entity_type if cls.entity_type else entity_type

        return entity_summary.get_single_data_summary(
            data=cls.entity_data,
            data_type=key,
        )

    @classmethod
    def get_summary_chart(cls, entity_type=None):
        # if data_frame has more than 1 item, use entity_type to help
        key = cls.entity_type if cls.entity_type else entity_type

        return entity_chart_summary.get_single_data_summary_chart(
            data=cls.entity_data,
            data_type=key,
        )
