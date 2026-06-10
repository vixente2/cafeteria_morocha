from django.shortcuts import render, redirect
from django.http import HttpResponse,  JsonResponse
from .db import ConexionDB
import json
# Create your views here.

def inicio(request):
    return render(request, 'appMorocha/inicio.html')

def login(request):
    return render(request, 'appMorocha/login.html')

def estadoPedido(request):
    cargarPedidos = cargarRegistrosPedidos()
    return render(request, 'appMorocha/estadoPedido.html', {'cargarPedidos': cargarPedidos})



def cargarRegistrosPedidos():
    conexion = ConexionDB()
    sintaxiSQL = """
    SELECT p.id_pedido, p.fecha_pedido,
           m.num_mesa, c.nombre_cliente, e.nombre_estadopedido
    FROM tb_pedido p
    LEFT JOIN tb_mesa         m ON p.id_mesa         = m.id_mesa
    LEFT JOIN tb_cliente      c ON p.id_cliente      = c.id_cliente
    LEFT JOIN tb_estadopedido e ON p.id_estadopedido = e.id_estadopedido
    ORDER BY 
        FIELD(e.nombre_estadopedido, 'Preparando', 'Espera', 'Listo', 'Finalizado'),
        p.id_pedido DESC
    """
    pedidos = conexion.consultar(sintaxiSQL)
    return pedidos



def registrarPedido(request):
    db = ConexionDB()

    if request.method == 'POST':
        # ── AJAX: agregar producto al detalle ──
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = json.loads(request.body)
            db.ejecutar("""
                INSERT INTO tb_detallepedido (id_pedido, id_producto, cantidad)
                VALUES (%s, %s, %s)
            """, [data['id_pedido'], data['id_producto'], data['cantidad']])

            # Devolver tabla actualizada
            detalles = db.consultar("""
                SELECT p.nombre_producto, d.cantidad, p.precio_producto,
                       (d.cantidad * p.precio_producto) as subtotal
                FROM tb_detallepedido d
                JOIN tb_producto p ON d.id_producto = p.id_producto
                WHERE d.id_pedido = %s
            """, [data['id_pedido']])

            return JsonResponse({'ok': True, 'detalles': detalles})

        # ── POST normal: crear pedido ──
        nombre_cliente = request.POST['nombre_cliente']

        db.ejecutar(
            "INSERT INTO tb_cliente (nombre_cliente) VALUES (%s)",
            [nombre_cliente]
        )
        resultado = db.consultar(
            "SELECT id_cliente FROM tb_cliente WHERE nombre_cliente = %s ORDER BY id_cliente DESC LIMIT 1",
            [nombre_cliente]
        )
        id_cliente = resultado[0]['id_cliente']

        estado = db.consultar(
            "SELECT id_estadopedido FROM tb_estadopedido WHERE nombre_estadopedido = 'Preparando' LIMIT 1"
        )
        id_estado = estado[0]['id_estadopedido']

        db.ejecutar("""
            INSERT INTO tb_pedido (fecha_pedido, id_cliente, id_mesa, id_usuario, id_estadopedido)
            VALUES (NOW(), %s, %s, %s, %s)
        """, [id_cliente, request.POST['id_mesa'], request.POST['id_usuario'], id_estado])

        pedido = db.consultar("""
            SELECT id_pedido FROM tb_pedido
            WHERE id_cliente = %s
            ORDER BY id_pedido DESC LIMIT 1
        """, [id_cliente])
        id_pedido = pedido[0]['id_pedido']

        productos = db.consultar(
            "SELECT id_producto, nombre_producto, precio_producto FROM tb_producto"
        )
        return render(request, 'appMorocha/registrarPedido.html', {
            'id_pedido': id_pedido,
            'productos': productos,
        })

    # GET
    context = {
        'mesas':    db.consultar("SELECT id_mesa, num_mesa FROM tb_mesa"),
        'usuarios': db.consultar("SELECT id_usuario, nombre_usuario FROM tb_usuario"),
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

    if request.method == 'POST':
        db.ejecutar("""
            INSERT INTO tb_detallepedido 
                (id_pedido, id_producto, cantidad)
            VALUES (%s, %s, %s)
        """, [
            id_pedido,
            request.POST['id_producto'],
            request.POST['cantidad'],
        ])

        return redirect('detallePedido', id_pedido=id_pedido)

    context = {
        'id_pedido':  id_pedido,
        'productos':  db.consultar("SELECT id_producto, nombre_producto, precio_producto FROM tb_producto"),
    }
    return render(request, 'appMorocha/detallePedido.html', context)


# Vistas para la gestión de usuarios
def usuario(request):
    db = ConexionDB()
    UsuariosRegistrados = cargarRegistros()
    roles = db.consultar("""
        SELECT id_rol, nombre_rol
        FROM tb_roles
    """)
    return render(request,'appMorocha/usuario.html',{
        'UsuariosRegistrados': UsuariosRegistrados,
        'roles': roles
    })

# Cargar usuarios registrados
def cargarRegistros():
    conexion=ConexionDB()
    sintaxiSQL="""
        SELECT
    u.id_usuario,
    u.nombre_usuario,
    u.clave,
    r.nombre_rol
    FROM tb_usuario u
    INNER JOIN tb_roles r
    ON u.id_rol = r.id_rol; 
    """
    usuario = conexion.consultar(sintaxiSQL)
    return usuario

# Eliminar usuario
def eliminarUsuario(request,nombreUsuario):
    conexion=ConexionDB()
    validarRegistro="""
        select * from tb_usuario where nombre_usuario = %s
    """
    if(conexion.consultar(validarRegistro,(nombreUsuario,))):
        #Existe un registro
        consultaEliminar="""
            delete from tb_usuario  where nombre_usuario = %s
        """
        conexion.ejecutar(consultaEliminar,(nombreUsuario,))
        usuarios = cargarRegistros()
        return render(request,'appMorocha/usuario.html',{
        "UsuariosRegistrados" : usuarios
        })

 # Guardar usuario
def procesarUsuario(request):
    db = ConexionDB()
    if(request.method == 'GET'):
        nombreUsuario=request.GET.get('txt_nombreusuario')
        clave=request.GET.get('txt_clave')
        rol=request.GET.get('txt_rol')
        conexion= ConexionDB()
        sintaxisValidar="""
            select * from tb_usuario where nombre_usuario=%s
        """
        if(conexion.verificar(sintaxisValidar,(nombreUsuario))):
            contexto={
                "msg":"Casi... Existe un Registro asociado",
                "color":"red"
            }
            return render(request,'appMorocha/usuario.html',contexto)
        sintaxisSQL = """
            INSERT INTO tb_usuario(nombre_usuario, clave, id_rol)
            VALUES (%s, %s, %s)
        """
        conexion.ejecutar(sintaxisSQL,(nombreUsuario,clave,rol))
        usuarios = cargarRegistros()
        contexto={
            "msg":"Registro Insertado Correctamente!",
            "color":"green",
            "UsuariosRegistrados" : usuarios
        }
        return render(request,'appMorocha/usuario.html',contexto)
    context = {
        'roles':  db.consultar("SELECT id_rol, nombre_rol FROM tb_roles"),
    }
    return render(request,'appMorocha/usuario.html',context)

# Ingresar vista para productos
def ingresarProducto(request):
    ProductosRegistrados = cargarRegistrosProductos()
    return render(request, 'appMorocha/ingresarProducto.html', {'ProductosRegistrados': ProductosRegistrados})

# Cargar productos registrados
def cargarRegistrosProductos():
    conexion=ConexionDB()
    sintaxiSQL="""
        SELECT id_producto, nombre_producto, precio_producto as precio
        FROM tb_producto
    """
    producto = conexion.consultar(sintaxiSQL)
    return producto
# Guardar producto
def procesarProducto(request):
    if request.method == 'GET':
        nombreProducto = request.GET.get('txt_nombreproducto')
        precio = request.GET.get('txt_precio')
        conexion = ConexionDB()
        sintaxisValidar = """
            SELECT * FROM tb_producto WHERE nombre_producto = %s
        """
        if conexion.verificar(sintaxisValidar, (nombreProducto,)):
            contexto = {
                "msg": "Casi... Existe un Registro asociado",
                "color": "red"
            }
            return render(request, 'appMorocha/ingresarProducto.html', contexto)
        sintaxisSQL = """
            INSERT INTO tb_producto(nombre_producto, precio_producto)
            VALUES (%s, %s)
        """
        conexion.ejecutar(sintaxisSQL, (nombreProducto, precio))
        ProductosRegistrados = cargarRegistrosProductos()
        contexto = {
            "msg": "Registro Insertado Correctamente!",
            "color": "green",
            "ProductosRegistrados": ProductosRegistrados
        }
        return render(request, 'appMorocha/ingresarProducto.html', contexto)
    return render(request, 'appMorocha/ingresarProducto.html')

# Ingresar vista para mesas
def ingresarMesa(request):
    cargarMesas = cargarRegistrosMesas()
    
    return render(request, 'appMorocha/ingresarMesa.html', {'cargarMesas': cargarMesas})

# Cargar mesas registradas
def cargarRegistrosMesas():
    conexion = ConexionDB()
    sintaxiSQL = """
    SELECT
        m.id_mesa,
        m.num_mesa,
        e.nombre_estado
    FROM tb_mesa m
    INNER JOIN tb_estadomesa e
    ON m.id_estadomesa = e.id_estadomesa
     ORDER BY 
        FIELD(e.nombre_estado, 'Libre', 'Ocupado', 'Mantenimiento'),
        m.id_mesa
    """
    mesa = conexion.consultar(sintaxiSQL)
    return mesa
