from eledata.core_engine.provider import BaseEngineProvider
from .question34_engine import Question34Engine
# from .question36_engine import Question36Engine
from .question37_engine import Question37Engine


class ContinuousMonitoringEngineProvider(BaseEngineProvider):
    classes = {
        'question_34': Question34Engine,
        # 'question_36': Question36Engine,
        'question_37': Question37Engine,
    }
