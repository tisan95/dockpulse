from django.urls import path
from . import views

urlpatterns = [
    path('checkin/',                          views.checkin,          name='checkin'),
    path('checkout/',                         views.checkout,         name='checkout'),
    path('pantalla/',                         views.pantalla,         name='pantalla'),
    path('dashboard/',                        views.dashboard,        name='dashboard'),
    path('visita/<int:visit_id>/estado/',     views.cambiar_estado,   name='cambiar_estado'),
    path('visita/<int:visit_id>/incidencia/', views.incidencia_crear, name='incidencia_crear'),
    path('',                                  views.pantalla,         name='home'),
]
