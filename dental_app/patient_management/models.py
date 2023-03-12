from django.db import models

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
