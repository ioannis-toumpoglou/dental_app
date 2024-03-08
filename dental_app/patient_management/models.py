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
    notes = models.CharField(max_length=5000, null=True, blank=True)

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
    notes = models.CharField(max_length=5000, null=True, blank=True)
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
    notes = models.CharField(max_length=5000, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)


class TreatmentPlan(models.Model):
    treatment_plan_description = models.CharField(max_length=500, blank=False)
    treatment_plan_start_date = models.DateField(blank=True, null=True)
    treatment_plan_end_date = models.DateField(blank=True, null=True)
    treatment_plan_notes = models.CharField(max_length=5000, blank=True, null=True)
    total_cost = models.FloatField(default=0.0, blank=True, null=True)
    treatment_plan_balance = models.FloatField(default=0.0, blank=True, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)


class Odontogram(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    tooth_11 = models.CharField(max_length=200, default=None, null=True)
    tooth_12 = models.CharField(max_length=200, default=None, null=True)
    tooth_13 = models.CharField(max_length=200, default=None, null=True)
    tooth_14 = models.CharField(max_length=200, default=None, null=True)
    tooth_15 = models.CharField(max_length=200, default=None, null=True)
    tooth_16 = models.CharField(max_length=200, default=None, null=True)
    tooth_17 = models.CharField(max_length=200, default=None, null=True)
    tooth_18 = models.CharField(max_length=200, default=None, null=True)

    tooth_21 = models.CharField(max_length=200, default=None, null=True)
    tooth_22 = models.CharField(max_length=200, default=None, null=True)
    tooth_23 = models.CharField(max_length=200, default=None, null=True)
    tooth_24 = models.CharField(max_length=200, default=None, null=True)
    tooth_25 = models.CharField(max_length=200, default=None, null=True)
    tooth_26 = models.CharField(max_length=200, default=None, null=True)
    tooth_27 = models.CharField(max_length=200, default=None, null=True)
    tooth_28 = models.CharField(max_length=200, default=None, null=True)

    tooth_31 = models.CharField(max_length=200, default=None, null=True)
    tooth_32 = models.CharField(max_length=200, default=None, null=True)
    tooth_33 = models.CharField(max_length=200, default=None, null=True)
    tooth_34 = models.CharField(max_length=200, default=None, null=True)
    tooth_35 = models.CharField(max_length=200, default=None, null=True)
    tooth_36 = models.CharField(max_length=200, default=None, null=True)
    tooth_37 = models.CharField(max_length=200, default=None, null=True)
    tooth_38 = models.CharField(max_length=200, default=None, null=True)

    tooth_41 = models.CharField(max_length=200, default=None, null=True)
    tooth_42 = models.CharField(max_length=200, default=None, null=True)
    tooth_43 = models.CharField(max_length=200, default=None, null=True)
    tooth_44 = models.CharField(max_length=200, default=None, null=True)
    tooth_45 = models.CharField(max_length=200, default=None, null=True)
    tooth_46 = models.CharField(max_length=200, default=None, null=True)
    tooth_47 = models.CharField(max_length=200, default=None, null=True)
    tooth_48 = models.CharField(max_length=200, default=None, null=True)


class Periodontogram(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    perio_tooth_11 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_12 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_13 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_14 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_15 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_16 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_17 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_18 = models.CharField(max_length=500, default=None, null=True)

    perio_tooth_21 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_22 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_23 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_24 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_25 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_26 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_27 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_28 = models.CharField(max_length=500, default=None, null=True)

    perio_tooth_31 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_32 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_33 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_34 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_35 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_36 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_37 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_38 = models.CharField(max_length=500, default=None, null=True)

    perio_tooth_41 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_42 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_43 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_44 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_45 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_46 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_47 = models.CharField(max_length=500, default=None, null=True)
    perio_tooth_48 = models.CharField(max_length=500, default=None, null=True)


class Financial(models.Model):
    transaction_amount = models.FloatField(null=True)
    transaction_date = models.DateField(null=True)
    treatment = models.ForeignKey(TreatmentPlan, on_delete=models.CASCADE)


class Appointment(models.Model):
    appointment_date = models.DateField(null=True)
    appointment_start_time = models.TimeField(null=True)
    appointment_end_time = models.TimeField(null=True, blank=True)
    appointment_header = models.CharField(max_length=500, null=False, blank=True)
    notes = models.CharField(max_length=5000, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
