from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from pymongo import MongoClient
from django.db.models import Q

from .forms import PatientForm
from .models import Patient


# Create your views here.

def main(request):
    filtered_patients = None
    if request.GET.get('search'):
        search = request.GET.get('search')
        filtered_patients = Patient.objects.filter(
            Q(last_name__icontains=search) |
            Q(first_name__icontains=search) |
            Q(address__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search) |
            Q(mobile_phone__icontains=search) |
            Q(amka__icontains=search)
        )
    return render(request, 'patient_management/main.html', {'filtered_patients': filtered_patients})


def connect_to_database(uri, db_name):
    """
    Method to establish connectivity with the MongoDB database, returns a DB client.

    :param uri:
    :param db_name:
    :return: client
    """
    try:
        client = MongoClient(uri)[db_name]
        return client
    except Exception as err:
        print(str(err))


class AddPatientFormView(FormView):
    form_class = PatientForm
    template_name = 'patient_management/add-patient.html'
    success_url = '/main/'
    context = {}

    def post(self, request, *args, **kwargs):
        if 'save' in request.POST:
            form = PatientForm(request.POST)
            self.context['form'] = form
            form.save()
            return redirect('/main/')


def edit_patient(request, patient_id):
    patient = Patient.objects.filter(pk=patient_id).first()
    form = PatientForm(instance=patient)
    if request.method == 'POST':
        if 'delete' in request.POST:
            patient.delete()
            return redirect('main')

        form = PatientForm(request.POST, instance=patient)

        if form.is_valid():
            form.save()
            return redirect('main')
        else:
            form = PatientForm(instance=patient)

    return render(request, 'patient_management/edit-patient.html', {'form': form})
