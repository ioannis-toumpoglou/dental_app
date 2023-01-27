from django import forms
from django.conf import settings


class PatientForm(forms.Form):
    first_name = forms.CharField(label='First Name:')
    last_name = forms.CharField(label='Last Name:')
    address = forms.CharField(label='Address:', required=False)
    email = forms.EmailField(label='Email:', required=False)
    phone = forms.CharField(label='Phone number:', required=False)
    mobile_phone = forms.CharField(label='Mobile phone:')
    amka = forms.CharField(label='AMKA:', required=False)
    date_of_birth = forms.DateField(label='Date of birth:', input_formats=settings.DATE_INPUT_FORMATS, required=False)
    notes = forms.CharField(widget=forms.Textarea(attrs={"rows": "5"}))
