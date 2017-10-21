from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from eledata.auth import CustomLoginRequiredMixin

from eledata.serializers.event import *
from eledata.verifiers.event import *
import eledata.handlers.stats as handler
from eledata.models.entity import *
from project.settings import CONSTANTS


class StatsViewSet(CustomLoginRequiredMixin, viewsets.ViewSet):
    """
    Read-only User endpoint
    """

    @list_route(methods=['get'])
    def get_entity_data_metrics(self, request):
        """
        Get all entity data metrics
        """
        entities = Entity.objects(group=request.user.group, state=2).fields(type=1, data_summary_chart=1, state=1)

        response = handler.get_entity_data_metrics(entities)
        return Response(response, status=200)

    @list_route(methods=['get'])
    def get_event_dashboard_summary(self, request):
        """
        Get event summary statistics for dashboard info boxes.
        :param request: object, With user information
        :return:
        """
        query_set = Event.objects(group=request.user.group, event_status=CONSTANTS.EVENT.STATUS.get("PENDING"))
        response_data = handler.get_event_dashboard_summary(
            pending_events=query_set,
        )
        return Response(response_data, status=200)
