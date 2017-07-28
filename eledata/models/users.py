import datetime
import binascii
import os

from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import _user_has_perm, _user_get_all_permissions, _user_has_module_perms

import mongoengine
from mongoengine.django import auth
from mongoengine import fields, Document, ImproperlyConfigured

from eledata.models.analysis_questions import GroupAnalysisSettings

class Group(Document):
    # 'counter' is used for testing
    counter = fields.IntField(default=0)
    name = fields.StringField(max_length=80, unique=True)
    analysis_settings = fields.EmbeddedDocumentField(GroupAnalysisSettings)

class User(auth.User):
    # 'counter' is used for testing
    counter = fields.IntField(default=0)
    group = fields.ReferenceField(Group)
    
