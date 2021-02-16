from django.core.management import BaseCommand
from eledata.models.entity import Entity, Change
from eledata.models.users import User, Group
from eledata.models.event import Event
from eledata.models.job import Job
from project.settings import CONSTANTS
from eledata.core_engine.provider import EngineProvider
from eledata.core_engine.h2o_engine.h2o_engine import H2OEngine
import datetime
from bson import objectid


# from eledata.models.analysis_questions import AnalysisQuestion, AnalysisParameter

# The class must be named Command, and subclass BaseCommand

# TODO: to be tested
class Command(BaseCommand):
    # A command must define handle()
    def handle(self, *args, **options):
        # H2O gc
        def h2o_gc(_job_list_cnt):
            if _job_list_cnt == 0:
                H2OEngine.overall_gc()

        # cron_job_related
        def get_engine_frequency():
            return datetime.timedelta(hours=12)

        executing_job_cnt = Job.objects(job_status__in=[
            CONSTANTS.JOB.STATUS.get('PENDING'),
            # CONSTANTS.JOB.STATUS.get('CONTINUOUS'), H2O job will not be continuous
            CONSTANTS.JOB.STATUS.get('UPDATING')
        ]).count()

        h2o_gc(executing_job_cnt)

        # Continuous jobs update
        continuous_job = Job.objects(job_status=CONSTANTS.JOB.STATUS.get('CONTINUOUS'))
        if continuous_job:
            for job in continuous_job:
                _old_event_id = job.event_id
                _new_event_id = objectid.ObjectId()

                engine = EngineProvider.provide(job.job_engine, event_id=_new_event_id,
                                                group=job.group, params=job.parameter)
                # TODO: make it sync?
                if datetime.datetime.now() > job.scheduled_at:
                    engine.execute()
                    engine.event_init()
                    Event.objects(pk=job.event_id).update_one(
                        status=CONSTANTS.EVENT.STATUS.get("ABORT")
                    )
                    job.event_id = _new_event_id
                    job.save()
