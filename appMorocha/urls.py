from django.urls import path
from . import views

urlpatterns = [
    path('',views.usuario),
    path('login/',views.login),
    path('registrarPedido/',views.registrarPedido),
    path('usuario/',views.usuario),
    path('procesarUsuario/',views.procesarUsuario),
    path('eliminarUsuario/<str:nombreUsuario>/',views.eliminarUsuario,name='eliminarUsuario'),
]