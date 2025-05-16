from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.exceptions import ValidationError


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
    number = models.CharField(max_length=255, unique=True)

    # IRL we also count volume of the baggage (e.g. not longer than 200cm) but I want to simplify for now
    max_checked_baggage_mass = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Passengers may bring one item of hand luggage. "
                  "Checked baggage exceeding max checked baggage mass will incur an additional charge."
    )
    min_checked_baggage_mass = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="If mass of checked baggage is less - customer shouldn't pay for it"
    )
    train_type = models.ForeignKey(
        TrainType,
        on_delete=models.CASCADE,
        related_name="trains"
    )

    def clean(self):
        if self.max_checked_baggage_mass <= self.min_checked_baggage_mass:
            raise ValidationError("Prohibited baggage mass can't be less than or equal to minimum baggage mass.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.number} ({self.train_type})"


class Route(models.Model):
    source = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="routes_from")
    destination = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="routes_to")
    # transit_stations = ...
    distance = models.PositiveIntegerField(help_text="distance in kilometers")

    def clean(self):
        if self.destination == self.source:
            raise ValidationError("Source and destination must be different.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.source} => {self.destination}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["source", "destination"], name="unique_route")
        ]


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
    checked_baggage_charge = models.BooleanField(
        default=False,
        help_text="Customer should pay extra fee if checked baggage exceeds min checked baggage mass."
    )
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

    def clean(self):
        if self.departure_time <= self.arrival_time:
            raise ValidationError("Arrival time must be after departure time.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.route} [{self.departure_time} - {self.arrival_time}]"
