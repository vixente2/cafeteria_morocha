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
    path('listarPedidos/',views.listarPedidos, name='listarPedidos'),
    path('auditoria/', views.auditoriaLogin, name='auditoria'),
    # Acciones para Pedidos
    path('eliminarPedido/<int:id_pedido>/', views.eliminarPedido, name='eliminarPedido'),
    path('actualizar-estado/<int:id_pedido>/<str:estado>/', views.actualizarEstadoPedido, name='actualizarEstadoPedido'),

    # Acciones para Usuario
    path('procesarUsuario/',views.procesarUsuario),
    path('editarUsuario/', views.editarUsuario, name='editarUsuario'),
    path('eliminarUsuario/<str:nombreUsuario>/',views.eliminarUsuario,name='eliminarUsuario'),
    # Acciones para Productos
    path('procesarProducto/',views.procesarProducto),
    path('editarProducto/',                      views.editarProducto,    name='editarProducto'),
    path('eliminarProducto/<int:id_producto>/',  views.eliminarProducto,  name='eliminarProducto'),
   # Acciones para Mesa
    path('editarMesa/', views.editarMesa, name='editarMesa'),
    path('agregarMesa/', views.agregarMesa, name='agregarMesa'),
    path('eliminarMesa/', views.eliminarMesa, name='eliminarMesa'),
    # Api para exportar a google sheets
    path('exportar-sheets/', views.exportar_a_sheets, name='exportar_sheets'),
    path('dashboard/datos/', views.datos_dashboard, name='datos_dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
   # hora 
    path('hora/', views.hora_actual, name='hora')
]