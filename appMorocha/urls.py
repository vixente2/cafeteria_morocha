from django.urls import path
from . import views

urlpatterns = [
    # Rutas para las vistas
    path('',views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('inicio/',views.inicio, name='inicio'),
    path('estadoPedido/',views.estadoPedido, name='estadoPedido'),
    path('usuario/',views.usuario),
    path('registrarPedido/',views.registrarPedido, name='registrarPedido'),
    path('ingresarProducto/',views.ingresarProducto, name='ingresarProducto'),
    path('ingresarMesa/',views.ingresarMesa, name='ingresarMesa'),
    # Acciones para Pedidos
    path('detallePedido/<int:id_pedido>/',views.detallePedido, name='detallePedido'),
    path('eliminarPedido/<int:id_pedido>/', views.eliminarPedido, name='eliminarPedido'),
    path('actualizar-estado/<int:id_pedido>/<str:estado>/', views.actualizarEstadoPedido, name='actualizarEstadoPedido'),

    # Acciones para Usuario
    path('procesarUsuario/',views.procesarUsuario),
    path('editarUsuario/', views.editarUsuario, name='editarUsuario'),
    path('eliminarUsuario/<str:nombreUsuario>/',views.eliminarUsuario,name='eliminarUsuario'),
    # Acciones para Productos
    path('procesarProducto/',views.procesarProducto),
    path('editarProducto/',                      views.editarProducto,    name='editarProducto'),
    path('eliminarProducto/<int:id_producto>/',  views.eliminarProducto,  name='eliminarProducto')
   

]