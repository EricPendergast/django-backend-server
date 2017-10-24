from mongoengine import *
from .users import Group
import datetime
from project.settings import CONSTANTS

"""
Event is a under group-referencing Document, auto-saving response generated by engines. 
Presentation use most likely.
"""


class EventChart(EmbeddedDocument):
    labels = ListField()
    x_label = StringField()
    y_label = StringField()
    r_label = StringField()
    x_stacked = BooleanField()
    y_stacked = BooleanField()
    datasets = ListField(DictField())


class EventDetailData(EmbeddedDocument):
    data = ListField(DictField())
    columns = ListField(DictField())


class Event(Document):
    event_id = ObjectIdField()  # We create a manual ObjectIdField for update
    event_category = StringField()
    event_type = StringField()  # We can check if event_type is under event category
    event_value = DictField()  # Update string to key value pair, for i18n purpose mainly

    event_desc = ListField(DictField())
    detailed_desc = ListField(DictField())
    analysis_desc = ListField(DictField())

    chart_type = StringField()  # Defined by event_type actually
    chart = EmbeddedDocumentField(EventChart)
    detailed_data = EmbeddedDocumentField(EventDetailData)
    expiry_date = DateTimeField()  # Only when status is not C
    event_status = StringField(default=CONSTANTS.EVENT.STATUS.get('INITIALIZING'))
    # event_status = StringField(
    #     default=constants().get('event').get('category').get(
    #         'initializing'))  # I = initializing, P = pending, # T = taken, # A = aborted, # C = continuous
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    tabs = DictField()
    selected_tab = DictField()

    # Not disposed, saving mother data here and present aggregated detailed_data and chart_data
    source_data = ListField(DictField())  # Only when status is C
    update_freq = IntField()  # Only when status is C, by hour
    group = ReferenceField(Group)

    # Disabled as so much referencing field would not be desired for MongoDB
    # # Referencing back to the analysis question, make tracking back easier
    # ref_analysis_question_label = StringField()
    # # Referencing back to the analysis parameter, make tracking back easier
    # ref_analysis_parameter_labels = ListField(StringField())

    @queryset_manager
    def objects(self, _queryset):
        """
        Reset query object with default order by updated_at

        This may actually also be done by defining a default ordering for
        the document, but this illustrates the use of manager methods
        """
        return _queryset.order_by('-updated_at')

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()

        super(Event, self).save(*args, **kwargs)

    def get_analysis_question(self, _label):
        _group = self.group
        for obj in _group.analysis_settings.questions:
            if obj.label == _label:
                return obj


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

    group = ReferenceField(Group)
    parameter = ListField(DictField())

    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    @queryset_manager
    def objects(self, _queryset):
        """
        Reset query object with default order by updated_at

        This may actually also be done by defining a default ordering for
        the document, but this illustrates the use of manager methods
        """
        return _queryset.order_by('-updated_at')

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()

        super(Job, self).save(*args, **kwargs)
