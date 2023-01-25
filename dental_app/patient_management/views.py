from django.shortcuts import render

# Create your views here.

def main(request):
    return render(request, 'patient_management/main.html')

def add_patient(request):
    return render(request, 'patient_management/add-patient.html')

