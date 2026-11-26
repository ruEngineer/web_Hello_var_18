from django.db import models

# Create your models here.
from django.db import models

# Таблица 1: Пассажир
class Passenger(models.Model):
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.full_name

# Таблица 2: Рейс
class Trip(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()

    def __str__(self):
        return self.name

# Таблица 3: Билет (Промежуточная таблица)
class Ticket(models.Model):
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    seat = models.IntegerField()

    def __str__(self):
        return f"Билет {self.id}: {self.passenger.full_name} на {self.trip.name}"