import os.path
import uuid

from eledata import util
from eledata.serializers.entity import EntityDetailedSerializer
from eledata.models.entity import Entity
from eledata.util import string_caster
from eledata.core.entity_frame import EntityFrame

from project import settings


class EntityViewSetHandler():
    @staticmethod
    def get_entity_list(entity_list):

        # retrieving list of active entity
        active_list = [x.type for x in entity_list]

        # retrieving list of constant entity
        constant_list = settings.CONSTANTS['entity']['type']
        for x in constant_list:
            x[u'status'] = u'Ready' if x['value'] in active_list else u'Pending'
        return constant_list

    @staticmethod
    def create_entity(request_data, request_file, group, verifier):
        verifier.verify(1, request_data)
        # The dir that the uploaded data file will be saved to.
        # Appending the original filename to the end so that the new
        # filename has the same extension, while also making the filename
        # more recognizable.
        filename = "temp/" + str(uuid.uuid4()) + "." + str(request_file)

        with open(filename, "w") as fi:
            fi.write(request_file.read())
        # Parsing the entity JSON passed in into a dictionary
        entity_dict = util.from_json(request_data["entity"])

        entity_dict["source"] = {
            "file": {"filename": filename,
                     "is_header_included": request_data["isHeaderIncluded"]}}

        entity_dict['state'] = 1
        verifier.verify(2, entity_dict)

        # TODO: calculate draft of data summary here?
        entity_data = util.file_to_list_of_dictionaries(
            open(entity_dict["source"]["file"]["filename"]),
            numLines=100,
            is_header_included=util.string_caster["bool"](
                entity_dict["source"]["file"]["is_header_included"]))

        serializer = EntityDetailedSerializer(data=entity_dict)
        verifier.verify(3, serializer)

        entity = serializer.create(serializer.validated_data)
        entity.group = group
        entity.save()

        response_data = {}
        # Saving the serializer while also adding its id to the response
        response_data['entity_id'] = str(entity.id)
        # Loading the first 100 lines of data from the request file
        response_data['data'] = entity_data
        # Passing header option from constants file
        response_data['header_option'] = \
            settings.CONSTANTS['entity']['header_option'][entity_dict["type"]]

        return response_data

    @staticmethod
    def create_entity_mapped(request_data, verifier, pk, group):
        entity = Entity.objects.get(pk=pk)
        verifier.verify(0, request_data, entity, pk)
        verifier.verify(1, entity, group)
        verifier.verify(2, request_data['data_header'], entity.source.file.filename)

        # We will create a dummy entity whose only purpose is to serialize the
        # two fields we give it, so we can add them to the actual entity. The
        # dummy starts as a dictionary and then becomes an Entity.
        dummy = {}
        dummy['data_header'] = request_data['data_header']

        assert os.path.isfile(entity.source.file.filename)
        data = util.file_to_list_of_dictionaries(
            open(entity.source.file.filename, 'r'),
            is_header_included=entity.source.file.is_header_included)

        # Changing the user created field names in data to the new mapped names
        for item in data:
            for mapping in dummy['data_header']:
                item[mapping["mapped"]] = item[mapping["source"]]
                del item[mapping["source"]]

        # Casting everything in data from strings to their proper data type
        # according to request.data['data_header']
        for item in data:
            for mapping in dummy['data_header']:
                item[mapping["mapped"]] = \
                    string_caster[mapping["data_type"]](item[mapping["mapped"]])

        # Generating Entity Summary after mapping is confirmed.
        entity_frame = EntityFrame.frame_from_file(entity_data=data, entity_type=entity.type)
        dummy['data_summary'] = entity_frame.get_summary()

        dummySerializer = EntityDetailedSerializer(data=dummy)

        verifier.verify(3, dummySerializer)

        dummy = Entity(**dummySerializer.validated_data)

        # Adding the dummy's fields to the actual entity

        entity.add_change(data)
        entity.data_header = dummy.data_header
        entity.data_summary = dummy.data_summary

        os.remove(entity.source.file.filename)
        entity.source.file = None
        entity.state = 2
        entity.save()
        entity.save_data_changes()
        return data[:100]
