from mongoengine.django import auth
from mongoengine import fields, Document
from project.settings import constants


class Group(Document):
    from eledata.models.analysis_questions import GroupAnalysisSettings

    # 'counter' is used for testing
    counter = fields.IntField(default=0)
    name = fields.StringField(max_length=80, unique=True, required=True)
    analysis_settings = fields.EmbeddedDocumentField(GroupAnalysisSettings, required=True)

    @classmethod
    def create_group(cls, name):
        from eledata.models.analysis_questions import GroupAnalysisSettings
        group = cls(name=name)
        group.analysis_settings = \
            GroupAnalysisSettings(**constants().get('analysis_settings'))
        group.save()

        return group

    def update_analysis_question_enable(self):
        from eledata.models.entity import Entity
        group = self
        # Further filter by property
        completed_entity = [x.type for x in Entity.objects(group=group) if x.is_completed]

        for question in group.analysis_settings.questions:
            question.enabled = set(question.required_entities).issubset(set(completed_entity))
        group.save()

    # TODO: has_entity function from group model
    # def has_entity(self, entity_name):


class User(auth.User):
    # 'counter' is used for testing
    counter = fields.IntField(default=0)
    group = fields.ReferenceField(Group)
    is_group_admin = fields.BooleanField(default=False)

    # Creates a group admin user with the given name. Creates a new group with
    # name=group_name if one does not already exist
    @classmethod
    def create_admin(cls, username, password, group_name, email=None):
        admin = User.create_user(username=username, password=password, email=email)
        admin.is_group_admin = True
        if not Group.objects(name=group_name):
            admin.group = Group.create_group(name=group_name)

        admin.save()
        return admin
