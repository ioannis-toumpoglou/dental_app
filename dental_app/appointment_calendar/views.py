from django.shortcuts import render
from django.views.decorators.cache import cache_control

from patient_management.models import Appointment


# Create your views here.

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def calendar_data(request):
    appointment_list = Appointment.objects.all()
    return render(request,
                  'patient_management/calendar.html',
                  {'appointment_list': appointment_list})
