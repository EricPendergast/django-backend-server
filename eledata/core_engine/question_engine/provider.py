from eledata.core_engine.provider import BaseEngineProvider
from .question07_engine import Question07Engine
from .question08_engine import Question08Engine
from .question09_engine import Question09Engine


class QuestionEngineProvider(BaseEngineProvider):
    classes = {
        'Question07Engine': Question07Engine,
        'Question08Engine': Question08Engine,
        'Question09Engine': Question09Engine
    }
