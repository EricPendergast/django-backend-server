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
from django.conf.urls import include, url
from django.contrib import admin
from django_mongo_rest.views import *
# from rest_framework import routers


# We use a single global DRF Router that routes views from all apps in project
# router = routers.SimpleRouter()

# app views and viewsets
# router.register(r'entity', EntityViewSet, r'entity')


get_all_entity = EntityViewSet.as_view({'get': 'get_all_entity'})
select_entity = EntityViewSet.as_view({'get': 'select_entity'})


urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # index page should be served by django to set cookies, headers etc.
    url(r'^$', index_view, {}, name='index'),

    url(r'^entity/$', get_all_entity, name='get-all-entity'),
    url(r'^entity/(?P<entity_type>[a-z]+)/$', select_entity, name='select-entity')
]

# urlpatterns += router.urls
