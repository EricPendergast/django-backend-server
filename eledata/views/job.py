from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from eledata.auth import CustomLoginRequiredMixin

from eledata.serializers.job import *
from eledata.verifiers.event import *
import eledata.handlers.event as handler
from eledata.models.job import *
from project.settings import CONSTANTS


class JobViewSet(CustomLoginRequiredMixin, viewsets.ViewSet):
    """
    Read-only User endpoint
    """

    @list_route(methods=['get'])
    def select_job_list(self, request):
        # TODO: make it only getting pending events?
        """
        Select list of all job.
        @param: event_type
        """
        data = Job.objects(group=request.user.group).order_by('-created_at')
        serializer = DetailedJobSerializer(data, many=True, required=True)
        return Response(serializer.data)
