from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.db import models
from django.core import serializers
from django.views import generic
from django.http import HttpResponse, QueryDict
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.utils.http import urlquote
from kiosk_auth_data import CLIENT

from helper import get_drchrono_user, get_appointments
from models import Appointment, Doctor, Patient, Office
# Create your views here.


def index_view(request):
    doctor = request.user.doctor
    return render(request, 'index.html', context={
        'username': request.user.username,
        'doctor': doctor,
    })


def login_view(request):
    return render(request, 'generic/login.html', context={
        'client_id': CLIENT['client_id'],
        'redirect_uri': CLIENT['redirect_uri'],
        'scope': urlquote(CLIENT['client_scope']),
    })


def oauth_view(request):
    if request.method == 'GET':
        if 'error' in request.GET:
            return redirect('kiosk:login_error')

        user = get_drchrono_user(request.GET)
        authentication = authenticate(
            username=user.username,
            password=user.doctor.set_random_password(),
        )

        login(request, authentication)
        return redirect('kiosk:index_view')


def login_error_view(request):
    return render(request, 'generic/login_error.html')


def logout_view(request):
    logout(request)
    return redirect('kiosk:login_view')


def setup_kiosk(request):
    doctor = request.user.doctor
    offices = Office.objects.all()
    return render(request, 'setup_kiosk.html', context={
        'offices': offices,
        'doctor': doctor,
    })


# def patients_list(request):


def office_view(request, office_id):
    # print 'HEY! ' + office_id
    doctor = request.user.doctor
    get_appointments(doctor, office_id, doctor.token)
    appt = Appointment.objects.all()
    for a in appt:
        print a
    return redirect('kiosk:checkin_view')


def checkin_view(request):
    return render(request, 'checkin.html')
