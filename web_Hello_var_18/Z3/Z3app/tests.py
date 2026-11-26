from datetime import date, time, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .forms import BusForm, BusPassportForm, PassengerForm, TicketForm, TripForm
from .models import Bus, BusPassport, Passenger, Ticket, Trip


class ModelRelationsTest(TestCase):
    def setUp(self):
        self.passenger = Passenger.objects.create(
            full_name='Иванов Иван Иванович',
            phone='+7 (999) 123-45-67',
            email='ivanov@example.ru',
            birth_date=date(1990, 5, 17),
        )
        self.bus = Bus.objects.create(
            model_name='ПАЗ-3205',
            plate_number='А123ВС77',
            seats=40,
        )
        self.trip = Trip.objects.create(
            bus=self.bus,
            from_city='Ярославль',
            to_city='Москва',
            price=Decimal('850.00'),
            travel_time=time(5, 30),
            departure_date=date.today() + timedelta(days=2),
            departure_time=time(8, 15),
        )

    def test_one_to_one_bus_passport(self):
        passport = BusPassport.objects.create(
            bus=self.bus,
            serial_number='АБ123456',
            issue_date=date(2023, 5, 10),
            valid_until=date(2026, 5, 10),
        )
        self.assertEqual(self.bus.passport, passport)
        with self.assertRaises(Exception):
            BusPassport.objects.create(
                bus=self.bus,
                serial_number='ВГ654321',
                issue_date=date(2023, 5, 10),
                valid_until=date(2026, 5, 10),
            )

    def test_ticket_total_with_baggage(self):
        ticket = Ticket.objects.create(
            passenger=self.passenger,
            trip=self.trip,
            seat=5,
            baggage=True,
        )
        self.assertEqual(ticket.total, Decimal('1150.00'))

    def test_main_table_has_two_foreign_keys(self):
        ticket = Ticket.objects.create(
            passenger=self.passenger,
            trip=self.trip,
            seat=7,
        )
        self.assertEqual(ticket.passenger, self.passenger)
        self.assertEqual(ticket.trip, self.trip)


class ValidationTest(TestCase):
    def setUp(self):
        self.passenger = Passenger.objects.create(
            full_name='Петров Пётр',
            phone='+7 (999) 111-22-33',
            email='petrov@example.ru',
            birth_date=date(1985, 1, 1),
        )
        self.bus = Bus.objects.create(
            model_name='ЛиАЗ-5256',
            plate_number='В456ОР76',
            seats=2,
        )
        self.trip = Trip.objects.create(
            bus=self.bus,
            from_city='Ярославль',
            to_city='Кострома',
            price=Decimal('400.00'),
            travel_time=time(2, 0),
            departure_date=date.today() + timedelta(days=1),
            departure_time=time(9, 0),
        )

    def test_passenger_future_birth_date(self):
        form = PassengerForm(data={
            'full_name': 'Сидоров Сидор',
            'phone': '+7 (999) 222-33-44',
            'email': 'sidorov@example.ru',
            'birth_date': (date.today() + timedelta(days=1)).isoformat(),
        })
        self.assertFalse(form.is_valid())
        self.assertIn('birth_date', form.errors)

    def test_passenger_bad_phone(self):
        form = PassengerForm(data={
            'full_name': 'Сидоров Сидор',
            'phone': '123',
            'email': 'sidorov@example.ru',
            'birth_date': '1990-01-01',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_trip_same_cities(self):
        form = TripForm(data={
            'bus': self.bus.pk,
            'from_city': 'Москва',
            'to_city': 'москва',
            'price': '500',
            'travel_time': '03:00',
            'departure_date': (date.today() + timedelta(days=2)).isoformat(),
            'departure_time': '10:00',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('to_city', form.errors)

    def test_trip_in_past(self):
        form = TripForm(data={
            'bus': self.bus.pk,
            'from_city': 'Москва',
            'to_city': 'Тверь',
            'price': '500',
            'travel_time': '03:00',
            'departure_date': (date.today() - timedelta(days=1)).isoformat(),
            'departure_time': '10:00',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('departure_time', form.errors)

    def test_ticket_seat_out_of_range(self):
        form = TicketForm(data={
            'full_name': 'Новиков Новый',
            'phone': '+7 (999) 111-22-33',
            'email': 'new@example.ru',
            'birth_date': '1993-04-05',
            'trip': self.trip.pk,
            'seat': 3,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('seat', form.errors)

    def test_ticket_duplicate_seat(self):
        Ticket.objects.create(passenger=self.passenger, trip=self.trip, seat=1)
        form = TicketForm(data={
            'full_name': 'Новиков Новый',
            'phone': '+7 (999) 111-22-33',
            'email': 'new@example.ru',
            'birth_date': '1993-04-05',
            'trip': self.trip.pk,
            'seat': 1,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('seat', form.errors)

    def test_ticket_passenger_fields_required(self):
        form = TicketForm(data={
            'trip': self.trip.pk,
            'seat': 2,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('full_name', form.errors)
        self.assertIn('phone', form.errors)

    def test_ticket_total_cannot_exceed_capacity(self):
        # В автобусе 2 места, оба уже проданы.
        Ticket.objects.create(passenger=self.passenger, trip=self.trip, seat=1)
        Ticket.objects.create(passenger=self.passenger, trip=self.trip, seat=2)
        form = TicketForm(data={
            'full_name': 'Новиков Новый',
            'phone': '+7 (999) 111-22-33',
            'email': 'new@example.ru',
            'birth_date': '1993-04-05',
            'trip': self.trip.pk,
            'seat': 1,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('trip', form.errors)

    def test_bus_capacity_reduction_blocked(self):
        bus = Bus.objects.create(
            model_name='Большой', plate_number='К123ОР77', seats=40,
        )
        trip = Trip.objects.create(
            bus=bus,
            from_city='Москва',
            to_city='Тверь',
            price=Decimal('500.00'),
            travel_time=time(3, 0),
            departure_date=date.today() + timedelta(days=2),
            departure_time=time(10, 0),
        )
        Ticket.objects.create(passenger=self.passenger, trip=trip, seat=5)
        form = BusForm(
            data={
                'model_name': bus.model_name,
                'plate_number': bus.plate_number,
                'seats': 2,
            },
            instance=bus,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('seats', form.errors)

    def test_trip_cannot_change_to_smaller_bus(self):
        big_bus = Bus.objects.create(
            model_name='Большой', plate_number='К123ОР77', seats=40,
        )
        small_bus = Bus.objects.create(
            model_name='Маленький', plate_number='М456НР77', seats=2,
        )
        trip = Trip.objects.create(
            bus=big_bus,
            from_city='Москва',
            to_city='Тверь',
            price=Decimal('500.00'),
            travel_time=time(3, 0),
            departure_date=date.today() + timedelta(days=2),
            departure_time=time(10, 0),
        )
        Ticket.objects.create(passenger=self.passenger, trip=trip, seat=5)
        form = TripForm(
            data={
                'bus': small_bus.pk,
                'from_city': trip.from_city,
                'to_city': trip.to_city,
                'price': trip.price,
                'travel_time': '03:00',
                'departure_date': trip.departure_date.isoformat(),
                'departure_time': '10:00',
            },
            instance=trip,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('bus', form.errors)

    def test_ticket_bad_phone(self):
        form = TicketForm(data={
            'full_name': 'Новиков Новый',
            'phone': '123',
            'email': 'new@example.ru',
            'birth_date': '1993-04-05',
            'trip': self.trip.pk,
            'seat': 2,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_second_passport_not_available(self):
        BusPassport.objects.create(
            bus=self.bus,
            serial_number='АБ123456',
            issue_date=date(2023, 5, 10),
            valid_until=date.today() + timedelta(days=300),
        )
        form = BusPassportForm()
        self.assertNotIn(self.bus, form.fields['bus'].queryset)

    def test_passport_valid_until_before_issue(self):
        form = BusPassportForm(data={
            'bus': self.bus.pk,
            'serial_number': 'ВГ654321',
            'issue_date': '2025-01-01',
            'valid_until': '2024-01-01',
            'registered': 'on',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('valid_until', form.errors)


class CrudViewsTest(TestCase):
    def setUp(self):
        self.passenger = Passenger.objects.create(
            full_name='Иванов Иван',
            phone='+7 (999) 123-45-67',
            email='ivanov@example.ru',
            birth_date=date(1990, 5, 17),
        )
        self.bus = Bus.objects.create(
            model_name='ПАЗ-3205',
            plate_number='А123ВС77',
            seats=40,
        )
        self.trip = Trip.objects.create(
            bus=self.bus,
            from_city='Ярославль',
            to_city='Москва',
            price=Decimal('850.00'),
            travel_time=time(5, 30),
            departure_date=date.today() + timedelta(days=2),
            departure_time=time(8, 15),
        )

    def test_pages_open(self):
        urls = [
            'home', 'passenger_list', 'passenger_create', 'bus_list', 'bus_create',
            'buspassport_list', 'buspassport_create', 'trip_list', 'trip_create',
            'ticket_list', 'ticket_create',
        ]
        for name in urls:
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_create_edit_delete_passenger(self):
        response = self.client.post(reverse('passenger_create'), {
            'full_name': 'Сидоров Сидор Сидорович',
            'phone': '+7 (999) 555-66-77',
            'email': 'sidorov@example.ru',
            'birth_date': '1992-03-04',
        })
        self.assertEqual(response.status_code, 302)
        passenger = Passenger.objects.get(full_name='Сидоров Сидор Сидорович')

        response = self.client.post(reverse('passenger_edit', args=[passenger.pk]), {
            'full_name': 'Сидоров Сидор',
            'phone': '+7 (999) 555-66-77',
            'email': 'sidorov@example.ru',
            'birth_date': '1992-03-04',
        })
        self.assertEqual(response.status_code, 302)
        passenger.refresh_from_db()
        self.assertEqual(passenger.full_name, 'Сидоров Сидор')

        response = self.client.post(reverse('passenger_delete', args=[passenger.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Passenger.objects.filter(pk=passenger.pk).exists())

    def test_create_bus_passport(self):
        response = self.client.post(reverse('buspassport_create'), {
            'bus': self.bus.pk,
            'serial_number': 'АБ123456',
            'issue_date': date.today().isoformat(),
            'valid_until': (date.today() + timedelta(days=365)).isoformat(),
            'registered': 'on',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(BusPassport.objects.filter(bus=self.bus).exists())

    def test_create_ticket_and_total(self):
        response = self.client.post(reverse('ticket_create'), {
            'full_name': 'Новиков Новый Пассажирович',
            'phone': '+7 (999) 777-88-99',
            'email': 'new@example.ru',
            'birth_date': '1993-04-05',
            'trip': self.trip.pk,
            'seat': 12,
            'baggage': 'on',
        })
        self.assertEqual(response.status_code, 302)
        passenger = Passenger.objects.get(full_name='Новиков Новый Пассажирович')
        ticket = Ticket.objects.get(passenger=passenger, trip=self.trip)
        self.assertEqual(ticket.total, Decimal('1150.00'))
        self.assertEqual(ticket.status, 'booked')

    def test_edit_and_delete_ticket(self):
        ticket = Ticket.objects.create(
            passenger=self.passenger, trip=self.trip, seat=3, status='paid',
        )
        response = self.client.post(reverse('ticket_edit', args=[ticket.pk]), {
            'full_name': 'Изменённый Пассажир',
            'phone': '+7 (999) 444-55-66',
            'email': 'changed@example.ru',
            'birth_date': '1991-01-02',
            'trip': self.trip.pk,
            'seat': 4,
        })
        self.assertEqual(response.status_code, 302)
        ticket.refresh_from_db()
        self.assertEqual(ticket.seat, 4)
        self.assertEqual(ticket.status, 'paid')
        ticket.passenger.refresh_from_db()
        self.assertEqual(ticket.passenger.full_name, 'Изменённый Пассажир')
        self.assertEqual(ticket.passenger.email, 'changed@example.ru')

        response = self.client.post(reverse('ticket_delete', args=[ticket.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Ticket.objects.filter(pk=ticket.pk).exists())

    def test_create_bus_and_trip(self):
        response = self.client.post(reverse('bus_create'), {
            'model_name': 'Ютонг',
            'plate_number': 'К123ОР77',
            'seats': 45,
        })
        self.assertEqual(response.status_code, 302)
        bus = Bus.objects.get(plate_number='К123ОР77')

        response = self.client.post(reverse('trip_create'), {
            'bus': bus.pk,
            'from_city': 'Ярославль',
            'to_city': 'Тверь',
            'price': '600',
            'travel_time': '04:20',
            'departure_date': (date.today() + timedelta(days=5)).isoformat(),
            'departure_time': '07:45',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Trip.objects.filter(bus=bus, from_city='Ярославль').exists())


class TicketPaymentAndRefundTest(TestCase):
    def setUp(self):
        self.passenger = Passenger.objects.create(
            full_name='Оплатов Оплат',
            phone='+7 (999) 321-45-67',
            email='pay@example.ru',
            birth_date=date(1990, 1, 1),
        )
        self.bus = Bus.objects.create(
            model_name='ПАЗ-3205',
            plate_number='А123ВС77',
            seats=40,
        )
        self.trip = Trip.objects.create(
            bus=self.bus,
            from_city='Ярославль',
            to_city='Москва',
            price=Decimal('850.00'),
            travel_time=time(5, 30),
            departure_date=date.today() + timedelta(days=2),
            departure_time=time(8, 15),
        )
        self.ticket = Ticket.objects.create(
            passenger=self.passenger, trip=self.trip, seat=1,
        )

    def test_pay_booked_ticket(self):
        response = self.client.post(reverse('ticket_pay', args=[self.ticket.pk]))
        self.assertRedirects(
            response, reverse('ticket_detail', args=[self.ticket.pk]),
        )
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'paid')
        self.assertIsNotNone(self.ticket.paid_at)

    def test_cannot_pay_cancelled_ticket(self):
        self.ticket.status = 'cancelled'
        self.ticket.save()
        self.client.post(reverse('ticket_pay', args=[self.ticket.pk]))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'cancelled')
        self.assertIsNone(self.ticket.paid_at)

    def test_refund_paid_ticket(self):
        self.ticket.status = 'paid'
        self.ticket.save()
        amount = self.ticket.total
        response = self.client.post(reverse('ticket_refund', args=[self.ticket.pk]))
        self.assertRedirects(
            response, reverse('ticket_detail', args=[self.ticket.pk]),
        )
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'cancelled')
        self.assertEqual(self.ticket.total, Decimal('0.00'))
        self.assertEqual(self.ticket.refund_amount, amount)
        self.assertIsNotNone(self.ticket.refunded_at)

    def test_refund_booked_ticket(self):
        amount = self.ticket.total
        self.client.post(reverse('ticket_refund', args=[self.ticket.pk]))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'cancelled')
        self.assertEqual(self.ticket.refund_amount, amount)
        self.assertEqual(self.ticket.total, Decimal('0.00'))

    def test_refund_twice_does_not_change_amount(self):
        self.client.post(reverse('ticket_refund', args=[self.ticket.pk]))
        self.ticket.refresh_from_db()
        amount = self.ticket.refund_amount
        self.client.post(reverse('ticket_refund', args=[self.ticket.pk]))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.refund_amount, amount)

    def test_refunded_seat_can_be_sold_again(self):
        self.client.post(reverse('ticket_refund', args=[self.ticket.pk]))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'cancelled')

        form = TicketForm(data={
            'full_name': 'Новый Пассажир',
            'phone': '+7 (999) 444-55-66',
            'email': 'new@example.ru',
            'birth_date': '1992-02-02',
            'trip': self.trip.pk,
            'seat': 1,
        })
        self.assertTrue(form.is_valid(), form.errors)
        new_ticket = form.save()
        self.assertEqual(new_ticket.seat, 1)
        self.assertEqual(new_ticket.status, 'booked')
