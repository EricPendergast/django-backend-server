# What is the price range for products being sold by my resellers?
from eledata.core_engine.provider import BaseEngineProvider
from .question37_engine import Question37Engine
from .question34_engine import Question34Engine
from .question36_engine import Question36Engine
# from .question08_engine import Question08Engine
# from .question09_engine import Question09Engine


class MonitoringReportEngineProvider(BaseEngineProvider):
    classes = {
        'question_37': Question37Engine,
        'question_34': Question34Engine,
        'question_36': Question36Engine,
        # 'Question08Engine': Question08Engine,
        # 'Question09Engine': Question09Engine
    }
