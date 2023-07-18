from django.urls import path

from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('add-patient/', views.AddPatientFormView.as_view(), name='add-patient'),
    path('patient-details/<int:patient_id>', views.edit_patient, name='patient-details'),
    path('delete-financial/<int:financial_form_id>', views.delete_financial, name='delete-financial'),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('backup/', views.backup_data, name='backup')
]
