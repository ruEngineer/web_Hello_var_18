from datetime import date

from django import forms
from django.core.validators import RegexValidator

from . import tablica_io as tablica

EXTRA_PRICES = {'Багаж': 300, 'Страховка': 150}


class TicketOrderForm(forms.Form):
    passenger = forms.CharField(label='ФИО пассажира', max_length=100)
    phone = forms.CharField(label='Телефон', max_length=20,
                            validators=[RegexValidator(r'^\+?[\d\s\-()]{10,18}$', 'Введите корректный номер телефона')])
    travel_date = forms.DateField(label='Дата поездки', initial=date.today,
                                  widget=forms.DateInput(attrs={'type': 'date'}))
    seats = forms.IntegerField(label='Количество мест', min_value=1, max_value=10, initial=1)
    route = forms.ChoiceField(label='Рейс')

    extras = forms.MultipleChoiceField(label='Дополнительные услуги', required=False,
                                       choices=[(name, f'{name} (+{price} ₽)') for name, price in EXTRA_PRICES.items()],
                                       widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['route'].choices = [
            (r['number'], f"{r['number']}: {r['from_city']} — {r['to_city']}, {r['departure']} ({r['price']} ₽)")
            for r in tablica.routes()
        ]

    def clean_travel_date(self):
        value = self.cleaned_data['travel_date']
        if value < date.today():
            raise forms.ValidationError('Дата поездки не может быть в прошлом')
        return value