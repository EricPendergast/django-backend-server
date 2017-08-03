from mongoengine.django import auth
from mongoengine import fields, Document

from eledata.models.analysis_questions import GroupAnalysisSettings

from project import settings

class Group(Document):
    # 'counter' is used for testing
    counter = fields.IntField(default=0)
    name = fields.StringField(max_length=80, unique=True, required=True)
    analysis_settings = fields.EmbeddedDocumentField(GroupAnalysisSettings, required=True)
    
    @classmethod
    def create_group(cls, name):
        group = cls(name=name)
        group.analysis_settings = \
                GroupAnalysisSettings(**settings.CONSTANTS['analysis_settings'])
        group.save()
        
        return group
        

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
