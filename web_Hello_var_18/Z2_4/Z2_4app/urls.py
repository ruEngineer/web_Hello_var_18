from django.urls import path
from . import views

urlpatterns = [
    path('', views.passport_create, name='home'),
    path('passports/edit/<int:id>/', views.passport_edit, name='passport_edit'),
    path('passports/delete/<int:id>/', views.passport_delete, name='passport_delete'),

    path('buses/', views.bus_create, name='bus_list'),
    path('buses/edit/<int:id>/', views.bus_edit, name='bus_edit'),
    path('buses/delete/<int:id>/', views.bus_delete, name='bus_delete'),
]