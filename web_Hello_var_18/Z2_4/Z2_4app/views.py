from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from .models import Bus, BusPassport

def passport_create(request):
    if request.method == "POST":
        passport = BusPassport()
        bus_id = request.POST.get("bus")
        passport.bus = Bus.objects.get(id=bus_id)
        passport.serial_number = request.POST.get("serial_number")
        passport.issue_date = request.POST.get("issue_date")
        passport.save()
        return HttpResponseRedirect("/")

    passports = BusPassport.objects.all()
    free_buses = Bus.objects.filter(passport__isnull=True)
    return render(request, "passport_create.html", {"passports": passports, "free_buses": free_buses})

def passport_edit(request, id):
    try:
        passport = BusPassport.objects.get(pk=id)
        if request.method == "POST":
            passport.serial_number = request.POST.get("serial_number")
            passport.issue_date = request.POST.get("issue_date")
            passport.save()
            return HttpResponseRedirect("/")
        else:
            return render(request, "passport_edit.html", {"passport": passport})
    except BusPassport.DoesNotExist:
        return HttpResponseNotFound("<h2>Паспорт не найден</h2>")

def passport_delete(request, id):
    try:
        passport = BusPassport.objects.get(pk=id)
        passport.delete()
        return HttpResponseRedirect("/")
    except BusPassport.DoesNotExist:
        return HttpResponseNotFound("<h2>Паспорт не найден</h2>")

def bus_create(request):
    if request.method == "POST":
        bus = Bus()
        bus.name = request.POST.get("name")
        bus.mest = request.POST.get("mest")
        bus.save()
        return HttpResponseRedirect("/buses/")

    buses = Bus.objects.all()
    return render(request, "bus_create.html", {"buses": buses})

def bus_edit(request, id):
    try:
        bus = Bus.objects.get(id=id)
        if request.method == "POST":
            bus.name = request.POST.get("name")
            bus.mest = request.POST.get("mest")
            bus.save()
            return HttpResponseRedirect("/buses/")
        else:
            return render(request, "bus_edit.html", {"bus": bus})
    except Bus.DoesNotExist:
        return HttpResponseNotFound("<h2>Автобус не найден</h2>")

def bus_delete(request, id):
    try:
        bus = Bus.objects.get(id=id)
        bus.delete() # При удалении автобуса удалится и его паспорт (CASCADE)
        return HttpResponseRedirect("/buses/")
    except Bus.DoesNotExist:
        return HttpResponseNotFound("<h2>Автобус не найден</h2>")