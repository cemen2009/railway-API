from rest_framework import viewsets

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
    SeatRetrieveSerializer, SeatListSerializer,
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

    def perform_create(self, serializer):
        # adding authenticated user
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderRetrieveSerializer
        return OrderSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_serializer_class(self):
        return TicketSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        if self.action == "retrieve":
            return JourneyRetrieveSerializer
        return JourneySerializer
