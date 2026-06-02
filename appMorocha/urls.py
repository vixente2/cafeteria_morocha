from django.urls import path
from . import views

urlpatterns = [
    path('',views.inicio, name='inicio'),
    path('login/',views.login, name='login'),
    path('registrarPedido/',views.registrarPedido, name='registrarPedido'),
    path('detallePedido/<int:id_pedido>/',views.detallePedido, name='detallePedido'),
    path('eliminarPedido/<int:id_pedido>/', views.eliminarPedido, name='eliminarPedido'),

]