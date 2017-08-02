from mongoengine.django import auth
from mongoengine import fields, Document

from eledata.models.analysis_questions import GroupAnalysisSettings

class Group(Document):
    # 'counter' is used for testing
    counter = fields.IntField(default=0)
    name = fields.StringField(max_length=80, unique=True, required=True)
    analysis_settings = fields.EmbeddedDocumentField(GroupAnalysisSettings, required=True)

class User(auth.User):
    # 'counter' is used for testing
    counter = fields.IntField(default=0)
    group = fields.ReferenceField(Group)
    is_group_admin = fields.BooleanField(default=False)
    
