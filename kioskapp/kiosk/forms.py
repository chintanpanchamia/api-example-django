# __author__ = 'chintanpanchamia'

from django import forms
from models import Patient


class CheckinForm(forms.Form):
    first_name = forms.CharField(max_length=20, label='First Name', widget=forms.TextInput(
        attrs={'required': True,
               'class': 'field office',
               'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=20, label='Last Name', widget=forms.TextInput(
        attrs={'required': True,
               'class': 'field office',
               'placeholder': 'Last Name'}))
    social_security_number = forms.RegexField(
        label='Social Security #(SSN)',
        regex='^(\d{3}\-\d{2}\-\d{4})$',
        widget=forms.TextInput(attrs={'required': True,
                                      'class': 'field office',
                                      'placeholder': 'Social Security #(SSN)'})
    )


class DemographicForm(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = ['first_name', 'middle_name', 'last_name', 'social_security_number', 'doctor']

# class DemographicForm(forms.Form):