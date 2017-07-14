from __future__ import unicode_literals
from mongoengine import *

from eledata.models.analysis import *

class User(Document):
    settings = EmbeddedDocumentField(UserSettings)
    
class Settings(EmbeddedDocument):
    analysis_questions = EmbeddedDocumentField(UserAnalysisQuestions)
