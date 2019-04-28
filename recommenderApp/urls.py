from django.conf.urls import url

from . import views

app_name = 'recommenderApp'
urlpatterns = [
    url(r'^$', views.Index, name='index'),
    url(r'^submit/$', views.Submit, name='submit'),
    url(r'^result/(?P<steamId>[A-Za-z0-9]+)&(?P<userName>[A-Za-z0-9]+)$', views.Result, name='result')
]