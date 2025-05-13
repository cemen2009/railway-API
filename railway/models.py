from django.contrib.auth import get_user_model
from django.db import models


class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class TrainType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=255, unique=True)
    places_for_cargo = models.PositiveIntegerField()
    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE, related_name="trains")

    def __str__(self):
        return f"{self.name} ({self.train_type})"


class Route(models.Model):
    source = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="routes_from")
    destination = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="routes_to")
    # transit_stations = ...
    distance = models.PositiveIntegerField(help_text="distance in kilometers")

    def __str__(self):
        return f"{self.source} => {self.destination}"


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="orders")

    def __str__(self):
        return f"Order of {self.user}"


class Ticket(models.Model):
    cargo = models.PositiveIntegerField(default=0, help_text="one cargo unit is 10 kg (9kg - 1 unit, 10kg - 1 unit, 11kg - 2 units)")
    seat = models.PositiveIntegerField(default=1)
    journey = models.ForeignKey("Journey", on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    def __str__(self):
        return f"{self.journey} (seats: {self.seat})"


class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="journeys")
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="journeys")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="journeys")

    def __str__(self):
        return f"{self.route} [{self.departure_time} - {self.arrival_time}]"
