"""django_mongoengine_restful URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin, auth

admin.autodiscover()

from eledata.views.create_entity import *
from eledata.views.analysis_questions import *
from eledata.views.event import *
from eledata.views.users import GroupAdminActions, UserLogin, UserActions
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'entity', EntityViewSet, r'entity')
router.register(r'analysis_questions', AnalysisQuestionsViewSet, r'analysis_questions')
router.register(r'event', EventViewSet, r'event')
router.register(r'users', GroupAdminActions, r'users')
router.register(r'users', UserLogin, r'users2')
router.register(r'users', UserActions, r'users2')

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # index page should be served by django to set cookies, headers etc.
    url(r'^$', index_view, {}, name='index'),
]

urlpatterns += router.urls
