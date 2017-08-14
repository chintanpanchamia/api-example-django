# __author__ = 'chintanpanchamia'
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    url(r'^$', login_required(views.index_view), name='index'),

    url(r'^oauth/$', views.oauth_view, name='oauth'),

    url(r'^accounts/login/$', views.login_view, name='login'),

    url(r'^accounts/logout/$', views.logout_view, name='logout'),
]

