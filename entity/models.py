# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from mongoengine import *
import datetime
from django.contrib.auth.hashers import check_password, make_password


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
    file = StringField()
    link = StringField()
    account = StringField()
    password = StringField(max_length=255)

    def check_password(self, raw_password):
        """
        Checks the user's password against a provided password - always use
        this rather than directly comparing to
        :attr:`~mongoengine.django.auth.User.password` as the password is
        hashed before storage.
        """
        return check_password(raw_password, self.password)

    def set_password(self, raw_password):
        """
        Sets the user's password - always use this rather than directly
        assigning to :attr:`~mongoengine.django.auth.User.password` as the
        password is hashed before storage.
        """
        self.password = make_password(raw_password)
        self.save()
        return self


class Entity(Document):
    type = StringField(max_length=20)
    source_type = StringField(max_length=15)
    source = EmbeddedDocumentField(DataSource)
    data_summary = EmbeddedDocumentListField(DataSummary)
    data_summary_chart = EmbeddedDocumentListField(DataSummary)
    data = ListField()
    data_header = EmbeddedDocumentListField(DataHeader)
    allowed_user = ListField()
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
