from datetime import date, datetime

from django import forms
from django.db.models import Q

from .models import Bus, BusPassport, Passenger, Ticket, Trip


class DateInput(forms.DateInput):
    input_type = 'date'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('format', '%Y-%m-%d')
        super().__init__(*args, **kwargs)


class TimeInput(forms.TimeInput):
    input_type = 'time'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('format', '%H:%M')
        super().__init__(*args, **kwargs)


# ==================== ПАССАЖИР ====================

class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = ['full_name', 'phone', 'email', 'birth_date', 'photo']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Иванов Иван Иванович'}),
            'phone': forms.TextInput(attrs={'placeholder': '+7 (999) 123-45-67'}),
            'email': forms.EmailInput(attrs={'placeholder': 'ivanov@example.ru'}),
            'birth_date': DateInput(),
        }

    def clean_birth_date(self):
        value = self.cleaned_data['birth_date']
        if value > date.today():
            raise forms.ValidationError('Дата рождения не может быть в будущем')
        age = date.today().year - value.year
        if age > 120:
            raise forms.ValidationError('Проверьте дату рождения')
        return value

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo and hasattr(photo, 'size') and photo.size > 4 * 1024 * 1024:
            raise forms.ValidationError('Фотография не должна быть больше 4 МБ')
        return photo


# ==================== АВТОБУС (ТРАНСПОРТ) ====================

class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        fields = ['model_name', 'plate_number', 'seats', 'photo']
        widgets = {
            'model_name': forms.TextInput(attrs={'placeholder': 'ПАЗ-3205'}),
            'plate_number': forms.TextInput(attrs={'placeholder': 'А123ВС77'}),
            'seats': forms.NumberInput(attrs={'min': 1, 'max': 100}),
        }

    def clean_plate_number(self):
        value = (self.cleaned_data.get('plate_number') or '').strip().upper()
        if value:
            return value
        return self.cleaned_data.get('plate_number')

    def clean_seats(self):
        seats = self.cleaned_data['seats']
        # Нельзя уменьшить вместимость, если на рейсы уже проданы билеты,
        # которые в неё не помещаются.
        if self.instance.pk and seats != self.instance.seats:
            for trip in self.instance.trips.all():
                tickets = trip.tickets.exclude(status='cancelled')
                if tickets.count() > seats or tickets.filter(seat__gt=seats).exists():
                    raise forms.ValidationError(
                        'Нельзя изменить количество мест: на рейс уже продано '
                        'больше билетов, чем помещается в автобус.'
                    )
        return seats


# ==================== ТЕХПАСПОРТ (СВЯЗЬ 1 К 1) ====================

class BusPassportForm(forms.ModelForm):
    class Meta:
        model = BusPassport
        fields = ['bus', 'serial_number', 'issue_date', 'valid_until', 'registered', 'scan']
        widgets = {
            'serial_number': forms.TextInput(attrs={'placeholder': 'АБ123456'}),
            'issue_date': DateInput(),
            'valid_until': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # В списке только автобусы без техпаспорта (связь 1 к 1).
        # При редактировании текущий автобус остаётся доступным.
        if self.instance.pk:
            available = Bus.objects.filter(
                Q(passport__isnull=True) | Q(pk=self.instance.bus_id)
            )
        else:
            available = Bus.objects.filter(passport__isnull=True)
        self.fields['bus'].queryset = available.order_by('model_name')
        self.fields['bus'].empty_label = '— выберите автобус —'

    def clean_issue_date(self):
        value = self.cleaned_data['issue_date']
        if value > date.today():
            raise forms.ValidationError('Дата выдачи не может быть в будущем')
        return value

    def clean(self):
        cleaned = super().clean()
        issue_date = cleaned.get('issue_date')
        valid_until = cleaned.get('valid_until')
        if issue_date and valid_until and valid_until <= issue_date:
            self.add_error('valid_until', 'Дата окончания должна быть позже даты выдачи')
        bus = cleaned.get('bus')
        if bus and not self.instance.pk:
            if hasattr(bus, 'passport'):
                self.add_error('bus', 'У этого автобуса уже есть техпаспорт')
        return cleaned


# ==================== РЕЙС ====================

class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = [
            'bus', 'from_city', 'to_city', 'price',
            'travel_time', 'departure_date', 'departure_time',
        ]
        widgets = {
            'from_city': forms.TextInput(attrs={'placeholder': 'Ярославль'}),
            'to_city': forms.TextInput(attrs={'placeholder': 'Москва'}),
            'travel_time': TimeInput(),
            'departure_date': DateInput(),
            'departure_time': TimeInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bus'].queryset = Bus.objects.all().order_by('model_name')
        self.fields['bus'].empty_label = '— выберите автобус —'

    def clean(self):
        cleaned = super().clean()
        from_city = (cleaned.get('from_city') or '').strip()
        to_city = (cleaned.get('to_city') or '').strip()
        if from_city and to_city and from_city.lower() == to_city.lower():
            self.add_error('to_city', 'Города отправления и прибытия должны различаться')
        price = cleaned.get('price')
        if price is not None and price <= 0:
            self.add_error('price', 'Цена должна быть больше нуля')

        departure_date = cleaned.get('departure_date')
        departure_time = cleaned.get('departure_time')
        if not self.instance.pk and departure_date and departure_time:
            moment = datetime.combine(departure_date, departure_time)
            if moment < datetime.now():
                self.add_error('departure_time', 'Нельзя создать рейс в прошлом')

        # Нельзя пересадить рейс на автобус, где не хватит мест
        # для уже проданных билетов.
        bus = cleaned.get('bus')
        if self.instance.pk and bus and bus.pk != self.instance.bus_id:
            tickets = self.instance.tickets.exclude(status='cancelled')
            if tickets.count() > bus.seats or tickets.filter(seat__gt=bus.seats).exists():
                self.add_error(
                    'bus',
                    f'В автобусе {bus.seats} мест, а на рейс уже продано '
                    f'{tickets.count()} билетов.',
                )
        return cleaned


# ==================== БИЛЕТ (ГЛАВНАЯ ТАБЛИЦА) ====================

class TicketForm(forms.Form):
    """Форма оформления билета: данные пассажира заполняются всегда."""
    full_name = forms.CharField(
        label='ФИО пассажира', max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Иванов Иван Иванович'}),
    )
    phone = forms.CharField(
        label='Телефон', max_length=20,
        widget=forms.TextInput(attrs={'placeholder': '+7 (999) 123-45-67'}),
    )
    email = forms.EmailField(
        label='Почта',
        widget=forms.EmailInput(attrs={'placeholder': 'ivanov@example.ru'}),
    )
    birth_date = forms.DateField(label='Дата рождения', widget=DateInput())
    trip = forms.ModelChoiceField(
        queryset=Trip.objects.none(), label='Рейс',
        empty_label='— выберите рейс —',
    )
    seat = forms.IntegerField(
        label='Место', min_value=1, max_value=100,
        widget=forms.NumberInput(attrs={'min': 1, 'max': 100}),
    )
    baggage = forms.BooleanField(label='Багаж (+300 ₽)', required=False)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        self.fields['trip'].queryset = Trip.objects.select_related('bus').order_by(
            'departure_date', 'departure_time'
        )
        self._passenger_cleaned = None

        # При редактировании подставляем данные пассажира из билета.
        if self.instance and not self.is_bound:
            passenger = self.instance.passenger
            self.initial.update({
                'full_name': passenger.full_name,
                'phone': passenger.phone,
                'email': passenger.email,
                'birth_date': passenger.birth_date,
                'trip': self.instance.trip_id,
                'seat': self.instance.seat,
                'baggage': self.instance.baggage,
            })

    def clean(self):
        cleaned = super().clean()

        # Данные пассажира обязательны и проверяются как в PassengerForm.
        required = all(cleaned.get(k) for k in ('full_name', 'phone', 'email', 'birth_date'))
        if required:
            passenger_form = PassengerForm(data={
                'full_name': cleaned.get('full_name'),
                'phone': cleaned.get('phone'),
                'email': cleaned.get('email'),
                'birth_date': cleaned.get('birth_date'),
            })
            if passenger_form.is_valid():
                self._passenger_cleaned = passenger_form.cleaned_data
            else:
                for field, errors in passenger_form.errors.items():
                    for error in errors:
                        self.add_error(field, error)

        trip = cleaned.get('trip')
        seat = cleaned.get('seat')
        if trip and seat:
            if seat > trip.bus.seats:
                self.add_error('seat', f'В автобусе всего {trip.bus.seats} мест')

            others = Ticket.objects.filter(trip=trip).exclude(status='cancelled')
            if self.instance and self.instance.pk:
                others = others.exclude(pk=self.instance.pk)

            if others.filter(seat=seat).exists():
                self.add_error('seat', 'Это место уже занято на выбранном рейсе')

            # Проверяем общее количество проданных билетов.
            # При редактировании билета на том же рейсе количество не увеличивается.
            moving = not (self.instance and self.instance.pk) or (
                self.instance.trip_id != trip.pk
            )
            if moving and others.count() >= trip.bus.seats:
                self.add_error('trip', 'На этот рейс больше нет свободных мест')

        if trip and not (self.instance and self.instance.pk) and trip.departure_date < date.today():
            self.add_error('trip', 'Нельзя оформить билет на прошедший рейс')

        return cleaned

    def save(self, commit=True):
        data = self.cleaned_data
        ticket = self.instance or Ticket()

        if self._passenger_cleaned:
            pd = self._passenger_cleaned
            if ticket.pk and ticket.passenger_id:
                passenger = ticket.passenger
                passenger.full_name = pd['full_name']
                passenger.phone = pd['phone']
                passenger.email = pd['email']
                passenger.birth_date = pd['birth_date']
            else:
                passenger = Passenger(
                    full_name=pd['full_name'],
                    phone=pd['phone'],
                    email=pd['email'],
                    birth_date=pd['birth_date'],
                )
            if commit:
                passenger.save()
            ticket.passenger = passenger

        ticket.trip = data['trip']
        ticket.seat = data['seat']
        ticket.baggage = data['baggage']

        if commit:
            ticket.save()
        return ticket
