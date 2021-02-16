from question01_engine import Question01Engine
from question02_engine import Question02Engine
from eledata.core_engine.provider import BaseEngineProvider


class H2OEngineProvider(BaseEngineProvider):
    classes = {
        'question_01': Question01Engine,
        'question_02': Question02Engine,
    }
