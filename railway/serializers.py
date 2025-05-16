from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

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
        fields = ["id", "number", "max_checked_baggage_mass", "min_checked_baggage_mass", "train_type"]
        extra_kwargs = {
            "max_checked_baggage_mass": {"label": "Max checked baggage mass (kg)"},
            "min_checked_baggage_mass": {"label": "Min checked baggage mass (kg)"},
        }

    def validate(self, attrs):
        if attrs["max_checked_baggage_mass"] <= attrs["min_checked_baggage_mass"]:
            raise ValidationError("Prohibited baggage mass can't be less than or equal to minimum baggage mass.")
        return attrs


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
        validators = [
            UniqueTogetherValidator(
                queryset=Route.objects.all(),
                fields=["source", "destination"],
                message="This route already exists.",
            )
        ]

    def validate(self, attrs):
        if attrs["destination"] == attrs["source"]:
            raise ValidationError("Destination must be different.")
        return attrs


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


class CrewListSerializer(CrewSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Crew
        fields = ["full_name"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "created_at", "user"]
        read_only_fields = ["id", "created_at", "user"]


class OrderListSerializer(OrderSerializer):
    user = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="email",
    )


class OrderRetrieveSerializer(OrderSerializer):
    user = UserSerializer(many=False, read_only=True)


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = ["id", "route", "train", "departure_time", "arrival_time", "crew"]

    def validate(self, attrs):
        if attrs["departure_time"] <= attrs["arrival_time"]:
            raise ValidationError("Arrival time must be after departure time.")
        return attrs


class JourneyListSerializer(JourneySerializer):
    route = serializers.SerializerMethodField()
    train = serializers.CharField(source="train.train_type.name", read_only=True)
    crew = CrewListSerializer(many=True, read_only=True)

    def get_route(self, obj):
        return f"{obj.route.source} => {obj.route.destination}"


class JourneyRetrieveSerializer(JourneySerializer):
    crew = CrewListSerializer(many=True, read_only=True)
    route = RouteListSerializer(many=False, read_only=True)
    train = TrainRetrieveSerializer(many=False, read_only=True)


class TicketSerializer(serializers.ModelSerializer):
    min_checked_baggage_mass = serializers.SerializerMethodField()
    max_checked_baggage_mass = serializers.IntegerField(
        source="journey.train.max_checked_baggage_mass",
        read_only=True,
    )
    journey = JourneyListSerializer(many=False, read_only=False)
    order = OrderListSerializer(many=False, read_only=False)

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
