from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from railway.models import TrainType, Train
from django.contrib.auth import get_user_model


class TrainViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.train_type = TrainType.objects.create(name="Express")
        self.train = Train.objects.create(
            number="IC-123",
            seats=5,
            train_type=self.train_type,
            min_checked_baggage_mass=10,
            max_checked_baggage_mass=20
        )

        self.user = get_user_model().objects.create_user(
            email="admin@example.com",
            password="pass1234",
            is_staff=True
        )

        self.client.force_authenticate(user=self.user)

    def test_list_trains(self):
        url = reverse("railway:trains-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["number"], self.train.number)

    def test_retrieve_train(self):
        url = reverse("railway:trains-detail", args=[self.train.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["number"], self.train.number)

    def test_create_train(self):
        url = reverse("railway:trains-list")
        data = {
            "number": "IC-999",
            "seats": 10,
            "min_checked_baggage_mass": 15,
            "max_checked_baggage_mass": 30,
            "train_type": self.train_type.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["number"], "IC-999")

    def test_create_invalid_train(self):
        url = reverse("railway:trains-list")
        data = {
            "number": "IC-000",
            "seats": 10,
            "min_checked_baggage_mass": 40,
            "max_checked_baggage_mass": 30,
            "train_type": self.train_type.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.data)
