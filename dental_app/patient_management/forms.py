from django import forms

from .models import Patient, MedicalHistory, DentalHistory, Appointment


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'
        widgets = {
            'notes': forms.Textarea(attrs={'rows':5}),}


class MedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = MedicalHistory
        exclude = ['patient']


class DentalHistoryForm(forms.ModelForm):
    class Meta:
        model = DentalHistory
        exclude = ['patient']

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        exclude = ['patient']
        widgets = {
            'notes': forms.Textarea(attrs={'style': 'width: 100%;', 'rows': '5'}),}
