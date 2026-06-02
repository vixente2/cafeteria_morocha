from django.shortcuts import render
from django.http import HttpResponse
from .db import ConexionDB

# Create your views here.
def inicio(request):
    return render(request,'appMorocha/inicio.html')

def login(request):
    return render(request,'appMorocha/login.html')

def registrarPedido(request):
    return render(request,'appMorocha/registrarPedido.html')

# Programacion de usuario
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