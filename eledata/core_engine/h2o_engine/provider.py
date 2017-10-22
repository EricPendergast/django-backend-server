from question01_engine import Question01Engine
from question02_engine import Question02Engine
from eledata.core_engine.provider import BaseEngineProvider


class H2OEngineProvider(BaseEngineProvider):
    classes = {
        'Question01Engine': Question01Engine,
        'Question02Engine': Question02Engine,
    }
