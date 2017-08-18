from __future__ import unicode_literals
from django.db import models

import string
import random
import datetime
from django.utils.timezone import now

from django.contrib.auth.models import User
# Create your models here.


class Doctor(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    first_name = models.CharField(max_length=50, default='')
    last_name = models.CharField(max_length=50, default='')
    token = models.CharField(max_length=256)
    current_patient_id = models.IntegerField(null=True, blank=True)
    kiosk_code = models.CharField(max_length=6, blank=True)

    def set_random_password(self):
        user = self.user
        characters = string.punctuation + string.letters + string.digits
        password = ''.join(random.choice(characters) for char in range(20))
        user.set_password(password)
        user.save()
        return password

    def __str__(self):
        return self.last_name


class Patient(models.Model):
    doctor = models.ForeignKey(Doctor)
    first_name = models.CharField(max_length=128, blank=True)
    middle_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    address = models.CharField(max_length=200, blank=True)
    email = models.CharField(max_length=200, blank=True)
    home_phone = models.CharField(max_length=14, blank=True)
    cell_phone = models.CharField(max_length=14, blank=True)
    city = models.CharField(max_length=200, blank=True)
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=200, blank=True)
    emergency_contact_relation = models.CharField(max_length=200, blank=True)
    employer = models.CharField(max_length=200, blank=True)
    employer_city = models.CharField(max_length=200, blank=True)
    employer_address = models.CharField(max_length=200, blank=True)
    employer_state = models.CharField(max_length=200, blank=True)
    employer_zip_code = models.CharField(blank=True, max_length=200)
    primary_care_physician = models.CharField(
        max_length=200, blank=True, null=True
    )
    zip_code = models.CharField(max_length=5, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    social_security_number = models.CharField(max_length=20, blank=True)
    responsible_party_name = models.CharField(max_length=200, blank=True)
    responsible_party_phone = models.CharField(max_length=14, blank=True)
    responsible_party_relation = models.CharField(max_length=200, blank=True)
    responsible_party_email = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return '{0}, {1}'.format(self.last_name, self.first_name)


class Office(models.Model):
    doctor = models.ForeignKey(Doctor)
    country = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    address = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=6)

    def __str__(self):

        return ', '.join((self.address, self.city, ' '.join((self.state, self.zip_code)), self.country))


class Appointment(models.Model):
    duration = models.IntegerField()
    doctor = models.ForeignKey(Doctor)
    patient = models.ForeignKey(Patient)
    office = models.ForeignKey(Office)
    exam_room = models.IntegerField()
    reason = models.CharField(max_length=1000, blank=True)
    status = models.CharField(max_length=20, null=True)
    deleted_flag = models.BooleanField()
    scheduled_time = models.DateTimeField()
    # some extra fields for arrival and called in time information
    in_room_time = models.DateTimeField(default=now, null=True)

    def __str__(self):
        return ', '.join((str(self.scheduled_time), self.patient.last_name, self.patient.first_name))

    class Meta:
        ordering = ['scheduled_time']




