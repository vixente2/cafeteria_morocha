from django.shortcuts import render, redirect
from django.http import HttpResponse
from .db import ConexionDB

def inicio(request):
    return render(request, 'appMorocha/inicio.html')

def login(request):
    return render(request, 'appMorocha/login.html')

def registrarPedido(request):
    if request.method == 'POST':
        db = ConexionDB()
        db.ejecutar("INSERT INTO tb_pedido (fecha_pedido) VALUES (%s)", 
                    [request.POST['fecha_pedido']])
        resultado = db.consultar("SELECT MAX(id_pedido) as id FROM tb_pedido")
        id_pedido = resultado[0]['id']
        # Pasar id al template de detallePedido
        return redirect('detallePedido', id_pedido=id_pedido)

    # ── GET: cargar tabla de pedidos ──────────────────────────
    db = ConexionDB()
    context = {
        'pedidos': db.consultar("""
    SELECT p.id_pedido, p.fecha_pedido,
           m.num_mesa, c.nombre_cliente, e.nombre_estadopedido
    FROM tb_pedido p
    LEFT JOIN tb_detallepedido d ON p.id_pedido = d.id_pedido
    LEFT JOIN tb_mesa m          ON d.id_mesa = m.id_mesa
    LEFT JOIN tb_cliente c       ON d.id_cliente = c.id_cliente
    LEFT JOIN tb_estadopedido e  ON d.id_estadopedido = e.id_estadopedido
    ORDER BY p.id_pedido DESC
    """),
    }
    return render(request, 'appMorocha/registrarPedido.html', context)
   
def eliminarPedido(request, id_pedido):
    if request.method == 'GET':
        db = ConexionDB()
        # Primero eliminar los detalles asociados al pedido
        db.ejecutar("DELETE FROM tb_detallepedido WHERE id_pedido = %s", [id_pedido])
        # Luego eliminar el pedido
        db.ejecutar("DELETE FROM tb_pedido WHERE id_pedido = %s", [id_pedido])
        return redirect('registrarPedido')
       
def detallePedido(request, id_pedido):
    db = ConexionDB()
        # ── POST: guardar los datos ──────────────────────────
    if request.method == 'POST':
        # 2 — Insertar el detalle con todas las FK
        db.ejecutar("""
            INSERT INTO tb_detallepedido 
                (id_pedido, id_mesa, id_cliente, id_producto, id_usuario, id_estadopedido)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, [
            id_pedido,
            request.POST['id_mesa'],
            request.POST['id_cliente'],
            request.POST['id_producto'],
            request.POST['id_usuario'],
            request.POST['id_estadopedido'],
        ])

        return redirect('detallePedido', id_pedido=id_pedido)  # permite agregar más productos
    
    # cargar selects
    context = {
        'id_pedido': id_pedido,  # ← debe estar aquí obligatoriamente
        'mesas':     db.consultar("SELECT id_mesa, num_mesa FROM tb_mesa"),
        'clientes':  db.consultar("SELECT id_cliente, nombre_cliente FROM tb_cliente"),
        'productos': db.consultar("SELECT id_producto, nombre_producto, precio_producto FROM tb_producto"),
        'usuarios':  db.consultar("SELECT id_usuario, nombre_usuario FROM tb_usuario"),
        'estados':   db.consultar("SELECT id_estadopedido, nombre_estadopedido FROM tb_estadopedido"),
    }
    return render(request, 'appMorocha/detallePedido.html', context)