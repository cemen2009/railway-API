from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.utils.timezone import now, timedelta

from railway.models import (
    Station, Route, TrainType, Train, Journey,
    Seat, Order, Crew
)
from railway.serializers import TicketSerializer
from django.contrib.auth import get_user_model


class TicketViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="testpass"
        )
        self.client.force_authenticate(user=self.user)

        self.station_from = Station.objects.create(name="Kyiv", latitude=50.45, longitude=30.52)
        self.station_to = Station.objects.create(name="Lviv", latitude=49.84, longitude=24.03)
        self.route = Route.objects.create(source=self.station_from, destination=self.station_to, distance=500)

        self.train_type = TrainType.objects.create(name="Express")
        self.train = Train.objects.create(
            number="IC-101",
            seats=5,
            train_type=self.train_type,
            min_checked_baggage_mass=10,
            max_checked_baggage_mass=20
        )

        self.crew_member = Crew.objects.create(first_name="Ivan", last_name="Franko")

        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=now() + timedelta(days=1),
            arrival_time=now() + timedelta(days=1, hours=4)
        )
        self.journey.crew.set([self.crew_member])

        self.seat = Seat.objects.get(journey=self.journey, number=1)
        self.order = Order.objects.create(user=self.user)

    def test_create_valid_ticket(self):
        url = reverse("railway:tickets-list")
        data = {
            "journey": self.journey.id,
            "seat": self.seat.id,
            "checked_baggage_charge": False,
            "order": self.order.id
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["seat"], self.seat.id)

    def test_create_ticket_with_occupied_seat(self):
        self.seat.is_occupied = True
        self.seat.save()

        data = {
            "journey": self.journey.id,
            "seat": self.seat.id,
            "checked_baggage_charge": False,
            "order": self.order.id
        }

        # обходимо обмеження queryset вручну
        serializer = TicketSerializer()
        serializer.initial_data = data
        serializer.fields["seat"].queryset = Seat.objects.all()

        self.assertFalse(serializer.is_valid())
        self.assertIn("Seat is already occupied.", str(serializer.errors["non_field_errors"]))

    def test_create_ticket_with_wrong_journey_seat(self):
        other_journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=now() + timedelta(days=2),
            arrival_time=now() + timedelta(days=2, hours=4),
        )
        other_journey.crew.set([self.crew_member])

        wrong_seat = Seat.objects.get(journey=other_journey, number=1)

        data = {
            "journey": self.journey.id,
            "seat": wrong_seat.id,
            "checked_baggage_charge": False,
            "order": self.order.id
        }

        serializer = TicketSerializer()
        serializer.initial_data = data
        serializer.fields["seat"].queryset = Seat.objects.all()

        self.assertFalse(serializer.is_valid())
        self.assertIn("Seat doesn't belong to the selected journey.", str(serializer.errors["non_field_errors"]))
