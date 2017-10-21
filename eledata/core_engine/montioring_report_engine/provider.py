# What is the price range for products being sold by my resellers?
from eledata.core_engine.provider import BaseEngineProvider
from .question37_engine import Question37Engine
# from .question08_engine import Question08Engine
# from .question09_engine import Question09Engine


class MonitoringReportEngineProvider(BaseEngineProvider):
    classes = {
        'Question37Engine': Question37Engine,
        # 'Question08Engine': Question08Engine,
        # 'Question09Engine': Question09Engine
    }
