from django.db import models

class Route(models.Model):
    number = models.CharField(max_length=10)
    from_city = models.CharField(max_length=50)
    to_city = models.CharField(max_length=50)
    price = models.IntegerField()

    def __str__(self):
        return f"{self.number}: {self.from_city} — {self.to_city}"

class Trip(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    departure_time = models.CharField(max_length=50)
    bus_name = models.CharField(max_length=50)

    def __str__(self):
        return f"Рейс {self.route.number} в {self.departure_time}"