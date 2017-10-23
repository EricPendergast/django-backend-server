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
        # TODO: make it only getting pending events?
        """
        Get all general events
        """
        response = handler.get_general_event(request.user.group)
        return Response(response)

    @detail_route(methods=['get'])
    def select_event_list(self, request, pk=None):
        # TODO: make it only getting pending events?
        """
        Select list of all events with single event category.
        @param: event_type
        """
        response = handler.select_event_list(
            group=request.user.group, event_category=pk
        )
        return Response(response)

    @detail_route(methods=['get'])
    def select_event(self, request, pk=None):
        """
        Select single event by event_id with detailed value
        :param request: object, user request with grouping and credentials
        :param pk: string, event_id
        :return: object, detailed single event
        """
        response = handler.select_event(event_id=pk, group=request.user.group)
        print(response)
        return Response(response)

    # Event is created by Core_Engine but not user request, user can only view and mark action on event status
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
