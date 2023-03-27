from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from pymongo import MongoClient
from django.db.models import Q

from .forms import PatientForm, MedicalHistoryForm, DentalHistoryForm, AppointmentForm
from .models import Patient, MedicalHistory, DentalHistory, Appointment


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
            form = PatientForm(request.POST)
            self.context['form'] = form
            form.save()
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

    if request.method == 'POST':
        if 'delete' in request.POST:
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
                                                                               'appointments_form_list': appointments_form_list})

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
                                                                               'appointments_form_list': appointments_form_list})

        if 'save-dental' in request.POST:
            dental_history.patient = patient
            dental_history_form = DentalHistoryForm(request.POST, instance=dental_history)
            dental_history_form.save()
            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'appointments_form_list': appointments_form_list})

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
                                                                               'appointments_form_list': appointments_form_list})

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
                                                                               'appointments_form_list': appointments_form_list})

        if 'edit-appointment' in request.POST:
            appointment_id = request.POST.get('id')
            edited_appointment = Appointment.objects.get(id=appointment_id)
            edited_appointment.notes = request.POST.get('notes')
            edited_appointment.save()
            appointment_form = AppointmentForm()

            appointments_form_list = get_appointments_form_list(patient_id=patient_id)

            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'appointments_form_list': appointments_form_list})

        patient_form = PatientForm(request.POST, instance=patient)

        if patient_form.is_valid():
            patient_form.save()
            return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                               'form': patient_form,
                                                                               'medical_form': medical_history_form,
                                                                               'dental_form': dental_history_form,
                                                                               'appointment_form': appointment_form,
                                                                               'appointments_form_list': appointments_form_list})

    return render(request, 'patient_management/patient-details.html', {'patient': patient,
                                                                       'form': patient_form,
                                                                       'medical_form': medical_history_form,
                                                                       'dental_form': dental_history_form,
                                                                       'appointment_form': appointment_form,
                                                                       'appointments_form_list': appointments_form_list})


def get_appointments_form_list(patient_id):
    appointments_list = Appointment.objects.filter(patient_id=patient_id).order_by('-appointment_date')
    appointments_form_list = list()

    for appointment in appointments_list:
        appointment_form = AppointmentForm(auto_id=appointment.id, instance=appointment)
        appointments_form_list.append(appointment_form)

    return appointments_form_list
