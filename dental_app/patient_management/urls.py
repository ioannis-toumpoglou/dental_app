from django.urls import path, include

from . import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('main/', views.main, name='main'),
    path('add-patient/', views.AddPatientFormView.as_view(), name='add-patient'),
    path('patient-details/<int:patient_id>', views.edit_patient, name='patient-details'),
    path('delete-financial/<int:financial_form_id>', views.delete_financial, name='delete-financial'),
    path('calendar/', views.calendar_data, name='calendar'),
    path('backup/', views.backup_data, name='backup'),
    path('', views.logout_user, name='logout')
]
