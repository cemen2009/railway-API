from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from railway.models import (
    Station,
    TrainType,
    Train,
    Route,
    Crew,
    Order, Ticket, Journey, Seat,
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
        fields = ["id", "number", "max_checked_baggage_mass", "min_checked_baggage_mass", "train_type", "seats"]
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
        if attrs["departure_time"] >= attrs["arrival_time"]:
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
    # journey = JourneyListSerializer(many=False, read_only=False)
    journey = serializers.PrimaryKeyRelatedField(queryset=Journey.objects.filter(departure_time__gt=timezone.now()))
    # order = OrderListSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "min_checked_baggage_mass",
            "max_checked_baggage_mass",
            "checked_baggage_charge",
            "journey",
            "seat",
            "order"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # filtering seats according to journey id from POST/PATCH json
        #
        # e.g. {"journey": 5, "seat": 65, ...}
        # then we create queryset with seats only for journey with ID 5

        data = kwargs.get("data", {})
        journey_id = data.get("journey")
        if journey_id:
            self.fields["seat"].queryset = Seat.objects.filter(
                journey_id=journey_id,
                is_occupied=False,
            )

    def get_min_checked_baggage_mass(self, obj):
        return obj.journey.train.min_checked_baggage_mass

    def validate(self, data):
        seat = data["seat"]
        journey = data["journey"]

        if seat.journey != journey:
            raise ValidationError("Seat doesn't belong to the selected journey.")
        if seat.is_occupied:
            raise ValidationError("Seat is already occupied.")

        return data

    def create(self, validated_data):
        seat = validated_data["seat"]
        seat.is_occupied = True
        seat.save()
        return super().create(validated_data)


class TicketListSerializer(TicketSerializer):
    journey = JourneyListSerializer(many=False, read_only=True)
    seat = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="number"
    )
    order = serializers.SerializerMethodField()

    def get_order(self, obj):
        return f"ID {obj.order.id} ({obj.order.user.email})"


class TicketRetrieveSerializer(TicketListSerializer):
    order = OrderListSerializer(many=False, read_only=True)


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ["id", "number", "journey", "is_occupied"]
        validators = [
            UniqueTogetherValidator(
                queryset=Seat.objects.all(),
                fields=["number", "journey"],
                message="Train can not has same seat numbers."
            )
        ]


class SeatRetrieveSerializer(SeatSerializer):
    journey = JourneyListSerializer(many=False, read_only=True)


class SeatListSerializer(SeatSerializer):
    journey = serializers.SerializerMethodField()

    def get_journey(self, obj):
        return (f"{obj.journey.route.source} => {obj.journey.route.destination} "
                f"[{obj.journey.departure_time} - {obj.journey.arrival_time}]")
