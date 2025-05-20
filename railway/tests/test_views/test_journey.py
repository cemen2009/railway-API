from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from railway.models import Station, Route, TrainType, Train, Journey, Crew
from django.utils.timezone import now, timedelta
from django.contrib.auth import get_user_model


class JourneyViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="admin@example.com",
            password="pass1234",
            is_staff=True
        )
        self.client.force_authenticate(user=self.user)

        self.station_a = Station.objects.create(name="Kyiv", latitude=50.45, longitude=30.52)
        self.station_b = Station.objects.create(name="Lviv", latitude=49.84, longitude=24.03)

        self.route = Route.objects.create(
            source=self.station_a,
            destination=self.station_b,
            distance=500
        )

        self.train_type = TrainType.objects.create(name="Express")
        self.train = Train.objects.create(
            number="IC-101",
            seats=10,
            train_type=self.train_type,
            min_checked_baggage_mass=10,
            max_checked_baggage_mass=30
        )

        self.crew_member = Crew.objects.create(first_name="Ivan", last_name="Franko")

        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=now() + timedelta(hours=1),
            arrival_time=now() + timedelta(hours=5),
        )
        self.journey.crew.set([self.crew_member])

    def test_list_journeys(self):
        url = reverse("railway:journeys-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.journey.id)

    def test_retrieve_journey(self):
        url = reverse("railway:journeys-detail", args=[self.journey.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.journey.id)

    def test_create_journey(self):
        url = reverse("railway:journeys-list")
        data = {
            "route": self.route.id,
            "train": self.train.id,
            "departure_time": (now() + timedelta(days=1)).isoformat(),
            "arrival_time": (now() + timedelta(days=1, hours=4)).isoformat(),
            "crew": [self.crew_member.id]
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["route"], self.route.id)
        self.assertEqual(response.data["train"], self.train.id)

    def test_create_invalid_journey_time(self):
        url = reverse("railway:journeys-list")
        data = {
            "route": self.route.id,
            "train": self.train.id,
            "departure_time": (now() + timedelta(hours=5)).isoformat(),
            "arrival_time": (now() + timedelta(hours=1)).isoformat(),
            "crew": [self.crew_member.id]
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.data)
