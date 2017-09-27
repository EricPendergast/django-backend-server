from django.core.management import BaseCommand
from eledata.models.entity import Entity, Change
from eledata.models.users import User, Group


# from eledata.models.analysis_questions import AnalysisQuestion, AnalysisParameter

# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    # A command must define handle()
    def handle(self, *args, **options):
        # Remove all the existing data
        Entity.drop_collection()
        Change.drop_collection()
        User.drop_collection()
        Group.drop_collection()
        self.stdout.write(self.OKGREEN + "Removed all the existing records!" + self.ENDC)

        User.create_admin(username="admin", password="password", group_name="Wright")
        self.stdout.write(self.OKGREEN + "Default Admin initialized!" + self.ENDC)
