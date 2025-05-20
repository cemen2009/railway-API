from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from railway.models import (
    Station,
    TrainType,
    Train,
    Route,
    Crew,
    Order,
    Ticket, Journey, Seat,
)
from railway.serializers import (
    StationSerializer,
    TrainTypeSerializer,
    TrainSerializer,
    TrainListSerializer,
    RouteSerializer,
    CrewSerializer,
    OrderSerializer,
    TicketSerializer,
    JourneySerializer, TrainRetrieveSerializer, RouteListSerializer, RouteRetrieveSerializer, OrderListSerializer,
    OrderRetrieveSerializer, CrewListSerializer, JourneyListSerializer, JourneyRetrieveSerializer, SeatSerializer,
    SeatRetrieveSerializer, SeatListSerializer, TicketRetrieveSerializer, TicketListSerializer,
)


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer
        if self.action == "retrieve":
            return TrainRetrieveSerializer
        return TrainSerializer


class SeatViewSet(viewsets.ModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SeatRetrieveSerializer
        if self.action == "list":
            return SeatListSerializer
        return SeatSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteRetrieveSerializer
        return RouteSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer
        return CrewSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # adding authenticated user
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderRetrieveSerializer
        return OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related(
        "seat",
        "journey__route__source",
        "journey__route__destination",
        "journey__train__train_type",
        "order__user"
    )
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TicketRetrieveSerializer
        if self.action == "list":
            return TicketListSerializer
        return TicketSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.select_related(
        "route__source",
        "route__destination",
        "train__train_type"
    ).prefetch_related("crew")
    serializer_class = JourneySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        if self.action == "retrieve":
            return JourneyRetrieveSerializer
        return JourneySerializer
