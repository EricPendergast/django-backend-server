from eledata.core_engine.provider import BaseEngineProvider
from .question07_engine import Question07Engine
from .question08_engine import Question08Engine
from .question09_engine import Question09Engine


class QuestionEngineProvider(BaseEngineProvider):
    classes = {
        'question_07': Question07Engine,
        'question_08': Question08Engine,
        'question_09': Question09Engine
    }
