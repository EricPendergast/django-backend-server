from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from eledata.auth import CustomLoginRequiredMixin

from django.http import HttpResponse

from eledata.serializers.entity import *
from eledata.verifiers.entity import *
from eledata.handlers.create_entity import *

def index_view(request):
    return HttpResponse("index stub page")


class EntityViewSet(CustomLoginRequiredMixin, viewsets.ViewSet):
    """
    Read-only User endpoint
    """

    """
    Get all entity summary
    """

    @list_route(methods=['get'])
    def get_all_entity(self, request):
        query_set = Entity.objects(group=request.user.group)
        serializer = EntitySummarySerializer(query_set, many=True, required=True)
        return Response(serializer.data)

    """
    Get list of entity with status
    """

    @list_route(methods=['get'])
    def get_entity_list(self, request):
        processing_query_set = Entity.objects(group=request.user.group, state=1).fields(type=1)
        completed_query_set = Entity.objects(group=request.user.group, state=2).fields(type=1)
        response_data = EntityViewSetHandler.get_entity_list(processing_query_set, completed_query_set)
        return Response(response_data)

    """
    Select Entity in-details
    @param: entity_type
    """

    @detail_route(methods=['get'])
    def select_entity(self, request, pk=None):

        # TODO: enhance the style by breaking into two views and move to handler
        filterKey = request.query_params.get('filterKey', None)
        filterValue = request.query_params.get('filterValue', None)
        order = request.query_params.get('order', None)
        page = request.query_params.get('page', None)
        rowSize = request.query_params.get('rowSize', None)
        sort = request.query_params.get('sort', None)
        # preparing pipeline
        operators = [{"$unwind": "$data"}]
        count_operators = [{"$unwind": "$data"}]

        if filterKey and filterValue:
            match_operator = {"$match": {"data." + filterKey: {"$regex": ".*" + filterValue + ".*"}}}
            operators.append(match_operator)
            count_operators.append(match_operator)

        if sort and order:
            order = 1 if order == 'asc' else -1
            sort_operator = {"$sort": {"data." + sort: order}}
            operators.append(sort_operator)
        if rowSize and page:
            skip = (int(page) - 1) * int(rowSize)
            skip_operator = {"$skip": skip}
            operators.append(skip_operator)
        if rowSize:
            limit_operator = {"$limit": int(rowSize)}
            operators.append(limit_operator)

        operators.append({"$group": {"_id": "$_id", "data": {"$push": "$data"}, }})
        count_operators.append({"$group": {"_id": "$_id", "count": {"$sum": 1}, }})

        grid_query_set = Entity.objects(type=pk, group=request.user.group).fields(data=0).first()
        _response_data = EntityViewSetHandler.select_entity(grid_query_set)
        response_data = _response_data

        if _response_data is not None:
            data_query_set = list(Entity.objects(type=pk, group=request.user.group).aggregate(*operators))
            count_query_set = list(Entity.objects(type=pk, group=request.user.group).aggregate(*count_operators))

            if len(data_query_set):
                data_view = EntityDetailedSerializer(data=data_query_set[0])
                if data_view.is_valid():
                    print(count_query_set[0])
                    response_data['data'] = data_view.data['data']
                    response_data['count'] = count_query_set[0][u'count']
        return Response(response_data)

    """
    Creates an entity (without mapping information). Adds it to the group of
    the user who made the request
    
    If there is an error, the response will contain an "error" key, which will
    map to the error message. Otherwise it will send a response with the
    following:
    
        "entity_id", which maps to the id of the newly created entity
        "data", which maps to the first 100 lines of data parsed from the input
            file, with the original headers, or generated headers if no headers
            were given
    """

    @list_route(methods=['post'])
    def create_entity(self, request):
        # 0. checking (to be developed afterwards)
        # 1. getting csv/tsv information, header information, uploaded data
        # 2. save file to temp dir
        # 3. save basic entity information, temp dir folder "progressing" state in mongo
        # 4. return 100 rows of data
        # try:
        verifier = CreateEntityVerifier()
        verifier.verify(0, request)

        response_data = EntityViewSetHandler.create_entity(
            request_data=request.data,
            request_file=request.FILES['file'],
            group=request.user.group,
            verifier=verifier)

        assert verifier.verified
        return Response(response_data, status=200)
        # except:
        #     return Response({"error": "fileError"}, status=400)


    """
    Creating entity (with mapping information)
    """

    @detail_route(methods=['post'])
    def create_entity_mapped(self, request, pk=None):
        # 0. checking (to be developed afterwards)
        # 1. getting targeted entity from data
        # 2. getting header_name/ column_type mapping information from data
        # 3. validating mapping (to be developed afterwards)
        # 4. return 100 rows of data

        verifier = CreateEntityMappedVerifier()
        response_data = EntityViewSetHandler.create_entity_mapped(
            request_data=request.data,
            verifier=verifier,
            pk=pk,
            group=request.user.group)

        assert verifier.verified
        return Response(response_data, status=200)

    @list_route(methods=['post'])
    def remove_stage1_entity(self, request):
        verifier = RemoveStage1EntityVerifier()
        response_data = EntityViewSetHandler.remove_stage1_entity(
            request_data=request.data,
            verifier=verifier,
            group=request.user.group)

        assert verifier.verified
        return Response(response_data, status=200)
