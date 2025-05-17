from django.test import TestCase
from railway.models import (
    TrainType, Train, Station, Route,
    Journey, Seat, Order, Ticket
)
from railway.serializers import TicketSerializer
from django.contrib.auth import get_user_model
from django.utils.timezone import now, timedelta


class TicketSerializerTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass"
        )

        self.train_type = TrainType.objects.create(name="Express")
        self.train = Train.objects.create(
            number="IC123",
            train_type=self.train_type,
            seats=5,
            min_checked_baggage_mass=10,
            max_checked_baggage_mass=20
        )

        self.station_from = Station.objects.create(name="Kyiv", latitude=50.45, longitude=30.52)
        self.station_to = Station.objects.create(name="Lviv", latitude=49.84, longitude=24.03)
        self.route = Route.objects.create(source=self.station_from, destination=self.station_to, distance=500)

        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=now() + timedelta(hours=1),
            arrival_time=now() + timedelta(hours=5),
        )

        self.seat = Seat.objects.get(journey=self.journey, number=1)

        self.order = Order.objects.create(user=self.user)

    def test_valid_ticket(self):
        data = {
            "journey": self.journey.id,
            "seat": self.seat.id,
            "checked_baggage_charge": False,
            "order": self.order.id
        }

        serializer = TicketSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_seat_does_not_belong_to_journey(self):
        # створимо інший journey і отримаємо перше місце з нього
        other_journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=now() + timedelta(days=1),
            arrival_time=now() + timedelta(days=1, hours=4),
        )
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

    def test_seat_already_occupied(self):
        self.seat.is_occupied = True
        self.seat.save()

        data = {
            "journey": self.journey.id,
            "seat": self.seat.id,
            "checked_baggage_charge": False,
            "order": self.order.id
        }

        serializer = TicketSerializer()
        serializer.initial_data = data
        serializer.fields["seat"].queryset = Seat.objects.all()

        self.assertFalse(serializer.is_valid())
        self.assertIn("Seat is already occupied.", str(serializer.errors["non_field_errors"]))
