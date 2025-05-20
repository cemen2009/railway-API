from django.test import TestCase
from railway.models import Station, TrainType, Train, Route, Crew, Journey
from django.utils.timezone import now
from datetime import timedelta


class StationModelTest(TestCase):
    def test_str(self):
        station = Station.objects.create(name="Kyiv", latitude=50.45, longitude=30.52)
        self.assertEqual(str(station), "Kyiv")


class TrainTypeModelTest(TestCase):
    def test_str(self):
        train_type = TrainType.objects.create(name="Express")
        self.assertEqual(str(train_type), "Express")


class TrainModelTest(TestCase):
    def test_str(self):
        train_type = TrainType.objects.create(name="IC+")
        train = Train.objects.create(
            number="705К",
            train_type=train_type,
            seats=10,
            min_checked_baggage_mass=10,
            max_checked_baggage_mass=20
        )
        self.assertEqual(str(train), "705К (IC+)")

    def test_baggage_mass_validation(self):
        train_type = TrainType.objects.create(name="Regional")
        with self.assertRaises(Exception):
            Train.objects.create(
                number="801Л",
                seats=20,
                train_type=train_type,
                min_checked_baggage_mass=30,
                max_checked_baggage_mass=25
            )


class RouteModelTest(TestCase):
    def test_str(self):
        s1 = Station.objects.create(name="Lviv", latitude=49.84, longitude=24.03)
        s2 = Station.objects.create(name="Kharkiv", latitude=49.99, longitude=36.23)
        route = Route.objects.create(source=s1, destination=s2, distance=1000)
        self.assertEqual(str(route), "Lviv => Kharkiv")

    def test_same_station_validation(self):
        s1 = Station.objects.create(name="Lviv", latitude=49.84, longitude=24.03)
        with self.assertRaises(Exception):
            Route.objects.create(source=s1, destination=s1, distance=500)


class CrewModelTest(TestCase):
    def test_str(self):
        crew = Crew.objects.create(first_name="Ivan", last_name="Franko")
        self.assertEqual(str(crew), "Ivan Franko")


class JourneyModelTest(TestCase):
    def test_time_validation(self):
        s1 = Station.objects.create(name="Dnipro", latitude=48.45, longitude=34.98)
        s2 = Station.objects.create(name="Ternopil", latitude=49.55, longitude=25.59)
        route = Route.objects.create(source=s1, destination=s2, distance=800)
        train_type = TrainType.objects.create(name="Fast")
        train = Train.objects.create(
            number="777Х",
            train_type=train_type,
            seats=20,
            min_checked_baggage_mass=10,
            max_checked_baggage_mass=15
        )
        arrival = now()
        departure = now() + timedelta(hours=2)
        with self.assertRaises(Exception):
            Journey.objects.create(
                route=route,
                train=train,
                arrival_time=arrival,
                departure_time=departure
            )
