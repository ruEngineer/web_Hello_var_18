from datetime import date

from django import forms
from django.core.validators import RegexValidator

from . import tablica_io as tablica

# Дополнительные услуги и их цена за одно место, руб.
EXTRA_PRICES = {'Багаж': 300, 'Страховка': 150}


class TicketOrderForm(forms.Form):
    # простые данные
    passenger = forms.CharField(label='ФИО пассажира', max_length=100)
    phone = forms.CharField(label='Телефон', max_length=20,
                            validators=[RegexValidator(r'^\+?[\d\s\-()]{10,18}$', 'Введите корректный номер телефона')])
    travel_date = forms.DateField(label='Дата поездки', initial=date.today,
                                  widget=forms.DateInput(attrs={'type': 'date'}))
    seats = forms.IntegerField(label='Количество мест', min_value=1, max_value=10, initial=1)
    # одинарный выбор из списка
    route = forms.ChoiceField(label='Рейс')
    operator = forms.ChoiceField(label='Оператор')
    # множественный выбор
    extras = forms.MultipleChoiceField(label='Дополнительные услуги', required=False,
                                       choices=[(name, f'{name} (+{price} ₽)') for name, price in EXTRA_PRICES.items()],
                                       widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # списки для выбора берутся из файлов папки tablica
        self.fields['route'].choices = [
            (r['number'], f"{r['number']}: {r['from_city']} — {r['to_city']}, {r['departure']} ({r['price']} ₽)")
            for r in tablica.routes()
        ]
        self.fields['operator'].choices = [(name, f'{name} — {place}') for name, place in tablica.operators()]

    def clean_travel_date(self):
        value = self.cleaned_data['travel_date']
        if value < date.today():
            raise forms.ValidationError('Дата поездки не может быть в прошлом')
        return value

    def clean(self):
        data = super().clean()
        route_number, travel_date = data.get('route'), data.get('travel_date')
        if route_number and travel_date:
            route = tablica.find_route(int(route_number))
            full, short = tablica.days()[str(travel_date.isoweekday())]
            if short not in route['days_list']:
                self.add_error('travel_date', f"Рейс {route['number']} не ходит в этот день: {full.lower()} (дни рейса: {route['days']})")
        return data
