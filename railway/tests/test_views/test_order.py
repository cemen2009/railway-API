from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from railway.models import Order
from django.contrib.auth import get_user_model


class OrderViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="testpass"
        )

        self.other_user = get_user_model().objects.create_user(
            email="other@example.com",
            password="otherpass"
        )

        self.order1 = Order.objects.create(user=self.user)
        self.order2 = Order.objects.create(user=self.user)
        self.order3 = Order.objects.create(user=self.other_user)

        self.client.force_authenticate(user=self.user)

    def test_list_orders_returns_only_user_orders(self):
        url = reverse("railway:orders-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

        returned_ids = {order["id"] for order in response.data["results"]}
        self.assertIn(self.order1.id, returned_ids)
        self.assertIn(self.order2.id, returned_ids)
        self.assertNotIn(self.order3.id, returned_ids)

    def test_retrieve_own_order(self):
        url = reverse("railway:orders-detail", args=[self.order1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.order1.id)

    def test_retrieve_other_users_order_forbidden(self):
        url = reverse("railway:orders-detail", args=[self.order3.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_create_order(self):
        url = reverse("railway:orders-list")
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"], self.user.id)
