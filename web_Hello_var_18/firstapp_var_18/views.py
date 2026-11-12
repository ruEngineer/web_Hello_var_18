from datetime import date, datetime

from django.http import *
from django.shortcuts import redirect, render
from django.urls import reverse

from . import tablica_io as tablica
from .forms import EXTRA_PRICES, TicketOrderForm
from web_Hello_var_18.Z2_1.Z2_1app.models import Bus


def index(request):
    routes = tablica.routes()
    _, orders = tablica.orders()

    db_buses = Bus.objects.all()

    context = {
        'routes': routes,
        'week': tablica.days(),
        'company': 'АвтоБилет-18',
        'routes_count': len(routes),
        'avg_price': round(sum(r['price'] for r in routes) / len(routes)) if routes else 0,
        'orders_count': len(orders),
        'is_open': 6 <= datetime.now().hour < 23,
        'today': date.today(),
        'popular': routes[min(8, len(routes) - 1)] if routes else None,
        'db_buses': db_buses,
    }
    return render(request, 'firstapp_var_18/index.html', context)


def route_detail(request, number):
    route = tablica.find_route(number)
    if route is None:
        raise Http404(f'Рейс {number} не найден')
    buses = {b['name']: b for b in tablica.bus_types()}
    return render(request, 'firstapp_var_18/route_detail.html', {'route': route, 'bus': buses.get(route['bus'])})


def routes_by_day(request, day):
    week = tablica.days()
    full, short = week[day]
    found = [r for r in tablica.routes() if short in r['days_list']]
    return render(request, 'firstapp_var_18/routes.html', {
        'routes': found, 'subtitle': f'Рейсы, которые ходят: {full.lower()}', 'week': week, 'active_day': day,
    })


def buses(request, kind='все'):
    all_buses = tablica.bus_types()
    kinds = sorted({b['kind'] for b in all_buses})
    items = all_buses if kind == 'все' else [b for b in all_buses if b['kind'] == kind]
    return render(request, 'firstapp_var_18/buses.html', {'buses': items, 'kind': kind, 'kinds': kinds})


def orders(request):
    header, rows = tablica.orders()
    return render(request, 'firstapp_var_18/orders.html', {'header': header, 'rows': rows})

def order_new(request):
    if request.method == 'POST':
        form = TicketOrderForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            route = tablica.find_route(int(cd['route']))
            per_seat = route['price'] + sum(EXTRA_PRICES[e] for e in cd['extras'])

            try:
                number = tablica.append_order({
                    'passenger': cd['passenger'], 'phone': cd['phone'],
                    'route': f"{route['number']} {route['from_city']} — {route['to_city']}",
                    'travel_date': cd['travel_date'], 'seats': cd['seats'],
                    'total': per_seat * cd['seats'], 'extras': cd['extras'],
                    # 'operator' удален
                })
            except PermissionError:
                form.add_error(None, 'Не удалось сохранить заказ: файл tablica/orders.xlsx открыт в другой программе.')
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


def create(request):
    if request.method == "POST":
        bus = Bus()
        bus.name = request.POST.get("name")
        bus.mest = request.POST.get("mest")
        bus.save()
        return HttpResponseRedirect("/create/")

    bus_list = Bus.objects.all()
    return render(request, "firstapp_var_18/create.html", {"bus_list": bus_list})

def edit(request, id):
    try:
        bus = Bus.objects.get(id=id)

        if request.method == "POST":
            bus.name = request.POST.get("name")
            bus.mest = request.POST.get("mest")
            bus.save()
            return HttpResponseRedirect("/")
        else:
            return render(request, "firstapp_var_18/edit.html", {"bus": bus})

    except Bus.DoesNotExist:
        return HttpResponseNotFound("<h2>Автобус не найден</h2>")

def delete(request,id):
    try:
        bus=Bus.objects.get(id=id)
        bus.delete()
        return HttpResponseRedirect("/")
    except Bus.DoesNotExist:
        return HttpResponseNotFound("<h2>Клиент не найден</h2>")
