from eledata.serializers.event import *
from eledata.verifiers.event import *


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

    serializer = DetailedEventSerializer(data=event_object)

    verifier.verify(1, serializer)
    _new_event = serializer.create(serializer.validated_data)
    _new_event.group = _group

    assert verifier.verified
    _new_event.save()
    return {"msg": "Change successful"}
