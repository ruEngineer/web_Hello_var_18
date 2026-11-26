from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone

# =====================================================================
#  Модель билетной кассы: пассажиры, автобусы, техпаспорта, рейсы, билеты.
#
#  Bus  ──1:1── BusPassport          (пара справочников со связью 1 к 1)
#   │ 1
#   │ M
#   ▼
#  Trip  ◄──M:1──  Ticket  ──M:1──  Passenger
#  (справочник рейсов)   (главная таблица)
#
#  Ticket — промежуточная (главная) таблица: у неё две связи
#  многие-к-одному к справочникам Passenger и Trip.
# =====================================================================

plate_validator = RegexValidator(
    r'^[А-Яа-яA-Za-z]\d{3}[А-Яа-яA-Za-z]{2}\d{2,3}$',
    'Госномер в формате А123ВС77',
)
serial_validator = RegexValidator(
    r'^[А-ЯA-Z]{2}\d{6}$',
    'Серийный номер в формате АБ123456',
)
phone_validator = RegexValidator(
    r'^\+?[\d\s\-()]{10,18}$',
    'Введите телефон в формате +7 (999) 123-45-67',
)
route_number_validator = RegexValidator(
    r'^[А-ЯA-Z0-9\-]{1,10}$',
    'Номер маршрута: до 10 букв, цифр или дефиса',
)


def validate_not_future(value):
    """Дата не может быть позже сегодняшнего дня."""
    if value and value > date.today():
        raise ValidationError('Дата не может быть в будущем')


# ---------------------------------------------------------------------
#  Таблица 1. Справочник пассажиров
# ---------------------------------------------------------------------
class Passenger(models.Model):
    full_name = models.CharField('ФИО', max_length=100)
    phone = models.CharField('Телефон', max_length=20, validators=[phone_validator])
    email = models.EmailField('Электронная почта')
    birth_date = models.DateField('Дата рождения', validators=[validate_not_future])
    photo = models.ImageField(
        'Фотография', upload_to='passengers/', blank=True, null=True,
    )

    class Meta:
        verbose_name = 'пассажир'
        verbose_name_plural = 'Пассажиры'
        ordering = ['full_name']

    def __str__(self):
        return self.full_name

    def clean(self):
        super().clean()
        if len(self.full_name.split()) < 2:
            raise ValidationError(
                {'full_name': 'Укажите хотя бы фамилию и имя'}
            )


# ---------------------------------------------------------------------
#  Таблица 2. Справочник автобусов (транспорта)
# ---------------------------------------------------------------------
class Bus(models.Model):
    model_name = models.CharField('Марка и модель', max_length=60)
    plate_number = models.CharField(
        'Госномер', max_length=12, unique=True, validators=[plate_validator],
    )
    seats = models.PositiveSmallIntegerField(
        'Количество мест', default=40,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    photo = models.ImageField(
        'Фотография автобуса', upload_to='buses/', blank=True, null=True,
    )

    class Meta:
        verbose_name = 'автобус'
        verbose_name_plural = 'Автобусы'
        ordering = ['model_name']

    def __str__(self):
        return f'{self.model_name} ({self.plate_number})'


# ---------------------------------------------------------------------
#  Таблица 3. Техпаспорт автобуса — связь 1 к 1 с автобусом
# ---------------------------------------------------------------------
class BusPassport(models.Model):
    bus = models.OneToOneField(
        Bus,
        on_delete=models.CASCADE,
        related_name='passport',
        verbose_name='Автобус',
    )
    serial_number = models.CharField(
        'Серийный номер', max_length=30, unique=True, validators=[serial_validator],
    )
    issue_date = models.DateField('Дата выдачи')
    valid_until = models.DateField('Действителен до')
    registered = models.BooleanField('Зарегистрирован в ГИБДД', default=True)
    scan = models.FileField(
        'Скан техпаспорта', upload_to='passports/', blank=True, null=True,
    )

    class Meta:
        verbose_name = 'техпаспорт'
        verbose_name_plural = 'Техпаспорта'
        ordering = ['-issue_date']

    def __str__(self):
        return f'Техпаспорт {self.serial_number} — {self.bus.model_name}'

    def clean(self):
        super().clean()
        if self.valid_until and self.issue_date and self.valid_until <= self.issue_date:
            raise ValidationError(
                {'valid_until': 'Дата окончания должна быть позже даты выдачи'}
            )


# ---------------------------------------------------------------------
#  Таблица 4. Справочник рейсов (многие-к-одному к автобусу)
# ---------------------------------------------------------------------
class Trip(models.Model):
    bus = models.ForeignKey(
        Bus, on_delete=models.CASCADE, related_name='trips', verbose_name='Автобус',
    )
    from_city = models.CharField('Откуда', max_length=50)
    to_city = models.CharField('Куда', max_length=50)
    price = models.DecimalField(
        'Цена билета, ₽', max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('1.00'))],
    )
    travel_time = models.TimeField('Время в пути')
    departure_date = models.DateField('Дата отправления')
    departure_time = models.TimeField('Время отправления')

    class Meta:
        verbose_name = 'рейс'
        verbose_name_plural = 'Рейсы'
        ordering = ['departure_date', 'departure_time']

    def __str__(self):
        return f'{self.from_city} — {self.to_city} · {self.departure_date:%d.%m.%Y} {self.departure_time:%H:%M}'

    def clean(self):
        super().clean()
        if self.from_city.strip().lower() == self.to_city.strip().lower():
            raise ValidationError(
                {'to_city': 'Города отправления и прибытия должны различаться'}
            )


# ---------------------------------------------------------------------
#  Таблица 5. Билет — главная (промежуточная) таблица.
#  Две связи многие-к-одному: на Passenger и на Trip.
# ---------------------------------------------------------------------
class Ticket(models.Model):
    STATUS_CHOICES = [
        ('booked', 'Забронирован'),
        ('paid', 'Оплачен'),
        ('cancelled', 'Отменён'),
    ]

    passenger = models.ForeignKey(
        Passenger, on_delete=models.CASCADE, related_name='tickets', verbose_name='Пассажир',
    )
    trip = models.ForeignKey(
        Trip, on_delete=models.CASCADE, related_name='tickets', verbose_name='Рейс',
    )
    seat = models.PositiveSmallIntegerField(
        'Место', validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    status = models.CharField(
        'Статус', max_length=10, choices=STATUS_CHOICES, default='booked',
    )
    baggage = models.BooleanField('Багаж (+300 ₽)', default=False)
    receipt = models.FileField(
        'Квитанция', upload_to='receipts/', blank=True, null=True,
    )
    created_at = models.DateTimeField('Оформлен', auto_now_add=True)
    total = models.DecimalField(
        'Итого, ₽', max_digits=10, decimal_places=2, default=0, editable=False,
    )
    paid_at = models.DateTimeField('Оплачен', null=True, blank=True, editable=False)
    refunded_at = models.DateTimeField('Возвращён', null=True, blank=True, editable=False)
    refund_amount = models.DecimalField(
        'Сумма возврата, ₽', max_digits=10, decimal_places=2, default=0, editable=False,
    )

    class Meta:
        verbose_name = 'билет'
        verbose_name_plural = 'Билеты'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['trip', 'seat'],
                condition=~models.Q(status='cancelled'),
                name='unique_active_seat_per_trip',
            ),
        ]

    def __str__(self):
        return f'Билет №{self.pk} — {self.passenger.full_name}, место {self.seat}'

    def clean(self):
        super().clean()
        if not (self.trip_id and self.seat):
            return
        capacity = self.trip.bus.seats
        if self.seat > capacity:
            raise ValidationError(
                {'seat': f'В автобусе всего {capacity} мест'}
            )
        # Нельзя продать больше билетов, чем мест в автобусе.
        if self._state.adding:
            sold = (
                Ticket.objects.filter(trip_id=self.trip_id)
                .exclude(status='cancelled')
                .count()
            )
            if sold >= capacity:
                raise ValidationError(
                    {'trip': 'На этот рейс больше нет свободных мест'}
                )

    def pay(self):
        """Оплата забронированного билета."""
        if self.status != 'booked':
            raise ValidationError('Оплатить можно только забронированный билет')
        self.status = 'paid'
        self.paid_at = timezone.now()
        self.save(update_fields=['status', 'paid_at', 'total'])

    def refund(self):
        """Возврат билета: фиксируем сумму и отменяем билет."""
        if self.status == 'cancelled':
            raise ValidationError('Билет уже возвращён')
        self.refund_amount = self.total
        self.status = 'cancelled'
        self.refunded_at = timezone.now()
        self.save(update_fields=['status', 'refunded_at', 'refund_amount', 'total'])

    def save(self, *args, **kwargs):
        """Стоимость считается автоматически: цена рейса + багаж."""
        if self.status == 'cancelled':
            self.total = Decimal('0.00')
        elif self.trip_id:
            price = self.trip.price
            if self.baggage:
                price += Decimal('300.00')
            self.total = price.quantize(Decimal('0.01'))
        super().save(*args, **kwargs)
