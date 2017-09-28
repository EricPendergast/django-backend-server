from eledata.core_engine.provider import BaseEngineProvider
from .jd_monitoring_engine import JDMonitoringEngine
from .tmall_monitoring_engine import TMallScrap


class MonitoringEngineProvider(BaseEngineProvider):
    classes = {
        'TMall': TMallScrap,
        'JD': JDMonitoringEngine,
    }
