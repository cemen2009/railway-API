from rest_framework.routers import DefaultRouter

from railway.views import (
    StationViewSet,
    TrainTypeViewSet,
    TrainViewSet,
    RouteViewSet,
    CrewViewSet,
    OrderViewSet,
    TicketViewSet,
    JourneyViewSet,
)


router = DefaultRouter()

router.register("stations", StationViewSet, basename="stations")
router.register("train-types", TrainTypeViewSet, basename="train_types")
router.register("trains", TrainViewSet, basename="trains")
router.register("routes", RouteViewSet, basename="routes")
router.register("crews", CrewViewSet, basename="crews")
router.register("orders", OrderViewSet, basename="orders")
router.register("tickets", TicketViewSet, basename="tickets")
router.register("journeys", JourneyViewSet, basename="journeys")

urlpatterns = router.urls

app_name = "railway"
