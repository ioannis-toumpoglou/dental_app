import os
from datetime import datetime
from pymongo import MongoClient
from pathlib import Path
from os import listdir
from os.path import isfile, join
import shutil
from datetime import datetime as dt
from django.http import FileResponse
from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from django.db.models import Q
from django.conf import settings
from django.template.defaulttags import register
from django.contrib.auth import logout
from django.views.decorators.cache import cache_control
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
import zipfile

from .forms import (PatientForm, MedicalHistoryForm, DentalHistoryForm, AppointmentForm, TreatmentPlanForm,
                    FinancialForm,
                    Tooth11Form, Tooth12Form, Tooth13Form, Tooth14Form, Tooth15Form, Tooth16Form,
                    Tooth17Form, Tooth18Form, Tooth21Form, Tooth22Form, Tooth23Form, Tooth24Form, Tooth25Form,
                    Tooth26Form, Tooth27Form, Tooth28Form, Tooth31Form, Tooth32Form, Tooth33Form, Tooth34Form,
                    Tooth35Form, Tooth36Form, Tooth37Form, Tooth38Form, Tooth41Form, Tooth42Form, Tooth43Form,
                    Tooth44Form, Tooth45Form, Tooth46Form, Tooth47Form, Tooth48Form,
                    PerioTooth11Form, PerioTooth12Form, PerioTooth13Form, PerioTooth14Form, PerioTooth15Form,
                    PerioTooth16Form, PerioTooth17Form, PerioTooth18Form, PerioTooth21Form, PerioTooth22Form,
                    PerioTooth23Form, PerioTooth24Form, PerioTooth25Form, PerioTooth26Form, PerioTooth27Form,
                    PerioTooth28Form, PerioTooth31Form, PerioTooth32Form, PerioTooth33Form, PerioTooth34Form,
                    PerioTooth35Form, PerioTooth36Form, PerioTooth37Form, PerioTooth38Form, PerioTooth41Form,
                    PerioTooth42Form, PerioTooth43Form, PerioTooth44Form, PerioTooth45Form, PerioTooth46Form,
                    PerioTooth47Form, PerioTooth48Form)
from .models import (Patient, MedicalHistory, DentalHistory, Appointment, TreatmentPlan, Financial,
                     Odontogram, Periodontogram)


# Create your views here.

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def main(request):
    filtered_patients = Patient.objects.all()
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


@method_decorator([never_cache, ], name='dispatch')
class AddPatientFormView(FormView):
    form_class = PatientForm
    template_name = 'patient_management/add-patient.html'
    success_url = 'main'
    context = {}

    def post(self, request, *args, **kwargs):
        if 'save' in request.POST:
            # Create new patient database record
            form = PatientForm(request.POST)
            self.context['form'] = form
            form.save()
            # Create patient local data
            data_path = Path(settings.PATIENT_DATA_FOLDER)
            patient_last_name = form.cleaned_data.get('last_name')
            patient_first_name = form.cleaned_data.get('first_name')
            patient_name = f'{patient_last_name}_{patient_first_name}'
            patient = Patient.objects.filter(last_name=patient_last_name, first_name=patient_first_name).first()
            path_name = data_path / f'{patient_name}_{patient.pk}'
            path_name.mkdir(parents=True, exist_ok=True)
            return redirect('main')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_financial(request, financial_form_id):
    transaction = Financial.objects.get(id=financial_form_id)
    treatment_plan_id = transaction.treatment.id
    treatment_plan = TreatmentPlan.objects.get(id=treatment_plan_id)
    patient_id = treatment_plan.patient.id
    transaction.delete()
    return redirect(f'/patient-details/{patient_id}')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_patient(request, patient_id):
    patient = Patient.objects.filter(pk=patient_id).first()
    patient_form = PatientForm(instance=patient)

    initial_first_name = patient.first_name
    initial_last_name = patient.last_name

    medical_history = MedicalHistory.objects.filter(patient=patient_id).first()

    if medical_history is None:
        medical_history = MedicalHistory.objects.create(patient_id=patient_id)
    medical_history_form = MedicalHistoryForm(instance=medical_history)

    dental_history = DentalHistory.objects.filter(patient=patient_id).first()

    if dental_history is None:
        dental_history = DentalHistory.objects.create(patient_id=patient_id)
    dental_history_form = DentalHistoryForm(instance=dental_history)

    appointments_form_list, treatment_plan_form_list, financial_form_lists = initiate_forms(patient_id=patient_id)

    context = {}
    appointment_form = AppointmentForm()
    context['appointment_form'] = appointment_form

    treatment_plan_form = TreatmentPlanForm(request.POST)
    context['treatment_plan_form'] = treatment_plan_form

    financial_form = FinancialForm(request.POST)
    context['financial_form'] = financial_form

    data_path = Path(settings.PATIENT_DATA_FOLDER)
    patient_last_name = patient.last_name
    patient_first_name = patient.first_name
    patient_name = f'{patient_last_name}_{patient_first_name}'
    path_name = data_path / f'{patient_name}_{patient.pk}'

    datafiles = [f for f in listdir(path_name) if isfile(join(path_name, f))]
    datafiles_metadata = []

    odontogram, treatments = get_odontogram(patient_id=patient_id)

    tooth_11_form = Tooth11Form(instance=odontogram)
    tooth_12_form = Tooth12Form(instance=odontogram)
    tooth_13_form = Tooth13Form(instance=odontogram)
    tooth_14_form = Tooth14Form(instance=odontogram)
    tooth_15_form = Tooth15Form(instance=odontogram)
    tooth_16_form = Tooth16Form(instance=odontogram)
    tooth_17_form = Tooth17Form(instance=odontogram)
    tooth_18_form = Tooth18Form(instance=odontogram)

    tooth_21_form = Tooth21Form(instance=odontogram)
    tooth_22_form = Tooth22Form(instance=odontogram)
    tooth_23_form = Tooth23Form(instance=odontogram)
    tooth_24_form = Tooth24Form(instance=odontogram)
    tooth_25_form = Tooth25Form(instance=odontogram)
    tooth_26_form = Tooth26Form(instance=odontogram)
    tooth_27_form = Tooth27Form(instance=odontogram)
    tooth_28_form = Tooth28Form(instance=odontogram)

    tooth_31_form = Tooth31Form(instance=odontogram)
    tooth_32_form = Tooth32Form(instance=odontogram)
    tooth_33_form = Tooth33Form(instance=odontogram)
    tooth_34_form = Tooth34Form(instance=odontogram)
    tooth_35_form = Tooth35Form(instance=odontogram)
    tooth_36_form = Tooth36Form(instance=odontogram)
    tooth_37_form = Tooth37Form(instance=odontogram)
    tooth_38_form = Tooth38Form(instance=odontogram)

    tooth_41_form = Tooth41Form(instance=odontogram)
    tooth_42_form = Tooth42Form(instance=odontogram)
    tooth_43_form = Tooth43Form(instance=odontogram)
    tooth_44_form = Tooth44Form(instance=odontogram)
    tooth_45_form = Tooth45Form(instance=odontogram)
    tooth_46_form = Tooth46Form(instance=odontogram)
    tooth_47_form = Tooth47Form(instance=odontogram)
    tooth_48_form = Tooth48Form(instance=odontogram)

    periodontogram, severity = get_periodontogram(patient_id=patient_id)

    perio_tooth_11_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_11)
    perio_tooth_11_form = PerioTooth11Form(instance=periodontogram)
    perio_tooth_12_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_12)
    perio_tooth_12_form = PerioTooth12Form(instance=periodontogram)
    perio_tooth_13_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_13)
    perio_tooth_13_form = PerioTooth13Form(instance=periodontogram)
    perio_tooth_14_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_14)
    perio_tooth_14_form = PerioTooth14Form(instance=periodontogram)
    perio_tooth_15_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_15)
    perio_tooth_15_form = PerioTooth15Form(instance=periodontogram)
    perio_tooth_16_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_16)
    perio_tooth_16_form = PerioTooth16Form(instance=periodontogram)
    perio_tooth_17_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_17)
    perio_tooth_17_form = PerioTooth17Form(instance=periodontogram)
    perio_tooth_18_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_18)
    perio_tooth_18_form = PerioTooth18Form(instance=periodontogram)

    perio_tooth_21_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_21)
    perio_tooth_21_form = PerioTooth21Form(instance=periodontogram)
    perio_tooth_22_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_22)
    perio_tooth_22_form = PerioTooth22Form(instance=periodontogram)
    perio_tooth_23_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_23)
    perio_tooth_23_form = PerioTooth23Form(instance=periodontogram)
    perio_tooth_24_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_24)
    perio_tooth_24_form = PerioTooth24Form(instance=periodontogram)
    perio_tooth_25_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_25)
    perio_tooth_25_form = PerioTooth25Form(instance=periodontogram)
    perio_tooth_26_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_26)
    perio_tooth_26_form = PerioTooth26Form(instance=periodontogram)
    perio_tooth_27_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_27)
    perio_tooth_27_form = PerioTooth27Form(instance=periodontogram)
    perio_tooth_28_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_28)
    perio_tooth_28_form = PerioTooth28Form(instance=periodontogram)

    perio_tooth_31_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_31)
    perio_tooth_31_form = PerioTooth31Form(instance=periodontogram)
    perio_tooth_32_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_32)
    perio_tooth_32_form = PerioTooth32Form(instance=periodontogram)
    perio_tooth_33_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_33)
    perio_tooth_33_form = PerioTooth33Form(instance=periodontogram)
    perio_tooth_34_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_34)
    perio_tooth_34_form = PerioTooth34Form(instance=periodontogram)
    perio_tooth_35_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_35)
    perio_tooth_35_form = PerioTooth35Form(instance=periodontogram)
    perio_tooth_36_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_36)
    perio_tooth_36_form = PerioTooth36Form(instance=periodontogram)
    perio_tooth_37_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_37)
    perio_tooth_37_form = PerioTooth37Form(instance=periodontogram)
    perio_tooth_38_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_38)
    perio_tooth_38_form = PerioTooth38Form(instance=periodontogram)

    perio_tooth_41_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_41)
    perio_tooth_41_form = PerioTooth41Form(instance=periodontogram)
    perio_tooth_42_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_42)
    perio_tooth_42_form = PerioTooth42Form(instance=periodontogram)
    perio_tooth_43_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_43)
    perio_tooth_43_form = PerioTooth43Form(instance=periodontogram)
    perio_tooth_44_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_44)
    perio_tooth_44_form = PerioTooth44Form(instance=periodontogram)
    perio_tooth_45_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_45)
    perio_tooth_45_form = PerioTooth45Form(instance=periodontogram)
    perio_tooth_46_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_46)
    perio_tooth_46_form = PerioTooth46Form(instance=periodontogram)
    perio_tooth_47_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_47)
    perio_tooth_47_form = PerioTooth47Form(instance=periodontogram)
    perio_tooth_48_notes = get_periodontogram_tooth_notes(periodontogram.perio_tooth_48)
    perio_tooth_48_form = PerioTooth48Form(instance=periodontogram)

    for file in datafiles:
        metadata = {'filename': file,
                    'path': f'{patient_name}_{patient.pk}\\{file}',
                    'created': datetime.fromtimestamp(os.stat(os.path.join(path_name, file)).st_ctime),
                    'size': round((os.stat(os.path.join(path_name, file)).st_size / 1000000), 2)
                    }
        datafiles_metadata.append(metadata)

    if request.method == 'POST':
        if 'delete' in request.POST:
            # Delete patient local data
            shutil.rmtree(path_name)
            # Delete patient database record
            patient.delete()
            return redirect('main')

        elif 'save-medical' in request.POST:
            medical_history.patient = patient
            medical_history_form = MedicalHistoryForm(request.POST, instance=medical_history)
            medical_history_form.save()
            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'odontogram': odontogram,
                                                                               'tooth_11_form': tooth_11_form,
                                                                               'tooth_12_form': tooth_12_form,
                                                                               'tooth_13_form': tooth_13_form,
                                                                               'tooth_14_form': tooth_14_form,
                                                                               'tooth_15_form': tooth_15_form,
                                                                               'tooth_16_form': tooth_16_form,
                                                                               'tooth_17_form': tooth_17_form,
                                                                               'tooth_18_form': tooth_18_form,
                                                                               'tooth_21_form': tooth_21_form,
                                                                               'tooth_22_form': tooth_22_form,
                                                                               'tooth_23_form': tooth_23_form,
                                                                               'tooth_24_form': tooth_24_form,
                                                                               'tooth_25_form': tooth_25_form,
                                                                               'tooth_26_form': tooth_26_form,
                                                                               'tooth_27_form': tooth_27_form,
                                                                               'tooth_28_form': tooth_28_form,
                                                                               'tooth_31_form': tooth_31_form,
                                                                               'tooth_32_form': tooth_32_form,
                                                                               'tooth_33_form': tooth_33_form,
                                                                               'tooth_34_form': tooth_34_form,
                                                                               'tooth_35_form': tooth_35_form,
                                                                               'tooth_36_form': tooth_36_form,
                                                                               'tooth_37_form': tooth_37_form,
                                                                               'tooth_38_form': tooth_38_form,
                                                                               'tooth_41_form': tooth_41_form,
                                                                               'tooth_42_form': tooth_42_form,
                                                                               'tooth_43_form': tooth_43_form,
                                                                               'tooth_44_form': tooth_44_form,
                                                                               'tooth_45_form': tooth_45_form,
                                                                               'tooth_46_form': tooth_46_form,
                                                                               'tooth_47_form': tooth_47_form,
                                                                               'tooth_48_form': tooth_48_form,
                                                                               'periodontogram': periodontogram,
                                                                               'perio_tooth_11_form': perio_tooth_11_form,
                                                                               'perio_tooth_11_notes': perio_tooth_11_notes,
                                                                               'perio_tooth_12_form': perio_tooth_12_form,
                                                                               'perio_tooth_12_notes': perio_tooth_12_notes,
                                                                               'perio_tooth_13_form': perio_tooth_13_form,
                                                                               'perio_tooth_13_notes': perio_tooth_13_notes,
                                                                               'perio_tooth_14_form': perio_tooth_14_form,
                                                                               'perio_tooth_14_notes': perio_tooth_14_notes,
                                                                               'perio_tooth_15_form': perio_tooth_15_form,
                                                                               'perio_tooth_15_notes': perio_tooth_15_notes,
                                                                               'perio_tooth_16_form': perio_tooth_16_form,
                                                                               'perio_tooth_16_notes': perio_tooth_16_notes,
                                                                               'perio_tooth_17_form': perio_tooth_17_form,
                                                                               'perio_tooth_17_notes': perio_tooth_17_notes,
                                                                               'perio_tooth_18_form': perio_tooth_18_form,
                                                                               'perio_tooth_18_notes': perio_tooth_18_notes,
                                                                               'perio_tooth_21_form': perio_tooth_21_form,
                                                                               'perio_tooth_21_notes': perio_tooth_21_notes,
                                                                               'perio_tooth_22_form': perio_tooth_22_form,
                                                                               'perio_tooth_22_notes': perio_tooth_22_notes,
                                                                               'perio_tooth_23_form': perio_tooth_23_form,
                                                                               'perio_tooth_23_notes': perio_tooth_23_notes,
                                                                               'perio_tooth_24_form': perio_tooth_24_form,
                                                                               'perio_tooth_24_notes': perio_tooth_24_notes,
                                                                               'perio_tooth_25_form': perio_tooth_25_form,
                                                                               'perio_tooth_25_notes': perio_tooth_25_notes,
                                                                               'perio_tooth_26_form': perio_tooth_26_form,
                                                                               'perio_tooth_26_notes': perio_tooth_26_notes,
                                                                               'perio_tooth_27_form': perio_tooth_27_form,
                                                                               'perio_tooth_27_notes': perio_tooth_27_notes,
                                                                               'perio_tooth_28_form': perio_tooth_28_form,
                                                                               'perio_tooth_28_notes': perio_tooth_28_notes,
                                                                               'perio_tooth_31_form': perio_tooth_31_form,
                                                                               'perio_tooth_31_notes': perio_tooth_31_notes,
                                                                               'perio_tooth_32_form': perio_tooth_32_form,
                                                                               'perio_tooth_32_notes': perio_tooth_32_notes,
                                                                               'perio_tooth_33_form': perio_tooth_33_form,
                                                                               'perio_tooth_33_notes': perio_tooth_33_notes,
                                                                               'perio_tooth_34_form': perio_tooth_34_form,
                                                                               'perio_tooth_34_notes': perio_tooth_34_notes,
                                                                               'perio_tooth_35_form': perio_tooth_35_form,
                                                                               'perio_tooth_35_notes': perio_tooth_35_notes,
                                                                               'perio_tooth_36_form': perio_tooth_36_form,
                                                                               'perio_tooth_36_notes': perio_tooth_36_notes,
                                                                               'perio_tooth_37_form': perio_tooth_37_form,
                                                                               'perio_tooth_37_notes': perio_tooth_37_notes,
                                                                               'perio_tooth_38_form': perio_tooth_38_form,
                                                                               'perio_tooth_38_notes': perio_tooth_38_notes,
                                                                               'perio_tooth_41_form': perio_tooth_41_form,
                                                                               'perio_tooth_41_notes': perio_tooth_41_notes,
                                                                               'perio_tooth_42_form': perio_tooth_42_form,
                                                                               'perio_tooth_42_notes': perio_tooth_42_notes,
                                                                               'perio_tooth_43_form': perio_tooth_43_form,
                                                                               'perio_tooth_43_notes': perio_tooth_43_notes,
                                                                               'perio_tooth_44_form': perio_tooth_44_form,
                                                                               'perio_tooth_44_notes': perio_tooth_44_notes,
                                                                               'perio_tooth_45_form': perio_tooth_45_form,
                                                                               'perio_tooth_45_notes': perio_tooth_45_notes,
                                                                               'perio_tooth_46_form': perio_tooth_46_form,
                                                                               'perio_tooth_46_notes': perio_tooth_46_notes,
                                                                               'perio_tooth_47_form': perio_tooth_47_form,
                                                                               'perio_tooth_47_notes': perio_tooth_47_notes,
                                                                               'perio_tooth_48_form': perio_tooth_48_form,
                                                                               'perio_tooth_48_notes': perio_tooth_48_notes,
                                                                               'treatments': treatments,
                                                                               'treatment_plan_form': treatment_plan_form,
                                                                               'financial_form': financial_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'treatment_plan_form_list': treatment_plan_form_list,
                                                                               'financial_form_lists': financial_form_lists,
                                                                               'datafiles': datafiles_metadata})

        elif 'clear-medical' in request.POST:
            medical_history = MedicalHistory.objects.get(patient_id=patient_id)
            medical_history.delete()
            medical_history = MedicalHistory.objects.create(patient_id=patient_id)
            medical_history_form = MedicalHistoryForm(instance=medical_history)
            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'odontogram': odontogram,
                                                                               'tooth_11_form': tooth_11_form,
                                                                               'tooth_12_form': tooth_12_form,
                                                                               'tooth_13_form': tooth_13_form,
                                                                               'tooth_14_form': tooth_14_form,
                                                                               'tooth_15_form': tooth_15_form,
                                                                               'tooth_16_form': tooth_16_form,
                                                                               'tooth_17_form': tooth_17_form,
                                                                               'tooth_18_form': tooth_18_form,
                                                                               'tooth_21_form': tooth_21_form,
                                                                               'tooth_22_form': tooth_22_form,
                                                                               'tooth_23_form': tooth_23_form,
                                                                               'tooth_24_form': tooth_24_form,
                                                                               'tooth_25_form': tooth_25_form,
                                                                               'tooth_26_form': tooth_26_form,
                                                                               'tooth_27_form': tooth_27_form,
                                                                               'tooth_28_form': tooth_28_form,
                                                                               'tooth_31_form': tooth_31_form,
                                                                               'tooth_32_form': tooth_32_form,
                                                                               'tooth_33_form': tooth_33_form,
                                                                               'tooth_34_form': tooth_34_form,
                                                                               'tooth_35_form': tooth_35_form,
                                                                               'tooth_36_form': tooth_36_form,
                                                                               'tooth_37_form': tooth_37_form,
                                                                               'tooth_38_form': tooth_38_form,
                                                                               'tooth_41_form': tooth_41_form,
                                                                               'tooth_42_form': tooth_42_form,
                                                                               'tooth_43_form': tooth_43_form,
                                                                               'tooth_44_form': tooth_44_form,
                                                                               'tooth_45_form': tooth_45_form,
                                                                               'tooth_46_form': tooth_46_form,
                                                                               'tooth_47_form': tooth_47_form,
                                                                               'tooth_48_form': tooth_48_form,
                                                                               'periodontogram': periodontogram,
                                                                               'perio_tooth_11_form': perio_tooth_11_form,
                                                                               'perio_tooth_11_notes': perio_tooth_11_notes,
                                                                               'perio_tooth_12_form': perio_tooth_12_form,
                                                                               'perio_tooth_12_notes': perio_tooth_12_notes,
                                                                               'perio_tooth_13_form': perio_tooth_13_form,
                                                                               'perio_tooth_13_notes': perio_tooth_13_notes,
                                                                               'perio_tooth_14_form': perio_tooth_14_form,
                                                                               'perio_tooth_14_notes': perio_tooth_14_notes,
                                                                               'perio_tooth_15_form': perio_tooth_15_form,
                                                                               'perio_tooth_15_notes': perio_tooth_15_notes,
                                                                               'perio_tooth_16_form': perio_tooth_16_form,
                                                                               'perio_tooth_16_notes': perio_tooth_16_notes,
                                                                               'perio_tooth_17_form': perio_tooth_17_form,
                                                                               'perio_tooth_17_notes': perio_tooth_17_notes,
                                                                               'perio_tooth_18_form': perio_tooth_18_form,
                                                                               'perio_tooth_18_notes': perio_tooth_18_notes,
                                                                               'perio_tooth_21_form': perio_tooth_21_form,
                                                                               'perio_tooth_21_notes': perio_tooth_21_notes,
                                                                               'perio_tooth_22_form': perio_tooth_22_form,
                                                                               'perio_tooth_22_notes': perio_tooth_22_notes,
                                                                               'perio_tooth_23_form': perio_tooth_23_form,
                                                                               'perio_tooth_23_notes': perio_tooth_23_notes,
                                                                               'perio_tooth_24_form': perio_tooth_24_form,
                                                                               'perio_tooth_24_notes': perio_tooth_24_notes,
                                                                               'perio_tooth_25_form': perio_tooth_25_form,
                                                                               'perio_tooth_25_notes': perio_tooth_25_notes,
                                                                               'perio_tooth_26_form': perio_tooth_26_form,
                                                                               'perio_tooth_26_notes': perio_tooth_26_notes,
                                                                               'perio_tooth_27_form': perio_tooth_27_form,
                                                                               'perio_tooth_27_notes': perio_tooth_27_notes,
                                                                               'perio_tooth_28_form': perio_tooth_28_form,
                                                                               'perio_tooth_28_notes': perio_tooth_28_notes,
                                                                               'perio_tooth_31_form': perio_tooth_31_form,
                                                                               'perio_tooth_31_notes': perio_tooth_31_notes,
                                                                               'perio_tooth_32_form': perio_tooth_32_form,
                                                                               'perio_tooth_32_notes': perio_tooth_32_notes,
                                                                               'perio_tooth_33_form': perio_tooth_33_form,
                                                                               'perio_tooth_33_notes': perio_tooth_33_notes,
                                                                               'perio_tooth_34_form': perio_tooth_34_form,
                                                                               'perio_tooth_34_notes': perio_tooth_34_notes,
                                                                               'perio_tooth_35_form': perio_tooth_35_form,
                                                                               'perio_tooth_35_notes': perio_tooth_35_notes,
                                                                               'perio_tooth_36_form': perio_tooth_36_form,
                                                                               'perio_tooth_36_notes': perio_tooth_36_notes,
                                                                               'perio_tooth_37_form': perio_tooth_37_form,
                                                                               'perio_tooth_37_notes': perio_tooth_37_notes,
                                                                               'perio_tooth_38_form': perio_tooth_38_form,
                                                                               'perio_tooth_38_notes': perio_tooth_38_notes,
                                                                               'perio_tooth_41_form': perio_tooth_41_form,
                                                                               'perio_tooth_41_notes': perio_tooth_41_notes,
                                                                               'perio_tooth_42_form': perio_tooth_42_form,
                                                                               'perio_tooth_42_notes': perio_tooth_42_notes,
                                                                               'perio_tooth_43_form': perio_tooth_43_form,
                                                                               'perio_tooth_43_notes': perio_tooth_43_notes,
                                                                               'perio_tooth_44_form': perio_tooth_44_form,
                                                                               'perio_tooth_44_notes': perio_tooth_44_notes,
                                                                               'perio_tooth_45_form': perio_tooth_45_form,
                                                                               'perio_tooth_45_notes': perio_tooth_45_notes,
                                                                               'perio_tooth_46_form': perio_tooth_46_form,
                                                                               'perio_tooth_46_notes': perio_tooth_46_notes,
                                                                               'perio_tooth_47_form': perio_tooth_47_form,
                                                                               'perio_tooth_47_notes': perio_tooth_47_notes,
                                                                               'perio_tooth_48_form': perio_tooth_48_form,
                                                                               'perio_tooth_48_notes': perio_tooth_48_notes,
                                                                               'treatments': treatments,
                                                                               'treatment_plan_form': treatment_plan_form,
                                                                               'financial_form': financial_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'treatment_plan_form_list': treatment_plan_form_list,
                                                                               'financial_form_lists': financial_form_lists,
                                                                               'datafiles': datafiles_metadata})

        elif 'save-dental' in request.POST:
            dental_history.patient = patient
            dental_history_form = DentalHistoryForm(request.POST, instance=dental_history)
            dental_history_form.save()
            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'odontogram': odontogram,
                                                                               'tooth_11_form': tooth_11_form,
                                                                               'tooth_12_form': tooth_12_form,
                                                                               'tooth_13_form': tooth_13_form,
                                                                               'tooth_14_form': tooth_14_form,
                                                                               'tooth_15_form': tooth_15_form,
                                                                               'tooth_16_form': tooth_16_form,
                                                                               'tooth_17_form': tooth_17_form,
                                                                               'tooth_18_form': tooth_18_form,
                                                                               'tooth_21_form': tooth_21_form,
                                                                               'tooth_22_form': tooth_22_form,
                                                                               'tooth_23_form': tooth_23_form,
                                                                               'tooth_24_form': tooth_24_form,
                                                                               'tooth_25_form': tooth_25_form,
                                                                               'tooth_26_form': tooth_26_form,
                                                                               'tooth_27_form': tooth_27_form,
                                                                               'tooth_28_form': tooth_28_form,
                                                                               'tooth_31_form': tooth_31_form,
                                                                               'tooth_32_form': tooth_32_form,
                                                                               'tooth_33_form': tooth_33_form,
                                                                               'tooth_34_form': tooth_34_form,
                                                                               'tooth_35_form': tooth_35_form,
                                                                               'tooth_36_form': tooth_36_form,
                                                                               'tooth_37_form': tooth_37_form,
                                                                               'tooth_38_form': tooth_38_form,
                                                                               'tooth_41_form': tooth_41_form,
                                                                               'tooth_42_form': tooth_42_form,
                                                                               'tooth_43_form': tooth_43_form,
                                                                               'tooth_44_form': tooth_44_form,
                                                                               'tooth_45_form': tooth_45_form,
                                                                               'tooth_46_form': tooth_46_form,
                                                                               'tooth_47_form': tooth_47_form,
                                                                               'tooth_48_form': tooth_48_form,
                                                                               'periodontogram': periodontogram,
                                                                               'perio_tooth_11_form': perio_tooth_11_form,
                                                                               'perio_tooth_11_notes': perio_tooth_11_notes,
                                                                               'perio_tooth_12_form': perio_tooth_12_form,
                                                                               'perio_tooth_12_notes': perio_tooth_12_notes,
                                                                               'perio_tooth_13_form': perio_tooth_13_form,
                                                                               'perio_tooth_13_notes': perio_tooth_13_notes,
                                                                               'perio_tooth_14_form': perio_tooth_14_form,
                                                                               'perio_tooth_14_notes': perio_tooth_14_notes,
                                                                               'perio_tooth_15_form': perio_tooth_15_form,
                                                                               'perio_tooth_15_notes': perio_tooth_15_notes,
                                                                               'perio_tooth_16_form': perio_tooth_16_form,
                                                                               'perio_tooth_16_notes': perio_tooth_16_notes,
                                                                               'perio_tooth_17_form': perio_tooth_17_form,
                                                                               'perio_tooth_17_notes': perio_tooth_17_notes,
                                                                               'perio_tooth_18_form': perio_tooth_18_form,
                                                                               'perio_tooth_18_notes': perio_tooth_18_notes,
                                                                               'perio_tooth_21_form': perio_tooth_21_form,
                                                                               'perio_tooth_21_notes': perio_tooth_21_notes,
                                                                               'perio_tooth_22_form': perio_tooth_22_form,
                                                                               'perio_tooth_22_notes': perio_tooth_22_notes,
                                                                               'perio_tooth_23_form': perio_tooth_23_form,
                                                                               'perio_tooth_23_notes': perio_tooth_23_notes,
                                                                               'perio_tooth_24_form': perio_tooth_24_form,
                                                                               'perio_tooth_24_notes': perio_tooth_24_notes,
                                                                               'perio_tooth_25_form': perio_tooth_25_form,
                                                                               'perio_tooth_25_notes': perio_tooth_25_notes,
                                                                               'perio_tooth_26_form': perio_tooth_26_form,
                                                                               'perio_tooth_26_notes': perio_tooth_26_notes,
                                                                               'perio_tooth_27_form': perio_tooth_27_form,
                                                                               'perio_tooth_27_notes': perio_tooth_27_notes,
                                                                               'perio_tooth_28_form': perio_tooth_28_form,
                                                                               'perio_tooth_28_notes': perio_tooth_28_notes,
                                                                               'perio_tooth_31_form': perio_tooth_31_form,
                                                                               'perio_tooth_31_notes': perio_tooth_31_notes,
                                                                               'perio_tooth_32_form': perio_tooth_32_form,
                                                                               'perio_tooth_32_notes': perio_tooth_32_notes,
                                                                               'perio_tooth_33_form': perio_tooth_33_form,
                                                                               'perio_tooth_33_notes': perio_tooth_33_notes,
                                                                               'perio_tooth_34_form': perio_tooth_34_form,
                                                                               'perio_tooth_34_notes': perio_tooth_34_notes,
                                                                               'perio_tooth_35_form': perio_tooth_35_form,
                                                                               'perio_tooth_35_notes': perio_tooth_35_notes,
                                                                               'perio_tooth_36_form': perio_tooth_36_form,
                                                                               'perio_tooth_36_notes': perio_tooth_36_notes,
                                                                               'perio_tooth_37_form': perio_tooth_37_form,
                                                                               'perio_tooth_37_notes': perio_tooth_37_notes,
                                                                               'perio_tooth_38_form': perio_tooth_38_form,
                                                                               'perio_tooth_38_notes': perio_tooth_38_notes,
                                                                               'perio_tooth_41_form': perio_tooth_41_form,
                                                                               'perio_tooth_41_notes': perio_tooth_41_notes,
                                                                               'perio_tooth_42_form': perio_tooth_42_form,
                                                                               'perio_tooth_42_notes': perio_tooth_42_notes,
                                                                               'perio_tooth_43_form': perio_tooth_43_form,
                                                                               'perio_tooth_43_notes': perio_tooth_43_notes,
                                                                               'perio_tooth_44_form': perio_tooth_44_form,
                                                                               'perio_tooth_44_notes': perio_tooth_44_notes,
                                                                               'perio_tooth_45_form': perio_tooth_45_form,
                                                                               'perio_tooth_45_notes': perio_tooth_45_notes,
                                                                               'perio_tooth_46_form': perio_tooth_46_form,
                                                                               'perio_tooth_46_notes': perio_tooth_46_notes,
                                                                               'perio_tooth_47_form': perio_tooth_47_form,
                                                                               'perio_tooth_47_notes': perio_tooth_47_notes,
                                                                               'perio_tooth_48_form': perio_tooth_48_form,
                                                                               'perio_tooth_48_notes': perio_tooth_48_notes,
                                                                               'treatments': treatments,
                                                                               'treatment_plan_form': treatment_plan_form,
                                                                               'financial_form': financial_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'treatment_plan_form_list': treatment_plan_form_list,
                                                                               'financial_form_lists': financial_form_lists,
                                                                               'datafiles': datafiles_metadata})

        elif 'clear-dental' in request.POST:
            dental_history = DentalHistory.objects.get(patient_id=patient_id)
            dental_history.delete()
            dental_history = DentalHistory.objects.create(patient_id=patient_id)
            dental_history_form = DentalHistoryForm(instance=dental_history)
            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'odontogram': odontogram,
                                                                               'tooth_11_form': tooth_11_form,
                                                                               'tooth_12_form': tooth_12_form,
                                                                               'tooth_13_form': tooth_13_form,
                                                                               'tooth_14_form': tooth_14_form,
                                                                               'tooth_15_form': tooth_15_form,
                                                                               'tooth_16_form': tooth_16_form,
                                                                               'tooth_17_form': tooth_17_form,
                                                                               'tooth_18_form': tooth_18_form,
                                                                               'tooth_21_form': tooth_21_form,
                                                                               'tooth_22_form': tooth_22_form,
                                                                               'tooth_23_form': tooth_23_form,
                                                                               'tooth_24_form': tooth_24_form,
                                                                               'tooth_25_form': tooth_25_form,
                                                                               'tooth_26_form': tooth_26_form,
                                                                               'tooth_27_form': tooth_27_form,
                                                                               'tooth_28_form': tooth_28_form,
                                                                               'tooth_31_form': tooth_31_form,
                                                                               'tooth_32_form': tooth_32_form,
                                                                               'tooth_33_form': tooth_33_form,
                                                                               'tooth_34_form': tooth_34_form,
                                                                               'tooth_35_form': tooth_35_form,
                                                                               'tooth_36_form': tooth_36_form,
                                                                               'tooth_37_form': tooth_37_form,
                                                                               'tooth_38_form': tooth_38_form,
                                                                               'tooth_41_form': tooth_41_form,
                                                                               'tooth_42_form': tooth_42_form,
                                                                               'tooth_43_form': tooth_43_form,
                                                                               'tooth_44_form': tooth_44_form,
                                                                               'tooth_45_form': tooth_45_form,
                                                                               'tooth_46_form': tooth_46_form,
                                                                               'tooth_47_form': tooth_47_form,
                                                                               'tooth_48_form': tooth_48_form,
                                                                               'periodontogram': periodontogram,
                                                                               'perio_tooth_11_form': perio_tooth_11_form,
                                                                               'perio_tooth_11_notes': perio_tooth_11_notes,
                                                                               'perio_tooth_12_form': perio_tooth_12_form,
                                                                               'perio_tooth_12_notes': perio_tooth_12_notes,
                                                                               'perio_tooth_13_form': perio_tooth_13_form,
                                                                               'perio_tooth_13_notes': perio_tooth_13_notes,
                                                                               'perio_tooth_14_form': perio_tooth_14_form,
                                                                               'perio_tooth_14_notes': perio_tooth_14_notes,
                                                                               'perio_tooth_15_form': perio_tooth_15_form,
                                                                               'perio_tooth_15_notes': perio_tooth_15_notes,
                                                                               'perio_tooth_16_form': perio_tooth_16_form,
                                                                               'perio_tooth_16_notes': perio_tooth_16_notes,
                                                                               'perio_tooth_17_form': perio_tooth_17_form,
                                                                               'perio_tooth_17_notes': perio_tooth_17_notes,
                                                                               'perio_tooth_18_form': perio_tooth_18_form,
                                                                               'perio_tooth_18_notes': perio_tooth_18_notes,
                                                                               'perio_tooth_21_form': perio_tooth_21_form,
                                                                               'perio_tooth_21_notes': perio_tooth_21_notes,
                                                                               'perio_tooth_22_form': perio_tooth_22_form,
                                                                               'perio_tooth_22_notes': perio_tooth_22_notes,
                                                                               'perio_tooth_23_form': perio_tooth_23_form,
                                                                               'perio_tooth_23_notes': perio_tooth_23_notes,
                                                                               'perio_tooth_24_form': perio_tooth_24_form,
                                                                               'perio_tooth_24_notes': perio_tooth_24_notes,
                                                                               'perio_tooth_25_form': perio_tooth_25_form,
                                                                               'perio_tooth_25_notes': perio_tooth_25_notes,
                                                                               'perio_tooth_26_form': perio_tooth_26_form,
                                                                               'perio_tooth_26_notes': perio_tooth_26_notes,
                                                                               'perio_tooth_27_form': perio_tooth_27_form,
                                                                               'perio_tooth_27_notes': perio_tooth_27_notes,
                                                                               'perio_tooth_28_form': perio_tooth_28_form,
                                                                               'perio_tooth_28_notes': perio_tooth_28_notes,
                                                                               'perio_tooth_31_form': perio_tooth_31_form,
                                                                               'perio_tooth_31_notes': perio_tooth_31_notes,
                                                                               'perio_tooth_32_form': perio_tooth_32_form,
                                                                               'perio_tooth_32_notes': perio_tooth_32_notes,
                                                                               'perio_tooth_33_form': perio_tooth_33_form,
                                                                               'perio_tooth_33_notes': perio_tooth_33_notes,
                                                                               'perio_tooth_34_form': perio_tooth_34_form,
                                                                               'perio_tooth_34_notes': perio_tooth_34_notes,
                                                                               'perio_tooth_35_form': perio_tooth_35_form,
                                                                               'perio_tooth_35_notes': perio_tooth_35_notes,
                                                                               'perio_tooth_36_form': perio_tooth_36_form,
                                                                               'perio_tooth_36_notes': perio_tooth_36_notes,
                                                                               'perio_tooth_37_form': perio_tooth_37_form,
                                                                               'perio_tooth_37_notes': perio_tooth_37_notes,
                                                                               'perio_tooth_38_form': perio_tooth_38_form,
                                                                               'perio_tooth_38_notes': perio_tooth_38_notes,
                                                                               'perio_tooth_41_form': perio_tooth_41_form,
                                                                               'perio_tooth_41_notes': perio_tooth_41_notes,
                                                                               'perio_tooth_42_form': perio_tooth_42_form,
                                                                               'perio_tooth_42_notes': perio_tooth_42_notes,
                                                                               'perio_tooth_43_form': perio_tooth_43_form,
                                                                               'perio_tooth_43_notes': perio_tooth_43_notes,
                                                                               'perio_tooth_44_form': perio_tooth_44_form,
                                                                               'perio_tooth_44_notes': perio_tooth_44_notes,
                                                                               'perio_tooth_45_form': perio_tooth_45_form,
                                                                               'perio_tooth_45_notes': perio_tooth_45_notes,
                                                                               'perio_tooth_46_form': perio_tooth_46_form,
                                                                               'perio_tooth_46_notes': perio_tooth_46_notes,
                                                                               'perio_tooth_47_form': perio_tooth_47_form,
                                                                               'perio_tooth_47_notes': perio_tooth_47_notes,
                                                                               'perio_tooth_48_form': perio_tooth_48_form,
                                                                               'perio_tooth_48_notes': perio_tooth_48_notes,
                                                                               'treatments': treatments,
                                                                               'treatment_plan_form': treatment_plan_form,
                                                                               'financial_form': financial_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'treatment_plan_form_list': treatment_plan_form_list,
                                                                               'financial_form_lists': financial_form_lists,
                                                                               'datafiles': datafiles_metadata})

        elif 'save-appointment' in request.POST:
            appointment = Appointment.objects.create(patient_id=patient_id)
            appointment.patient = patient
            appointment_form = AppointmentForm(request.POST, instance=appointment)
            appointment_form.save()
            appointments_form_list = get_appointments_form_list(patient_id=patient_id)
            appointment_form = AppointmentForm()
            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'odontogram': odontogram,
                                                                               'tooth_11_form': tooth_11_form,
                                                                               'tooth_12_form': tooth_12_form,
                                                                               'tooth_13_form': tooth_13_form,
                                                                               'tooth_14_form': tooth_14_form,
                                                                               'tooth_15_form': tooth_15_form,
                                                                               'tooth_16_form': tooth_16_form,
                                                                               'tooth_17_form': tooth_17_form,
                                                                               'tooth_18_form': tooth_18_form,
                                                                               'tooth_21_form': tooth_21_form,
                                                                               'tooth_22_form': tooth_22_form,
                                                                               'tooth_23_form': tooth_23_form,
                                                                               'tooth_24_form': tooth_24_form,
                                                                               'tooth_25_form': tooth_25_form,
                                                                               'tooth_26_form': tooth_26_form,
                                                                               'tooth_27_form': tooth_27_form,
                                                                               'tooth_28_form': tooth_28_form,
                                                                               'tooth_31_form': tooth_31_form,
                                                                               'tooth_32_form': tooth_32_form,
                                                                               'tooth_33_form': tooth_33_form,
                                                                               'tooth_34_form': tooth_34_form,
                                                                               'tooth_35_form': tooth_35_form,
                                                                               'tooth_36_form': tooth_36_form,
                                                                               'tooth_37_form': tooth_37_form,
                                                                               'tooth_38_form': tooth_38_form,
                                                                               'tooth_41_form': tooth_41_form,
                                                                               'tooth_42_form': tooth_42_form,
                                                                               'tooth_43_form': tooth_43_form,
                                                                               'tooth_44_form': tooth_44_form,
                                                                               'tooth_45_form': tooth_45_form,
                                                                               'tooth_46_form': tooth_46_form,
                                                                               'tooth_47_form': tooth_47_form,
                                                                               'tooth_48_form': tooth_48_form,
                                                                               'periodontogram': periodontogram,
                                                                               'perio_tooth_11_form': perio_tooth_11_form,
                                                                               'perio_tooth_11_notes': perio_tooth_11_notes,
                                                                               'perio_tooth_12_form': perio_tooth_12_form,
                                                                               'perio_tooth_12_notes': perio_tooth_12_notes,
                                                                               'perio_tooth_13_form': perio_tooth_13_form,
                                                                               'perio_tooth_13_notes': perio_tooth_13_notes,
                                                                               'perio_tooth_14_form': perio_tooth_14_form,
                                                                               'perio_tooth_14_notes': perio_tooth_14_notes,
                                                                               'perio_tooth_15_form': perio_tooth_15_form,
                                                                               'perio_tooth_15_notes': perio_tooth_15_notes,
                                                                               'perio_tooth_16_form': perio_tooth_16_form,
                                                                               'perio_tooth_16_notes': perio_tooth_16_notes,
                                                                               'perio_tooth_17_form': perio_tooth_17_form,
                                                                               'perio_tooth_17_notes': perio_tooth_17_notes,
                                                                               'perio_tooth_18_form': perio_tooth_18_form,
                                                                               'perio_tooth_18_notes': perio_tooth_18_notes,
                                                                               'perio_tooth_21_form': perio_tooth_21_form,
                                                                               'perio_tooth_21_notes': perio_tooth_21_notes,
                                                                               'perio_tooth_22_form': perio_tooth_22_form,
                                                                               'perio_tooth_22_notes': perio_tooth_22_notes,
                                                                               'perio_tooth_23_form': perio_tooth_23_form,
                                                                               'perio_tooth_23_notes': perio_tooth_23_notes,
                                                                               'perio_tooth_24_form': perio_tooth_24_form,
                                                                               'perio_tooth_24_notes': perio_tooth_24_notes,
                                                                               'perio_tooth_25_form': perio_tooth_25_form,
                                                                               'perio_tooth_25_notes': perio_tooth_25_notes,
                                                                               'perio_tooth_26_form': perio_tooth_26_form,
                                                                               'perio_tooth_26_notes': perio_tooth_26_notes,
                                                                               'perio_tooth_27_form': perio_tooth_27_form,
                                                                               'perio_tooth_27_notes': perio_tooth_27_notes,
                                                                               'perio_tooth_28_form': perio_tooth_28_form,
                                                                               'perio_tooth_28_notes': perio_tooth_28_notes,
                                                                               'perio_tooth_31_form': perio_tooth_31_form,
                                                                               'perio_tooth_31_notes': perio_tooth_31_notes,
                                                                               'perio_tooth_32_form': perio_tooth_32_form,
                                                                               'perio_tooth_32_notes': perio_tooth_32_notes,
                                                                               'perio_tooth_33_form': perio_tooth_33_form,
                                                                               'perio_tooth_33_notes': perio_tooth_33_notes,
                                                                               'perio_tooth_34_form': perio_tooth_34_form,
                                                                               'perio_tooth_34_notes': perio_tooth_34_notes,
                                                                               'perio_tooth_35_form': perio_tooth_35_form,
                                                                               'perio_tooth_35_notes': perio_tooth_35_notes,
                                                                               'perio_tooth_36_form': perio_tooth_36_form,
                                                                               'perio_tooth_36_notes': perio_tooth_36_notes,
                                                                               'perio_tooth_37_form': perio_tooth_37_form,
                                                                               'perio_tooth_37_notes': perio_tooth_37_notes,
                                                                               'perio_tooth_38_form': perio_tooth_38_form,
                                                                               'perio_tooth_38_notes': perio_tooth_38_notes,
                                                                               'perio_tooth_41_form': perio_tooth_41_form,
                                                                               'perio_tooth_41_notes': perio_tooth_41_notes,
                                                                               'perio_tooth_42_form': perio_tooth_42_form,
                                                                               'perio_tooth_42_notes': perio_tooth_42_notes,
                                                                               'perio_tooth_43_form': perio_tooth_43_form,
                                                                               'perio_tooth_43_notes': perio_tooth_43_notes,
                                                                               'perio_tooth_44_form': perio_tooth_44_form,
                                                                               'perio_tooth_44_notes': perio_tooth_44_notes,
                                                                               'perio_tooth_45_form': perio_tooth_45_form,
                                                                               'perio_tooth_45_notes': perio_tooth_45_notes,
                                                                               'perio_tooth_46_form': perio_tooth_46_form,
                                                                               'perio_tooth_46_notes': perio_tooth_46_notes,
                                                                               'perio_tooth_47_form': perio_tooth_47_form,
                                                                               'perio_tooth_47_notes': perio_tooth_47_notes,
                                                                               'perio_tooth_48_form': perio_tooth_48_form,
                                                                               'perio_tooth_48_notes': perio_tooth_48_notes,
                                                                               'treatments': treatments,
                                                                               'treatment_plan_form': treatment_plan_form,
                                                                               'financial_form': financial_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'treatment_plan_form_list': treatment_plan_form_list,
                                                                               'financial_form_lists': financial_form_lists,
                                                                               'datafiles': datafiles_metadata})

        elif 'edit-appointment' in request.POST:
            appointment_id = request.POST.get('id')
            edited_appointment = Appointment.objects.get(id=appointment_id)
            appointment_form = AppointmentForm(request.POST, instance=edited_appointment)
            appointment_form.save()

            appointment_form = AppointmentForm()

            appointments_form_list = get_appointments_form_list(patient_id=patient_id) \
                if len(get_appointments_form_list(patient_id=patient_id)) > 0 else None

            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'financial_form': financial_form,
                                                                               'odontogram': odontogram,
                                                                               'tooth_11_form': tooth_11_form,
                                                                               'tooth_12_form': tooth_12_form,
                                                                               'tooth_13_form': tooth_13_form,
                                                                               'tooth_14_form': tooth_14_form,
                                                                               'tooth_15_form': tooth_15_form,
                                                                               'tooth_16_form': tooth_16_form,
                                                                               'tooth_17_form': tooth_17_form,
                                                                               'tooth_18_form': tooth_18_form,
                                                                               'tooth_21_form': tooth_21_form,
                                                                               'tooth_22_form': tooth_22_form,
                                                                               'tooth_23_form': tooth_23_form,
                                                                               'tooth_24_form': tooth_24_form,
                                                                               'tooth_25_form': tooth_25_form,
                                                                               'tooth_26_form': tooth_26_form,
                                                                               'tooth_27_form': tooth_27_form,
                                                                               'tooth_28_form': tooth_28_form,
                                                                               'tooth_31_form': tooth_31_form,
                                                                               'tooth_32_form': tooth_32_form,
                                                                               'tooth_33_form': tooth_33_form,
                                                                               'tooth_34_form': tooth_34_form,
                                                                               'tooth_35_form': tooth_35_form,
                                                                               'tooth_36_form': tooth_36_form,
                                                                               'tooth_37_form': tooth_37_form,
                                                                               'tooth_38_form': tooth_38_form,
                                                                               'tooth_41_form': tooth_41_form,
                                                                               'tooth_42_form': tooth_42_form,
                                                                               'tooth_43_form': tooth_43_form,
                                                                               'tooth_44_form': tooth_44_form,
                                                                               'tooth_45_form': tooth_45_form,
                                                                               'tooth_46_form': tooth_46_form,
                                                                               'tooth_47_form': tooth_47_form,
                                                                               'tooth_48_form': tooth_48_form,
                                                                               'periodontogram': periodontogram,
                                                                               'perio_tooth_11_form': perio_tooth_11_form,
                                                                               'perio_tooth_11_notes': perio_tooth_11_notes,
                                                                               'perio_tooth_12_form': perio_tooth_12_form,
                                                                               'perio_tooth_12_notes': perio_tooth_12_notes,
                                                                               'perio_tooth_13_form': perio_tooth_13_form,
                                                                               'perio_tooth_13_notes': perio_tooth_13_notes,
                                                                               'perio_tooth_14_form': perio_tooth_14_form,
                                                                               'perio_tooth_14_notes': perio_tooth_14_notes,
                                                                               'perio_tooth_15_form': perio_tooth_15_form,
                                                                               'perio_tooth_15_notes': perio_tooth_15_notes,
                                                                               'perio_tooth_16_form': perio_tooth_16_form,
                                                                               'perio_tooth_16_notes': perio_tooth_16_notes,
                                                                               'perio_tooth_17_form': perio_tooth_17_form,
                                                                               'perio_tooth_17_notes': perio_tooth_17_notes,
                                                                               'perio_tooth_18_form': perio_tooth_18_form,
                                                                               'perio_tooth_18_notes': perio_tooth_18_notes,
                                                                               'perio_tooth_21_form': perio_tooth_21_form,
                                                                               'perio_tooth_21_notes': perio_tooth_21_notes,
                                                                               'perio_tooth_22_form': perio_tooth_22_form,
                                                                               'perio_tooth_22_notes': perio_tooth_22_notes,
                                                                               'perio_tooth_23_form': perio_tooth_23_form,
                                                                               'perio_tooth_23_notes': perio_tooth_23_notes,
                                                                               'perio_tooth_24_form': perio_tooth_24_form,
                                                                               'perio_tooth_24_notes': perio_tooth_24_notes,
                                                                               'perio_tooth_25_form': perio_tooth_25_form,
                                                                               'perio_tooth_25_notes': perio_tooth_25_notes,
                                                                               'perio_tooth_26_form': perio_tooth_26_form,
                                                                               'perio_tooth_26_notes': perio_tooth_26_notes,
                                                                               'perio_tooth_27_form': perio_tooth_27_form,
                                                                               'perio_tooth_27_notes': perio_tooth_27_notes,
                                                                               'perio_tooth_28_form': perio_tooth_28_form,
                                                                               'perio_tooth_28_notes': perio_tooth_28_notes,
                                                                               'perio_tooth_31_form': perio_tooth_31_form,
                                                                               'perio_tooth_31_notes': perio_tooth_31_notes,
                                                                               'perio_tooth_32_form': perio_tooth_32_form,
                                                                               'perio_tooth_32_notes': perio_tooth_32_notes,
                                                                               'perio_tooth_33_form': perio_tooth_33_form,
                                                                               'perio_tooth_33_notes': perio_tooth_33_notes,
                                                                               'perio_tooth_34_form': perio_tooth_34_form,
                                                                               'perio_tooth_34_notes': perio_tooth_34_notes,
                                                                               'perio_tooth_35_form': perio_tooth_35_form,
                                                                               'perio_tooth_35_notes': perio_tooth_35_notes,
                                                                               'perio_tooth_36_form': perio_tooth_36_form,
                                                                               'perio_tooth_36_notes': perio_tooth_36_notes,
                                                                               'perio_tooth_37_form': perio_tooth_37_form,
                                                                               'perio_tooth_37_notes': perio_tooth_37_notes,
                                                                               'perio_tooth_38_form': perio_tooth_38_form,
                                                                               'perio_tooth_38_notes': perio_tooth_38_notes,
                                                                               'perio_tooth_41_form': perio_tooth_41_form,
                                                                               'perio_tooth_41_notes': perio_tooth_41_notes,
                                                                               'perio_tooth_42_form': perio_tooth_42_form,
                                                                               'perio_tooth_42_notes': perio_tooth_42_notes,
                                                                               'perio_tooth_43_form': perio_tooth_43_form,
                                                                               'perio_tooth_43_notes': perio_tooth_43_notes,
                                                                               'perio_tooth_44_form': perio_tooth_44_form,
                                                                               'perio_tooth_44_notes': perio_tooth_44_notes,
                                                                               'perio_tooth_45_form': perio_tooth_45_form,
                                                                               'perio_tooth_45_notes': perio_tooth_45_notes,
                                                                               'perio_tooth_46_form': perio_tooth_46_form,
                                                                               'perio_tooth_46_notes': perio_tooth_46_notes,
                                                                               'perio_tooth_47_form': perio_tooth_47_form,
                                                                               'perio_tooth_47_notes': perio_tooth_47_notes,
                                                                               'perio_tooth_48_form': perio_tooth_48_form,
                                                                               'perio_tooth_48_notes': perio_tooth_48_notes,
                                                                               'treatments': treatments,
                                                                               'treatment_plan_form': treatment_plan_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'treatment_plan_form_list': treatment_plan_form_list,
                                                                               'financial_form_lists': financial_form_lists,
                                                                               'datafiles': datafiles_metadata})

        elif 'delete-appointment' in request.POST:
            appointment_id = request.POST.get('id')
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.delete()
            appointments_form_list = get_appointments_form_list(patient_id=patient_id)
            appointment_form = AppointmentForm()

            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'odontogram': odontogram,
                                                                               'tooth_11_form': tooth_11_form,
                                                                               'tooth_12_form': tooth_12_form,
                                                                               'tooth_13_form': tooth_13_form,
                                                                               'tooth_14_form': tooth_14_form,
                                                                               'tooth_15_form': tooth_15_form,
                                                                               'tooth_16_form': tooth_16_form,
                                                                               'tooth_17_form': tooth_17_form,
                                                                               'tooth_18_form': tooth_18_form,
                                                                               'tooth_21_form': tooth_21_form,
                                                                               'tooth_22_form': tooth_22_form,
                                                                               'tooth_23_form': tooth_23_form,
                                                                               'tooth_24_form': tooth_24_form,
                                                                               'tooth_25_form': tooth_25_form,
                                                                               'tooth_26_form': tooth_26_form,
                                                                               'tooth_27_form': tooth_27_form,
                                                                               'tooth_28_form': tooth_28_form,
                                                                               'tooth_31_form': tooth_31_form,
                                                                               'tooth_32_form': tooth_32_form,
                                                                               'tooth_33_form': tooth_33_form,
                                                                               'tooth_34_form': tooth_34_form,
                                                                               'tooth_35_form': tooth_35_form,
                                                                               'tooth_36_form': tooth_36_form,
                                                                               'tooth_37_form': tooth_37_form,
                                                                               'tooth_38_form': tooth_38_form,
                                                                               'tooth_41_form': tooth_41_form,
                                                                               'tooth_42_form': tooth_42_form,
                                                                               'tooth_43_form': tooth_43_form,
                                                                               'tooth_44_form': tooth_44_form,
                                                                               'tooth_45_form': tooth_45_form,
                                                                               'tooth_46_form': tooth_46_form,
                                                                               'tooth_47_form': tooth_47_form,
                                                                               'tooth_48_form': tooth_48_form,
                                                                               'periodontogram': periodontogram,
                                                                               'perio_tooth_11_form': perio_tooth_11_form,
                                                                               'perio_tooth_11_notes': perio_tooth_11_notes,
                                                                               'perio_tooth_12_form': perio_tooth_12_form,
                                                                               'perio_tooth_12_notes': perio_tooth_12_notes,
                                                                               'perio_tooth_13_form': perio_tooth_13_form,
                                                                               'perio_tooth_13_notes': perio_tooth_13_notes,
                                                                               'perio_tooth_14_form': perio_tooth_14_form,
                                                                               'perio_tooth_14_notes': perio_tooth_14_notes,
                                                                               'perio_tooth_15_form': perio_tooth_15_form,
                                                                               'perio_tooth_15_notes': perio_tooth_15_notes,
                                                                               'perio_tooth_16_form': perio_tooth_16_form,
                                                                               'perio_tooth_16_notes': perio_tooth_16_notes,
                                                                               'perio_tooth_17_form': perio_tooth_17_form,
                                                                               'perio_tooth_17_notes': perio_tooth_17_notes,
                                                                               'perio_tooth_18_form': perio_tooth_18_form,
                                                                               'perio_tooth_18_notes': perio_tooth_18_notes,
                                                                               'perio_tooth_21_form': perio_tooth_21_form,
                                                                               'perio_tooth_21_notes': perio_tooth_21_notes,
                                                                               'perio_tooth_22_form': perio_tooth_22_form,
                                                                               'perio_tooth_22_notes': perio_tooth_22_notes,
                                                                               'perio_tooth_23_form': perio_tooth_23_form,
                                                                               'perio_tooth_23_notes': perio_tooth_23_notes,
                                                                               'perio_tooth_24_form': perio_tooth_24_form,
                                                                               'perio_tooth_24_notes': perio_tooth_24_notes,
                                                                               'perio_tooth_25_form': perio_tooth_25_form,
                                                                               'perio_tooth_25_notes': perio_tooth_25_notes,
                                                                               'perio_tooth_26_form': perio_tooth_26_form,
                                                                               'perio_tooth_26_notes': perio_tooth_26_notes,
                                                                               'perio_tooth_27_form': perio_tooth_27_form,
                                                                               'perio_tooth_27_notes': perio_tooth_27_notes,
                                                                               'perio_tooth_28_form': perio_tooth_28_form,
                                                                               'perio_tooth_28_notes': perio_tooth_28_notes,
                                                                               'perio_tooth_31_form': perio_tooth_31_form,
                                                                               'perio_tooth_31_notes': perio_tooth_31_notes,
                                                                               'perio_tooth_32_form': perio_tooth_32_form,
                                                                               'perio_tooth_32_notes': perio_tooth_32_notes,
                                                                               'perio_tooth_33_form': perio_tooth_33_form,
                                                                               'perio_tooth_33_notes': perio_tooth_33_notes,
                                                                               'perio_tooth_34_form': perio_tooth_34_form,
                                                                               'perio_tooth_34_notes': perio_tooth_34_notes,
                                                                               'perio_tooth_35_form': perio_tooth_35_form,
                                                                               'perio_tooth_35_notes': perio_tooth_35_notes,
                                                                               'perio_tooth_36_form': perio_tooth_36_form,
                                                                               'perio_tooth_36_notes': perio_tooth_36_notes,
                                                                               'perio_tooth_37_form': perio_tooth_37_form,
                                                                               'perio_tooth_37_notes': perio_tooth_37_notes,
                                                                               'perio_tooth_38_form': perio_tooth_38_form,
                                                                               'perio_tooth_38_notes': perio_tooth_38_notes,
                                                                               'perio_tooth_41_form': perio_tooth_41_form,
                                                                               'perio_tooth_41_notes': perio_tooth_41_notes,
                                                                               'perio_tooth_42_form': perio_tooth_42_form,
                                                                               'perio_tooth_42_notes': perio_tooth_42_notes,
                                                                               'perio_tooth_43_form': perio_tooth_43_form,
                                                                               'perio_tooth_43_notes': perio_tooth_43_notes,
                                                                               'perio_tooth_44_form': perio_tooth_44_form,
                                                                               'perio_tooth_44_notes': perio_tooth_44_notes,
                                                                               'perio_tooth_45_form': perio_tooth_45_form,
                                                                               'perio_tooth_45_notes': perio_tooth_45_notes,
                                                                               'perio_tooth_46_form': perio_tooth_46_form,
                                                                               'perio_tooth_46_notes': perio_tooth_46_notes,
                                                                               'perio_tooth_47_form': perio_tooth_47_form,
                                                                               'perio_tooth_47_notes': perio_tooth_47_notes,
                                                                               'perio_tooth_48_form': perio_tooth_48_form,
                                                                               'perio_tooth_48_notes': perio_tooth_48_notes,
                                                                               'treatments': treatments,
                                                                               'treatment_plan_form': treatment_plan_form,
                                                                               'financial_form': financial_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'treatment_plan_form_list': treatment_plan_form_list,
                                                                               'financial_form_lists': financial_form_lists,
                                                                               'datafiles': datafiles_metadata})

        elif 'save-treatment-plan' in request.POST:
            treatment_plan = TreatmentPlan.objects.create(patient_id=patient_id)
            treatment_plan.patient = patient
            treatment_plan_form = TreatmentPlanForm(request.POST, instance=treatment_plan)
            treatment_plan_form.save()
            treatment_plan_form_list = get_treatment_plan_form_list(patient_id=patient_id)
            treatment_plan_form = TreatmentPlanForm()
            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'odontogram': odontogram,
                                                                               'tooth_11_form': tooth_11_form,
                                                                               'tooth_12_form': tooth_12_form,
                                                                               'tooth_13_form': tooth_13_form,
                                                                               'tooth_14_form': tooth_14_form,
                                                                               'tooth_15_form': tooth_15_form,
                                                                               'tooth_16_form': tooth_16_form,
                                                                               'tooth_17_form': tooth_17_form,
                                                                               'tooth_18_form': tooth_18_form,
                                                                               'tooth_21_form': tooth_21_form,
                                                                               'tooth_22_form': tooth_22_form,
                                                                               'tooth_23_form': tooth_23_form,
                                                                               'tooth_24_form': tooth_24_form,
                                                                               'tooth_25_form': tooth_25_form,
                                                                               'tooth_26_form': tooth_26_form,
                                                                               'tooth_27_form': tooth_27_form,
                                                                               'tooth_28_form': tooth_28_form,
                                                                               'tooth_31_form': tooth_31_form,
                                                                               'tooth_32_form': tooth_32_form,
                                                                               'tooth_33_form': tooth_33_form,
                                                                               'tooth_34_form': tooth_34_form,
                                                                               'tooth_35_form': tooth_35_form,
                                                                               'tooth_36_form': tooth_36_form,
                                                                               'tooth_37_form': tooth_37_form,
                                                                               'tooth_38_form': tooth_38_form,
                                                                               'tooth_41_form': tooth_41_form,
                                                                               'tooth_42_form': tooth_42_form,
                                                                               'tooth_43_form': tooth_43_form,
                                                                               'tooth_44_form': tooth_44_form,
                                                                               'tooth_45_form': tooth_45_form,
                                                                               'tooth_46_form': tooth_46_form,
                                                                               'tooth_47_form': tooth_47_form,
                                                                               'tooth_48_form': tooth_48_form,
                                                                               'periodontogram': periodontogram,
                                                                               'perio_tooth_11_form': perio_tooth_11_form,
                                                                               'perio_tooth_11_notes': perio_tooth_11_notes,
                                                                               'perio_tooth_12_form': perio_tooth_12_form,
                                                                               'perio_tooth_12_notes': perio_tooth_12_notes,
                                                                               'perio_tooth_13_form': perio_tooth_13_form,
                                                                               'perio_tooth_13_notes': perio_tooth_13_notes,
                                                                               'perio_tooth_14_form': perio_tooth_14_form,
                                                                               'perio_tooth_14_notes': perio_tooth_14_notes,
                                                                               'perio_tooth_15_form': perio_tooth_15_form,
                                                                               'perio_tooth_15_notes': perio_tooth_15_notes,
                                                                               'perio_tooth_16_form': perio_tooth_16_form,
                                                                               'perio_tooth_16_notes': perio_tooth_16_notes,
                                                                               'perio_tooth_17_form': perio_tooth_17_form,
                                                                               'perio_tooth_17_notes': perio_tooth_17_notes,
                                                                               'perio_tooth_18_form': perio_tooth_18_form,
                                                                               'perio_tooth_18_notes': perio_tooth_18_notes,
                                                                               'perio_tooth_21_form': perio_tooth_21_form,
                                                                               'perio_tooth_21_notes': perio_tooth_21_notes,
                                                                               'perio_tooth_22_form': perio_tooth_22_form,
                                                                               'perio_tooth_22_notes': perio_tooth_22_notes,
                                                                               'perio_tooth_23_form': perio_tooth_23_form,
                                                                               'perio_tooth_23_notes': perio_tooth_23_notes,
                                                                               'perio_tooth_24_form': perio_tooth_24_form,
                                                                               'perio_tooth_24_notes': perio_tooth_24_notes,
                                                                               'perio_tooth_25_form': perio_tooth_25_form,
                                                                               'perio_tooth_25_notes': perio_tooth_25_notes,
                                                                               'perio_tooth_26_form': perio_tooth_26_form,
                                                                               'perio_tooth_26_notes': perio_tooth_26_notes,
                                                                               'perio_tooth_27_form': perio_tooth_27_form,
                                                                               'perio_tooth_27_notes': perio_tooth_27_notes,
                                                                               'perio_tooth_28_form': perio_tooth_28_form,
                                                                               'perio_tooth_28_notes': perio_tooth_28_notes,
                                                                               'perio_tooth_31_form': perio_tooth_31_form,
                                                                               'perio_tooth_31_notes': perio_tooth_31_notes,
                                                                               'perio_tooth_32_form': perio_tooth_32_form,
                                                                               'perio_tooth_32_notes': perio_tooth_32_notes,
                                                                               'perio_tooth_33_form': perio_tooth_33_form,
                                                                               'perio_tooth_33_notes': perio_tooth_33_notes,
                                                                               'perio_tooth_34_form': perio_tooth_34_form,
                                                                               'perio_tooth_34_notes': perio_tooth_34_notes,
                                                                               'perio_tooth_35_form': perio_tooth_35_form,
                                                                               'perio_tooth_35_notes': perio_tooth_35_notes,
                                                                               'perio_tooth_36_form': perio_tooth_36_form,
                                                                               'perio_tooth_36_notes': perio_tooth_36_notes,
                                                                               'perio_tooth_37_form': perio_tooth_37_form,
                                                                               'perio_tooth_37_notes': perio_tooth_37_notes,
                                                                               'perio_tooth_38_form': perio_tooth_38_form,
                                                                               'perio_tooth_38_notes': perio_tooth_38_notes,
                                                                               'perio_tooth_41_form': perio_tooth_41_form,
                                                                               'perio_tooth_41_notes': perio_tooth_41_notes,
                                                                               'perio_tooth_42_form': perio_tooth_42_form,
                                                                               'perio_tooth_42_notes': perio_tooth_42_notes,
                                                                               'perio_tooth_43_form': perio_tooth_43_form,
                                                                               'perio_tooth_43_notes': perio_tooth_43_notes,
                                                                               'perio_tooth_44_form': perio_tooth_44_form,
                                                                               'perio_tooth_44_notes': perio_tooth_44_notes,
                                                                               'perio_tooth_45_form': perio_tooth_45_form,
                                                                               'perio_tooth_45_notes': perio_tooth_45_notes,
                                                                               'perio_tooth_46_form': perio_tooth_46_form,
                                                                               'perio_tooth_46_notes': perio_tooth_46_notes,
                                                                               'perio_tooth_47_form': perio_tooth_47_form,
                                                                               'perio_tooth_47_notes': perio_tooth_47_notes,
                                                                               'perio_tooth_48_form': perio_tooth_48_form,
                                                                               'perio_tooth_48_notes': perio_tooth_48_notes,
                                                                               'treatments': treatments,
                                                                               'treatment_plan_form': treatment_plan_form,
                                                                               'financial_form': financial_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'treatment_plan_form_list': treatment_plan_form_list,
                                                                               'financial_form_lists': financial_form_lists,
                                                                               'datafiles': datafiles_metadata})

        elif 'edit-treatment-plan' in request.POST:
            treatment_plan_id = request.POST.get('id')
            edited_treatment_plan = TreatmentPlan.objects.get(id=treatment_plan_id)
            edited_treatment_plan.treatment_plan_description = request.POST.get('treatment_plan_description')
            edited_treatment_plan.total_cost = request.POST.get('total_cost')
            treatment_plan_balance = calculate_balance(treatment_plan_id)
            edited_treatment_plan.treatment_plan_balance = edited_treatment_plan.total_cost \
                if treatment_plan_balance == edited_treatment_plan.total_cost \
                else treatment_plan_balance
            edited_treatment_plan.treatment_plan_start_date = request.POST.get('treatment_plan_start_date')
            edited_treatment_plan.treatment_plan_end_date = request.POST.get('treatment_plan_end_date') \
                if request.POST.get('treatment_plan_end_date') \
                else None
            edited_treatment_plan.treatment_plan_notes = request.POST.get('treatment_plan_notes')
            edited_treatment_plan.save()
            appointment_form = AppointmentForm()

            appointments_form_list, treatment_plan_form_list, financial_form_lists = initiate_forms(
                patient_id=patient_id)

            treatment_plan_form_list = get_treatment_plan_form_list(patient_id=patient_id) \
                if len(get_treatment_plan_form_list(patient_id=patient_id)) > 0 else None

            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'odontogram': odontogram,
                                                                               'tooth_11_form': tooth_11_form,
                                                                               'tooth_12_form': tooth_12_form,
                                                                               'tooth_13_form': tooth_13_form,
                                                                               'tooth_14_form': tooth_14_form,
                                                                               'tooth_15_form': tooth_15_form,
                                                                               'tooth_16_form': tooth_16_form,
                                                                               'tooth_17_form': tooth_17_form,
                                                                               'tooth_18_form': tooth_18_form,
                                                                               'tooth_21_form': tooth_21_form,
                                                                               'tooth_22_form': tooth_22_form,
                                                                               'tooth_23_form': tooth_23_form,
                                                                               'tooth_24_form': tooth_24_form,
                                                                               'tooth_25_form': tooth_25_form,
                                                                               'tooth_26_form': tooth_26_form,
                                                                               'tooth_27_form': tooth_27_form,
                                                                               'tooth_28_form': tooth_28_form,
                                                                               'tooth_31_form': tooth_31_form,
                                                                               'tooth_32_form': tooth_32_form,
                                                                               'tooth_33_form': tooth_33_form,
                                                                               'tooth_34_form': tooth_34_form,
                                                                               'tooth_35_form': tooth_35_form,
                                                                               'tooth_36_form': tooth_36_form,
                                                                               'tooth_37_form': tooth_37_form,
                                                                               'tooth_38_form': tooth_38_form,
                                                                               'tooth_41_form': tooth_41_form,
                                                                               'tooth_42_form': tooth_42_form,
                                                                               'tooth_43_form': tooth_43_form,
                                                                               'tooth_44_form': tooth_44_form,
                                                                               'tooth_45_form': tooth_45_form,
                                                                               'tooth_46_form': tooth_46_form,
                                                                               'tooth_47_form': tooth_47_form,
                                                                               'tooth_48_form': tooth_48_form,
                                                                               'periodontogram': periodontogram,
                                                                               'perio_tooth_11_form': perio_tooth_11_form,
                                                                               'perio_tooth_11_notes': perio_tooth_11_notes,
                                                                               'perio_tooth_12_form': perio_tooth_12_form,
                                                                               'perio_tooth_12_notes': perio_tooth_12_notes,
                                                                               'perio_tooth_13_form': perio_tooth_13_form,
                                                                               'perio_tooth_13_notes': perio_tooth_13_notes,
                                                                               'perio_tooth_14_form': perio_tooth_14_form,
                                                                               'perio_tooth_14_notes': perio_tooth_14_notes,
                                                                               'perio_tooth_15_form': perio_tooth_15_form,
                                                                               'perio_tooth_15_notes': perio_tooth_15_notes,
                                                                               'perio_tooth_16_form': perio_tooth_16_form,
                                                                               'perio_tooth_16_notes': perio_tooth_16_notes,
                                                                               'perio_tooth_17_form': perio_tooth_17_form,
                                                                               'perio_tooth_17_notes': perio_tooth_17_notes,
                                                                               'perio_tooth_18_form': perio_tooth_18_form,
                                                                               'perio_tooth_18_notes': perio_tooth_18_notes,
                                                                               'perio_tooth_21_form': perio_tooth_21_form,
                                                                               'perio_tooth_21_notes': perio_tooth_21_notes,
                                                                               'perio_tooth_22_form': perio_tooth_22_form,
                                                                               'perio_tooth_22_notes': perio_tooth_22_notes,
                                                                               'perio_tooth_23_form': perio_tooth_23_form,
                                                                               'perio_tooth_23_notes': perio_tooth_23_notes,
                                                                               'perio_tooth_24_form': perio_tooth_24_form,
                                                                               'perio_tooth_24_notes': perio_tooth_24_notes,
                                                                               'perio_tooth_25_form': perio_tooth_25_form,
                                                                               'perio_tooth_25_notes': perio_tooth_25_notes,
                                                                               'perio_tooth_26_form': perio_tooth_26_form,
                                                                               'perio_tooth_26_notes': perio_tooth_26_notes,
                                                                               'perio_tooth_27_form': perio_tooth_27_form,
                                                                               'perio_tooth_27_notes': perio_tooth_27_notes,
                                                                               'perio_tooth_28_form': perio_tooth_28_form,
                                                                               'perio_tooth_28_notes': perio_tooth_28_notes,
                                                                               'perio_tooth_31_form': perio_tooth_31_form,
                                                                               'perio_tooth_31_notes': perio_tooth_31_notes,
                                                                               'perio_tooth_32_form': perio_tooth_32_form,
                                                                               'perio_tooth_32_notes': perio_tooth_32_notes,
                                                                               'perio_tooth_33_form': perio_tooth_33_form,
                                                                               'perio_tooth_33_notes': perio_tooth_33_notes,
                                                                               'perio_tooth_34_form': perio_tooth_34_form,
                                                                               'perio_tooth_34_notes': perio_tooth_34_notes,
                                                                               'perio_tooth_35_form': perio_tooth_35_form,
                                                                               'perio_tooth_35_notes': perio_tooth_35_notes,
                                                                               'perio_tooth_36_form': perio_tooth_36_form,
                                                                               'perio_tooth_36_notes': perio_tooth_36_notes,
                                                                               'perio_tooth_37_form': perio_tooth_37_form,
                                                                               'perio_tooth_37_notes': perio_tooth_37_notes,
                                                                               'perio_tooth_38_form': perio_tooth_38_form,
                                                                               'perio_tooth_38_notes': perio_tooth_38_notes,
                                                                               'perio_tooth_41_form': perio_tooth_41_form,
                                                                               'perio_tooth_41_notes': perio_tooth_41_notes,
                                                                               'perio_tooth_42_form': perio_tooth_42_form,
                                                                               'perio_tooth_42_notes': perio_tooth_42_notes,
                                                                               'perio_tooth_43_form': perio_tooth_43_form,
                                                                               'perio_tooth_43_notes': perio_tooth_43_notes,
                                                                               'perio_tooth_44_form': perio_tooth_44_form,
                                                                               'perio_tooth_44_notes': perio_tooth_44_notes,
                                                                               'perio_tooth_45_form': perio_tooth_45_form,
                                                                               'perio_tooth_45_notes': perio_tooth_45_notes,
                                                                               'perio_tooth_46_form': perio_tooth_46_form,
                                                                               'perio_tooth_46_notes': perio_tooth_46_notes,
                                                                               'perio_tooth_47_form': perio_tooth_47_form,
                                                                               'perio_tooth_47_notes': perio_tooth_47_notes,
                                                                               'perio_tooth_48_form': perio_tooth_48_form,
                                                                               'perio_tooth_48_notes': perio_tooth_48_notes,
                                                                               'treatments': treatments,
                                                                               'treatment_plan_form': treatment_plan_form,
                                                                               'financial_form': financial_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'treatment_plan_form_list': treatment_plan_form_list,
                                                                               'financial_form_lists': financial_form_lists,
                                                                               'datafiles': datafiles_metadata})

        elif 'delete-treatment-plan' in request.POST:
            treatment_plan_id = request.POST.get('id')
            treatment_plan = TreatmentPlan.objects.get(id=treatment_plan_id)
            treatment_plan.delete()
            treatment_plan_form_list = get_treatment_plan_form_list(patient_id=patient_id)
            treatment_plan_form = TreatmentPlanForm()

            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'odontogram': odontogram,
                                                                               'tooth_11_form': tooth_11_form,
                                                                               'tooth_12_form': tooth_12_form,
                                                                               'tooth_13_form': tooth_13_form,
                                                                               'tooth_14_form': tooth_14_form,
                                                                               'tooth_15_form': tooth_15_form,
                                                                               'tooth_16_form': tooth_16_form,
                                                                               'tooth_17_form': tooth_17_form,
                                                                               'tooth_18_form': tooth_18_form,
                                                                               'tooth_21_form': tooth_21_form,
                                                                               'tooth_22_form': tooth_22_form,
                                                                               'tooth_23_form': tooth_23_form,
                                                                               'tooth_24_form': tooth_24_form,
                                                                               'tooth_25_form': tooth_25_form,
                                                                               'tooth_26_form': tooth_26_form,
                                                                               'tooth_27_form': tooth_27_form,
                                                                               'tooth_28_form': tooth_28_form,
                                                                               'tooth_31_form': tooth_31_form,
                                                                               'tooth_32_form': tooth_32_form,
                                                                               'tooth_33_form': tooth_33_form,
                                                                               'tooth_34_form': tooth_34_form,
                                                                               'tooth_35_form': tooth_35_form,
                                                                               'tooth_36_form': tooth_36_form,
                                                                               'tooth_37_form': tooth_37_form,
                                                                               'tooth_38_form': tooth_38_form,
                                                                               'tooth_41_form': tooth_41_form,
                                                                               'tooth_42_form': tooth_42_form,
                                                                               'tooth_43_form': tooth_43_form,
                                                                               'tooth_44_form': tooth_44_form,
                                                                               'tooth_45_form': tooth_45_form,
                                                                               'tooth_46_form': tooth_46_form,
                                                                               'tooth_47_form': tooth_47_form,
                                                                               'tooth_48_form': tooth_48_form,
                                                                               'periodontogram': periodontogram,
                                                                               'perio_tooth_11_form': perio_tooth_11_form,
                                                                               'perio_tooth_11_notes': perio_tooth_11_notes,
                                                                               'perio_tooth_12_form': perio_tooth_12_form,
                                                                               'perio_tooth_12_notes': perio_tooth_12_notes,
                                                                               'perio_tooth_13_form': perio_tooth_13_form,
                                                                               'perio_tooth_13_notes': perio_tooth_13_notes,
                                                                               'perio_tooth_14_form': perio_tooth_14_form,
                                                                               'perio_tooth_14_notes': perio_tooth_14_notes,
                                                                               'perio_tooth_15_form': perio_tooth_15_form,
                                                                               'perio_tooth_15_notes': perio_tooth_15_notes,
                                                                               'perio_tooth_16_form': perio_tooth_16_form,
                                                                               'perio_tooth_16_notes': perio_tooth_16_notes,
                                                                               'perio_tooth_17_form': perio_tooth_17_form,
                                                                               'perio_tooth_17_notes': perio_tooth_17_notes,
                                                                               'perio_tooth_18_form': perio_tooth_18_form,
                                                                               'perio_tooth_18_notes': perio_tooth_18_notes,
                                                                               'perio_tooth_21_form': perio_tooth_21_form,
                                                                               'perio_tooth_21_notes': perio_tooth_21_notes,
                                                                               'perio_tooth_22_form': perio_tooth_22_form,
                                                                               'perio_tooth_22_notes': perio_tooth_22_notes,
                                                                               'perio_tooth_23_form': perio_tooth_23_form,
                                                                               'perio_tooth_23_notes': perio_tooth_23_notes,
                                                                               'perio_tooth_24_form': perio_tooth_24_form,
                                                                               'perio_tooth_24_notes': perio_tooth_24_notes,
                                                                               'perio_tooth_25_form': perio_tooth_25_form,
                                                                               'perio_tooth_25_notes': perio_tooth_25_notes,
                                                                               'perio_tooth_26_form': perio_tooth_26_form,
                                                                               'perio_tooth_26_notes': perio_tooth_26_notes,
                                                                               'perio_tooth_27_form': perio_tooth_27_form,
                                                                               'perio_tooth_27_notes': perio_tooth_27_notes,
                                                                               'perio_tooth_28_form': perio_tooth_28_form,
                                                                               'perio_tooth_28_notes': perio_tooth_28_notes,
                                                                               'perio_tooth_31_form': perio_tooth_31_form,
                                                                               'perio_tooth_31_notes': perio_tooth_31_notes,
                                                                               'perio_tooth_32_form': perio_tooth_32_form,
                                                                               'perio_tooth_32_notes': perio_tooth_32_notes,
                                                                               'perio_tooth_33_form': perio_tooth_33_form,
                                                                               'perio_tooth_33_notes': perio_tooth_33_notes,
                                                                               'perio_tooth_34_form': perio_tooth_34_form,
                                                                               'perio_tooth_34_notes': perio_tooth_34_notes,
                                                                               'perio_tooth_35_form': perio_tooth_35_form,
                                                                               'perio_tooth_35_notes': perio_tooth_35_notes,
                                                                               'perio_tooth_36_form': perio_tooth_36_form,
                                                                               'perio_tooth_36_notes': perio_tooth_36_notes,
                                                                               'perio_tooth_37_form': perio_tooth_37_form,
                                                                               'perio_tooth_37_notes': perio_tooth_37_notes,
                                                                               'perio_tooth_38_form': perio_tooth_38_form,
                                                                               'perio_tooth_38_notes': perio_tooth_38_notes,
                                                                               'perio_tooth_41_form': perio_tooth_41_form,
                                                                               'perio_tooth_41_notes': perio_tooth_41_notes,
                                                                               'perio_tooth_42_form': perio_tooth_42_form,
                                                                               'perio_tooth_42_notes': perio_tooth_42_notes,
                                                                               'perio_tooth_43_form': perio_tooth_43_form,
                                                                               'perio_tooth_43_notes': perio_tooth_43_notes,
                                                                               'perio_tooth_44_form': perio_tooth_44_form,
                                                                               'perio_tooth_44_notes': perio_tooth_44_notes,
                                                                               'perio_tooth_45_form': perio_tooth_45_form,
                                                                               'perio_tooth_45_notes': perio_tooth_45_notes,
                                                                               'perio_tooth_46_form': perio_tooth_46_form,
                                                                               'perio_tooth_46_notes': perio_tooth_46_notes,
                                                                               'perio_tooth_47_form': perio_tooth_47_form,
                                                                               'perio_tooth_47_notes': perio_tooth_47_notes,
                                                                               'perio_tooth_48_form': perio_tooth_48_form,
                                                                               'perio_tooth_48_notes': perio_tooth_48_notes,
                                                                               'treatments': treatments,
                                                                               'treatment_plan_form': treatment_plan_form,
                                                                               'financial_form': financial_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'treatment_plan_form_list': treatment_plan_form_list,
                                                                               'financial_form_lists': financial_form_lists,
                                                                               'datafiles': datafiles_metadata})

        elif 'save-financial' in request.POST:
            treatment_plan_id = request.POST.get('id')
            transaction = Financial.objects.create(treatment_id=treatment_plan_id)
            treatment_plan = TreatmentPlan.objects.get(id=treatment_plan_id)

            transaction.total_cost = request.POST.get('total_cost')
            transaction.transaction_amount = request.POST.get('transaction_amount')
            transaction.transaction_date = request.POST.get('transaction_date')
            transaction.treatment = treatment_plan

            financial_form = FinancialForm(request.POST, instance=transaction)
            financial_form.save()

            appointments_form_list, treatment_plan_form_list, financial_form_lists = initiate_forms(
                patient_id=patient_id)

            financial_form = FinancialForm()

            treatment_plan_balance = calculate_balance(treatment_id=treatment_plan_id)
            treatment_plan.treatment_plan_balance = treatment_plan_balance
            treatment_plan.save()

            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'odontogram': odontogram,
                                                                               'tooth_11_form': tooth_11_form,
                                                                               'tooth_12_form': tooth_12_form,
                                                                               'tooth_13_form': tooth_13_form,
                                                                               'tooth_14_form': tooth_14_form,
                                                                               'tooth_15_form': tooth_15_form,
                                                                               'tooth_16_form': tooth_16_form,
                                                                               'tooth_17_form': tooth_17_form,
                                                                               'tooth_18_form': tooth_18_form,
                                                                               'tooth_21_form': tooth_21_form,
                                                                               'tooth_22_form': tooth_22_form,
                                                                               'tooth_23_form': tooth_23_form,
                                                                               'tooth_24_form': tooth_24_form,
                                                                               'tooth_25_form': tooth_25_form,
                                                                               'tooth_26_form': tooth_26_form,
                                                                               'tooth_27_form': tooth_27_form,
                                                                               'tooth_28_form': tooth_28_form,
                                                                               'tooth_31_form': tooth_31_form,
                                                                               'tooth_32_form': tooth_32_form,
                                                                               'tooth_33_form': tooth_33_form,
                                                                               'tooth_34_form': tooth_34_form,
                                                                               'tooth_35_form': tooth_35_form,
                                                                               'tooth_36_form': tooth_36_form,
                                                                               'tooth_37_form': tooth_37_form,
                                                                               'tooth_38_form': tooth_38_form,
                                                                               'tooth_41_form': tooth_41_form,
                                                                               'tooth_42_form': tooth_42_form,
                                                                               'tooth_43_form': tooth_43_form,
                                                                               'tooth_44_form': tooth_44_form,
                                                                               'tooth_45_form': tooth_45_form,
                                                                               'tooth_46_form': tooth_46_form,
                                                                               'tooth_47_form': tooth_47_form,
                                                                               'tooth_48_form': tooth_48_form,
                                                                               'periodontogram': periodontogram,
                                                                               'perio_tooth_11_form': perio_tooth_11_form,
                                                                               'perio_tooth_11_notes': perio_tooth_11_notes,
                                                                               'perio_tooth_12_form': perio_tooth_12_form,
                                                                               'perio_tooth_12_notes': perio_tooth_12_notes,
                                                                               'perio_tooth_13_form': perio_tooth_13_form,
                                                                               'perio_tooth_13_notes': perio_tooth_13_notes,
                                                                               'perio_tooth_14_form': perio_tooth_14_form,
                                                                               'perio_tooth_14_notes': perio_tooth_14_notes,
                                                                               'perio_tooth_15_form': perio_tooth_15_form,
                                                                               'perio_tooth_15_notes': perio_tooth_15_notes,
                                                                               'perio_tooth_16_form': perio_tooth_16_form,
                                                                               'perio_tooth_16_notes': perio_tooth_16_notes,
                                                                               'perio_tooth_17_form': perio_tooth_17_form,
                                                                               'perio_tooth_17_notes': perio_tooth_17_notes,
                                                                               'perio_tooth_18_form': perio_tooth_18_form,
                                                                               'perio_tooth_18_notes': perio_tooth_18_notes,
                                                                               'perio_tooth_21_form': perio_tooth_21_form,
                                                                               'perio_tooth_21_notes': perio_tooth_21_notes,
                                                                               'perio_tooth_22_form': perio_tooth_22_form,
                                                                               'perio_tooth_22_notes': perio_tooth_22_notes,
                                                                               'perio_tooth_23_form': perio_tooth_23_form,
                                                                               'perio_tooth_23_notes': perio_tooth_23_notes,
                                                                               'perio_tooth_24_form': perio_tooth_24_form,
                                                                               'perio_tooth_24_notes': perio_tooth_24_notes,
                                                                               'perio_tooth_25_form': perio_tooth_25_form,
                                                                               'perio_tooth_25_notes': perio_tooth_25_notes,
                                                                               'perio_tooth_26_form': perio_tooth_26_form,
                                                                               'perio_tooth_26_notes': perio_tooth_26_notes,
                                                                               'perio_tooth_27_form': perio_tooth_27_form,
                                                                               'perio_tooth_27_notes': perio_tooth_27_notes,
                                                                               'perio_tooth_28_form': perio_tooth_28_form,
                                                                               'perio_tooth_28_notes': perio_tooth_28_notes,
                                                                               'perio_tooth_31_form': perio_tooth_31_form,
                                                                               'perio_tooth_31_notes': perio_tooth_31_notes,
                                                                               'perio_tooth_32_form': perio_tooth_32_form,
                                                                               'perio_tooth_32_notes': perio_tooth_32_notes,
                                                                               'perio_tooth_33_form': perio_tooth_33_form,
                                                                               'perio_tooth_33_notes': perio_tooth_33_notes,
                                                                               'perio_tooth_34_form': perio_tooth_34_form,
                                                                               'perio_tooth_34_notes': perio_tooth_34_notes,
                                                                               'perio_tooth_35_form': perio_tooth_35_form,
                                                                               'perio_tooth_35_notes': perio_tooth_35_notes,
                                                                               'perio_tooth_36_form': perio_tooth_36_form,
                                                                               'perio_tooth_36_notes': perio_tooth_36_notes,
                                                                               'perio_tooth_37_form': perio_tooth_37_form,
                                                                               'perio_tooth_37_notes': perio_tooth_37_notes,
                                                                               'perio_tooth_38_form': perio_tooth_38_form,
                                                                               'perio_tooth_38_notes': perio_tooth_38_notes,
                                                                               'perio_tooth_41_form': perio_tooth_41_form,
                                                                               'perio_tooth_41_notes': perio_tooth_41_notes,
                                                                               'perio_tooth_42_form': perio_tooth_42_form,
                                                                               'perio_tooth_42_notes': perio_tooth_42_notes,
                                                                               'perio_tooth_43_form': perio_tooth_43_form,
                                                                               'perio_tooth_43_notes': perio_tooth_43_notes,
                                                                               'perio_tooth_44_form': perio_tooth_44_form,
                                                                               'perio_tooth_44_notes': perio_tooth_44_notes,
                                                                               'perio_tooth_45_form': perio_tooth_45_form,
                                                                               'perio_tooth_45_notes': perio_tooth_45_notes,
                                                                               'perio_tooth_46_form': perio_tooth_46_form,
                                                                               'perio_tooth_46_notes': perio_tooth_46_notes,
                                                                               'perio_tooth_47_form': perio_tooth_47_form,
                                                                               'perio_tooth_47_notes': perio_tooth_47_notes,
                                                                               'perio_tooth_48_form': perio_tooth_48_form,
                                                                               'perio_tooth_48_notes': perio_tooth_48_notes,
                                                                               'treatments': treatments,
                                                                               'treatment_plan_form': treatment_plan_form,
                                                                               'financial_form': financial_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'treatment_plan_form_list': treatment_plan_form_list,
                                                                               'financial_form_lists': financial_form_lists,
                                                                               'datafiles': datafiles_metadata})

        elif 'save-odontogram-top-view' in request.POST:
            if 'tooth_11' in request.POST:
                tooth_11_form = Tooth11Form(request.POST, instance=odontogram)
                tooth_11_form.save()
            elif 'tooth_12' in request.POST:
                tooth_12_form = Tooth12Form(request.POST, instance=odontogram)
                tooth_12_form.save()
            elif 'tooth_13' in request.POST:
                tooth_13_form = Tooth13Form(request.POST, instance=odontogram)
                tooth_13_form.save()
            elif 'tooth_14' in request.POST:
                tooth_14_form = Tooth14Form(request.POST, instance=odontogram)
                tooth_14_form.save()
            elif 'tooth_15' in request.POST:
                tooth_15_form = Tooth15Form(request.POST, instance=odontogram)
                tooth_15_form.save()
            elif 'tooth_16' in request.POST:
                tooth_16_form = Tooth16Form(request.POST, instance=odontogram)
                tooth_16_form.save()
            elif 'tooth_17' in request.POST:
                tooth_17_form = Tooth17Form(request.POST, instance=odontogram)
                tooth_17_form.save()
            elif 'tooth_18' in request.POST:
                tooth_18_form = Tooth18Form(request.POST, instance=odontogram)
                tooth_18_form.save()
            elif 'tooth_21' in request.POST:
                tooth_21_form = Tooth21Form(request.POST, instance=odontogram)
                tooth_21_form.save()
            elif 'tooth_22' in request.POST:
                tooth_22_form = Tooth22Form(request.POST, instance=odontogram)
                tooth_22_form.save()
            elif 'tooth_23' in request.POST:
                tooth_23_form = Tooth23Form(request.POST, instance=odontogram)
                tooth_23_form.save()
            elif 'tooth_24' in request.POST:
                tooth_24_form = Tooth24Form(request.POST, instance=odontogram)
                tooth_24_form.save()
            elif 'tooth_25' in request.POST:
                tooth_25_form = Tooth25Form(request.POST, instance=odontogram)
                tooth_25_form.save()
            elif 'tooth_26' in request.POST:
                tooth_26_form = Tooth26Form(request.POST, instance=odontogram)
                tooth_26_form.save()
            elif 'tooth_27' in request.POST:
                tooth_27_form = Tooth27Form(request.POST, instance=odontogram)
                tooth_27_form.save()
            elif 'tooth_28' in request.POST:
                tooth_28_form = Tooth28Form(request.POST, instance=odontogram)
                tooth_28_form.save()
            elif 'tooth_31' in request.POST:
                tooth_31_form = Tooth31Form(request.POST, instance=odontogram)
                tooth_31_form.save()
            elif 'tooth_32' in request.POST:
                tooth_32_form = Tooth32Form(request.POST, instance=odontogram)
                tooth_32_form.save()
            elif 'tooth_33' in request.POST:
                tooth_33_form = Tooth33Form(request.POST, instance=odontogram)
                tooth_33_form.save()
            elif 'tooth_34' in request.POST:
                tooth_34_form = Tooth34Form(request.POST, instance=odontogram)
                tooth_34_form.save()
            elif 'tooth_35' in request.POST:
                tooth_35_form = Tooth35Form(request.POST, instance=odontogram)
                tooth_35_form.save()
            elif 'tooth_36' in request.POST:
                tooth_36_form = Tooth36Form(request.POST, instance=odontogram)
                tooth_36_form.save()
            elif 'tooth_37' in request.POST:
                tooth_37_form = Tooth37Form(request.POST, instance=odontogram)
                tooth_37_form.save()
            elif 'tooth_38' in request.POST:
                tooth_38_form = Tooth38Form(request.POST, instance=odontogram)
                tooth_38_form.save()
            elif 'tooth_41' in request.POST:
                tooth_41_form = Tooth41Form(request.POST, instance=odontogram)
                tooth_41_form.save()
            elif 'tooth_42' in request.POST:
                tooth_42_form = Tooth42Form(request.POST, instance=odontogram)
                tooth_42_form.save()
            elif 'tooth_43' in request.POST:
                tooth_43_form = Tooth43Form(request.POST, instance=odontogram)
                tooth_43_form.save()
            elif 'tooth_44' in request.POST:
                tooth_44_form = Tooth44Form(request.POST, instance=odontogram)
                tooth_44_form.save()
            elif 'tooth_45' in request.POST:
                tooth_45_form = Tooth45Form(request.POST, instance=odontogram)
                tooth_45_form.save()
            elif 'tooth_46' in request.POST:
                tooth_46_form = Tooth46Form(request.POST, instance=odontogram)
                tooth_46_form.save()
            elif 'tooth_47' in request.POST:
                tooth_47_form = Tooth47Form(request.POST, instance=odontogram)
                tooth_47_form.save()
            elif 'tooth_48' in request.POST:
                tooth_48_form = Tooth48Form(request.POST, instance=odontogram)
                tooth_48_form.save()

            odontogram.save()

            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'odontogram': odontogram,
                                                                               'tooth_11_form': tooth_11_form,
                                                                               'tooth_12_form': tooth_12_form,
                                                                               'tooth_13_form': tooth_13_form,
                                                                               'tooth_14_form': tooth_14_form,
                                                                               'tooth_15_form': tooth_15_form,
                                                                               'tooth_16_form': tooth_16_form,
                                                                               'tooth_17_form': tooth_17_form,
                                                                               'tooth_18_form': tooth_18_form,
                                                                               'tooth_21_form': tooth_21_form,
                                                                               'tooth_22_form': tooth_22_form,
                                                                               'tooth_23_form': tooth_23_form,
                                                                               'tooth_24_form': tooth_24_form,
                                                                               'tooth_25_form': tooth_25_form,
                                                                               'tooth_26_form': tooth_26_form,
                                                                               'tooth_27_form': tooth_27_form,
                                                                               'tooth_28_form': tooth_28_form,
                                                                               'tooth_31_form': tooth_31_form,
                                                                               'tooth_32_form': tooth_32_form,
                                                                               'tooth_33_form': tooth_33_form,
                                                                               'tooth_34_form': tooth_34_form,
                                                                               'tooth_35_form': tooth_35_form,
                                                                               'tooth_36_form': tooth_36_form,
                                                                               'tooth_37_form': tooth_37_form,
                                                                               'tooth_38_form': tooth_38_form,
                                                                               'tooth_41_form': tooth_41_form,
                                                                               'tooth_42_form': tooth_42_form,
                                                                               'tooth_43_form': tooth_43_form,
                                                                               'tooth_44_form': tooth_44_form,
                                                                               'tooth_45_form': tooth_45_form,
                                                                               'tooth_46_form': tooth_46_form,
                                                                               'tooth_47_form': tooth_47_form,
                                                                               'tooth_48_form': tooth_48_form,
                                                                               'periodontogram': periodontogram,
                                                                               'perio_tooth_11_form': perio_tooth_11_form,
                                                                               'perio_tooth_11_notes': perio_tooth_11_notes,
                                                                               'perio_tooth_12_form': perio_tooth_12_form,
                                                                               'perio_tooth_12_notes': perio_tooth_12_notes,
                                                                               'perio_tooth_13_form': perio_tooth_13_form,
                                                                               'perio_tooth_13_notes': perio_tooth_13_notes,
                                                                               'perio_tooth_14_form': perio_tooth_14_form,
                                                                               'perio_tooth_14_notes': perio_tooth_14_notes,
                                                                               'perio_tooth_15_form': perio_tooth_15_form,
                                                                               'perio_tooth_15_notes': perio_tooth_15_notes,
                                                                               'perio_tooth_16_form': perio_tooth_16_form,
                                                                               'perio_tooth_16_notes': perio_tooth_16_notes,
                                                                               'perio_tooth_17_form': perio_tooth_17_form,
                                                                               'perio_tooth_17_notes': perio_tooth_17_notes,
                                                                               'perio_tooth_18_form': perio_tooth_18_form,
                                                                               'perio_tooth_18_notes': perio_tooth_18_notes,
                                                                               'perio_tooth_21_form': perio_tooth_21_form,
                                                                               'perio_tooth_21_notes': perio_tooth_21_notes,
                                                                               'perio_tooth_22_form': perio_tooth_22_form,
                                                                               'perio_tooth_22_notes': perio_tooth_22_notes,
                                                                               'perio_tooth_23_form': perio_tooth_23_form,
                                                                               'perio_tooth_23_notes': perio_tooth_23_notes,
                                                                               'perio_tooth_24_form': perio_tooth_24_form,
                                                                               'perio_tooth_24_notes': perio_tooth_24_notes,
                                                                               'perio_tooth_25_form': perio_tooth_25_form,
                                                                               'perio_tooth_25_notes': perio_tooth_25_notes,
                                                                               'perio_tooth_26_form': perio_tooth_26_form,
                                                                               'perio_tooth_26_notes': perio_tooth_26_notes,
                                                                               'perio_tooth_27_form': perio_tooth_27_form,
                                                                               'perio_tooth_27_notes': perio_tooth_27_notes,
                                                                               'perio_tooth_28_form': perio_tooth_28_form,
                                                                               'perio_tooth_28_notes': perio_tooth_28_notes,
                                                                               'perio_tooth_31_form': perio_tooth_31_form,
                                                                               'perio_tooth_31_notes': perio_tooth_31_notes,
                                                                               'perio_tooth_32_form': perio_tooth_32_form,
                                                                               'perio_tooth_32_notes': perio_tooth_32_notes,
                                                                               'perio_tooth_33_form': perio_tooth_33_form,
                                                                               'perio_tooth_33_notes': perio_tooth_33_notes,
                                                                               'perio_tooth_34_form': perio_tooth_34_form,
                                                                               'perio_tooth_34_notes': perio_tooth_34_notes,
                                                                               'perio_tooth_35_form': perio_tooth_35_form,
                                                                               'perio_tooth_35_notes': perio_tooth_35_notes,
                                                                               'perio_tooth_36_form': perio_tooth_36_form,
                                                                               'perio_tooth_36_notes': perio_tooth_36_notes,
                                                                               'perio_tooth_37_form': perio_tooth_37_form,
                                                                               'perio_tooth_37_notes': perio_tooth_37_notes,
                                                                               'perio_tooth_38_form': perio_tooth_38_form,
                                                                               'perio_tooth_38_notes': perio_tooth_38_notes,
                                                                               'perio_tooth_41_form': perio_tooth_41_form,
                                                                               'perio_tooth_41_notes': perio_tooth_41_notes,
                                                                               'perio_tooth_42_form': perio_tooth_42_form,
                                                                               'perio_tooth_42_notes': perio_tooth_42_notes,
                                                                               'perio_tooth_43_form': perio_tooth_43_form,
                                                                               'perio_tooth_43_notes': perio_tooth_43_notes,
                                                                               'perio_tooth_44_form': perio_tooth_44_form,
                                                                               'perio_tooth_44_notes': perio_tooth_44_notes,
                                                                               'perio_tooth_45_form': perio_tooth_45_form,
                                                                               'perio_tooth_45_notes': perio_tooth_45_notes,
                                                                               'perio_tooth_46_form': perio_tooth_46_form,
                                                                               'perio_tooth_46_notes': perio_tooth_46_notes,
                                                                               'perio_tooth_47_form': perio_tooth_47_form,
                                                                               'perio_tooth_47_notes': perio_tooth_47_notes,
                                                                               'perio_tooth_48_form': perio_tooth_48_form,
                                                                               'perio_tooth_48_notes': perio_tooth_48_notes,
                                                                               'treatments': treatments,
                                                                               'treatment_plan_form': treatment_plan_form,
                                                                               'financial_form': financial_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'treatment_plan_form_list': treatment_plan_form_list,
                                                                               'financial_form_lists': financial_form_lists,
                                                                               'datafiles': datafiles_metadata})

        elif 'save-periodontogram' in request.POST:
            if 'perio_tooth_11' in request.POST:
                periodontogram.perio_tooth_11 = request.POST.getlist('perio_tooth_11')
                perio_tooth_11_notes = periodontogram.perio_tooth_11[1]
            elif 'perio_tooth_12' in request.POST:
                periodontogram.perio_tooth_12 = request.POST.getlist('perio_tooth_12')
                perio_tooth_12_notes = periodontogram.perio_tooth_12[1]
            elif 'perio_tooth_13' in request.POST:
                periodontogram.perio_tooth_13 = request.POST.getlist('perio_tooth_13')
                perio_tooth_13_notes = periodontogram.perio_tooth_13[1]
            elif 'perio_tooth_14' in request.POST:
                periodontogram.perio_tooth_14 = request.POST.getlist('perio_tooth_14')
                perio_tooth_14_notes = periodontogram.perio_tooth_14[1]
            elif 'perio_tooth_15' in request.POST:
                periodontogram.perio_tooth_15 = request.POST.getlist('perio_tooth_15')
                perio_tooth_15_notes = periodontogram.perio_tooth_15[1]
            elif 'perio_tooth_16' in request.POST:
                periodontogram.perio_tooth_16 = request.POST.getlist('perio_tooth_16')
                perio_tooth_16_notes = periodontogram.perio_tooth_16[1]
            elif 'perio_tooth_17' in request.POST:
                periodontogram.perio_tooth_17 = request.POST.getlist('perio_tooth_17')
                perio_tooth_17_notes = periodontogram.perio_tooth_17[1]
            elif 'perio_tooth_18' in request.POST:
                periodontogram.perio_tooth_18 = request.POST.getlist('perio_tooth_18')
                perio_tooth_18_notes = periodontogram.perio_tooth_18[1]
            elif 'perio_tooth_21' in request.POST:
                periodontogram.perio_tooth_21 = request.POST.getlist('perio_tooth_21')
                perio_tooth_21_notes = periodontogram.perio_tooth_21[1]
            elif 'perio_tooth_22' in request.POST:
                periodontogram.perio_tooth_22 = request.POST.getlist('perio_tooth_22')
                perio_tooth_22_notes = periodontogram.perio_tooth_22[1]
            elif 'perio_tooth_23' in request.POST:
                periodontogram.perio_tooth_23 = request.POST.getlist('perio_tooth_23')
                perio_tooth_23_notes = periodontogram.perio_tooth_23[1]
            elif 'perio_tooth_24' in request.POST:
                periodontogram.perio_tooth_24 = request.POST.getlist('perio_tooth_24')
                perio_tooth_24_notes = periodontogram.perio_tooth_24[1]
            elif 'perio_tooth_25' in request.POST:
                periodontogram.perio_tooth_25 = request.POST.getlist('perio_tooth_25')
                perio_tooth_25_notes = periodontogram.perio_tooth_25[1]
            elif 'perio_tooth_26' in request.POST:
                periodontogram.perio_tooth_26 = request.POST.getlist('perio_tooth_26')
                perio_tooth_26_notes = periodontogram.perio_tooth_26[1]
            elif 'perio_tooth_27' in request.POST:
                periodontogram.perio_tooth_27 = request.POST.getlist('perio_tooth_27')
                perio_tooth_27_notes = periodontogram.perio_tooth_27[1]
            elif 'perio_tooth_28' in request.POST:
                periodontogram.perio_tooth_28 = request.POST.getlist('perio_tooth_28')
                perio_tooth_28_notes = periodontogram.perio_tooth_28[1]
            elif 'perio_tooth_31' in request.POST:
                periodontogram.perio_tooth_31 = request.POST.getlist('perio_tooth_31')
                perio_tooth_31_notes = periodontogram.perio_tooth_31[1]
            elif 'perio_tooth_32' in request.POST:
                periodontogram.perio_tooth_32 = request.POST.getlist('perio_tooth_32')
                perio_tooth_32_notes = periodontogram.perio_tooth_32[1]
            elif 'perio_tooth_33' in request.POST:
                periodontogram.perio_tooth_33 = request.POST.getlist('perio_tooth_33')
                perio_tooth_33_notes = periodontogram.perio_tooth_33[1]
            elif 'perio_tooth_34' in request.POST:
                periodontogram.perio_tooth_34 = request.POST.getlist('perio_tooth_34')
                perio_tooth_34_notes = periodontogram.perio_tooth_34[1]
            elif 'perio_tooth_35' in request.POST:
                periodontogram.perio_tooth_35 = request.POST.getlist('perio_tooth_35')
                perio_tooth_35_notes = periodontogram.perio_tooth_35[1]
            elif 'perio_tooth_36' in request.POST:
                periodontogram.perio_tooth_36 = request.POST.getlist('perio_tooth_36')
                perio_tooth_36_notes = periodontogram.perio_tooth_36[1]
            elif 'perio_tooth_37' in request.POST:
                periodontogram.perio_tooth_37 = request.POST.getlist('perio_tooth_37')
                perio_tooth_37_notes = periodontogram.perio_tooth_37[1]
            elif 'perio_tooth_38' in request.POST:
                periodontogram.perio_tooth_38 = request.POST.getlist('perio_tooth_38')
                perio_tooth_38_notes = periodontogram.perio_tooth_38[1]
            elif 'perio_tooth_41' in request.POST:
                periodontogram.perio_tooth_41 = request.POST.getlist('perio_tooth_41')
                perio_tooth_41_notes = periodontogram.perio_tooth_41[1]
            elif 'perio_tooth_42' in request.POST:
                periodontogram.perio_tooth_42 = request.POST.getlist('perio_tooth_42')
                perio_tooth_42_notes = periodontogram.perio_tooth_42[1]
            elif 'perio_tooth_43' in request.POST:
                periodontogram.perio_tooth_43 = request.POST.getlist('perio_tooth_43')
                perio_tooth_43_notes = periodontogram.perio_tooth_43[1]
            elif 'perio_tooth_44' in request.POST:
                periodontogram.perio_tooth_44 = request.POST.getlist('perio_tooth_44')
                perio_tooth_44_notes = periodontogram.perio_tooth_44[1]
            elif 'perio_tooth_45' in request.POST:
                periodontogram.perio_tooth_45 = request.POST.getlist('perio_tooth_45')
                perio_tooth_45_notes = periodontogram.perio_tooth_45[1]
            elif 'perio_tooth_46' in request.POST:
                periodontogram.perio_tooth_46 = request.POST.getlist('perio_tooth_46')
                perio_tooth_46_notes = periodontogram.perio_tooth_46[1]
            elif 'perio_tooth_47' in request.POST:
                periodontogram.perio_tooth_47 = request.POST.getlist('perio_tooth_47')
                perio_tooth_47_notes = periodontogram.perio_tooth_47[1]
            elif 'perio_tooth_48' in request.POST:
                periodontogram.perio_tooth_48 = request.POST.getlist('perio_tooth_48')
                perio_tooth_48_notes = periodontogram.perio_tooth_48[1]
            periodontogram.save()

            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'odontogram': odontogram,
                                                                               'tooth_11_form': tooth_11_form,
                                                                               'tooth_12_form': tooth_12_form,
                                                                               'tooth_13_form': tooth_13_form,
                                                                               'tooth_14_form': tooth_14_form,
                                                                               'tooth_15_form': tooth_15_form,
                                                                               'tooth_16_form': tooth_16_form,
                                                                               'tooth_17_form': tooth_17_form,
                                                                               'tooth_18_form': tooth_18_form,
                                                                               'tooth_21_form': tooth_21_form,
                                                                               'tooth_22_form': tooth_22_form,
                                                                               'tooth_23_form': tooth_23_form,
                                                                               'tooth_24_form': tooth_24_form,
                                                                               'tooth_25_form': tooth_25_form,
                                                                               'tooth_26_form': tooth_26_form,
                                                                               'tooth_27_form': tooth_27_form,
                                                                               'tooth_28_form': tooth_28_form,
                                                                               'tooth_31_form': tooth_31_form,
                                                                               'tooth_32_form': tooth_32_form,
                                                                               'tooth_33_form': tooth_33_form,
                                                                               'tooth_34_form': tooth_34_form,
                                                                               'tooth_35_form': tooth_35_form,
                                                                               'tooth_36_form': tooth_36_form,
                                                                               'tooth_37_form': tooth_37_form,
                                                                               'tooth_38_form': tooth_38_form,
                                                                               'tooth_41_form': tooth_41_form,
                                                                               'tooth_42_form': tooth_42_form,
                                                                               'tooth_43_form': tooth_43_form,
                                                                               'tooth_44_form': tooth_44_form,
                                                                               'tooth_45_form': tooth_45_form,
                                                                               'tooth_46_form': tooth_46_form,
                                                                               'tooth_47_form': tooth_47_form,
                                                                               'tooth_48_form': tooth_48_form,
                                                                               'periodontogram': periodontogram,
                                                                               'perio_tooth_11_form': perio_tooth_11_form,
                                                                               'perio_tooth_11_notes': perio_tooth_11_notes,
                                                                               'perio_tooth_12_form': perio_tooth_12_form,
                                                                               'perio_tooth_12_notes': perio_tooth_12_notes,
                                                                               'perio_tooth_13_form': perio_tooth_13_form,
                                                                               'perio_tooth_13_notes': perio_tooth_13_notes,
                                                                               'perio_tooth_14_form': perio_tooth_14_form,
                                                                               'perio_tooth_14_notes': perio_tooth_14_notes,
                                                                               'perio_tooth_15_form': perio_tooth_15_form,
                                                                               'perio_tooth_15_notes': perio_tooth_15_notes,
                                                                               'perio_tooth_16_form': perio_tooth_16_form,
                                                                               'perio_tooth_16_notes': perio_tooth_16_notes,
                                                                               'perio_tooth_17_form': perio_tooth_17_form,
                                                                               'perio_tooth_17_notes': perio_tooth_17_notes,
                                                                               'perio_tooth_18_form': perio_tooth_18_form,
                                                                               'perio_tooth_18_notes': perio_tooth_18_notes,
                                                                               'perio_tooth_21_form': perio_tooth_21_form,
                                                                               'perio_tooth_21_notes': perio_tooth_21_notes,
                                                                               'perio_tooth_22_form': perio_tooth_22_form,
                                                                               'perio_tooth_22_notes': perio_tooth_22_notes,
                                                                               'perio_tooth_23_form': perio_tooth_23_form,
                                                                               'perio_tooth_23_notes': perio_tooth_23_notes,
                                                                               'perio_tooth_24_form': perio_tooth_24_form,
                                                                               'perio_tooth_24_notes': perio_tooth_24_notes,
                                                                               'perio_tooth_25_form': perio_tooth_25_form,
                                                                               'perio_tooth_25_notes': perio_tooth_25_notes,
                                                                               'perio_tooth_26_form': perio_tooth_26_form,
                                                                               'perio_tooth_26_notes': perio_tooth_26_notes,
                                                                               'perio_tooth_27_form': perio_tooth_27_form,
                                                                               'perio_tooth_27_notes': perio_tooth_27_notes,
                                                                               'perio_tooth_28_form': perio_tooth_28_form,
                                                                               'perio_tooth_28_notes': perio_tooth_28_notes,
                                                                               'perio_tooth_31_form': perio_tooth_31_form,
                                                                               'perio_tooth_31_notes': perio_tooth_31_notes,
                                                                               'perio_tooth_32_form': perio_tooth_32_form,
                                                                               'perio_tooth_32_notes': perio_tooth_32_notes,
                                                                               'perio_tooth_33_form': perio_tooth_33_form,
                                                                               'perio_tooth_33_notes': perio_tooth_33_notes,
                                                                               'perio_tooth_34_form': perio_tooth_34_form,
                                                                               'perio_tooth_34_notes': perio_tooth_34_notes,
                                                                               'perio_tooth_35_form': perio_tooth_35_form,
                                                                               'perio_tooth_35_notes': perio_tooth_35_notes,
                                                                               'perio_tooth_36_form': perio_tooth_36_form,
                                                                               'perio_tooth_36_notes': perio_tooth_36_notes,
                                                                               'perio_tooth_37_form': perio_tooth_37_form,
                                                                               'perio_tooth_37_notes': perio_tooth_37_notes,
                                                                               'perio_tooth_38_form': perio_tooth_38_form,
                                                                               'perio_tooth_38_notes': perio_tooth_38_notes,
                                                                               'perio_tooth_41_form': perio_tooth_41_form,
                                                                               'perio_tooth_41_notes': perio_tooth_41_notes,
                                                                               'perio_tooth_42_form': perio_tooth_42_form,
                                                                               'perio_tooth_42_notes': perio_tooth_42_notes,
                                                                               'perio_tooth_43_form': perio_tooth_43_form,
                                                                               'perio_tooth_43_notes': perio_tooth_43_notes,
                                                                               'perio_tooth_44_form': perio_tooth_44_form,
                                                                               'perio_tooth_44_notes': perio_tooth_44_notes,
                                                                               'perio_tooth_45_form': perio_tooth_45_form,
                                                                               'perio_tooth_45_notes': perio_tooth_45_notes,
                                                                               'perio_tooth_46_form': perio_tooth_46_form,
                                                                               'perio_tooth_46_notes': perio_tooth_46_notes,
                                                                               'perio_tooth_47_form': perio_tooth_47_form,
                                                                               'perio_tooth_47_notes': perio_tooth_47_notes,
                                                                               'perio_tooth_48_form': perio_tooth_48_form,
                                                                               'perio_tooth_48_notes': perio_tooth_48_notes,
                                                                               'treatments': treatments,
                                                                               'treatment_plan_form': treatment_plan_form,
                                                                               'financial_form': financial_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'treatment_plan_form_list': treatment_plan_form_list,
                                                                               'financial_form_lists': financial_form_lists,
                                                                               'datafiles': datafiles_metadata})

        elif 'clear-periodontogram-modal-data' in request.POST:
            if 'perio_tooth_11' in request.POST:
                periodontogram.perio_tooth_11 = None
                perio_tooth_11_notes = ''
            elif 'perio_tooth_12' in request.POST:
                periodontogram.perio_tooth_12 = None
                perio_tooth_12_notes = ''
            elif 'perio_tooth_13' in request.POST:
                periodontogram.perio_tooth_13 = None
                perio_tooth_13_notes = ''
            elif 'perio_tooth_14' in request.POST:
                periodontogram.perio_tooth_14 = None
                perio_tooth_14_notes = ''
            elif 'perio_tooth_15' in request.POST:
                periodontogram.perio_tooth_15 = None
                perio_tooth_15_notes = ''
            elif 'perio_tooth_16' in request.POST:
                periodontogram.perio_tooth_16 = None
                perio_tooth_16_notes = ''
            elif 'perio_tooth_17' in request.POST:
                periodontogram.perio_tooth_17 = None
                perio_tooth_17_notes = ''
            elif 'perio_tooth_18' in request.POST:
                periodontogram.perio_tooth_18 = None
                perio_tooth_18_notes = ''
            elif 'perio_tooth_21' in request.POST:
                periodontogram.perio_tooth_21 = None
                perio_tooth_21_notes = ''
            elif 'perio_tooth_22' in request.POST:
                periodontogram.perio_tooth_22 = None
                perio_tooth_22_notes = ''
            elif 'perio_tooth_23' in request.POST:
                periodontogram.perio_tooth_23 = None
                perio_tooth_23_notes = ''
            elif 'perio_tooth_24' in request.POST:
                periodontogram.perio_tooth_24 = None
                perio_tooth_24_notes = ''
            elif 'perio_tooth_25' in request.POST:
                periodontogram.perio_tooth_25 = None
                perio_tooth_25_notes = ''
            elif 'perio_tooth_26' in request.POST:
                periodontogram.perio_tooth_26 = None
                perio_tooth_26_notes = ''
            elif 'perio_tooth_27' in request.POST:
                periodontogram.perio_tooth_27 = None
                perio_tooth_27_notes = ''
            elif 'perio_tooth_28' in request.POST:
                periodontogram.perio_tooth_28 = None
                perio_tooth_28_notes = ''
            elif 'perio_tooth_31' in request.POST:
                periodontogram.perio_tooth_31 = None
                perio_tooth_31_notes = ''
            elif 'perio_tooth_32' in request.POST:
                periodontogram.perio_tooth_32 = None
                perio_tooth_32_notes = ''
            elif 'perio_tooth_33' in request.POST:
                periodontogram.perio_tooth_33 = None
                perio_tooth_33_notes = ''
            elif 'perio_tooth_34' in request.POST:
                periodontogram.perio_tooth_34 = None
                perio_tooth_34_notes = ''
            elif 'perio_tooth_35' in request.POST:
                periodontogram.perio_tooth_35 = None
                perio_tooth_35_notes = ''
            elif 'perio_tooth_36' in request.POST:
                periodontogram.perio_tooth_36 = None
                perio_tooth_36_notes = ''
            elif 'perio_tooth_37' in request.POST:
                periodontogram.perio_tooth_37 = None
                perio_tooth_37_notes = ''
            elif 'perio_tooth_38' in request.POST:
                periodontogram.perio_tooth_38 = None
                perio_tooth_38_notes = ''
            elif 'perio_tooth_41' in request.POST:
                periodontogram.perio_tooth_41 = None
                perio_tooth_41_notes = ''
            elif 'perio_tooth_42' in request.POST:
                periodontogram.perio_tooth_42 = None
                perio_tooth_42_notes = ''
            elif 'perio_tooth_43' in request.POST:
                periodontogram.perio_tooth_43 = None
                perio_tooth_43_notes = ''
            elif 'perio_tooth_44' in request.POST:
                periodontogram.perio_tooth_44 = None
                perio_tooth_44_notes = ''
            elif 'perio_tooth_45' in request.POST:
                periodontogram.perio_tooth_45 = None
                perio_tooth_45_notes = ''
            elif 'perio_tooth_46' in request.POST:
                periodontogram.perio_tooth_46 = None
                perio_tooth_46_notes = ''
            elif 'perio_tooth_47' in request.POST:
                periodontogram.perio_tooth_47 = None
                perio_tooth_47_notes = ''
            elif 'perio_tooth_48' in request.POST:
                periodontogram.perio_tooth_48 = None
                perio_tooth_48_notes = ''
            periodontogram.save()

            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'odontogram': odontogram,
                                                                               'tooth_11_form': tooth_11_form,
                                                                               'tooth_12_form': tooth_12_form,
                                                                               'tooth_13_form': tooth_13_form,
                                                                               'tooth_14_form': tooth_14_form,
                                                                               'tooth_15_form': tooth_15_form,
                                                                               'tooth_16_form': tooth_16_form,
                                                                               'tooth_17_form': tooth_17_form,
                                                                               'tooth_18_form': tooth_18_form,
                                                                               'tooth_21_form': tooth_21_form,
                                                                               'tooth_22_form': tooth_22_form,
                                                                               'tooth_23_form': tooth_23_form,
                                                                               'tooth_24_form': tooth_24_form,
                                                                               'tooth_25_form': tooth_25_form,
                                                                               'tooth_26_form': tooth_26_form,
                                                                               'tooth_27_form': tooth_27_form,
                                                                               'tooth_28_form': tooth_28_form,
                                                                               'tooth_31_form': tooth_31_form,
                                                                               'tooth_32_form': tooth_32_form,
                                                                               'tooth_33_form': tooth_33_form,
                                                                               'tooth_34_form': tooth_34_form,
                                                                               'tooth_35_form': tooth_35_form,
                                                                               'tooth_36_form': tooth_36_form,
                                                                               'tooth_37_form': tooth_37_form,
                                                                               'tooth_38_form': tooth_38_form,
                                                                               'tooth_41_form': tooth_41_form,
                                                                               'tooth_42_form': tooth_42_form,
                                                                               'tooth_43_form': tooth_43_form,
                                                                               'tooth_44_form': tooth_44_form,
                                                                               'tooth_45_form': tooth_45_form,
                                                                               'tooth_46_form': tooth_46_form,
                                                                               'tooth_47_form': tooth_47_form,
                                                                               'tooth_48_form': tooth_48_form,
                                                                               'periodontogram': periodontogram,
                                                                               'perio_tooth_11_form': perio_tooth_11_form,
                                                                               'perio_tooth_11_notes': perio_tooth_11_notes,
                                                                               'perio_tooth_12_form': perio_tooth_12_form,
                                                                               'perio_tooth_12_notes': perio_tooth_12_notes,
                                                                               'perio_tooth_13_form': perio_tooth_13_form,
                                                                               'perio_tooth_13_notes': perio_tooth_13_notes,
                                                                               'perio_tooth_14_form': perio_tooth_14_form,
                                                                               'perio_tooth_14_notes': perio_tooth_14_notes,
                                                                               'perio_tooth_15_form': perio_tooth_15_form,
                                                                               'perio_tooth_15_notes': perio_tooth_15_notes,
                                                                               'perio_tooth_16_form': perio_tooth_16_form,
                                                                               'perio_tooth_16_notes': perio_tooth_16_notes,
                                                                               'perio_tooth_17_form': perio_tooth_17_form,
                                                                               'perio_tooth_17_notes': perio_tooth_17_notes,
                                                                               'perio_tooth_18_form': perio_tooth_18_form,
                                                                               'perio_tooth_18_notes': perio_tooth_18_notes,
                                                                               'perio_tooth_21_form': perio_tooth_21_form,
                                                                               'perio_tooth_21_notes': perio_tooth_21_notes,
                                                                               'perio_tooth_22_form': perio_tooth_22_form,
                                                                               'perio_tooth_22_notes': perio_tooth_22_notes,
                                                                               'perio_tooth_23_form': perio_tooth_23_form,
                                                                               'perio_tooth_23_notes': perio_tooth_23_notes,
                                                                               'perio_tooth_24_form': perio_tooth_24_form,
                                                                               'perio_tooth_24_notes': perio_tooth_24_notes,
                                                                               'perio_tooth_25_form': perio_tooth_25_form,
                                                                               'perio_tooth_25_notes': perio_tooth_25_notes,
                                                                               'perio_tooth_26_form': perio_tooth_26_form,
                                                                               'perio_tooth_26_notes': perio_tooth_26_notes,
                                                                               'perio_tooth_27_form': perio_tooth_27_form,
                                                                               'perio_tooth_27_notes': perio_tooth_27_notes,
                                                                               'perio_tooth_28_form': perio_tooth_28_form,
                                                                               'perio_tooth_28_notes': perio_tooth_28_notes,
                                                                               'perio_tooth_31_form': perio_tooth_31_form,
                                                                               'perio_tooth_31_notes': perio_tooth_31_notes,
                                                                               'perio_tooth_32_form': perio_tooth_32_form,
                                                                               'perio_tooth_32_notes': perio_tooth_32_notes,
                                                                               'perio_tooth_33_form': perio_tooth_33_form,
                                                                               'perio_tooth_33_notes': perio_tooth_33_notes,
                                                                               'perio_tooth_34_form': perio_tooth_34_form,
                                                                               'perio_tooth_34_notes': perio_tooth_34_notes,
                                                                               'perio_tooth_35_form': perio_tooth_35_form,
                                                                               'perio_tooth_35_notes': perio_tooth_35_notes,
                                                                               'perio_tooth_36_form': perio_tooth_36_form,
                                                                               'perio_tooth_36_notes': perio_tooth_36_notes,
                                                                               'perio_tooth_37_form': perio_tooth_37_form,
                                                                               'perio_tooth_37_notes': perio_tooth_37_notes,
                                                                               'perio_tooth_38_form': perio_tooth_38_form,
                                                                               'perio_tooth_38_notes': perio_tooth_38_notes,
                                                                               'perio_tooth_41_form': perio_tooth_41_form,
                                                                               'perio_tooth_41_notes': perio_tooth_41_notes,
                                                                               'perio_tooth_42_form': perio_tooth_42_form,
                                                                               'perio_tooth_42_notes': perio_tooth_42_notes,
                                                                               'perio_tooth_43_form': perio_tooth_43_form,
                                                                               'perio_tooth_43_notes': perio_tooth_43_notes,
                                                                               'perio_tooth_44_form': perio_tooth_44_form,
                                                                               'perio_tooth_44_notes': perio_tooth_44_notes,
                                                                               'perio_tooth_45_form': perio_tooth_45_form,
                                                                               'perio_tooth_45_notes': perio_tooth_45_notes,
                                                                               'perio_tooth_46_form': perio_tooth_46_form,
                                                                               'perio_tooth_46_notes': perio_tooth_46_notes,
                                                                               'perio_tooth_47_form': perio_tooth_47_form,
                                                                               'perio_tooth_47_notes': perio_tooth_47_notes,
                                                                               'perio_tooth_48_form': perio_tooth_48_form,
                                                                               'perio_tooth_48_notes': perio_tooth_48_notes,
                                                                               'treatments': treatments,
                                                                               'treatment_plan_form': treatment_plan_form,
                                                                               'financial_form': financial_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'treatment_plan_form_list': treatment_plan_form_list,
                                                                               'financial_form_lists': financial_form_lists,
                                                                               'datafiles': datafiles_metadata})

        elif 'file-upload' in request.POST:
            files = request.FILES.getlist('files')
            for file in files:
                handle_uploaded_file(patient_name=f'{patient_name}_{patient.pk}',
                                     destination_folder=f'{settings.PATIENT_DATA_FOLDER}',
                                     file=file)
                metadata = {'filename': file,
                            'path': f'{patient_name}_{patient.pk}\\{file}',
                            'created': datetime.fromtimestamp(os.stat(os.path.join(path_name, file.name)).st_ctime),
                            'size': round((os.stat(os.path.join(path_name, file.name)).st_size / 1000000), 3)
                            }
                datafiles_metadata.append(metadata)

            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'odontogram': odontogram,
                                                                               'tooth_11_form': tooth_11_form,
                                                                               'tooth_12_form': tooth_12_form,
                                                                               'tooth_13_form': tooth_13_form,
                                                                               'tooth_14_form': tooth_14_form,
                                                                               'tooth_15_form': tooth_15_form,
                                                                               'tooth_16_form': tooth_16_form,
                                                                               'tooth_17_form': tooth_17_form,
                                                                               'tooth_18_form': tooth_18_form,
                                                                               'tooth_21_form': tooth_21_form,
                                                                               'tooth_22_form': tooth_22_form,
                                                                               'tooth_23_form': tooth_23_form,
                                                                               'tooth_24_form': tooth_24_form,
                                                                               'tooth_25_form': tooth_25_form,
                                                                               'tooth_26_form': tooth_26_form,
                                                                               'tooth_27_form': tooth_27_form,
                                                                               'tooth_28_form': tooth_28_form,
                                                                               'tooth_31_form': tooth_31_form,
                                                                               'tooth_32_form': tooth_32_form,
                                                                               'tooth_33_form': tooth_33_form,
                                                                               'tooth_34_form': tooth_34_form,
                                                                               'tooth_35_form': tooth_35_form,
                                                                               'tooth_36_form': tooth_36_form,
                                                                               'tooth_37_form': tooth_37_form,
                                                                               'tooth_38_form': tooth_38_form,
                                                                               'tooth_41_form': tooth_41_form,
                                                                               'tooth_42_form': tooth_42_form,
                                                                               'tooth_43_form': tooth_43_form,
                                                                               'tooth_44_form': tooth_44_form,
                                                                               'tooth_45_form': tooth_45_form,
                                                                               'tooth_46_form': tooth_46_form,
                                                                               'tooth_47_form': tooth_47_form,
                                                                               'tooth_48_form': tooth_48_form,
                                                                               'periodontogram': periodontogram,
                                                                               'perio_tooth_11_form': perio_tooth_11_form,
                                                                               'perio_tooth_11_notes': perio_tooth_11_notes,
                                                                               'perio_tooth_12_form': perio_tooth_12_form,
                                                                               'perio_tooth_12_notes': perio_tooth_12_notes,
                                                                               'perio_tooth_13_form': perio_tooth_13_form,
                                                                               'perio_tooth_13_notes': perio_tooth_13_notes,
                                                                               'perio_tooth_14_form': perio_tooth_14_form,
                                                                               'perio_tooth_14_notes': perio_tooth_14_notes,
                                                                               'perio_tooth_15_form': perio_tooth_15_form,
                                                                               'perio_tooth_15_notes': perio_tooth_15_notes,
                                                                               'perio_tooth_16_form': perio_tooth_16_form,
                                                                               'perio_tooth_16_notes': perio_tooth_16_notes,
                                                                               'perio_tooth_17_form': perio_tooth_17_form,
                                                                               'perio_tooth_17_notes': perio_tooth_17_notes,
                                                                               'perio_tooth_18_form': perio_tooth_18_form,
                                                                               'perio_tooth_18_notes': perio_tooth_18_notes,
                                                                               'perio_tooth_21_form': perio_tooth_21_form,
                                                                               'perio_tooth_21_notes': perio_tooth_21_notes,
                                                                               'perio_tooth_22_form': perio_tooth_22_form,
                                                                               'perio_tooth_22_notes': perio_tooth_22_notes,
                                                                               'perio_tooth_23_form': perio_tooth_23_form,
                                                                               'perio_tooth_23_notes': perio_tooth_23_notes,
                                                                               'perio_tooth_24_form': perio_tooth_24_form,
                                                                               'perio_tooth_24_notes': perio_tooth_24_notes,
                                                                               'perio_tooth_25_form': perio_tooth_25_form,
                                                                               'perio_tooth_25_notes': perio_tooth_25_notes,
                                                                               'perio_tooth_26_form': perio_tooth_26_form,
                                                                               'perio_tooth_26_notes': perio_tooth_26_notes,
                                                                               'perio_tooth_27_form': perio_tooth_27_form,
                                                                               'perio_tooth_27_notes': perio_tooth_27_notes,
                                                                               'perio_tooth_28_form': perio_tooth_28_form,
                                                                               'perio_tooth_28_notes': perio_tooth_28_notes,
                                                                               'perio_tooth_31_form': perio_tooth_31_form,
                                                                               'perio_tooth_31_notes': perio_tooth_31_notes,
                                                                               'perio_tooth_32_form': perio_tooth_32_form,
                                                                               'perio_tooth_32_notes': perio_tooth_32_notes,
                                                                               'perio_tooth_33_form': perio_tooth_33_form,
                                                                               'perio_tooth_33_notes': perio_tooth_33_notes,
                                                                               'perio_tooth_34_form': perio_tooth_34_form,
                                                                               'perio_tooth_34_notes': perio_tooth_34_notes,
                                                                               'perio_tooth_35_form': perio_tooth_35_form,
                                                                               'perio_tooth_35_notes': perio_tooth_35_notes,
                                                                               'perio_tooth_36_form': perio_tooth_36_form,
                                                                               'perio_tooth_36_notes': perio_tooth_36_notes,
                                                                               'perio_tooth_37_form': perio_tooth_37_form,
                                                                               'perio_tooth_37_notes': perio_tooth_37_notes,
                                                                               'perio_tooth_38_form': perio_tooth_38_form,
                                                                               'perio_tooth_38_notes': perio_tooth_38_notes,
                                                                               'perio_tooth_41_form': perio_tooth_41_form,
                                                                               'perio_tooth_41_notes': perio_tooth_41_notes,
                                                                               'perio_tooth_42_form': perio_tooth_42_form,
                                                                               'perio_tooth_42_notes': perio_tooth_42_notes,
                                                                               'perio_tooth_43_form': perio_tooth_43_form,
                                                                               'perio_tooth_43_notes': perio_tooth_43_notes,
                                                                               'perio_tooth_44_form': perio_tooth_44_form,
                                                                               'perio_tooth_44_notes': perio_tooth_44_notes,
                                                                               'perio_tooth_45_form': perio_tooth_45_form,
                                                                               'perio_tooth_45_notes': perio_tooth_45_notes,
                                                                               'perio_tooth_46_form': perio_tooth_46_form,
                                                                               'perio_tooth_46_notes': perio_tooth_46_notes,
                                                                               'perio_tooth_47_form': perio_tooth_47_form,
                                                                               'perio_tooth_47_notes': perio_tooth_47_notes,
                                                                               'perio_tooth_48_form': perio_tooth_48_form,
                                                                               'perio_tooth_48_notes': perio_tooth_48_notes,
                                                                               'treatments': treatments,
                                                                               'treatment_plan_form': treatment_plan_form,
                                                                               'financial_form': financial_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'treatment_plan_form_list': treatment_plan_form_list,
                                                                               'financial_form_lists': financial_form_lists,
                                                                               'datafiles': datafiles_metadata})

        patient_form = PatientForm(request.POST, instance=patient)

        if patient_form.is_valid():
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')

            if initial_first_name != first_name or initial_last_name != last_name:
                new_patient_name = f'{last_name}_{first_name}'
                new_path_name = data_path / f'{new_patient_name}_{patient.pk}'
                os.rename(path_name, new_path_name)

            patient_form.save()
            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'odontogram': odontogram,
                                                                               'tooth_11_form': tooth_11_form,
                                                                               'tooth_12_form': tooth_12_form,
                                                                               'tooth_13_form': tooth_13_form,
                                                                               'tooth_14_form': tooth_14_form,
                                                                               'tooth_15_form': tooth_15_form,
                                                                               'tooth_16_form': tooth_16_form,
                                                                               'tooth_17_form': tooth_17_form,
                                                                               'tooth_18_form': tooth_18_form,
                                                                               'tooth_21_form': tooth_21_form,
                                                                               'tooth_22_form': tooth_22_form,
                                                                               'tooth_23_form': tooth_23_form,
                                                                               'tooth_24_form': tooth_24_form,
                                                                               'tooth_25_form': tooth_25_form,
                                                                               'tooth_26_form': tooth_26_form,
                                                                               'tooth_27_form': tooth_27_form,
                                                                               'tooth_28_form': tooth_28_form,
                                                                               'tooth_31_form': tooth_31_form,
                                                                               'tooth_32_form': tooth_32_form,
                                                                               'tooth_33_form': tooth_33_form,
                                                                               'tooth_34_form': tooth_34_form,
                                                                               'tooth_35_form': tooth_35_form,
                                                                               'tooth_36_form': tooth_36_form,
                                                                               'tooth_37_form': tooth_37_form,
                                                                               'tooth_38_form': tooth_38_form,
                                                                               'tooth_41_form': tooth_41_form,
                                                                               'tooth_42_form': tooth_42_form,
                                                                               'tooth_43_form': tooth_43_form,
                                                                               'tooth_44_form': tooth_44_form,
                                                                               'tooth_45_form': tooth_45_form,
                                                                               'tooth_46_form': tooth_46_form,
                                                                               'tooth_47_form': tooth_47_form,
                                                                               'tooth_48_form': tooth_48_form,
                                                                               'periodontogram': periodontogram,
                                                                               'perio_tooth_11_form': perio_tooth_11_form,
                                                                               'perio_tooth_11_notes': perio_tooth_11_notes,
                                                                               'perio_tooth_12_form': perio_tooth_12_form,
                                                                               'perio_tooth_12_notes': perio_tooth_12_notes,
                                                                               'perio_tooth_13_form': perio_tooth_13_form,
                                                                               'perio_tooth_13_notes': perio_tooth_13_notes,
                                                                               'perio_tooth_14_form': perio_tooth_14_form,
                                                                               'perio_tooth_14_notes': perio_tooth_14_notes,
                                                                               'perio_tooth_15_form': perio_tooth_15_form,
                                                                               'perio_tooth_15_notes': perio_tooth_15_notes,
                                                                               'perio_tooth_16_form': perio_tooth_16_form,
                                                                               'perio_tooth_16_notes': perio_tooth_16_notes,
                                                                               'perio_tooth_17_form': perio_tooth_17_form,
                                                                               'perio_tooth_17_notes': perio_tooth_17_notes,
                                                                               'perio_tooth_18_form': perio_tooth_18_form,
                                                                               'perio_tooth_18_notes': perio_tooth_18_notes,
                                                                               'perio_tooth_21_form': perio_tooth_21_form,
                                                                               'perio_tooth_21_notes': perio_tooth_21_notes,
                                                                               'perio_tooth_22_form': perio_tooth_22_form,
                                                                               'perio_tooth_22_notes': perio_tooth_22_notes,
                                                                               'perio_tooth_23_form': perio_tooth_23_form,
                                                                               'perio_tooth_23_notes': perio_tooth_23_notes,
                                                                               'perio_tooth_24_form': perio_tooth_24_form,
                                                                               'perio_tooth_24_notes': perio_tooth_24_notes,
                                                                               'perio_tooth_25_form': perio_tooth_25_form,
                                                                               'perio_tooth_25_notes': perio_tooth_25_notes,
                                                                               'perio_tooth_26_form': perio_tooth_26_form,
                                                                               'perio_tooth_26_notes': perio_tooth_26_notes,
                                                                               'perio_tooth_27_form': perio_tooth_27_form,
                                                                               'perio_tooth_27_notes': perio_tooth_27_notes,
                                                                               'perio_tooth_28_form': perio_tooth_28_form,
                                                                               'perio_tooth_28_notes': perio_tooth_28_notes,
                                                                               'perio_tooth_31_form': perio_tooth_31_form,
                                                                               'perio_tooth_31_notes': perio_tooth_31_notes,
                                                                               'perio_tooth_32_form': perio_tooth_32_form,
                                                                               'perio_tooth_32_notes': perio_tooth_32_notes,
                                                                               'perio_tooth_33_form': perio_tooth_33_form,
                                                                               'perio_tooth_33_notes': perio_tooth_33_notes,
                                                                               'perio_tooth_34_form': perio_tooth_34_form,
                                                                               'perio_tooth_34_notes': perio_tooth_34_notes,
                                                                               'perio_tooth_35_form': perio_tooth_35_form,
                                                                               'perio_tooth_35_notes': perio_tooth_35_notes,
                                                                               'perio_tooth_36_form': perio_tooth_36_form,
                                                                               'perio_tooth_36_notes': perio_tooth_36_notes,
                                                                               'perio_tooth_37_form': perio_tooth_37_form,
                                                                               'perio_tooth_37_notes': perio_tooth_37_notes,
                                                                               'perio_tooth_38_form': perio_tooth_38_form,
                                                                               'perio_tooth_38_notes': perio_tooth_38_notes,
                                                                               'perio_tooth_41_form': perio_tooth_41_form,
                                                                               'perio_tooth_41_notes': perio_tooth_41_notes,
                                                                               'perio_tooth_42_form': perio_tooth_42_form,
                                                                               'perio_tooth_42_notes': perio_tooth_42_notes,
                                                                               'perio_tooth_43_form': perio_tooth_43_form,
                                                                               'perio_tooth_43_notes': perio_tooth_43_notes,
                                                                               'perio_tooth_44_form': perio_tooth_44_form,
                                                                               'perio_tooth_44_notes': perio_tooth_44_notes,
                                                                               'perio_tooth_45_form': perio_tooth_45_form,
                                                                               'perio_tooth_45_notes': perio_tooth_45_notes,
                                                                               'perio_tooth_46_form': perio_tooth_46_form,
                                                                               'perio_tooth_46_notes': perio_tooth_46_notes,
                                                                               'perio_tooth_47_form': perio_tooth_47_form,
                                                                               'perio_tooth_47_notes': perio_tooth_47_notes,
                                                                               'perio_tooth_48_form': perio_tooth_48_form,
                                                                               'perio_tooth_48_notes': perio_tooth_48_notes,
                                                                               'treatments': treatments,
                                                                               'treatment_plan_form': treatment_plan_form,
                                                                               'financial_form': financial_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'treatment_plan_form_list': treatment_plan_form_list,
                                                                               'financial_form_lists': financial_form_lists,
                                                                               'datafiles': datafiles_metadata})

    return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                       'form': patient_form,
                                                                       'medical_form': medical_history_form,
                                                                       'dental_form': dental_history_form,
                                                                       'appointment_form': appointment_form,
                                                                       'odontogram': odontogram,
                                                                       'tooth_11_form': tooth_11_form,
                                                                       'tooth_12_form': tooth_12_form,
                                                                       'tooth_13_form': tooth_13_form,
                                                                       'tooth_14_form': tooth_14_form,
                                                                       'tooth_15_form': tooth_15_form,
                                                                       'tooth_16_form': tooth_16_form,
                                                                       'tooth_17_form': tooth_17_form,
                                                                       'tooth_18_form': tooth_18_form,
                                                                       'tooth_21_form': tooth_21_form,
                                                                       'tooth_22_form': tooth_22_form,
                                                                       'tooth_23_form': tooth_23_form,
                                                                       'tooth_24_form': tooth_24_form,
                                                                       'tooth_25_form': tooth_25_form,
                                                                       'tooth_26_form': tooth_26_form,
                                                                       'tooth_27_form': tooth_27_form,
                                                                       'tooth_28_form': tooth_28_form,
                                                                       'tooth_31_form': tooth_31_form,
                                                                       'tooth_32_form': tooth_32_form,
                                                                       'tooth_33_form': tooth_33_form,
                                                                       'tooth_34_form': tooth_34_form,
                                                                       'tooth_35_form': tooth_35_form,
                                                                       'tooth_36_form': tooth_36_form,
                                                                       'tooth_37_form': tooth_37_form,
                                                                       'tooth_38_form': tooth_38_form,
                                                                       'tooth_41_form': tooth_41_form,
                                                                       'tooth_42_form': tooth_42_form,
                                                                       'tooth_43_form': tooth_43_form,
                                                                       'tooth_44_form': tooth_44_form,
                                                                       'tooth_45_form': tooth_45_form,
                                                                       'tooth_46_form': tooth_46_form,
                                                                       'tooth_47_form': tooth_47_form,
                                                                       'tooth_48_form': tooth_48_form,
                                                                       'periodontogram': periodontogram,
                                                                       'perio_tooth_11_form': perio_tooth_11_form,
                                                                       'perio_tooth_11_notes': perio_tooth_11_notes,
                                                                       'perio_tooth_12_form': perio_tooth_12_form,
                                                                       'perio_tooth_12_notes': perio_tooth_12_notes,
                                                                       'perio_tooth_13_form': perio_tooth_13_form,
                                                                       'perio_tooth_13_notes': perio_tooth_13_notes,
                                                                       'perio_tooth_14_form': perio_tooth_14_form,
                                                                       'perio_tooth_14_notes': perio_tooth_14_notes,
                                                                       'perio_tooth_15_form': perio_tooth_15_form,
                                                                       'perio_tooth_15_notes': perio_tooth_15_notes,
                                                                       'perio_tooth_16_form': perio_tooth_16_form,
                                                                       'perio_tooth_16_notes': perio_tooth_16_notes,
                                                                       'perio_tooth_17_form': perio_tooth_17_form,
                                                                       'perio_tooth_17_notes': perio_tooth_17_notes,
                                                                       'perio_tooth_18_form': perio_tooth_18_form,
                                                                       'perio_tooth_18_notes': perio_tooth_18_notes,
                                                                       'perio_tooth_21_form': perio_tooth_21_form,
                                                                       'perio_tooth_21_notes': perio_tooth_21_notes,
                                                                       'perio_tooth_22_form': perio_tooth_22_form,
                                                                       'perio_tooth_22_notes': perio_tooth_22_notes,
                                                                       'perio_tooth_23_form': perio_tooth_23_form,
                                                                       'perio_tooth_23_notes': perio_tooth_23_notes,
                                                                       'perio_tooth_24_form': perio_tooth_24_form,
                                                                       'perio_tooth_24_notes': perio_tooth_24_notes,
                                                                       'perio_tooth_25_form': perio_tooth_25_form,
                                                                       'perio_tooth_25_notes': perio_tooth_25_notes,
                                                                       'perio_tooth_26_form': perio_tooth_26_form,
                                                                       'perio_tooth_26_notes': perio_tooth_26_notes,
                                                                       'perio_tooth_27_form': perio_tooth_27_form,
                                                                       'perio_tooth_27_notes': perio_tooth_27_notes,
                                                                       'perio_tooth_28_form': perio_tooth_28_form,
                                                                       'perio_tooth_28_notes': perio_tooth_28_notes,
                                                                       'perio_tooth_31_form': perio_tooth_31_form,
                                                                       'perio_tooth_31_notes': perio_tooth_31_notes,
                                                                       'perio_tooth_32_form': perio_tooth_32_form,
                                                                       'perio_tooth_32_notes': perio_tooth_32_notes,
                                                                       'perio_tooth_33_form': perio_tooth_33_form,
                                                                       'perio_tooth_33_notes': perio_tooth_33_notes,
                                                                       'perio_tooth_34_form': perio_tooth_34_form,
                                                                       'perio_tooth_34_notes': perio_tooth_34_notes,
                                                                       'perio_tooth_35_form': perio_tooth_35_form,
                                                                       'perio_tooth_35_notes': perio_tooth_35_notes,
                                                                       'perio_tooth_36_form': perio_tooth_36_form,
                                                                       'perio_tooth_36_notes': perio_tooth_36_notes,
                                                                       'perio_tooth_37_form': perio_tooth_37_form,
                                                                       'perio_tooth_37_notes': perio_tooth_37_notes,
                                                                       'perio_tooth_38_form': perio_tooth_38_form,
                                                                       'perio_tooth_38_notes': perio_tooth_38_notes,
                                                                       'perio_tooth_41_form': perio_tooth_41_form,
                                                                       'perio_tooth_41_notes': perio_tooth_41_notes,
                                                                       'perio_tooth_42_form': perio_tooth_42_form,
                                                                       'perio_tooth_42_notes': perio_tooth_42_notes,
                                                                       'perio_tooth_43_form': perio_tooth_43_form,
                                                                       'perio_tooth_43_notes': perio_tooth_43_notes,
                                                                       'perio_tooth_44_form': perio_tooth_44_form,
                                                                       'perio_tooth_44_notes': perio_tooth_44_notes,
                                                                       'perio_tooth_45_form': perio_tooth_45_form,
                                                                       'perio_tooth_45_notes': perio_tooth_45_notes,
                                                                       'perio_tooth_46_form': perio_tooth_46_form,
                                                                       'perio_tooth_46_notes': perio_tooth_46_notes,
                                                                       'perio_tooth_47_form': perio_tooth_47_form,
                                                                       'perio_tooth_47_notes': perio_tooth_47_notes,
                                                                       'perio_tooth_48_form': perio_tooth_48_form,
                                                                       'perio_tooth_48_notes': perio_tooth_48_notes,
                                                                       'treatments': treatments,
                                                                       'treatment_plan_form': treatment_plan_form,
                                                                       'financial_form': financial_form,
                                                                       'appointments_form_list': appointments_form_list,
                                                                       'treatment_plan_form_list': treatment_plan_form_list,
                                                                       'financial_form_lists': financial_form_lists,
                                                                       'datafiles': datafiles_metadata})


def get_appointments_form_list(patient_id):
    appointments_list = Appointment.objects.filter(patient_id=patient_id).order_by('-appointment_date')
    appointments_form_list = list()

    for appointment in appointments_list:
        appointment_form = AppointmentForm(auto_id=appointment.id, instance=appointment)
        appointments_form_list.append(appointment_form)

    return appointments_form_list


def get_odontogram(patient_id):
    odontogram = Odontogram.objects.get_or_create(patient_id=patient_id)[0]

    treatments = [
        'default', 'black_1', 'black_2', 'black_3', 'black_4', 'black_5', 'brown_1', 'brown_2', 'brown_3', 'brown_4',
        'brown_5', 'yellow_1', 'yellow_2', 'yellow_3', 'yellow_4', 'yellow_5', 'endo_top', 'extracted_top',
        'for_extraction', 'implant_top', 'endo_side', 'extracted_side', 'implant_side'
    ]
    return odontogram, treatments


def get_periodontogram(patient_id):
    periodontogram = Periodontogram.objects.get_or_create(patient_id=patient_id)[0]

    severity = [
        'minor', 'major'
    ]
    return periodontogram, severity


def get_periodontogram_tooth_notes(tooth):
    if tooth is not None:
        return tooth.strip("][").split(', ')[1].strip("'")
    else:
        return ''


def get_treatment_plan_form_list(patient_id):
    treatment_plan_list = TreatmentPlan.objects.filter(patient_id=patient_id).order_by('-treatment_plan_start_date')
    treatment_plan_form_list = list()

    for treatment_plan in treatment_plan_list:
        treatment_plan_form = TreatmentPlanForm(auto_id=treatment_plan.id, instance=treatment_plan)
        treatment_plan_form_list.append(treatment_plan_form)
        # calculate_balance(treatment_plan.id)

    return treatment_plan_form_list


def calculate_balance(treatment_id):
    treatment_plan = TreatmentPlan.objects.get(id=treatment_id)
    transaction_list = Financial.objects.filter(treatment_id=treatment_id)
    amount_paid = 0

    for transaction in transaction_list:
        amount_paid += transaction.transaction_amount
    treatment_plan.treatment_plan_balance = treatment_plan.total_cost - amount_paid
    treatment_plan.save()
    return treatment_plan.total_cost - amount_paid


def get_financial_form_list(treatment_id):
    financial_transaction_list = Financial.objects.filter(treatment_id=treatment_id).order_by('-transaction_date')
    financial_form_list = list()

    for financial_transaction in financial_transaction_list:
        financial_form = FinancialForm(auto_id=financial_transaction.id, instance=financial_transaction)
        financial_form_list.append(financial_form)

    return financial_form_list


def handle_uploaded_file(patient_name, destination_folder, file):
    with open(f'{destination_folder}\\{patient_name}\\{file}', "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def initiate_forms(patient_id):
    treatment_ids = list()
    financial_form_lists = dict()
    try:
        treatments = TreatmentPlan.objects.filter(patient_id=patient_id)
        for treatment in treatments:
            treatment_ids.append(treatment.id)
            treatment.treatment_plan_balance = calculate_balance(treatment_id=treatment.id)
        for treatment_id in treatment_ids:
            financial_form_list = get_financial_form_list(treatment_id=treatment_id)
            financial_form_lists[treatment_id] = financial_form_list
    except Exception as err:
        print(str(err))

    appointments_form_list = get_appointments_form_list(patient_id=patient_id)
    treatment_plan_form_list = get_treatment_plan_form_list(patient_id=patient_id)

    return appointments_form_list, treatment_plan_form_list, financial_form_lists


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def backup_data(request):
    print(f'[INFO] Data backup in progress...')
    # Check if the temp folder exists
    temp_folder = os.path.join(settings.BASE_DIR, 'temp')
    if not os.path.isdir(temp_folder):
        os.mkdir(temp_folder)
    # Remove previously created files, only the most recent one is stored on the server
    if os.listdir(temp_folder):
        for files in os.listdir(temp_folder):
            path = os.path.join(temp_folder, files)
            try:
                shutil.rmtree(path)
            except OSError:
                os.remove(path)
    # Create a zip file containing the sqlite database file
    # plus the patient data files, using datetime in the name
    now = dt.now().strftime("%Y%m%d_%H%M%S")
    fp_zip = os.path.join(settings.BASE_DIR, temp_folder, f'backup_{now}.zip')
    directory_to_archive = Path(settings.BASE_DIR / 'patient_management/static/patient_data')

    with zipfile.ZipFile(fp_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for fp in directory_to_archive.glob('**/*'):
            zipf.write(fp, arcname=fp.relative_to(directory_to_archive))

    print(f'[INFO] Data backup completed successfully')

    return FileResponse(open(fp_zip, 'rb'), as_attachment=True)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def restore_data(request):
    if 'restore' in request.POST:
        uploaded_file = request.FILES['file']
        if not uploaded_file.name.endswith('.zip'):
            print(f'[INFO] The file must be in ZIP format')
            print(f'[INFO] Please select a ZIP file')
            return render(request,
                          'patient_management/main.html',
                          {'message': 'The file must be in ZIP format. Please select a ZIP file'})
        else:
            print(f'[INFO] Restoring data...')
            extract_directory = Path(settings.BASE_DIR / 'patient_management/static')
            file_to_extract = os.path.join(extract_directory, uploaded_file.name)
            with open(file_to_extract, 'wb') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            zipfile.ZipFile(file_to_extract).extractall(os.path.join(extract_directory, 'patient_data'))
            os.remove(file_to_extract)
            print(f'[INFO] Data restored successfully')
            return render(request,
                          'patient_management/main.html',
                          {'message': 'Data restored successfully'})
    return redirect('main')


def copy_file(source_path, destination_path):
    shutil.copy2(source_path, destination_path)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout_user(request):
    logout(request)
    return redirect('login')
