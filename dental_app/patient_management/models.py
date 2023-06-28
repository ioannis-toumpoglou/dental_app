from django.db import models
from calendar import HTMLCalendar
from django.urls import reverse


# Create your models here.

class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=100, blank=True)
    mobile_phone = models.CharField(max_length=100)
    amka = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=500, null=True, blank=True)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.full_name()


class MedicalHistory(models.Model):
    aids = models.BooleanField(default=False)
    anemia = models.BooleanField(default=False)
    arthritis = models.BooleanField(default=False)
    artificial_joint = models.BooleanField(default=False)
    asthma = models.BooleanField(default=False)
    blood_disease = models.BooleanField(default=False)
    breathing_problem = models.BooleanField(default=False)
    cancer = models.BooleanField(default=False)
    chemotherapy = models.BooleanField(default=False)
    cortisone_medicine = models.BooleanField(default=False)
    diabetes = models.BooleanField(default=False)
    excessive_bleeding = models.BooleanField(default=False)
    hepatitis_A = models.BooleanField(default=False)
    hepatitis_B_or_C = models.BooleanField(default=False)
    hemophilia = models.BooleanField(default=False)
    high_blood_pressure = models.BooleanField(default=False)
    high_cholesterol = models.BooleanField(default=False)
    low_blood_pressure = models.BooleanField(default=False)
    osteoporosis = models.BooleanField(default=False)
    pain_in_jaw_joints = models.BooleanField(default=False)
    parathyroid_disease = models.BooleanField(default=False)
    radiation_treatments = models.BooleanField(default=False)
    rheumatoid_arthritis = models.BooleanField(default=False)
    thyroid_disease = models.BooleanField(default=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)


class DentalHistory(models.Model):
    complications_past_treatment = models.BooleanField(default=False)
    reactions_anesthesia = models.BooleanField(default=False)
    teeth_removed = models.BooleanField(default=False)
    orthodontic_treatment = models.BooleanField(default=False)
    gums_bleed = models.BooleanField(default=False)
    gum_disease = models.BooleanField(default=False)
    bone_loss_around_teeth = models.BooleanField(default=False)
    mouth_unpleasant_taste_smell = models.BooleanField(default=False)
    family_history_periodontal_gum_disease = models.BooleanField(default=False)
    gum_recession = models.BooleanField(default=False)
    teeth_become_loose = models.BooleanField(default=False)
    cavities_past_three_years = models.BooleanField(default=False)
    teeth_sensitive_to_hot_cold = models.BooleanField(default=False)
    food_caught_between_teeth = models.BooleanField(default=False)
    ever_broken_chipped_cracked_any_teeth = models.BooleanField(default=False)
    problems_with_jaw_joint = models.BooleanField(default=False)
    teeth_changed_in_last_five_years = models.BooleanField(default=False)
    clench_teeth_during_day_night = models.BooleanField(default=False)
    wear_or_worn_bite_appliance = models.BooleanField(default=False)
    ever_whitened_bleached_teeth = models.BooleanField(default=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)


class TreatmentPlan(models.Model):
    treatment_plan_description = models.CharField(max_length=500, null=False)
    treatment_plan_start_date = models.DateField(null=True)
    treatment_plan_end_date = models.DateField(null=True, blank=True)
    treatment_plan_notes = models.CharField(max_length=500, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)


class Appointment(models.Model):
    appointment_date = models.DateField(null=True)
    appointment_time = models.TimeField(null=True)
    appointment_header = models.CharField(max_length=500, null=False, blank=True)
    notes = models.CharField(max_length=500, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    @property
    def get_html_url(self):
        url = reverse('patient-details', args=(self.patient.id,))
        return f'<a href="{url}"> {self.patient} </a>'


class AppointmentCalendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(AppointmentCalendar, self).__init__()

    def formatday(self, day, events):
        events_per_day = events.filter(appointment_date__day=day)
        d = ''
        for event in events_per_day:
            if event.appointment_time is not None:
                event.appointment_time = event.appointment_time.strftime("%H:%M")
            else:
                event.appointment_time = ''
            d += f'<li> {event.appointment_time} {event.get_html_url} {event.appointment_header} </li>'

        if day != 0:
            return f"<td><span class='date'>{day}</span><ol id='calendar-appointment-list'> {d} </ol></td>"

        return '<td></td>'

    def formatweek(self, theweek, events):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, events)
        return f'<tr> {week} </tr>'

    def formatmonth(self, withyear=True):
        events = Appointment.objects.filter(appointment_date__year=self.year, appointment_date__month=self.month)

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, events)}\n'
        return cal
