from django.contrib import admin

from .models import Patient


# Register your models here.

class PatientAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'address', 'email', 'phone', 'mobile_phone', 'amka', 'date_of_birth')


admin.site.register(Patient, PatientAdmin)
