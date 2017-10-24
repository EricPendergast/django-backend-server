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
    def select_job_list(self, request):
        # TODO: make it only getting pending events?
        """
        Select list of all events with single event category.
        @param: event_type
        """

        data = map(lambda _x: _x['first'],
                   list(Job.objects(group=request.user.group)))
        serializer = DetailedJobSerializer(data, many=True, required=True)
        return Response([x for x in serializer.data])