from eledata.core_engine.provider import BaseEngineProvider
from .question07_engine import Question07Engine


class QuestionEngineProvider(BaseEngineProvider):
    classes = {
        'Customer': Question07Engine
    }
