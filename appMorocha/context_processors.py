
def usuario_context(request):
    return {
        'rol': request.COOKIES.get('rol', ''),
        'nombre_usuario': request.COOKIES.get('nombre_usuario', ''),
    }