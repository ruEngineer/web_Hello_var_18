"""Заполнение базы демонстрационными данными.

Запуск:
    python manage.py seed_demo
"""

from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from Z3app.models import Bus, BusPassport, Passenger, Ticket, Trip


class Command(BaseCommand):
    help = 'Добавляет демонстрационные пассажиров, автобусы, рейсы и билеты'

    def handle(self, *args, **options):
        passengers = []
        for full_name, phone, email, birth in [
            ('Иванов Иван Иванович', '+7 (999) 123-45-67', 'ivanov@example.ru', date(1990, 5, 17)),
            ('Петрова Анна Сергеевна', '+7 (999) 765-43-21', 'petrova@example.ru', date(1995, 11, 2)),
            ('Сидоров Пётр Алексеевич', '+7 (999) 555-66-77', 'sidorov@example.ru', date(1987, 3, 24)),
        ]:
            passenger, _ = Passenger.objects.get_or_create(
                full_name=full_name,
                defaults={'phone': phone, 'email': email, 'birth_date': birth},
            )
            passengers.append(passenger)

        buses = []
        for model_name, plate_number, seats in [
            ('ПАЗ-3205', 'А123ВС77', 40),
            ('ЛиАЗ-5256', 'В456ОР76', 35),
            ('ГАЗель Next', 'Е789КХ76', 18),
        ]:
            bus, _ = Bus.objects.get_or_create(
                plate_number=plate_number,
                defaults={'model_name': model_name, 'seats': seats},
            )
            buses.append(bus)

        BusPassport.objects.get_or_create(
            bus=buses[0],
            defaults={
                'serial_number': 'АБ123456',
                'issue_date': date(2023, 5, 10),
                'valid_until': date.today() + timedelta(days=365),
            },
        )
        BusPassport.objects.get_or_create(
            bus=buses[1],
            defaults={
                'serial_number': 'ВГ654321',
                'issue_date': date(2024, 2, 20),
                'valid_until': date.today() + timedelta(days=200),
            },
        )

        trips = []
        for index, (bus, days, departure, from_city, to_city, price, travel_time) in enumerate([
            (buses[0], 2, time(8, 15), 'Ярославль', 'Москва', Decimal('850.00'), time(5, 30)),
            (buses[1], 3, time(10, 40), 'Ярославль', 'Кострома', Decimal('420.00'), time(2, 15)),
            (buses[2], 5, time(14, 20), 'Москва', 'Тверь', Decimal('560.00'), time(3, 40)),
            (buses[0], 7, time(18, 0), 'Ярославль', 'Москва', Decimal('850.00'), time(5, 30)),
        ]):
            trip, _ = Trip.objects.get_or_create(
                bus=bus,
                departure_date=date.today() + timedelta(days=days),
                departure_time=departure,
                defaults={
                    'from_city': from_city,
                    'to_city': to_city,
                    'price': price,
                    'travel_time': travel_time,
                },
            )
            trips.append(trip)

        now = timezone.now()
        Ticket.objects.get_or_create(
            passenger=passengers[0], trip=trips[0],
            defaults={
                'seat': 5, 'status': 'paid', 'baggage': True,
                'paid_at': now - timedelta(days=1),
            },
        )
        Ticket.objects.get_or_create(
            passenger=passengers[1], trip=trips[0],
            defaults={'seat': 6, 'status': 'booked'},
        )
        Ticket.objects.get_or_create(
            passenger=passengers[2], trip=trips[1],
            defaults={
                'seat': 12, 'status': 'paid',
                'paid_at': now - timedelta(days=2),
            },
        )
        # Демонстрационный возвращённый билет.
        Ticket.objects.get_or_create(
            passenger=passengers[2], trip=trips[0],
            defaults={
                'seat': 1,
                'status': 'cancelled',
                'refunded_at': now - timedelta(hours=3),
                'refund_amount': Decimal('850.00'),
            },
        )

        # Заполняем даты у билетов, созданных до появления этих полей.
        for ticket in Ticket.objects.filter(status='paid', paid_at__isnull=True):
            ticket.paid_at = ticket.created_at or now
            ticket.save(update_fields=['paid_at'])
        for ticket in Ticket.objects.filter(status='cancelled', refunded_at__isnull=True):
            ticket.refunded_at = ticket.created_at or now
            ticket.save(update_fields=['refunded_at'])

        self.stdout.write(self.style.SUCCESS(
            'Демо-данные добавлены: 3 пассажира, 3 автобуса, 2 техпаспорта, '
            '4 рейса, оплаченные, забронированный и возвращённый билеты.'
        ))
