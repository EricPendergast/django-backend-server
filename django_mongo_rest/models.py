# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from mongoengine import *
import bcrypt
import datetime
# Create your models here.

# example entity document


class DataHeader(EmbeddedDocument):
    source = StringField()
    mapped = StringField()
    data_type = StringField()


class DataSummary(EmbeddedDocument):
    key = StringField()
    value = StringField()
    order = IntField(unique=True)


class DataSource(EmbeddedDocument):
    link = StringField()
    account = StringField()
    _password = StringField(max_length=255)

    def __init__(self, *args, **kwargs):
        EmbeddedDocument.__init__(self, *args, **kwargs)

        if 'password' in kwargs:
                self.password = kwargs[str('password')]

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = bcrypt.hashpw(password, bcrypt.gensalt())


class Entity(Document):
    type = StringField(max_length=20)
    source_type = StringField(max_length=15)
    source = EmbeddedDocumentField(DataSource)
    data_summary = EmbeddedDocumentListField(DataSummary)
    data_summary_chart = EmbeddedDocumentField(DataSummary)
    data = SortedListField(DictField)
    data_header = EmbeddedDocumentListField(DataHeader)
    allowed_user = ListField()
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

