__author__ = 'chintanpanchamia'

from django.contrib.auth.models import User
from kiosk_auth_data import CLIENT
import requests
from models import Doctor,Patient


def get_drchrono_user(request_params):
    access_token = exchange_token(request_params)
    doctor = get_doctor_data(access_token)
    user = save_user(doctor, access_token)
    # get_my_patients(user, access_token)
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
    user = User.objects.create_user(
        id=doctor['id'],
        username=doctor['username'],
        first_name=doctor['first_name'],
        last_name=doctor['last_name'],
    )

    doctor = Doctor(user=user, token=access_token)
    doctor.save()
    return user
