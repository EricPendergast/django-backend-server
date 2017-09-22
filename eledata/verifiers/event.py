from eledata.verifiers.verifier import Verifier
from eledata.util import InvalidInputError
from project.settings import constants


class UpdateEventStatusVerifier(Verifier):
    def stage0(self, request_data):
        if 'event_id' not in request_data or 'status' not in request_data:
            raise InvalidInputError('Invalid input for updating event status')

    def stage1(self, event):
        if not event:
            raise InvalidInputError("No corresponding event exists")

    def stage2(self, event):
        if event.event_status is not constants().get('Event').get("Status").get("Pending"):
            raise InvalidInputError("No pending event is found")

    stages = [stage0, stage1, stage2, ]


class InitNewEventVerifier(Verifier):
    def stage0(self, event_obj):
        # check event_obj if all tasks from event_spec is done
        pass

    def stage1(self, serializer):
        if not serializer.is_valid():
            raise InvalidInputError("Invalid serializer")

    stages = [stage0, stage1, ]
