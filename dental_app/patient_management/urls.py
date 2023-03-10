from django.urls import path

from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('add-patient/', views.AddPatientFormView.as_view(), name='add-patient'),
    path('patient-details/<int:patient_id>', views.edit_patient, name='patient-details')
]
