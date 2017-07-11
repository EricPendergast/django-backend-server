# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from mongoengine import *
import datetime
from django.contrib.auth.hashers import check_password, make_password

import util

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
    
    
    
class Verifier(object):
    @classmethod
    def ver_field(cls, field_name, field_content):
        assert cls is not Verifier, "class 'Verifier' is abstract"
        return not (field_name in cls.fields_options) or (field_content in cls.fields_options[field_name])
    
    @classmethod
    def ver_all(cls, all_data):
        # Verify 'all_data' has all the required fields
        for field in cls.required_fields:
            if not field in all_data:
                return False
        # Verify that every field in 'all_data' follows the correct format
        for field in all_data:
            if not cls.ver_field(field, all_data[field]):
                return False
        
        return True
    
    
class EntityVerifier(Verifier):
    fields_options = {"type":{"transaction", "something else",},
            "source_type": {"local",}}
    
    required_fields = {"type", "source_type"}
    
    
class DataHeaderVerifier(Verifier):
    fields_options = {"data_type":util.string_caster}
    
    required_fields = {"source","mapped","data_type"}
