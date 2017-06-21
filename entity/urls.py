from django.conf.urls import url

from .views import EntityViewSet

get_all_entity = EntityViewSet.as_view({'get': 'get_all_entity'})
select_entity = EntityViewSet.as_view({'get': 'select_entity'})

urlpatterns = [
    # url(r'^$', views.index, name='index'),
    url(r'^$', get_all_entity, name='get-all-entity'),
    url(r'^(?P<entity_type>[a-z]+)/$', select_entity, name='select-entity')
]
