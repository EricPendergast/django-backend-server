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

    def __init__(self, entity_data, entity_type):
        # TODO: verify if entity type is missing
        # TODO: verify if data header has been set properly
        df = pd.DataFrame(entity_data)
        self.entity_data = df
        self.entity_type = entity_type

    def get_summary(self, entity_type=None):
        # if data_frame has more than 1 item, use entity_type to help
        key = self.entity_type if self.entity_type else entity_type

        return entity_summary.get_single_data_summary(
            data=self.entity_data,
            data_type=key,
        )

    def get_summary_chart(self, entity_type=None):
        # if data_frame has more than 1 item, use entity_type to help
        key = self.entity_type if self.entity_type else entity_type

        return entity_chart_summary.get_single_data_summary_chart(
            data=self.entity_data,
            data_type=key,
        )
