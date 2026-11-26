from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='home'),

    # Пассажиры
    path('passengers/', views.passenger_list, name='passenger_list'),
    path('passengers/add/', views.passenger_create, name='passenger_create'),
    path('passengers/<int:pk>/edit/', views.passenger_edit, name='passenger_edit'),
    path('passengers/<int:pk>/delete/', views.passenger_delete, name='passenger_delete'),

    # Автобусы (транспорт)
    path('buses/', views.bus_list, name='bus_list'),
    path('buses/add/', views.bus_create, name='bus_create'),
    path('buses/<int:pk>/edit/', views.bus_edit, name='bus_edit'),
    path('buses/<int:pk>/delete/', views.bus_delete, name='bus_delete'),

    # Техпаспорта (1 к 1 с автобусом)
    path('passports/', views.buspassport_list, name='buspassport_list'),
    path('passports/add/', views.buspassport_create, name='buspassport_create'),
    path('passports/<int:pk>/edit/', views.buspassport_edit, name='buspassport_edit'),
    path('passports/<int:pk>/delete/', views.buspassport_delete, name='buspassport_delete'),

    # Рейсы
    path('trips/', views.trip_list, name='trip_list'),
    path('trips/add/', views.trip_create, name='trip_create'),
    path('trips/<int:pk>/edit/', views.trip_edit, name='trip_edit'),
    path('trips/<int:pk>/delete/', views.trip_delete, name='trip_delete'),

    # Билеты
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/add/', views.ticket_create, name='ticket_create'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('tickets/<int:pk>/pay/', views.ticket_pay, name='ticket_pay'),
    path('tickets/<int:pk>/refund/', views.ticket_refund, name='ticket_refund'),
    path('tickets/<int:pk>/edit/', views.ticket_edit, name='ticket_edit'),
    path('tickets/<int:pk>/delete/', views.ticket_delete, name='ticket_delete'),
]
