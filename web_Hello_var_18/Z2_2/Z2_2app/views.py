from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from .models import Route, Trip

# ==================== CRUD ДЛЯ МАРШРУТОВ ====================

def route_create(request):
    if request.method == "POST":
        route = Route()
        route.number = request.POST.get("number")
        route.from_city = request.POST.get("from_city")
        route.to_city = request.POST.get("to_city")
        route.price = request.POST.get("price")
        route.save()
        return HttpResponseRedirect("/") # Возврат на главную (список маршрутов)

    routes = Route.objects.all()
    return render(request, "route_create.html", {"routes": routes})

def route_edit(request, id):
    try:
        route = Route.objects.get(id=id)
        if request.method == "POST":
            route.number = request.POST.get("number")
            route.from_city = request.POST.get("from_city")
            route.to_city = request.POST.get("to_city")
            route.price = request.POST.get("price")
            route.save()
            return HttpResponseRedirect("/")
        else:
            return render(request, "route_edit.html", {"route": route})
    except Route.DoesNotExist:
        return HttpResponseNotFound("<h2>Маршрут не найден</h2>")

def route_delete(request, id):
    try:
        route = Route.objects.get(id=id)
        route.delete() # При удалении маршрута удалятся и его рейсы (CASCADE)
        return HttpResponseRedirect("/")
    except Route.DoesNotExist:
        return HttpResponseNotFound("<h2>Маршрут не найден</h2>")


# ==================== CRUD ДЛЯ РЕЙСОВ ====================

def trip_create(request):
    if request.method == "POST":
        trip = Trip()
        # Получаем id маршрута из выпадающего списка
        route_id = request.POST.get("route")
        trip.route = Route.objects.get(id=route_id)
        trip.departure_time = request.POST.get("departure_time")
        trip.bus_name = request.POST.get("bus_name")
        trip.save()
        return HttpResponseRedirect("/trips/")

    trips = Trip.objects.all()
    routes = Route.objects.all() # Нужны для выпадающего списка
    return render(request, "trip_create.html", {"trips": trips, "routes": routes})

def trip_edit(request, id):
    try:
        trip = Trip.objects.get(id=id)
        if request.method == "POST":
            route_id = request.POST.get("route")
            trip.route = Route.objects.get(id=route_id)
            trip.departure_time = request.POST.get("departure_time")
            trip.bus_name = request.POST.get("bus_name")
            trip.save()
            return HttpResponseRedirect("/trips/")
        else:
            routes = Route.objects.all()
            return render(request, "trip_edit.html", {"trip": trip, "routes": routes})
    except Trip.DoesNotExist:
        return HttpResponseNotFound("<h2>Рейс не найден</h2>")

def trip_delete(request, id):
    try:
        trip = Trip.objects.get(id=id)
        trip.delete()
        return HttpResponseRedirect("/trips/")
    except Trip.DoesNotExist:
        return HttpResponseNotFound("<h2>Рейс не найден</h2>")