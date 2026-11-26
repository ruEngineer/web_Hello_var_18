from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from .models import Bus

def create(request):
    if request.method == "POST":
        bus = Bus()
        bus.name = request.POST.get("name")
        bus.mest = request.POST.get("mest")
        bus.save()
        return HttpResponseRedirect("/")

    bus_list = Bus.objects.all()
    return render(request, "create.html", {"bus_list": bus_list})

def edit(request, id):
    try:
        bus = Bus.objects.get(id=id)
        if request.method == "POST":
            bus.name = request.POST.get("name")
            bus.mest = request.POST.get("mest")
            bus.save()
            return HttpResponseRedirect("/")
        else:
            return render(request, "edit.html", {"bus": bus})
    except Bus.DoesNotExist:
        return HttpResponseNotFound("<h2>Автобус не найден</h2>")

def delete(request, id):
    try:
        bus = Bus.objects.get(id=id)
        bus.delete()
        return HttpResponseRedirect("/")
    except Bus.DoesNotExist:
        return HttpResponseNotFound("<h2>Автобус не найден</h2>")