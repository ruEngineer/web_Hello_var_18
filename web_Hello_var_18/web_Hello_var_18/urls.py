from django.urls import include, path

urlpatterns = [
    path('', include('firstapp_var_18.urls')),
    path('firstapp_var_18_z2_1', include('firstapp_var_18_z2_1.urls')),
]
