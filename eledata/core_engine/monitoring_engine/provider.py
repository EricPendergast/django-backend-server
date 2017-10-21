from eledata.core_engine.provider import BaseEngineProvider
from .jd_monitoring_engine import JDMonitoringEngine
from .tmall_monitoring_engine import TMallScrap
from .tao_monitoring_engine import TaoMonitoringEngine


class MonitoringEngineProvider(BaseEngineProvider):
    classes = {
        'TMall': TMallScrap,
        'JD': JDMonitoringEngine,
        'Tao': TaoMonitoringEngine,
    }
