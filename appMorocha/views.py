from .services.google_sheets import exportar_pedidos
from django.shortcuts import render, redirect
from django.http import HttpResponse,  JsonResponse
# api para exportar a google sheets
from django.views.decorators.http import require_POST
from .db import ConexionDB
import json

# Create your views here.

def inicio(request):
    if login_requerido(request):
        return redirect('login')    
    return render(request, 'appMorocha/inicio.html')

def login(request):
    if request.method == 'POST':
        nombre_usuario = request.POST.get('txt_usuario')
        clave = request.POST.get('txt_clave')
        
        conexion = ConexionDB()
        consulta = """
            SELECT u.id_usuario, u.nombre_usuario, r.nombre_rol
            FROM tb_usuario u
            INNER JOIN tb_roles r ON u.id_rol = r.id_rol
            WHERE u.nombre_usuario = %s AND u.clave = %s
        """
        resultado = conexion.consultar(consulta, (nombre_usuario, clave))
        
        if resultado:
            usuario = resultado[0]
            # comparamos los datos como cookies para no tener que crear las tablas migratorias de django en nuestra bd.
            res = redirect('inicio')        # guardar el redirect en "res"
            res.set_cookie('id_usuario', usuario['id_usuario'])
            res.set_cookie('nombre_usuario', usuario['nombre_usuario'])
            res.set_cookie('rol', usuario['nombre_rol'])
            return res  # redirige al inicio si es correcto
        else:
            return render(request, 'appMorocha/login.html', {
                'msg': 'Usuario o contraseña incorrectos',
                'color': 'red'
            })
    
    return render(request, 'appMorocha/login.html')

def login_requerido(request):
    return not request.COOKIES.get('id_usuario')

def logout(request):
    res = redirect('login')
    res.delete_cookie('id_usuario')
    res.delete_cookie('nombre_usuario')
    res.delete_cookie('rol')
    return res

def estadoPedido(request):
    if login_requerido(request):
        return redirect('login')
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
    if login_requerido(request):
        return redirect('login')
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
        'mesas': db.consultar("""
        SELECT m.id_mesa, m.num_mesa, e.nombre_estado
        FROM tb_mesa m
        INNER JOIN tb_estadomesa e ON m.id_estadomesa = e.id_estadomesa
        ORDER BY m.num_mesa
    """),
    'usuarios': db.consultar("SELECT id_usuario, nombre_usuario FROM tb_usuario"),
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

# cambiar estado de los pedidos
def actualizarEstadoPedido(request, id_pedido, estado):
    db = ConexionDB()
    resultado = db.consultar(
        "SELECT id_estadopedido FROM tb_estadopedido WHERE nombre_estadopedido = %s LIMIT 1",
        [estado]
    )
    if resultado:
        db.ejecutar(
            "UPDATE tb_pedido SET id_estadopedido = %s WHERE id_pedido = %s",
            [resultado[0]['id_estadopedido'], id_pedido]
        )
    return redirect('estadoPedido')

def listarPedidos(request):
    if login_requerido(request):
        return redirect('login')
    pedidos = cargarRegistrosPedidos()
    return render(request, 'appMorocha/listaPedidos.html', {'cargarPedidos': pedidos})

# Vistas para la gestión de usuarios
def usuario(request):
    if login_requerido(request):
        return redirect('login')    
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
    
# Editar usuario
def editarUsuario(request):
    if request.method == 'GET':
        id_usuario    = request.GET.get('id_usuario')
        nombreUsuario = request.GET.get('txt_nombreusuario')
        clave         = request.GET.get('txt_clave')
        rol           = request.GET.get('txt_rol')
        conexion = ConexionDB()

        # Verificar que el nombre no lo use otro usuario
        duplicado = conexion.consultar(
            "SELECT * FROM tb_usuario WHERE nombre_usuario = %s AND id_usuario != %s",
            (nombreUsuario, id_usuario)
        )
        if duplicado:
            usuarios = cargarRegistros()
            roles = conexion.consultar("SELECT id_rol, nombre_rol FROM tb_roles")
            return render(request, 'appMorocha/usuario.html', {
                'msg': 'Ese nombre de usuario ya está en uso.',
                'color': 'red',
                'UsuariosRegistrados': usuarios,
                'roles': roles
            })

        conexion.ejecutar(
            "UPDATE tb_usuario SET nombre_usuario = %s, clave = %s, id_rol = %s WHERE id_usuario = %s",
            (nombreUsuario, clave, rol, id_usuario)
        )
        usuarios = cargarRegistros()
        roles = conexion.consultar("SELECT id_rol, nombre_rol FROM tb_roles")
        return render(request, 'appMorocha/usuario.html', {
            'msg': 'Usuario actualizado correctamente!',
            'color': 'green',
            'UsuariosRegistrados': usuarios,
            'roles': roles
        })
    return redirect('usuario')

# Ingresar vista para productos
def ingresarProducto(request):
    if login_requerido(request):
        return redirect('login')    
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

def editarProducto(request):
    if request.method == 'GET':
        id_producto    = request.GET.get('id_producto')
        nombreProducto = request.GET.get('txt_nombreproducto')
        precio         = request.GET.get('txt_precio')
        conexion = ConexionDB()

        duplicado = conexion.consultar(
            "SELECT * FROM tb_producto WHERE nombre_producto = %s AND id_producto != %s",
            (nombreProducto, id_producto)
        )
        if duplicado:
            contexto = {
                "msg": "Ese nombre ya pertenece a otro producto.",
                "color": "red",
                "ProductosRegistrados": cargarRegistrosProductos()
            }
            return render(request, 'appMorocha/ingresarProducto.html', contexto)

        conexion.ejecutar(
            "UPDATE tb_producto SET nombre_producto = %s, precio_producto = %s WHERE id_producto = %s",
            (nombreProducto, precio, id_producto)
        )
        contexto = {
            "msg": "Producto actualizado correctamente!",
            "color": "green",
            "ProductosRegistrados": cargarRegistrosProductos()
        }
        return render(request, 'appMorocha/ingresarProducto.html', contexto)
    return redirect('ingresarProducto')


def eliminarProducto(request, id_producto):
    conexion = ConexionDB()
    conexion.ejecutar(
        "DELETE FROM tb_producto WHERE id_producto = %s", (id_producto,)
    )
    return redirect('ingresarProducto')

# Ingresar vista para mesas
def ingresarMesa(request):
    if login_requerido(request):
        return redirect('login')    
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

# Editar mesa
@require_POST
def editarMesa(request):
    if login_requerido(request):
        return redirect('login')
    id_mesa = request.POST.get('id_mesa')
    estado = request.POST.get('estado')
    estados_permitidos = {'1', '2', '3'}
    if not (id_mesa and id_mesa.isdigit() and estado in estados_permitidos):
        return redirect('ingresarMesa')
    conexion = ConexionDB()
    conexion.ejecutar(
        "UPDATE tb_mesa SET id_estadomesa = %s WHERE id_mesa = %s",
        (estado, id_mesa)
    )
    return redirect('ingresarMesa')

# Api 


def exportar_a_sheets(request):
    con = ConexionDB()

    pedidos = con.consultar("""
    SELECT p.id_pedido, p.fecha_pedido, p.id_cliente,
           m.num_mesa, u.nombre_usuario, e.nombre_estadopedido,
           SUM(pr.precio_producto * d.cantidad) as total_pedido
    FROM tb_pedido p
    LEFT JOIN tb_mesa m ON p.id_mesa = m.id_mesa
    LEFT JOIN tb_usuario u ON p.id_usuario = u.id_usuario
    LEFT JOIN tb_estadopedido e ON p.id_estadopedido = e.id_estadopedido
    LEFT JOIN tb_detallepedido d ON p.id_pedido = d.id_pedido
    LEFT JOIN tb_producto pr ON d.id_producto = pr.id_producto
    GROUP BY p.id_pedido, p.fecha_pedido, p.id_cliente,
             m.num_mesa, u.nombre_usuario, e.nombre_estadopedido
""")
    detalles = con.consultar("""
        SELECT d.id_detallepedido, d.id_pedido,
               pr.nombre_producto, pr.precio_producto, d.cantidad
        FROM tb_detallepedido d
        LEFT JOIN tb_producto pr ON d.id_producto = pr.id_producto
    """)

    exportar_pedidos(pedidos, detalles)
    return JsonResponse({'mensaje': 'Exportado correctamente', 'status': 'ok'})