from django.shortcuts import render
from django.views.generic.edit import FormView
import os
from pymongo import MongoClient

from .forms import PatientForm


# Create your views here.

def main(request):
    return render(request, 'patient_management/main.html')

def add_patient(request):
    return render(request, 'patient_management/add-patient.html')

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
    success_url = '/main'

    uri = os.environ.get('MONGO_DB_URI')
    db_name = os.environ.get('MONGO_DB_NAME')
    client = connect_to_database(uri=uri, db_name=db_name)
    collection = client['patients']

    print(uri)
    print(db_name)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        print(request.POST)

        if 'save' in request.POST:
            if form.is_valid():
                self.collection.insert_one({
                    'first_name': str(request.POST.get('first_name')),
                    'last_name': str(request.POST.get('last_name')),
                    'address': str(request.POST.get('address')),
                    'email': str(request.POST.get('email')),
                    'phone': str(request.POST.get('phone')),
                    'cell_phone': str(request.POST.get('cell_phone')),
                    'amka': str(request.POST.get('amka')),
                    'date_of_birth': str(request.POST.get('date_of_birth'))
                })
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
