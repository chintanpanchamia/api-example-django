from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.db import models
from django.core import serializers
from django.contrib import messages
from django.views import generic
from django.http import HttpResponse, QueryDict
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.utils.http import urlquote
from kiosk_auth_data import CLIENT
import requests
import datetime

from helper import get_drchrono_user, get_appointments, verify_patient, patch_appointment
from models import Appointment, Doctor, Patient, Office
from forms import CheckinForm, DemographicForm
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
    # Appointment.objects.all().delete()
    print datetime.datetime.now()
    logout(request)
    return redirect('kiosk:login_view')


def setup_kiosk(request):
    doctor = request.user.doctor
    offices = Office.objects.all()
    return render(request, 'setup_kiosk.html', context={
        'offices': offices,
        'doctor': doctor,
    })


def appointments_list_view(request):
    appointments = Appointment.objects.all()
    current_time = datetime.datetime.now()
    total_wait_time = 0
    count_appointments = 0
    average_wait_time = 0

    averaging_appointments = appointments.filter(status='Complete')
    for appointment in averaging_appointments:
        wait_time = appointment.in_room_time - appointment.scheduled_time
        if wait_time.seconds//60 > 0:
            total_wait_time += wait_time.total_seconds()/60
            count_appointments += 1

    if count_appointments > 0:
        average_wait_time = total_wait_time/count_appointments

    context = {
        'appointments': appointments,
        'current_time': current_time,
        'average_wait_time': average_wait_time,
        'doctor': request.user.doctor,
    }

    return render(request, 'appointment_list.html', context)


def office_view(request, office_id):
    doctor = request.user.doctor
    get_appointments(doctor, office_id, doctor.token)
    for appt in Appointment.objects.all():
        print str(appt)
    return redirect('kiosk:checkin_view')


def checkin_view(request):
    checkin_form = CheckinForm(request.POST or None)
    context = {'form': checkin_form}

    if checkin_form.is_valid():
        first_name = checkin_form.cleaned_data['first_name']
        last_name = checkin_form.cleaned_data['last_name']
        social_security_number = checkin_form.cleaned_data['social_security_number']

        form_data = {'first_name': first_name, 'last_name': last_name, 'social_security_number': social_security_number}
        result_type, result = verify_patient(form_data)

        if result == 0:
            p = Patient.objects.get(social_security_number=social_security_number)
            print p.id
            request.session['p_id'] = {'patient_id': p.id}
            return redirect('kiosk:demographic_init')

        if result == 1:
            context['message'] = 'Sorry, we couldn\'t find you! Please try again.'

        if result == 2:
            context['message'] = 'Sorry, but you don\'t have an appointment today'

    return render(request, 'checkin.html', context)


def demographic_init(request):
    pid = request.session['p_id']['patient_id']
    context = {
        'patient': Patient.objects.get(pk=pid)
    }
    return render(request, 'demographic.html', context)


class DemographicView(generic.DetailView):
    model = Patient
    form_class = DemographicForm

    def post(self, request, **kwargs):
        if request.POST['_method'] == 'PATCH':
            patient = get_object_or_404(Patient, pk=kwargs['patient_id'])
            form = self.form_class(request.POST, instance=patient)
            if form.is_valid():
                form.save()
                self.post_drchrono(request, kwargs['patient_id'])
                messages.success(request, 'Save Successful')
            else:
                messages.success(request, 'Save Failed')

            return redirect('kiosk:demographic_init')

    def post_drchrono(self, request, patient_id):
        url = 'https://drchrono.com/api/patients/%s' % patient_id
        token = request.user.doctor.token
        header = {'Authorization': 'Bearer %s' % token}
        # print request.POST, '\n\n'
        temp = dict(request.POST.iterlists())
        temp.pop('csrfmiddlewaretoken')
        response = requests.patch(
            url=url, data=temp, headers=header
        )
        print response
        try:
            response.raise_for_status()
        except:
            return


# for updating status of the closest appointment of the said patient
def mark_checked_in(request):
    patient_id = request.session['p_id']['patient_id']
    checked_in_patient_appointments = Appointment.objects.filter(patient=patient_id, status='')
    appointment = checked_in_patient_appointments[0]
    status = 'Arrived'
    appointment.status = status
    appointment.save()

    patch_appointment(request, appointment.id, status)

    return redirect('kiosk:checkin_view')


def mark_completed_view(request, appointment_id):
    current_appointment = Appointment.objects.get(id=appointment_id)
    status = 'Complete'
    current_appointment.status = status
    current_appointment.save()

    patch_appointment(request, appointment_id, status)

    return redirect('kiosk:appointments_list_view')


def call_in_view(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    status = 'In Session'
    appointment.status = status
    appointment.save()
    appointment.in_room_time = datetime.datetime.now()
    patch_appointment(request, appointment_id, status)

    return redirect('kiosk:appointments_list_view')
