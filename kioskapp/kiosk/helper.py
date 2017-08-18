# __author__ = 'chintanpanchamia'
from django.contrib.auth.models import User
from kiosk_auth_data import CLIENT
import requests, datetime
from models import Doctor, Patient, Appointment, Office


def get_drchrono_user(request_params):
    """

    :param request_params:
    :return: user object for performing doctor operations
    """
    access_token = exchange_token(request_params)
    doctor = get_doctor_data(access_token)
    doc, user = save_user(doctor, access_token)
    get_my_patients(doc, access_token)
    get_offices(doc, access_token)
    # get_appointments(doc, access_token)
    return user


def exchange_token(request_params):
    """
    :param request_params:
    :return: access_token, required for communicating with the API
    """
    if 'error' in request_params:
        raise ValueError('Error authorizing application: %s' % request_params['error'])

    response = requests.post('https://drchrono.com/o/token/', {
        'code': request_params['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': CLIENT['redirect_uri'],
        'client_id': CLIENT['client_id'],
        'client_secret': CLIENT['client_secret'],
    })

    response.raise_for_status()
    data = response.json()
    return data['access_token']


def get_doctor_data(access_token):
    """
    :param access_token:
    :return: username of doctor
    """
    header = {'Authorization': 'Bearer %s' % access_token}
    user_data = get_user(header)

    doctor_endpoint = 'doctors/{0}'.format(user_data['doctor'])
    data = get_drchrono_data(doctor_endpoint, header)
    data['username'] = user_data['username']
    return data


def get_user(header):
    """
    :param header:
    :return: user data, to get current logged in user
    """
    user_endpoint = 'users/current'
    current_doctor = get_drchrono_data(user_endpoint, header)
    return current_doctor


def get_drchrono_data(endpoint, header):
    """
    :param endpoint:
    :param header:
    :return: json formatted data received from the API when hitting the endpoint
    """
    response = requests.get(('https://drchrono.com/api/%s' % endpoint), headers=header)
    response.raise_for_status()
    return response.json()


def save_user(doctor, access_token):
    """

    :param doctor:
    :param access_token:
    :return: saved user and doctor objects which can be used for performing operations
    """
    user = User.objects.create_user(
        id=doctor['id'],
        username=doctor['username'],
    )
    doctor = Doctor(
        first_name=doctor['first_name'],
        last_name=doctor['last_name'],
        user=user,
        token=access_token,
    )
    if Doctor.objects.filter(pk=user).exists():
        doctor.save(update_fields=['first_name', 'last_name'])
    else:
        doctor.save()

    return doctor, user


def get_offices(doctor, access_token):
    """

    :param doctor:
    :param access_token:
    Saves data about offices associated with a particular doctor, to be used when setting up kiosk
    """
    office_endpoint = 'offices'
    offices = get_paginated_data(office_endpoint, access_token)
    save_offices(offices, doctor)


def verify_patient(form_data):
    first_name = form_data['first_name']
    last_name = form_data['last_name']
    social_security_number = form_data['social_security_number']

    try:
        patient = Patient.objects.get(first_name=first_name, last_name=last_name,
                                      social_security_number=social_security_number)

    except Patient.DoesNotExist:
        return None, 1

    try:
        appointment = Appointment.objects.get(patient=patient, status='')
    except Appointment.DoesNotExist:
        return None, 2

    return appointment, 0


def get_appointments(doctor, office, access_token):
    """

    :param doctor:
    :param office:
    :param access_token:
    Get Appointment object data by hitting the appropriate endpoint, after selecting the office
    """
    date = datetime.date.today().strftime('%Y-%m-%d')
    appointments_endpoint = 'appointments?doctor={0}&office={1}&date={2}'.format(str(doctor), str(office), date)
    appointments = get_paginated_data(appointments_endpoint, access_token)
    save_appointments(appointments)


def save_appointments(appointments):
    """

    :param appointments:
    Saves Appointment
    """
    for appt in appointments:
        appointment = Appointment(
            id=appt['id'],
            duration=appt['duration'],
            doctor=Doctor.objects.get(pk=appt['doctor']),
            patient=Patient.objects.get(pk=appt['patient']),
            office=Office.objects.get(pk=appt['office']),
            exam_room=appt['exam_room'],
            reason=appt['reason'],
            status=appt['status'],
            deleted_flag=appt['deleted_flag'],
            scheduled_time=appt['scheduled_time'],
            in_room_time=appt['scheduled_time'],
        )
        print appointment
        appointment.save()


def save_offices(offices, doctor):
    """

    :param offices:
    :param doctor:
    save Office object data to local database
    """
    for office_data in offices:
        office = Office(
            id=office_data['id'],
            doctor=doctor,
            country=office_data['country'],
            state=office_data['state'],
            city=office_data['city'],
            address=office_data['address'],
            zip_code=office_data['zip_code'],
        )

        office.save()


def get_my_patients(doctor, access_token):
    """

    :param doctor:
    :param access_token:
    Get patients data by hitting the appropriate endpoint
    """
    patients_endpoint = 'patients'
    patients = get_paginated_data(patients_endpoint, access_token)

    for data in patients:
        save_patient(data, doctor)


def save_patient(patient_data, user):
    """

    :param patient_data:
    :param user:
    Save patient data to local database to provide quicker access when editing demographics
    """
    patient = Patient(
        id=patient_data['id'],
        doctor=user,
        first_name=patient_data['first_name'],
        middle_name=patient_data['middle_name'],
        last_name=patient_data['last_name'],
        address=patient_data['address'],
        email=patient_data['email'],
        home_phone=patient_data['home_phone'],
        cell_phone=patient_data['cell_phone'],
        city=patient_data['city'],
        zip_code=patient_data['zip_code'],
        state=patient_data['state'],
        emergency_contact_name=patient_data['emergency_contact_name'],
        emergency_contact_phone=patient_data['emergency_contact_phone'],
        emergency_contact_relation=patient_data['emergency_contact_relation'],
        employer=patient_data['employer'],
        employer_city=patient_data['employer_city'],
        employer_state=patient_data['employer_state'],
        employer_address=patient_data['employer_address'],
        employer_zip_code=patient_data['employer_zip_code'],
        primary_care_physician=patient_data['primary_care_physician'],
        social_security_number=patient_data['social_security_number'],
        responsible_party_name=patient_data['responsible_party_name'],
        responsible_party_phone=patient_data['responsible_party_phone'],
        responsible_party_relation=patient_data['responsible_party_relation'],
        responsible_party_email=patient_data['responsible_party_email'],
    )

    patient.save()


def get_paginated_data(endpoint, access_token):
    """

    :param endpoint:
    :param access_token:
    :return: data_object list (depending on the kind of objects requested
    """
    url = 'https://drchrono.com/api/%s' % endpoint
    header = {'Authorization': 'Bearer %s' % access_token}
    data_objects = []

    while url:
        response = requests.get(url, headers=header)
        data = response.json()
        for object_data in data['results']:
            data_objects.append(object_data)

        url = data['next']

    return data_objects


def patch_appointment(request, a_id, status):
    """
    :param request:
    :param a_id:
    :param status:
    For patching appointment status to DrChrono API
    """
    url = 'https://drchrono.com/api/appointments/%s' % a_id
    token = request.user.doctor.token
    header = {'Authorization': 'Bearer %s' % token}
    requests.patch(
        url=url,
        headers=header,
        data={
            'status': status
        }
    )