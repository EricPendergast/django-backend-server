from mongoengine import *
from .users import Group
import datetime
from project.settings import CONSTANTS


class Job(Document):
    """
    Created just before engines are executed.

    Job mainly plays 2 roles:
    - Providing a middle layer between Engines action and Events, so the life cycle and be traced
    and manipulated before Event objects.

    - Action to be displayed (in the future), or easily manipulated (in case error happens)

    Well its not appear in the first design, but its common!
    """

    job_engine = StringField()
    job_status = StringField()
    job_error_message = StringField()

    event_id = ObjectIdField()
    event_type = StringField()

    group = ReferenceField(Group)
    parameter = ListField(DictField())

    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()

        super(Job, self).save(*args, **kwargs)
