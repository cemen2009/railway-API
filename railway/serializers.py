from django.contrib.auth import get_user_model
from rest_framework import serializers

from railway.models import (
    Station,
    TrainType,
    Train,
    Route,
    Crew,
    Order, Ticket, Journey,
)


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "username"]


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ["id", "name", "latitude", "longitude"]


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ["id", "name"]


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ["id", "name", "max_checked_baggage_mass", "min_checked_baggage_mass", "train_type"]
        extra_kwargs = {
            "max_checked_baggage_mass": {"label": "Max checked baggage mass (kg)"},
            "min_checked_baggage_mass": {"label": "Min checked baggage mass (kg)"},
        }


class TrainListSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name",
    )


class TrainRetrieveSerializer(TrainSerializer):
    train_type = TrainTypeSerializer(many=False, read_only=True)


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name",
    )
    destination = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name",
    )


class RouteRetrieveSerializer(RouteSerializer):
    source = StationSerializer(many=False, read_only=True)
    destination = StationSerializer(many=False, read_only=True)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name"]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "created_at", "user"]

        # I don't have authentication rn, so this stuff doesn't make any sense
        read_only_fields = ["id", "created_at", "user"]


class OrderListSerializer(OrderSerializer):
    user = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="email",
    )


class OrderRetrieveSerializer(OrderSerializer):
    user = UserSerializer(many=False, read_only=True)


class TicketSerializer(serializers.ModelSerializer):
    min_checked_baggage_mass = serializers.SerializerMethodField()
    max_checked_baggage_mass = serializers.IntegerField(
        source="journey.train.max_checked_baggage_mass",
        read_only=True
    )

    class Meta:
        model = Ticket
        fields = [
            "id",
            "min_checked_baggage_mass",
            "max_checked_baggage_mass",
            "checked_baggage_charge",
            "seat",
            "journey",
            "order"
        ]
        extra_kwargs = {
            "seat": {"label": "Amount of seats"},
        }

    def get_min_checked_baggage_mass(self, obj):
        return obj.journey.train.min_checked_baggage_mass


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = ["id", "route", "train", "departure_time", "arrival_time", "crew"]
