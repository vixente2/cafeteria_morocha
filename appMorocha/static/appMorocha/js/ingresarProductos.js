$(document).ready(function () {

    // ── VER MÁS ─────────────────────────────────────────────────────
    $('.btnVerMas').click(function () {
        let id = $(this).data('id');
        let producto = $(this).data('producto');
        let precio = $(this).data('precio');

        Swal.fire({
            title: 'Detalle del Producto',
            icon: 'info',
            html: `
                <table class="table table-bordered">
                    <thead class="table-dark">
                        <tr><th colspan="2" class="text-center">Vista Previa</th></tr>
                    </thead>
                    <tbody>
                        <tr>
                        <td><strong>ID</strong></td>
                        <td>${id}</td>
                        </tr>
                        <tr>
                        <td><strong>Nombre</strong></td>
                        <td>${producto}</td>
                        </tr>
                        <tr>
                        <td><strong>Precio</strong></td>
                        <td>$${precio}</td>
                        </tr>
                    </tbody>
                </table>
            `,
            confirmButtonText: 'Cerrar',
            confirmButtonColor: '#0AA34A'
        });
    });

    $('.btnEliminar').click(function () {
        let id = $(this).data('id');
        let producto = $(this).data('producto');

        Swal.fire({
            title: '¿Eliminar producto?',
            html: `<b>${producto}</b> será eliminado permanentemente.`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed)
                window.location.href = '/eliminarProducto/' + id + '/';
        });
    });

    $('.btnEditar').click(function () {
        let id = $(this).data('id');
        let producto = $(this).data('producto');
        let precio = $(this).data('precio');

        Swal.fire({
            title: 'Editar Producto',
            icon: 'warning',
            html: `
                <div class="text-start">
                    <label class="form-label">Nombre producto</label>
                    <input type="text" id="swal_nombre" class="form-control mb-3" value="${producto}"/>
                    <label class="form-label">Precio</label>
                    <input type="text" id="swal_precio" class="form-control" value="${precio}" inputmode="numeric"/>
                </div>
            `,
            showCancelButton: true,
            confirmButtonText: 'Guardar Cambios',
            confirmButtonColor: '#ffc107',
            cancelButtonText: 'Cancelar',
            cancelButtonColor: '#6c757d',
            didOpen: () => {
                // Solo números en precio
                document.getElementById('swal_precio').addEventListener('input', function () {
                    this.value = this.value.replace(/[^0-9]/g, '');
                });
            },
            preConfirm: () => {
                const nombre = document.getElementById('swal_nombre').value.trim();
                const p = document.getElementById('swal_precio').value.trim();

                if (!nombre) {
                    Swal.showValidationMessage('El nombre no puede estar vacío');
                    return false;
                }
                if (!p) {
                    Swal.showValidationMessage('El precio no puede estar vacío');
                    return false;
                }
                return { nombre, precio: p };
            }
        }).then((result) => {
            if (result.isConfirmed) {
                const { nombre, precio: p } = result.value;
                window.location.href =
                    '/editarProducto/?id_producto=' + id +
                    '&txt_nombreproducto=' + encodeURIComponent(nombre) +
                    '&txt_precio=' + encodeURIComponent(p);
            }
        });
    });

});