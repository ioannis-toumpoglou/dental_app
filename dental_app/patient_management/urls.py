from django.urls import path

from . import views

urlpatterns = [
    path('main/', views.main, name='main'),
    path('add-patient/', views.AddPatientFormView.as_view(), name='add-patient')
]
