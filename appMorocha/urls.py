from django.urls import path
from . import views

urlpatterns = [
    # Rutas para las vistas
    path('',views.inicio, name='inicio'),
    path('login/',views.login, name='login'),
    path('estadoPedido/',views.estadoPedido, name='estadoPedido'),
    path('usuario/',views.usuario),
    path('registrarPedido/',views.registrarPedido, name='registrarPedido'),
    path('ingresarProducto/',views.ingresarProducto, name='ingresarProducto'),
    path('ingresarMesa/',views.ingresarMesa, name='ingresarMesa'),
    # Rutas para las acciones
    path('detallePedido/<int:id_pedido>/',views.detallePedido, name='detallePedido'),
    path('eliminarPedido/<int:id_pedido>/', views.eliminarPedido, name='eliminarPedido'),
    # Guardar datos de usuarios y liminar usuario
    path('procesarUsuario/',views.procesarUsuario),
    path('eliminarUsuario/<str:nombreUsuario>/',views.eliminarUsuario,name='eliminarUsuario'),
    # Guardar datos de productos
    path('procesarProducto/',views.procesarProducto),
   

]