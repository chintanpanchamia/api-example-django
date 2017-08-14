from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.db import models
from django.core import serializers
from django.views import generic
from django.http import HttpResponse, QueryDict
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User


from kiosk_auth_data import CLIENT_DATA
from helper import get_drchrono_user
# Create your views here.


def login_view(request):
    return render(request, 'generic/login.html', context={
        'client_key': CLIENT_DATA['client_id'],
        'redirect_url': CLIENT_DATA['redirect_url']
    })


def oauth(request):
    if request.method == 'GET':
        if 'error' in request.GET:
            return redirect('generic/login_error.html')

    user = get_drchrono_user(request.GET)
