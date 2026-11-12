import django.db
from django.db import models


#Задание 2.1
class Bus(models.Model):
    name = models.TextField(max_length=20)
    mest = models.IntegerField()
    objects = models.Manager()
    DoesNotExist = models.Manager()