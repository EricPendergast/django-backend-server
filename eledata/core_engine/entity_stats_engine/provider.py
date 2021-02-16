from eledata.core_engine.provider import BaseEngineProvider
from .chart_entity_stats_engine import ChartEntityStatsEngine
from .summary_entity_stats_engine import SummaryEntityStatsEngine


class EntityStatsEngineProvider(BaseEngineProvider):
    classes = {
        'Chart': ChartEntityStatsEngine,
        'Summary': SummaryEntityStatsEngine,
    }
