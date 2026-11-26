from django.db import models

# Таблица 1: Автобус
class Bus(models.Model):
    name = models.CharField(max_length=50)
    mest = models.IntegerField()

    def __str__(self):
        return self.name

# Таблица 2: Техпаспорт (связь 1 к 1)
class BusPassport(models.Model):
    bus = models.OneToOneField(Bus, on_delete=models.CASCADE, primary_key=True, related_name='passport')
    serial_number = models.CharField(max_length=30)
    issue_date = models.DateField()

    def __str__(self):
        return f"Паспорт {self.serial_number} ({self.bus.name})"