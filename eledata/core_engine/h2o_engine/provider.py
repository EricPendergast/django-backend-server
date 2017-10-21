from clv_h2o_engine import ClvH2OEngine
from eledata.core_engine.provider import BaseEngineProvider
from leaving_h2o_engine import LeavingH2OEngine


class H2OEngineProvider(BaseEngineProvider):
    classes = {
        'Leaving': LeavingH2OEngine,
        'Clv': ClvH2OEngine,
    }
