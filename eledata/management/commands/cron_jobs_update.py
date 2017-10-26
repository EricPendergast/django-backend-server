from django.core.management import BaseCommand
from eledata.models.entity import Entity, Change
from eledata.models.users import User, Group
from eledata.models.job import Job
from project.settings import CONSTANTS
from eledata.core_engine.provider import EngineProvider
from eledata.core_engine.h2o_engine.h2o_engine import H2OEngine
import datetime


# from eledata.models.analysis_questions import AnalysisQuestion, AnalysisParameter

# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # A command must define handle()
    def handle(self, *args, **options):
        # H2O gc
        def h2o_gc(_job_list_cnt):
            if _job_list_cnt == 0:
                H2OEngine.overall_gc()

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

                time_difference = datetime.datetime.now() - job.updated_at
                engine = EngineProvider.provide(job.job_engine, group=job.group, params=job.parameter)

                if time_difference > engine.get_engine_frequency():
                    engine.execute()
                    engine.event_init()
