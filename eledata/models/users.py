# from __future__ import unicode_literals
# from mongoengine import *
#
# from eledata.models.analysis import *
#
#
# ## Note: for now this is dead code
# class User(Document):
#     settings = EmbeddedDocumentField(UserSettings)
#
# class Settings(EmbeddedDocument):
#     analysis_questions = EmbeddedDocumentField(UserAnalysisQuestions)
# ##
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

class Group(Document):
    # 'counter' is used for testing
    counter = fields.IntField(default=0)
    name = fields.StringField(max_length=80, unique=True)

class User(auth.User):
    # 'counter' is used for testing
    counter = fields.IntField(default=0)
    group = fields.ReferenceField(Group)
    

#TODO: Is Token being used by anything?
@python_2_unicode_compatible
class Token(Document):
    """
    This is a mongoengine adaptation of DRF's default Token.

    The default authorization token model.
    """
    key = fields.StringField(required=True)
    # user = fields.ReferenceField(User, reverse_delete_rule=mongoengine.CASCADE)
    user = fields.ReferenceField(User, reverse_delete_rule=mongoengine.CASCADE)
    created = fields.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
