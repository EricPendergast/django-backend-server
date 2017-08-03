from eledata import util
from eledata.util import InvalidInputError
from verifier import Verifier
from project import settings


class CreateEntityVerifier(Verifier):
    def stage0(self, request):
        if not ('entity' in request.data):
            raise InvalidInputError("No entity data in request")
        if not ('file' in request.FILES):
            raise InvalidInputError("No file uploaded")
        if not ('isHeaderIncluded' in request.data):
            raise InvalidInputError("Didn't specify whether the file header is included")

    def stage1(self, request_data):
        pass

    def stage2(self, entity_dict):
        options = {"type": settings.CONSTANTS['entity']['type'],
                   "source_type": settings.CONSTANTS['entity']['source_type'],
                   "state": {1}}

        required = {"type", "source_type", "state"}

        Verifier.ver_dict(entity_dict, required, options)

    def stage3(self, serializer):
        if not serializer.is_valid():
            raise InvalidInputError("Invalid serializer")

    stages = [stage0, stage1, stage2, stage3]


class CreateEntityMappedVerifier(Verifier):
    def stage0(self, request_data, entity, pk):
        if entity is None:
            raise InvalidInputError("Can't find the entity with the given id: %s" % pk)
        if not ('data_header' in request_data):
            raise InvalidInputError("No data header.")

    def stage1(self, entity, group):
        if entity.group != group:
            raise InvalidInputError("User does not have permission to access this entity")

    def stage2(self, headers, entity_source_file):
        required = {"source", "mapped", "data_type"}
        options = {"data_type": util.string_caster, }

        for header in headers:
            Verifier.ver_dict(header, required, options)

        if entity_source_file == None:
            raise InvalidInputError("Can't find the entity source file.")

    def stage3(self, serializer):
        if not serializer.is_valid():
            raise InvalidInputError("Invalid serializer")

    stages = [stage0, stage1, stage2, stage3]
