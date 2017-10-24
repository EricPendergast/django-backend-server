from eledata.core_engine.provider import BaseEngineProvider
from .question37_engine import Question37Engine


class ContinuousMonitoringEngineProvider(BaseEngineProvider):
    classes = {
        'question_37': Question37Engine,
    }
