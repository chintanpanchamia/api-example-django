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

    url(r'^mark_checked_in/$', login_required(views.mark_checked_in), name='update_checkin_view'),

    url(r'^demographics/(?P<patient_id>[0-9]+)/$',
        login_required(views.DemographicView.as_view()), name='demographic_view'),

    url(r'^demographics/$', login_required(views.demographic_init), name='demographic_init'),

    url(r'^appointments-list/$', login_required(views.appointments_list_view), name='appointments_list_view'),

    url(r'^call_in_view/(?P<appointment_id>[0-9]+)/$', login_required(views.call_in_view), name='call_in_view'),

    url(r'^mark_completed_view/(?P<appointment_id>[0-9]+)/$', login_required(views.mark_completed_view),
        name='mark_completed_view')
]

