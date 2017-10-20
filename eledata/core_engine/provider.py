class EngineProvider(object):
    """
    Mother Engine Provider Class, for providing other BaseEngineProvider Classes
    """

    @classmethod
    def provide(cls, name, *args, **kwargs):
        pre_name, post_name = name.split('.')

        from entity_stats_engine.provider import EntityStatsEngineProvider
        from monitoring_engine.provider import MonitoringEngineProvider
        from h2o_engine.provider import H2OEngineProvider
        from question_engine.provider import QuestionEngineProvider

        providers = {
            "EntityStats": EntityStatsEngineProvider,
            "Monitoring": MonitoringEngineProvider,
            "H2O": H2OEngineProvider,
            "Question": QuestionEngineProvider
        }

        p = providers.get(pre_name)
        if not p:
            raise EngineProviderNotFound(pre_name)
        return p.provide(post_name, *args, **kwargs)


class BaseEngineProvider(object):
    """
    Abstract Engine Class Provider for provide function to return Engine Classes
    """
    classes = {}

    @classmethod
    def provide(cls, name, *args, **kwargs):
        def get_engine(_name):
            p = cls.classes.get(_name)
            if not p:
                raise EngineNotFound(_name)
            return p

        return get_engine(name)(*args, **kwargs)


class EngineNotFound(NameError):
    def __init__(self, name):
        self._name = name

    def __str__(self):
        return 'Engine {} Not Found'.format(self._name)


class EngineProviderNotFound(NameError):
    def __init__(self, name):
        self._name = name

    def __str__(self):
        return 'Engine Provider {} Not Found'.format(self._name)
