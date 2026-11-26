from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from .models import Passenger, Trip, Ticket

def ticket_create(request):
    if request.method == "POST":
        ticket = Ticket()
        passenger_id = request.POST.get("passenger")
        trip_id = request.POST.get("trip")

        ticket.passenger = Passenger.objects.get(id=passenger_id)
        ticket.trip = Trip.objects.get(id=trip_id)
        ticket.seat = request.POST.get("seat")
        ticket.save()
        return HttpResponseRedirect("/")

    tickets = Ticket.objects.all()
    passengers = Passenger.objects.all()
    trips = Trip.objects.all()
    return render(request, "ticket_create.html", {"tickets": tickets, "passengers": passengers, "trips": trips})


def ticket_delete(request, id):
    try:
        ticket = Ticket.objects.get(id=id)
        ticket.delete()
        return HttpResponseRedirect("/")
    except Ticket.DoesNotExist:
        return HttpResponseNotFound("<h2>Билет не найден</h2>")


def passenger_create(request):
    if request.method == "POST":
        p = Passenger()
        p.full_name = request.POST.get("full_name")
        p.phone = request.POST.get("phone")
        p.save()
        return HttpResponseRedirect("/passengers/")

    passengers = Passenger.objects.all()
    return render(request, "passenger_create.html", {"passengers": passengers})


def passenger_delete(request, id):
    try:
        p = Passenger.objects.get(id=id)
        p.delete()
        return HttpResponseRedirect("/passengers/")
    except Passenger.DoesNotExist:
        return HttpResponseNotFound("<h2>Пассажир не найден</h2>")


def trip_create(request):
    if request.method == "POST":
        t = Trip()
        t.name = request.POST.get("name")
        t.price = request.POST.get("price")
        t.save()
        return HttpResponseRedirect("/trips/")

    trips = Trip.objects.all()
    return render(request, "trip_create.html", {"trips": trips})


def trip_delete(request, id):
    try:
        t = Trip.objects.get(id=id)
        t.delete()
        return HttpResponseRedirect("/trips/")
    except Trip.DoesNotExist:
        return HttpResponseNotFound("<h2>Рейс не найден</h2>")