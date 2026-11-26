from datetime import date

from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import BusForm, BusPassportForm, PassengerForm, TicketForm, TripForm
from .models import Bus, BusPassport, Passenger, Ticket, Trip


# ==================== ГЛАВНАЯ СТРАНИЦА ====================

def index(request):
    trips = list(
        Trip.objects.select_related('bus')
        .filter(departure_date__gte=timezone.localdate())
        .annotate(sold=Count('tickets', filter=~Q(tickets__status='cancelled')))
        .order_by('departure_date', 'departure_time')
    )
    for trip in trips:
        trip.free_seats = max(0, trip.bus.seats - trip.sold)
    return render(request, 'index.html', {'trips': trips})


# ==================== CRUD: ПАССАЖИРЫ ====================

def passenger_list(request):
    passengers = Passenger.objects.order_by('full_name')
    return render(request, 'passenger_list.html', {'passengers': passengers})


def passenger_create(request):
    form = PassengerForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        passenger = form.save()
        messages.success(request, f'Пассажир «{passenger.full_name}» добавлен')
        return redirect('passenger_list')
    return render(request, 'form.html', {
        'form': form,
        'title': 'Новый пассажир',
        'header': 'Добавление пассажира',
        'back_url': 'passenger_list',
        'submit_label': 'Сохранить пассажира',
    })


def passenger_edit(request, pk):
    passenger = get_object_or_404(Passenger, pk=pk)
    form = PassengerForm(
        request.POST or None, request.FILES or None, instance=passenger,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Данные пассажира обновлены')
        return redirect('passenger_list')
    return render(request, 'form.html', {
        'form': form,
        'title': f'Пассажир: {passenger.full_name}',
        'header': 'Редактирование пассажира',
        'back_url': 'passenger_list',
        'submit_label': 'Сохранить изменения',
    })


def passenger_delete(request, pk):
    passenger = get_object_or_404(Passenger, pk=pk)
    if request.method == 'POST':
        passenger.delete()
        messages.success(request, 'Пассажир удалён')
        return redirect('passenger_list')
    return render(request, 'confirm_delete.html', {
        'object': passenger,
        'title': 'Удаление пассажира',
        'back_url': 'passenger_list',
        'warning': 'Вместе с пассажиром удалятся все его билеты.',
    })


# ==================== CRUD: АВТОБУСЫ (ТРАНСПОРТ) ====================

def bus_list(request):
    buses = (
        Bus.objects.select_related('passport')
        .annotate(trips_count=Count('trips'))
        .order_by('model_name')
    )
    return render(request, 'bus_list.html', {'buses': buses})


def bus_create(request):
    form = BusForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        bus = form.save()
        messages.success(request, f'Автобус {bus.model_name} добавлен')
        return redirect('bus_list')
    return render(request, 'form.html', {
        'form': form,
        'title': 'Новый автобус',
        'header': 'Добавление автобуса',
        'back_url': 'bus_list',
        'submit_label': 'Сохранить автобус',
    })


def bus_edit(request, pk):
    bus = get_object_or_404(Bus, pk=pk)
    form = BusForm(request.POST or None, request.FILES or None, instance=bus)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Автобус обновлён')
        return redirect('bus_list')
    return render(request, 'form.html', {
        'form': form,
        'title': f'Автобус {bus.model_name}',
        'header': 'Редактирование автобуса',
        'back_url': 'bus_list',
        'submit_label': 'Сохранить изменения',
    })


def bus_delete(request, pk):
    bus = get_object_or_404(Bus, pk=pk)
    if request.method == 'POST':
        bus.delete()
        messages.success(request, 'Автобус удалён')
        return redirect('bus_list')
    return render(request, 'confirm_delete.html', {
        'object': bus,
        'title': 'Удаление автобуса',
        'back_url': 'bus_list',
        'warning': 'Вместе с автобусом удалятся его техпаспорт и все рейсы с билетами.',
    })


# ==================== CRUD: ТЕХПАСПОРТА (1 К 1) ====================

def buspassport_list(request):
    passports = BusPassport.objects.select_related('bus').order_by('-issue_date')
    return render(request, 'buspassport_list.html', {'passports': passports})


def buspassport_create(request):
    form = BusPassportForm(request.POST or None, request.FILES or None, initial={'issue_date': date.today()})
    if request.method == 'POST' and form.is_valid():
        passport = form.save()
        messages.success(request, f'Техпаспорт {passport.serial_number} выдан')
        return redirect('buspassport_list')
    return render(request, 'form.html', {
        'form': form,
        'title': 'Новый техпаспорт',
        'header': 'Выдача техпаспорта',
        'back_url': 'buspassport_list',
        'submit_label': 'Выдать техпаспорт',
        'hint': 'В списке показаны только автобусы, у которых ещё нет техпаспорта.',
    })


def buspassport_edit(request, pk):
    passport = get_object_or_404(BusPassport, pk=pk)
    form = BusPassportForm(request.POST or None, request.FILES or None, instance=passport)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Техпаспорт обновлён')
        return redirect('buspassport_list')
    return render(request, 'form.html', {
        'form': form,
        'title': f'Техпаспорт {passport.serial_number}',
        'header': 'Редактирование техпаспорта',
        'back_url': 'buspassport_list',
        'submit_label': 'Сохранить изменения',
    })


def buspassport_delete(request, pk):
    passport = get_object_or_404(BusPassport, pk=pk)
    if request.method == 'POST':
        passport.delete()
        messages.success(request, 'Техпаспорт удалён')
        return redirect('buspassport_list')
    return render(request, 'confirm_delete.html', {
        'object': passport,
        'title': 'Удаление техпаспорта',
        'back_url': 'buspassport_list',
    })


# ==================== CRUD: РЕЙСЫ ====================

def trip_list(request):
    trips = (
        Trip.objects.select_related('bus')
        .annotate(tickets_count=Count('tickets'))
        .order_by('departure_date', 'departure_time')
    )
    return render(request, 'trip_list.html', {'trips': trips})


def trip_create(request):
    form = TripForm(request.POST or None, initial={'departure_date': date.today()})
    if request.method == 'POST' and form.is_valid():
        trip = form.save()
        messages.success(request, f'Рейс {trip} создан')
        return redirect('trip_list')
    return render(request, 'form.html', {
        'form': form,
        'title': 'Новый рейс',
        'header': 'Добавление рейса',
        'back_url': 'trip_list',
        'submit_label': 'Создать рейс',
        'hint': 'Автобус выбирается из справочника. Мест в рейсе столько, сколько у автобуса.',
    })


def trip_edit(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    form = TripForm(request.POST or None, instance=trip)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Рейс обновлён')
        return redirect('trip_list')
    return render(request, 'form.html', {
        'form': form,
        'title': f'Рейс {trip}',
        'header': 'Редактирование рейса',
        'back_url': 'trip_list',
        'submit_label': 'Сохранить изменения',
    })


def trip_delete(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    if request.method == 'POST':
        trip.delete()
        messages.success(request, 'Рейс удалён')
        return redirect('trip_list')
    return render(request, 'confirm_delete.html', {
        'object': trip,
        'title': 'Удаление рейса',
        'back_url': 'trip_list',
        'warning': 'Вместе с рейсом удалятся все билеты на него.',
    })


# ==================== CRUD: БИЛЕТЫ (ГЛАВНАЯ ТАБЛИЦА) ====================

def ticket_list(request):
    tickets = (
        Ticket.objects.select_related('passenger', 'trip')
        .order_by('-created_at')
    )
    return render(request, 'ticket_list.html', {'tickets': tickets})


def ticket_detail(request, pk):
    ticket = get_object_or_404(
        Ticket.objects.select_related('passenger', 'trip', 'trip__bus'), pk=pk,
    )
    passport = getattr(ticket.trip.bus, 'passport', None)
    return render(request, 'ticket_detail.html', {'ticket': ticket, 'passport': passport})


def ticket_pay(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        if ticket.status == 'booked':
            ticket.pay()
            messages.success(request, f'Билет №{ticket.pk} оплачен')
        elif ticket.status == 'paid':
            messages.warning(request, 'Билет уже оплачен')
        else:
            messages.error(request, 'Нельзя оплатить отменённый билет')
    return redirect('ticket_detail', pk=ticket.pk)


def ticket_refund(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        if ticket.status != 'cancelled':
            amount = ticket.total
            ticket.refund()
            messages.success(
                request,
                f'Возврат по билету №{ticket.pk} оформлен на {amount} ₽',
            )
        else:
            messages.warning(request, 'Билет уже возвращён')
    return redirect('ticket_detail', pk=ticket.pk)


def ticket_create(request):
    initial = {}
    trip_id = request.GET.get('trip', '')
    if trip_id.isdigit():
        initial['trip'] = trip_id
    form = TicketForm(request.POST or None, request.FILES or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        ticket = form.save()
        messages.success(request, f'Билет №{ticket.pk} оформлен')
        return redirect('ticket_detail', pk=ticket.pk)
    return render(request, 'form.html', {
        'form': form,
        'title': 'Новый билет',
        'header': 'Оформление билета',
        'back_url': 'ticket_list',
        'submit_label': 'Оформить билет',
        'hint': 'Заполните данные пассажира — они обязательны. Стоимость рассчитается автоматически.',
    })


def ticket_edit(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    form = TicketForm(request.POST or None, request.FILES or None, instance=ticket)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Билет обновлён')
        return redirect('ticket_detail', pk=ticket.pk)
    return render(request, 'form.html', {
        'form': form,
        'title': f'Билет №{ticket.pk}',
        'header': 'Редактирование билета',
        'back_url': 'ticket_detail',
        'back_pk': ticket.pk,
        'submit_label': 'Сохранить изменения',
    })


def ticket_delete(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        ticket.delete()
        messages.success(request, 'Билет удалён')
        return redirect('ticket_list')
    return render(request, 'confirm_delete.html', {
        'object': ticket,
        'title': 'Удаление билета',
        'back_url': 'ticket_detail',
        'back_pk': ticket.pk,
    })
