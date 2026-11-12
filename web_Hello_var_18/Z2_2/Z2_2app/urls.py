from django.urls import path
from . import views

urlpatterns = [
    path('', views.route_create, name='home'),
    path('edit/<int:id>/', views.route_edit, name='route_edit'),
    path('delete/<int:id>/', views.route_delete, name='route_delete'),

    path('trips/', views.trip_create, name='trip_list'),
    path('trips/edit/<int:id>/', views.trip_edit, name='trip_edit'),
    path('trips/delete/<int:id>/', views.trip_delete, name='trip_delete'),
]