from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.db import models
from django.core import serializers
from django.views import generic
from django.http import HttpResponse, QueryDict
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User



# Create your views here.
