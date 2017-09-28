from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from eledata.auth import CustomLoginRequiredMixin

from eledata.serializers.event import *
from eledata.verifiers.event import *
import eledata.handlers.event as handler
from eledata.models.event import *
from project.settings import CONSTANTS


class EventViewSet(CustomLoginRequiredMixin, viewsets.ViewSet):
    """
    Read-only User endpoint
    """

    @list_route(methods=['get'])
    def get_general_event(self, request):
        """
        Get all general events
        """
        query_set = Event.objects(group=request.user.group)
        serializer = GeneralEventSerializer(query_set, many=True, required=True)
        response = {
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
        return Response(response)

    @detail_route(methods=['get'])
    def select_event(self, request, pk=None):
        """
        Select event list
        @param: event_type
        """
        event = Event.objects(event_category=pk, group=request.user.group)
        if event is None:
            return Response()
        if event.group != request.user.group:
            return Response({"error": "User does not have permission to access this event"})
        serializer = DetailedEventSerializer(event, many=True, required=True)
        return Response(serializer.data)

    """
    Event is created by Core_Engine but not user request, user can only view and mark action on event status
    """

    @list_route(methods=['put'])
    def update_event_status(self, request):
        """
        Update Event Status
        :param request:
            {
                "event_id": event_id
                "status": true/false
            }
        :return:
        """
        verifier = UpdateEventStatusVerifier()
        verifier.verify(0, request.data)

        event = Event.objects(_id=request.data.event_id).first()

        response_data = handler.update_event_status(
            event=event,
            status=request.data.status,
            verifier=verifier)

        assert verifier.verified
        return Response(response_data, status=200)
