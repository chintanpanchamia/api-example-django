# __author__ = 'chintanpanchamia'
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    url(r'^$', login_required(views.index_view), name='index_view'),

    url(r'^oauth/$', views.oauth_view, name='oauth_view'),

    url(r'^accounts/login/$', views.login_view, name='login_view'),

    url(r'^accounts/logout/$', views.logout_view, name='logout_view'),

    url(r'^setup-kiosk/$', login_required(views.setup_kiosk), name='setup_view'),

    url(r'^office/(?P<office_id>[0-9]+)/$', login_required(views.office_view), name='office_view'),

    url(r'^checkin/$', login_required(views.checkin_view), name='checkin_view'),

    url(r'^checkin/?(?P<message>[a-z]+)?/?$', login_required(views.checkin_view), name='checkin_view'),

    url(r'^demographics/$', login_required(views.DemographicView.as_view()), name='demographic_view')

    # url(r'^patients-list/$', login_required(views.patients_list), name='patients_view'),
]

