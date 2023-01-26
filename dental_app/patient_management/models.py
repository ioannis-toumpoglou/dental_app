from django.db import models

# Create your models here.

class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    email_address = models.EmailField()
    phone = models.CharField(max_length=100)
    cell_phone = models.CharField(max_length=100)
    amka = models.CharField(max_length=100)
    date_of_birth = models.DateField()

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.full_name()
