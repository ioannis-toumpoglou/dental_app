import calendar
import os
from datetime import datetime, date, timedelta
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from django.views import generic
from django.views.generic.edit import FormView
from pymongo import MongoClient
from django.db.models import Q
from pathlib import Path
from os import listdir
from os.path import isfile, join
import shutil
from django.conf import settings

from .forms import PatientForm, MedicalHistoryForm, DentalHistoryForm, AppointmentForm
from .models import Patient, MedicalHistory, DentalHistory, Appointment, AppointmentCalendar


# Create your views here.

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


def edit_patient(request, patient_id):
    patient = Patient.objects.filter(pk=patient_id).first()
    patient_form = PatientForm(instance=patient)

    medical_history = MedicalHistory.objects.filter(patient=patient_id).first()

    if medical_history is None:
        medical_history = MedicalHistory.objects.create(patient_id=patient_id)
    medical_history_form = MedicalHistoryForm(instance=medical_history)

    dental_history = DentalHistory.objects.filter(patient=patient_id).first()

    if dental_history is None:
        dental_history = DentalHistory.objects.create(patient_id=patient_id)
    dental_history_form = DentalHistoryForm(instance=dental_history)

    appointments_form_list = get_appointments_form_list(patient_id=patient_id)

    context = {}
    appointment_form = AppointmentForm(request.POST)
    context['appointment_form'] = appointment_form

    data_path = Path(settings.PATIENT_DATA_FOLDER)
    patient_last_name = patient.last_name
    patient_first_name = patient.first_name
    patient_name = f'{patient_last_name}_{patient_first_name}'
    path_name = data_path / f'{patient_name}_{patient.pk}'

    datafiles = [f for f in listdir(path_name) if isfile(join(path_name, f))]
    datafiles_metadata = []

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

        if 'save-medical' in request.POST:
            medical_history.patient = patient
            medical_history_form = MedicalHistoryForm(request.POST, instance=medical_history)
            medical_history_form.save()
            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'datafiles': datafiles_metadata})

        if 'clear-medical' in request.POST:
            medical_history = MedicalHistory.objects.get(patient_id=patient_id)
            medical_history.delete()
            medical_history = MedicalHistory.objects.create(patient_id=patient_id)
            medical_history_form = MedicalHistoryForm(instance=medical_history)
            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'datafiles': datafiles_metadata})

        if 'save-dental' in request.POST:
            dental_history.patient = patient
            dental_history_form = DentalHistoryForm(request.POST, instance=dental_history)
            dental_history_form.save()
            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'datafiles': datafiles_metadata})

        if 'clear-dental' in request.POST:
            dental_history = DentalHistory.objects.get(patient_id=patient_id)
            dental_history.delete()
            dental_history = DentalHistory.objects.create(patient_id=patient_id)
            dental_history_form = DentalHistoryForm(instance=dental_history)
            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'datafiles': datafiles_metadata})

        if 'save-appointment' in request.POST:
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
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'datafiles': datafiles_metadata})

        if 'edit-appointment' in request.POST:
            appointment_id = request.POST.get('id')
            edited_appointment = Appointment.objects.get(id=appointment_id)
            edited_appointment.appointment_time = request.POST.get('appointment_time')
            edited_appointment.notes = request.POST.get('notes')
            edited_appointment.save()
            appointment_form = AppointmentForm()

            appointments_form_list = get_appointments_form_list(patient_id=patient_id) \
                if len(get_appointments_form_list(patient_id=patient_id)) > 0 else None

            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'datafiles': datafiles_metadata})

        if 'delete-appointment' in request.POST:
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
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'datafiles': datafiles_metadata})

        if 'file-upload' in request.POST:
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
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'datafiles': datafiles_metadata})

        patient_form = PatientForm(request.POST, instance=patient)

        if patient_form.is_valid():
            patient_form.save()
            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'appointments_form_list': appointments_form_list,
                                                                               'datafiles': datafiles_metadata})

    return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                       'form': patient_form,
                                                                       'medical_form': medical_history_form,
                                                                       'dental_form': dental_history_form,
                                                                       'appointment_form': appointment_form,
                                                                       'appointments_form_list': appointments_form_list,
                                                                       'datafiles': datafiles_metadata})


def get_appointments_form_list(patient_id):
    appointments_list = Appointment.objects.filter(patient_id=patient_id).order_by('-appointment_date')
    appointments_form_list = list()

    for appointment in appointments_list:
        appointment_form = AppointmentForm(auto_id=appointment.id, instance=appointment)
        appointments_form_list.append(appointment_form)

    return appointments_form_list


def handle_uploaded_file(patient_name, destination_folder, file):
    with open(f'{destination_folder}\\{patient_name}\\{file}', "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)


class CalendarView(generic.ListView):
    model = Appointment
    template_name = 'patient_management/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = AppointmentCalendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    the_prev_month = first - timedelta(days=1)
    month = 'month=' + str(the_prev_month.year) + '-' + str(the_prev_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    the_next_month = last + timedelta(days=1)
    month = 'month=' + str(the_next_month.year) + '-' + str(the_next_month.month)
    return month
