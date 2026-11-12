from django.urls import path
from . import views

urlpatterns = [
    path('', views.ticket_create, name='ticket_home'),
    path('tickets/delete/<int:id>/', views.ticket_delete, name='ticket_delete'),

    path('passengers/', views.passenger_create, name='passenger_list'),
    path('passengers/delete/<int:id>/', views.passenger_delete, name='passenger_delete'),

    path('trips/', views.trip_create, name='trip_list'),
    path('trips/delete/<int:id>/', views.trip_delete, name='trip_delete'),
]