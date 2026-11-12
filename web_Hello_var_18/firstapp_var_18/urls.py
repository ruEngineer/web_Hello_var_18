from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('route/<int:number>/', views.route_detail, name='route_detail'),
    re_path(r'^day/(?P<day>[1-7])/$', views.routes_by_day, name='routes_by_day'),
    path('buses/', views.buses, name='buses'),
    path('buses/<str:kind>/', views.buses, name='buses_kind'),
    path('orders/', views.orders, name='orders'),
    path('order/new/', views.order_new, name='order_new'),
    path('order/done/', views.order_done, name='order_done'),
]
