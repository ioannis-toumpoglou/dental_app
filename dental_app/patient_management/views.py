from django.shortcuts import render
from django.views.generic.edit import FormView
import os
from pymongo import MongoClient
import datetime

from .forms import PatientForm


# Create your views here.

def main(request):
    uri = os.environ.get('MONGO_DB_URI')
    db_name = os.environ.get('MONGO_DB_NAME')
    client = connect_to_database(uri=uri, db_name=db_name)
    collection = client['patients']

    all_patients = collection.find({})

    return render(request, 'patient_management/main.html', {'all_patients': all_patients})


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

    uri = os.environ.get('MONGO_DB_URI')
    db_name = os.environ.get('MONGO_DB_NAME')
    client = connect_to_database(uri=uri, db_name=db_name)
    collection = client['patients']

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if 'save' in request.POST:
            if form.is_valid():
                original_date = datetime.datetime.strptime(request.POST.get('date_of_birth'), '%Y-%m-%d')
                date_of_birth = original_date.strftime("%d/%m/%Y")
                self.collection.insert_one({
                    'first_name': str(request.POST.get('first_name')),
                    'last_name': str(request.POST.get('last_name')),
                    'address': str(request.POST.get('address')),
                    'email': str(request.POST.get('email')),
                    'phone': str(request.POST.get('phone')),
                    'mobile_phone': str(request.POST.get('mobile_phone')),
                    'amka': str(request.POST.get('amka')),
                    'date_of_birth': date_of_birth,
                    'notes': str(request.POST.get('notes'))
                })
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
