$(document).ready(function () {
 
    // ── Eliminar ──────────────────────────────────────────────────────────────
    $('.btnEliminar').click(function () {
        let nombreUsuario = $(this).data('usuario');
        Swal.fire({
            title: "Eliminar Registro",
            text: "¿Estás seguro que quieres eliminar el registro de " + nombreUsuario + " ?",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            cancelButtonText: "No",
            confirmButtonText: "Si, Eliminar"
        }).then((result) => {
            if (result.isConfirmed)
                window.location.href = "/eliminarUsuario/" + nombreUsuario;
        });
    });
 
    // ── Ver Más ───────────────────────────────────────────────────────────────
    $('.btnVerMas').click(function () {
        let idUsuario     = $(this).data("id");
        let nombreUsuario = $(this).data("usuario");
        let rol           = $(this).data("rol");
        let clave         = $(this).data("clave");
        Swal.fire({
            title: "Información",
            icon: 'info',
            html: `
            <table class="table table-bordered">
                <tr><td><strong>ID</strong></td><td>${idUsuario}</td></tr>
                <tr><td><strong>Usuario</strong></td><td>${nombreUsuario}</td></tr>
                <tr><td><strong>Rol</strong></td><td>${rol}</td></tr>
                <tr><td><strong>Clave</strong></td><td>${clave}</td></tr>
            </table>`
        });
    });
 
    // ── Editar ────────────────────────────────────────────────────────────────
    $('.btnEditar').click(function () {
        let idUsuario     = $(this).data("id");
        let nombreUsuario = $(this).data("usuario");
        let clave         = $(this).data("clave");
        let idRol         = $(this).data("id-rol");
 
        // Clonar el select de roles que ya existe en la página
        let rolesHTML = $('#txt_rol').clone()
            .attr('id', 'swal_rol')
            .addClass('form-select mb-2');
 
        // Pre-seleccionar el rol actual del usuario
        rolesHTML.find('option[value="' + idRol + '"]').attr('selected', true);
 
        Swal.fire({
            title: "Editar Usuario",
            icon: 'warning',
            html: `
            <div class="text-start">
                <label class="form-label">Nombre usuario</label>
                <input id="swal_nombre" type="text" class="form-control mb-2"
                       value="${nombreUsuario}" autocomplete="off"/>
                <label class="form-label">Clave</label>
                <input id="swal_clave" type="password" class="form-control mb-2"
                       value="${clave}" autocomplete="off"/>
                <label class="form-label">Rol</label>
                ${rolesHTML[0].outerHTML}
            </div>`,
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            cancelButtonText: "Cancelar",
            confirmButtonText: "Guardar",
            preConfirm: () => {
                let nuevoNombre = document.getElementById('swal_nombre').value.trim();
                let nuevaClave  = document.getElementById('swal_clave').value.trim();
                let nuevoRol    = document.getElementById('swal_rol').value;
 
                if (!nuevoNombre || !nuevaClave || !nuevoRol) {
                    Swal.showValidationMessage('Todos los campos son obligatorios');
                    return false;
                }
                return { nuevoNombre, nuevaClave, nuevoRol };
            }
        }).then((result) => {
            if (result.isConfirmed) {
                let { nuevoNombre, nuevaClave, nuevoRol } = result.value;
                window.location.href = `/editarUsuario/?id_usuario=${idUsuario}&txt_nombreusuario=${encodeURIComponent(nuevoNombre)}&txt_clave=${encodeURIComponent(nuevaClave)}&txt_rol=${nuevoRol}`;
            }
        });
    });
 
});