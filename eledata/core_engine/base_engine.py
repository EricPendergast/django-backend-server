"""
This is the mother class for engine executing executing questions in EleData.

@params:
- group:
    Model Object of user group, corresponding for retrieving the entity data and the destination for the output(event).

And all executing engine should experience the same life-cycle:

Initializing Engine
- engine.init()
"""

from multiprocessing import Process
from abc import abstractmethod


class BaseEngine(object):
    group = None
    response = None

    def __init__(self, group):
        self.group = group

    @abstractmethod
    def execute(self):
        """
        void function to update intermediate/ ultimate response
        """

    @abstractmethod
    def event_init(self):
        """
        (When engine is for Event Response)
        void function to update
        """

    def get_processed(self):
        """
        (When engine is not for Event Response)
        Return engine response in series way
        :return: engine ultimate response
        """
        return self.response

    def sync_run(self):
        """
        (When engine is for Event Response)
        Synchronous Wrapper of _run, executing Engine Workflow in parallel job
        """
        def _run(_self):
            _self.execute()
            _self.event_init()

        p = Process(target=_run(self))
        p.start()
        p.join()
