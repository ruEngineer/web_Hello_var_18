from datetime import date, datetime

from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from . import tablica_io as tablica
from .forms import EXTRA_PRICES, TicketOrderForm


def index(request):
    """Главная: расписание рейсов и передача простых данных разных типов в шаблон."""
    routes = tablica.routes()
    _, orders = tablica.orders()
    context = {
        'routes': routes,                                # list словарей из routes.xlsx
        'week': tablica.days(),                          # dict из days.txt
        'company': 'АвтоБилет-18',                       # str
        'routes_count': len(routes),                     # int
        'avg_price': round(sum(r['price'] for r in routes) / len(routes)) if routes else 0,  # int
        'orders_count': len(orders),
        'is_open': 6 <= datetime.now().hour < 23,        # bool
        'today': date.today(),                           # date
        'popular': routes[min(8, len(routes) - 1)] if routes else None,  # dict (9-й рейс или последний)
    }
    return render(request, 'firstapp_var_18/index.html', context)


def route_detail(request, number):
    """path('route/<int:number>/') — параметр из маршрута."""
    route = tablica.find_route(number)
    if route is None:
        raise Http404(f'Рейс {number} не найден')
    buses = {b['name']: b for b in tablica.bus_types()}
    return render(request, 'firstapp_var_18/route_detail.html', {'route': route, 'bus': buses.get(route['bus'])})


def routes_by_day(request, day):
    """re_path(r'^day/(?P<day>[1-7])/$') — рейсы в выбранный день недели."""
    week = tablica.days()
    full, short = week[day]
    found = [r for r in tablica.routes() if short in r['days_list']]
    return render(request, 'firstapp_var_18/routes.html', {
        'routes': found, 'subtitle': f'Рейсы, которые ходят: {full.lower()}', 'week': week, 'active_day': day,
    })


def buses(request, kind='все'):
    """Параметр по умолчанию: /buses/ и /buses/<kind>/."""
    all_buses = tablica.bus_types()
    kinds = sorted({b['kind'] for b in all_buses})
    items = all_buses if kind == 'все' else [b for b in all_buses if b['kind'] == kind]
    return render(request, 'firstapp_var_18/buses.html', {'buses': items, 'kind': kind, 'kinds': kinds})


def orders(request):
    header, rows = tablica.orders()
    return render(request, 'firstapp_var_18/orders.html', {'header': header, 'rows': rows})


def order_new(request):
    """Форма заказа билета (POST) -> запись в orders.xlsx -> переадресация на результат (GET)."""
    if request.method == 'POST':
        form = TicketOrderForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            route = tablica.find_route(int(cd['route']))
            per_seat = route['price'] + sum(EXTRA_PRICES[e] for e in cd['extras'])
            day = tablica.days()[str(cd['travel_date'].isoweekday())][0]   # день недели по дате поездки
            try:
                number = tablica.append_order({
                    'passenger': cd['passenger'], 'phone': cd['phone'],
                    'route': f"{route['number']} {route['from_city']} — {route['to_city']}",
                    'travel_date': cd['travel_date'], 'day': day, 'seats': cd['seats'],
                    'total': per_seat * cd['seats'], 'operator': cd['operator'], 'extras': cd['extras'],
                })
            except PermissionError:   # файл открыт в Excel — Windows не даёт его перезаписать
                form.add_error(None, 'Не удалось сохранить заказ: файл tablica/orders.xlsx открыт в другой программе. '
                                     'Закройте его и отправьте форму ещё раз.')
            else:
                return redirect(f"{reverse('order_done')}?number={number}")
    else:
        initial = {}
        if request.GET.get('route', '').isdigit():
            initial['route'] = request.GET['route']
        form = TicketOrderForm(initial=initial)
    return render(request, 'firstapp_var_18/order_form.html', {'form': form})


def order_done(request):
    number = request.GET.get('number', '')
    order = tablica.find_order(int(number)) if number.isdigit() else None
    if order is None:
        return redirect('order_new')
    return render(request, 'firstapp_var_18/order_done.html', {'order': order, 'number': number})
