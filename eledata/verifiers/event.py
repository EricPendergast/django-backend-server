from eledata.verifiers.verifier import Verifier
from eledata.util import InvalidInputError
from project.settings import CONSTANTS


class UpdateEventStatusVerifier(Verifier):
    def stage0(self, request_data):
        if 'event_id' not in request_data or 'status' not in request_data:
            raise InvalidInputError('Invalid input for updating event status')

    def stage1(self, event):
        if not event:
            raise InvalidInputError("No corresponding event exists")

    def stage2(self, event):
        if event.event_status is not CONSTANTS.EVENT.STATUS.get("PENDING"):
            raise InvalidInputError("No pending event is found")

    stages = [stage0, stage1, stage2, ]


class InitNewEventVerifier(Verifier):
    def stage0(self, event_obj):
        # print(event_obj)
        pass

    def stage1(self, group):
        if not group:
            raise InvalidInputError("No group object is used to init new event")

    def stage2(self, serializer):
        if not serializer.is_valid():
            raise InvalidInputError("Invalid serialized data")

    def stage3(self, _new_event_obj):
        if not _new_event_obj.group:
            raise InvalidInputError("No group object is referable")

    stages = [stage0, stage1, stage2, stage3, ]
