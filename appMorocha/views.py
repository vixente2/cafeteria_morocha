from .services.google_sheets import exportar_pedidos
from django.shortcuts import render, redirect
from django.http import HttpResponse,  JsonResponse
# api para exportar a google sheets
from django.views.decorators.http import require_POST
from .db import ConexionDB
import json
import requests

# Create your views here.

def inicio(request):
    if login_requerido(request):
        return redirect('login')    
    return render(request, 'appMorocha/inicio.html')

#funcion para retornar si no es admin
def admin_requerido(request):
    return request.COOKIES.get('rol') != 'admin'

def login(request):
    if request.method == 'POST':
        nombre_usuario = request.POST.get('txt_usuario')
        clave = request.POST.get('txt_clave')

        conexion = ConexionDB()

        consulta = """
            SELECT u.id_usuario, u.nombre_usuario, u.clave, r.nombre_rol
            FROM tb_usuario u
            INNER JOIN tb_roles r ON u.id_rol = r.id_rol
            WHERE u.nombre_usuario = %s
        """
        resultado = conexion.consultar(consulta, (nombre_usuario,))

        id_correcto = obtenerIdEstadoLogin(conexion, 'Login Correcto')
        id_incorrecto = obtenerIdEstadoLogin(conexion, 'Login Incorrecto')

        if not resultado:
            registrarAuditoria(conexion, nombre_usuario, id_incorrecto, clave)
            return render(request, 'appMorocha/login.html', {
                'msg': 'Usuario o contraseña incorrectos',
                'color': 'red'
            })

        usuario = resultado[0]

        if usuario['clave'] != clave:
            registrarAuditoria(conexion, nombre_usuario, id_incorrecto, clave)
            return render(request, 'appMorocha/login.html', {
                'msg': 'Usuario o contraseña incorrectos',
                'color': 'red'
            })

        registrarAuditoria(conexion, nombre_usuario, id_correcto)

        res = redirect('inicio')
        res.set_cookie('id_usuario', usuario['id_usuario'])
        res.set_cookie('nombre_usuario', usuario['nombre_usuario'])
        res.set_cookie('rol', usuario['nombre_rol'])
        return res

    return render(request, 'appMorocha/login.html')


def obtenerIdEstadoLogin(conexion, nombre_estado):
    resultado = conexion.consultar(
        "SELECT id_estado FROM tb_estadologin WHERE nombre_estado = %s LIMIT 1",
        (nombre_estado,)
    )
    return resultado[0]['id_estado'] if resultado else None


def registrarAuditoria(conexion, username, id_estado, password=None):
    conexion.ejecutar("""
        INSERT INTO tb_auditoria (username, fecha_hora, id_estado, passwordIngresada)
        VALUES (%s, NOW(), %s, %s)
    """, (username, id_estado, password))

def auditoriaLogin(request):
    if login_requerido(request):
        return redirect('login')
    if admin_requerido(request):
        return redirect('inicio')
    conexion = ConexionDB()
    registros = conexion.consultar("""
        SELECT au.id_auditoria, au.username, au.fecha_hora,
               e.nombre_estado, au.passwordIngresada
        FROM tb_auditoria au
        JOIN tb_estadologin e ON au.id_estado = e.id_estado
        ORDER BY au.fecha_hora DESC
    """)
    return render(request, 'appMorocha/auditoria.html', {'registros': registros})


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
           m.num_mesa, c.nombre_cliente, e.nombre_estadopedido,
           COALESCE(SUM(d.cantidad * pr.precio_producto), 0) AS total
    FROM tb_pedido p
    LEFT JOIN tb_mesa          m  ON p.id_mesa         = m.id_mesa
    LEFT JOIN tb_cliente       c  ON p.id_cliente      = c.id_cliente
    LEFT JOIN tb_estadopedido  e  ON p.id_estadopedido = e.id_estadopedido
    LEFT JOIN tb_detallepedido d  ON p.id_pedido       = d.id_pedido
    LEFT JOIN tb_producto      pr ON d.id_producto     = pr.id_producto
    GROUP BY p.id_pedido, p.fecha_pedido, m.num_mesa, c.nombre_cliente, e.nombre_estadopedido
    ORDER BY 
        FIELD(e.nombre_estadopedido, 'Preparando', 'Espera', 'Listo', 'Finalizado'),
        p.id_pedido DESC
    """
    pedidos = conexion.consultar(sintaxiSQL)
    return pedidos



def registrarPedido(request):
    if login_requerido(request):
        return redirect('login')
    if admin_requerido(request):
        return redirect('inicio')    
    db = ConexionDB()

    if request.method == 'POST':

        # ── AJAX: agregar producto al detalle ──
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = json.loads(request.body)
            db.ejecutar("""
                INSERT INTO tb_detallepedido (id_pedido, id_producto, cantidad)
                VALUES (%s, %s, %s)
            """, [data['id_pedido'], data['id_producto'], data['cantidad']])

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

        # Marcar la mesa como Ocupada
        estado_ocupado = db.consultar(
            "SELECT id_estadomesa FROM tb_estadomesa WHERE nombre_estado = 'Ocupado' LIMIT 1"
        )
        if estado_ocupado:
            db.ejecutar(
                "UPDATE tb_mesa SET id_estadomesa = %s WHERE id_mesa = %s",
                [estado_ocupado[0]['id_estadomesa'], request.POST['id_mesa']]
            )

        # ── Redirigir al GET con el id_pedido en la URL ──
        return redirect(f"/registrarPedido/?id_pedido={id_pedido}")

    # ── GET ──
    id_pedido = request.GET.get('id_pedido')
    context = {
        'mesas': db.consultar("""
            SELECT m.id_mesa, m.num_mesa, e.nombre_estado
            FROM tb_mesa m
            INNER JOIN tb_estadomesa e ON m.id_estadomesa = e.id_estadomesa
            ORDER BY m.num_mesa
        """),
        'usuarios': db.consultar("SELECT id_usuario, nombre_usuario FROM tb_usuario"),
    }

    if id_pedido:
        id_pedido = int(id_pedido)
        productos = db.consultar(
            "SELECT id_producto, nombre_producto, precio_producto FROM tb_producto"
        )
        context['id_pedido'] = id_pedido
        context['productos'] = productos

    return render(request, 'appMorocha/registrarPedido.html', context)

def eliminarPedido(request, id_pedido):
    if login_requerido(request):
        return redirect('login')
    if admin_requerido(request):
        return redirect('inicio')
    if request.method == 'GET':        
        db = ConexionDB()
                
        # Obtener la mesa antes de eliminar
        pedido = db.consultar(
            "SELECT id_mesa FROM tb_pedido WHERE id_pedido = %s LIMIT 1",
            [id_pedido]
        )

        db.ejecutar("DELETE FROM tb_detallepedido WHERE id_pedido = %s", [id_pedido])
        db.ejecutar("DELETE FROM tb_pedido WHERE id_pedido = %s", [id_pedido])

        # Liberar la mesa
        if pedido and pedido[0]['id_mesa']:
            estado_libre = db.consultar(
                "SELECT id_estadomesa FROM tb_estadomesa WHERE nombre_estado = 'Libre' LIMIT 1"
            )
            if estado_libre:
                db.ejecutar(
                    "UPDATE tb_mesa SET id_estadomesa = %s WHERE id_mesa = %s",
                    [estado_libre[0]['id_estadomesa'], pedido[0]['id_mesa']]
                )

        return redirect('listarPedidos')
       
# cambiar estado de los pedidos
def actualizarEstadoPedido(request, id_pedido, estado):
    db = ConexionDB()

    # Actualizar estado del pedido
    resultado = db.consultar(
        "SELECT id_estadopedido FROM tb_estadopedido WHERE nombre_estadopedido = %s LIMIT 1",
        [estado]
    )
    if resultado:
        db.ejecutar(
            "UPDATE tb_pedido SET id_estadopedido = %s WHERE id_pedido = %s",
            [resultado[0]['id_estadopedido'], id_pedido]
        )

    # Obtener la mesa asociada a este pedido
    pedido = db.consultar(
        "SELECT id_mesa FROM tb_pedido WHERE id_pedido = %s LIMIT 1",
        [id_pedido]
    )

    if pedido and pedido[0]['id_mesa']:
        id_mesa = pedido[0]['id_mesa']

        # Determinar el nuevo estado de la mesa
        if estado in ['Finalizado']:
            nombre_estado_mesa = 'Libre'
        else:  # Preparando, Espera
            nombre_estado_mesa = 'Ocupado'

        estado_mesa = db.consultar(
            "SELECT id_estadomesa FROM tb_estadomesa WHERE nombre_estado = %s LIMIT 1",
            [nombre_estado_mesa]
        )
        if estado_mesa:
            db.ejecutar(
                "UPDATE tb_mesa SET id_estadomesa = %s WHERE id_mesa = %s",
                [estado_mesa[0]['id_estadomesa'], id_mesa]
            )

    return redirect('estadoPedido')

def listarPedidos(request):
    if login_requerido(request):        
        return redirect('login')
    if admin_requerido(request):
        return redirect('inicio')    
    pedidos = cargarRegistrosPedidos()
    return render(request, 'appMorocha/listarPedidos.html', {'cargarPedidos': pedidos})

# Vistas para la gestión de usuarios
def usuario(request):
    if login_requerido(request):
        return redirect('login')
    if admin_requerido(request):
        return redirect('inicio')        
    db = ConexionDB()
    UsuariosRegistrados = cargarRegistros()
    roles = db.consultar("SELECT id_rol, nombre_rol FROM tb_roles")
    context = {
        'UsuariosRegistrados': UsuariosRegistrados,
        'roles': roles
    }
    if request.GET.get('error') == 'tiene_pedidos':
        context['msg'] = f"No se puede eliminar: el usuario '{request.GET.get('usuario')}' tiene pedidos asociados."
        context['color'] = 'red'
    return render(request, 'appMorocha/usuario.html', context)

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
    if login_requerido(request):
        return redirect('login')
    if admin_requerido(request):
        return redirect('inicio')    
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
def eliminarUsuario(request, nombreUsuario):
    if login_requerido(request):
        return redirect('login')    
    if admin_requerido(request):
        return redirect('inicio')       
    conexion = ConexionDB()
    # Verificar si tiene pedidos asociados
    tiene_pedidos = conexion.consultar("""
        SELECT p.id_pedido FROM tb_pedido p
        INNER JOIN tb_usuario u ON p.id_usuario = u.id_usuario
        WHERE u.nombre_usuario = %s LIMIT 1
    """, (nombreUsuario,))
    if tiene_pedidos:
        return redirect(f'/usuario/?error=tiene_pedidos&usuario={nombreUsuario}')
    # Verificar si existe y eliminar
    existe = conexion.consultar(
        "SELECT * FROM tb_usuario WHERE nombre_usuario = %s",
        (nombreUsuario,)
    )
    if existe:
        conexion.ejecutar(
            "DELETE FROM tb_usuario WHERE nombre_usuario = %s",
            (nombreUsuario,)
        )
    return redirect('/usuario/')
    
# Editar usuario
def editarUsuario(request):
    if login_requerido(request):
        return redirect('login')
    if admin_requerido(request):
        return redirect('inicio')    
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
    if admin_requerido(request):
        return redirect('inicio')        
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
    if login_requerido(request):
        return redirect('login')
    if admin_requerido(request):
        return redirect('inicio')    
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
    if login_requerido(request):
        return redirect('login')
    if admin_requerido(request):
        return redirect('inicio')    
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
    if login_requerido(request):
        return redirect('login')
    if admin_requerido(request):
        return redirect('inicio')    
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
    #aviso de que no se puede eliminar una mesa con pedidos asociados.
    context = {'cargarMesas': cargarMesas}
    if request.GET.get('error') == 'tiene_pedidos':
        context['msg'] = 'No se puede eliminar: esta mesa tiene pedidos asociados.'
        context['color'] = 'red'    
    
    return render(request, 'appMorocha/ingresarMesa.html', context)

# Agregar Mesas
@require_POST
def agregarMesa(request):
    if login_requerido(request):
        return redirect('login')
    if admin_requerido(request):
        return redirect('ingresarMesa')    

    conexion = ConexionDB()

    # Calcular automáticamente el siguiente número de mesa
    siguiente = conexion.consultar(
        "SELECT COALESCE(MAX(num_mesa), 0) + 1 AS siguiente FROM tb_mesa"
    )
    num_mesa = siguiente[0]['siguiente']

    estado_libre = conexion.consultar(
        "SELECT id_estadomesa FROM tb_estadomesa WHERE nombre_estado = 'Libre' LIMIT 1"
    )
    if estado_libre:
        conexion.ejecutar(
            "INSERT INTO tb_mesa (num_mesa, id_estadomesa) VALUES (%s, %s)",
            (num_mesa, estado_libre[0]['id_estadomesa'])
        )

    return redirect('ingresarMesa')
    
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

@require_POST
def eliminarMesa(request):
    if login_requerido(request):
        return redirect('login')
    if admin_requerido(request):
        return redirect('ingresarMesa')
    id_mesa = request.POST.get('id_mesa')
    if not (id_mesa and id_mesa.isdigit()):
        return redirect('ingresarMesa')
    conexion = ConexionDB()
    # Consulta por si la mesa tiene pedidos para validar si se elimina o no
    tiene_pedidos = conexion.consultar(
        "SELECT id_pedido FROM tb_pedido WHERE id_mesa = %s LIMIT 1",
        (id_mesa,)
    )
    if tiene_pedidos:
        return redirect('/ingresarMesa/?error=tiene_pedidos')
    conexion.ejecutar(
        "DELETE FROM tb_mesa WHERE id_mesa = %s",
        (id_mesa,)
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

# dashboard
def datos_dashboard(request):
    if login_requerido(request):
        return JsonResponse({'error': 'no autorizado'}, status=401)
    if admin_requerido(request):
        return JsonResponse({'error': 'sin permiso'}, status=403)
    db = ConexionDB()

    # Gráfico 1: Productos más pedidos
    productos = db.consultar("""
        SELECT pr.nombre_producto, SUM(d.cantidad) AS total
        FROM tb_detallepedido d
        JOIN tb_producto pr ON d.id_producto = pr.id_producto
        GROUP BY pr.nombre_producto
        ORDER BY total DESC
    """)

    # Gráfico 2: Pedidos por estado
    estados_pedido = db.consultar("""
        SELECT e.nombre_estadopedido, COUNT(p.id_pedido) AS total
        FROM tb_estadopedido e
        LEFT JOIN tb_pedido p ON e.id_estadopedido = p.id_estadopedido
        GROUP BY e.nombre_estadopedido
    """)

    # Gráfico 3: Mesas por estado
    estados_mesa = db.consultar("""
        SELECT e.nombre_estado, COUNT(m.id_mesa) AS total
        FROM tb_estadomesa e
        LEFT JOIN tb_mesa m ON e.id_estadomesa = m.id_estadomesa
        GROUP BY e.nombre_estado
    """)

    return JsonResponse({
        'productos': list(productos),
        'estados_pedido': list(estados_pedido),
        'estados_mesa': list(estados_mesa),
    })

def dashboard(request):
    if login_requerido(request):
        return redirect('login')
    if admin_requerido(request):
        return redirect('inicio')
    return render(request, 'appMorocha/dashboard.html')

#Api hora
def hora_actual(request):
    response = requests.get("https://timeapi.io/api/time/current/zone?timeZone=America/Santiago")
    data = response.json()
    return JsonResponse({
        "hora": data["time"],
        "fecha": data["date"],
        "dia": data["dayOfWeek"]
    })