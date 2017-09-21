class EngineProvider(object):
    """
    Mother Engine Provider Class, for providing other BaseEngineProvider Classes
    """

    @classmethod
    def equip(cls, name):

        from entity_stats_engine.provider import EntityStatsEngineProvider

        providers = {
            "EntityStats": EntityStatsEngineProvider()
        }

        p = providers.get(name)
        if not p:
            raise EngineProviderNotFound(name)
        return p


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
        return 'Engine Provider{} Not Found'.format(self._name)
