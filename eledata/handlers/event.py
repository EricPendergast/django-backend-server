from urllib2 import URLError

from eledata.serializers.event import *
from eledata.serializers.job import *
from eledata.verifiers.event import *
from project.settings import CONSTANTS
from eledata.core_engine.provider import EngineProvider
from eledata.util import EngineExecutingError
from multiprocessing import Process
import time
from bson import objectid
from bson.json_util import dumps
from dateutil.relativedelta import relativedelta


def get_general_event(group):
    """
    Return the events among each categories
    :param group: object, user group mongo object
    :return: dictionary, having merged events
    """
    # Querying from MongoDB. Grouping by sku_id, search_keyword and platform
    pipeline = [
        {
            "$group": {
                "_id": {
                    "event_id": "$event_id",
                },
                "first": {"$first": "$$ROOT"},
            }
        }
    ]
    data = map(lambda _x: _x['first'], list(Event.objects(group=group).aggregate(*pipeline)))
    serializer = GeneralEventSerializer(data, many=True, required=True)
    return {
        "opportunity": [
            x for x in serializer.data if
            x.get('event_category') == CONSTANTS.EVENT.CATEGORY.get('OPPORTUNITY')
        ],
        "risk": [
            x for x in serializer.data if
            x.get('event_category') == CONSTANTS.EVENT.CATEGORY.get('RISK')
        ],
        "insight": [
            x for x in serializer.data if
            x.get('event_category') == CONSTANTS.EVENT.CATEGORY.get('INSIGHT')
        ]
    }


def select_event_list(group, event_category):
    """
    Return event list of brief information among single category
    :param group: object, user group MongoDB object
    :param event_category: string, user input for category, to be mapped to get constants
    :return: dictionary, list of events
    """
    # Querying from MongoDB. Grouping by sku_id, search_keyword and platform
    pipeline = [
        {
            "$group": {
                "_id": {
                    "event_id": "$event_id",
                },
                "first": {"$first": "$$ROOT"},
            }
        }
    ]
    data = map(lambda _x: _x['first'],
               list(Event.objects(group=group, event_category=CONSTANTS.EVENT.CATEGORY.get(event_category.upper()))
                    .aggregate(*pipeline)))
    serializer = GeneralEventSerializer(data, many=True, required=True)
    return [x for x in serializer.data]


def select_event(event_id, group, query_params):
    if query_params:
        event_data = Event.objects(
            group=group, event_id=objectid.ObjectId(event_id))
        selected_event_data = filter(lambda x: dumps(x['selected_tab']) == dumps(query_params), event_data)[0]
        return DetailedEventSerializer(selected_event_data, required=True).data
    else:
        event_data = Event.objects(
            group=group, event_id=objectid.ObjectId(event_id)
        ).first()
    return DetailedEventSerializer(event_data, required=True).data


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
        # Assert all engine is valid in this stage
        assert EngineProvider.provide(job.get('job_engine'), None, None, None)

        serializers = GeneralJobSerializer(data=job)

        assert serializers.is_valid()

        temp_job = serializers.create(serializers.validated_data)
        temp_job.group = job[u'group']
        _job += [temp_job, ]

    # Only save jobs and return when all jobs are valid
    map(lambda x: x.save(), _job)

    return {"msg": "Change successful"}


def start_all_initializing_job(_group):
    def sync_engine_executor(s_job):
        try:
            engine_prefix, engine_postfix = s_job.job_engine.split('.')

            _event_id = objectid.ObjectId()

            # TODO: handle overwriting and multi instance continuous engine
            # if engine_prefix == 'ContinuousMonitoring' and THERE_EXIST_IDENTICAL RUNNING ENGINE

            s_job.job_status = CONSTANTS.JOB.STATUS.get("PENDING")
            s_job.save()
            s_engine = EngineProvider.provide(s_job.job_engine, event_id=_event_id,
                                              group=_group, params=s_job.parameter)

            # TODO: Show more detailed engine process by passing s_job to s_engine to update.
            s_engine.execute()

            # TODO: Event_status should be used in the event_init(); Exception should have been threw in case for KeyError.
            s_engine.event_init()

            # TODO: what i am doing with this event?
            event = Event.objects(event_id=_event_id).first()

            # Use engine prefix in provider to identify
            if engine_prefix == "ContinuousMonitoring":
                updated_time = datetime.datetime.now()
                s_job.event_id = _event_id
                s_job.job_status = CONSTANTS.JOB.STATUS.get("CONTINUOUS")
                s_job.updated_at = updated_time
                s_job.scheduled_at = updated_time + relativedelta(hours=12)
            else:
                s_job.event_id = _event_id
                s_job.job_status = CONSTANTS.JOB.STATUS.get("UPDATED")
            s_job.save()
        # Use custom Exception case to wrap all the exception from Engine Execution
        except (KeyError, EngineExecutingError, URLError, ValueError, KeyError, IndexError) as _e:
            s_job.job_status = CONSTANTS.JOB.STATUS.get("FAILED")
            s_job.job_error_message = _e.message
            s_job.save()

    _initializing_jobs = Job.objects(group=_group, job_status=CONSTANTS.JOB.STATUS.get("INITIALIZING"))

    for job in _initializing_jobs:
        # Loosen racing condition by firing jobs with slightly delay
        time.sleep(1)

        p = Process(target=sync_engine_executor, args=(job,))
        p.start()

    # return when all the jobs are executed
    return {"msg": "Change successful"}
