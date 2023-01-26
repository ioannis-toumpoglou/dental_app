from django import forms


class PatientForm(forms.Form):
    first_name = forms.CharField(label='First Name:')
    last_name = forms.CharField(label='Last Name:')
    address = forms.CharField(label='Address:')
    email = forms.EmailField(label='Email:')
    phone = forms.CharField(label='Phone number:')
    cell_phone = forms.CharField(label='Cell phone:')
    amka = forms.CharField(label='AMKA:')
    date_of_birth = forms.DateField(label='Date of birth:')
