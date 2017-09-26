from eledata.serializers.event import *
from eledata.verifiers.event import *
from project.settings import CONSTANTS
from eledata.core_engine.provider import EngineProvider
from eledata.util import EngineExecutingError
from eledata.core_engine.provider import EngineProviderNotFound
from multiprocessing import Process


def update_event_status(event, status, verifier):
    """
    :param event: Desired event to be updated.
    :param status: New Status
    :param verifier: UpdateEventStatusVerifier
    :return:
    """
    verifier.verify(1, event)
    verifier.verify(2, event)

    event.event_status = status
    event.save()

    return {"msg": "Change successful"}


def init_new_event(event_object, _group):
    verifier = InitNewEventVerifier()

    verifier.verify(0, event_object)
    verifier.verify(1, _group)

    serializer = DetailedEventSerializer(data=event_object)

    verifier.verify(2, serializer)

    _new_event = serializer.create(serializer.validated_data)
    _new_event.group = _group

    verifier.verify(3, _new_event)

    assert verifier.verified
    _new_event.save()
    return {"msg": "Change successful"}


def create_new_initializing_job(jobs):
    _job = []
    for job in jobs:
        serializers = DetailedJobSerializer(data=job)
        assert serializers.is_valid()
        temp_job = serializers.create(serializers.validated_data)
        temp_job.group = job[u'group']
        _job += [temp_job, ]

    # TODO: Assert all engine is valid in this stage
    map(lambda x: x.save(), _job)

    return {"msg": "Change successful"}


def start_all_initializing_job(_group):

    def sync_engine_executor(s_job):
        try:

            s_job.job_status = CONSTANTS.JOB.STATUS.get("PENDING")
            s_job.save()

            s_engine = EngineProvider.provide(s_job.job_engine, group=_group, params=s_job.parameter)
            s_engine.execute()
            # TODO: we should be able to update the s_job's status if s_job is some continuous guys
            # Do something to update s_engine status

            s_engine.event_init()
            s_engine.job_status = CONSTANTS.JOB.STATUS.get("UPDATED")
        # Use custom Exception case to wrap all the exception from Engine Execution
        except EngineExecutingError as _e:
            s_job.job_status = CONSTANTS.JOB.STATUS.get("FAILED")
            s_job.job_error_message = _e
            s_job.save()

        except EngineProviderNotFound:
            # It should be fixed in production case
            pass

    _initializing_jobs = Job.objects(group=_group, job_status=CONSTANTS.JOB.STATUS.get("INITIALIZING"))

    for job in _initializing_jobs:
        p = Process(target=sync_engine_executor, args=(job, ))
        p.start()

    # return when all the jobs are executed
    return {"msg": "Change successful"}
