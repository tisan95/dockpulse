from django.urls import path
from . import views

urlpatterns = [
    path('checkin/',   views.checkin,   name='checkin'),
    path('checkout/',  views.checkout,  name='checkout'),
    path('pantalla/',  views.pantalla,  name='pantalla'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('',           views.pantalla,  name='home'),
]