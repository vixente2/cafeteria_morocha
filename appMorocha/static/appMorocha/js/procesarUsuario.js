$(document).ready(function () {
    $('.btnEliminar').click(function () {
        let nombreUsuario = $(this).data('usuario');
        let clave = $(this).data('clave');
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
                window.location.href = "/eliminarUsuario/" + nombreUsuario
        });
    });

    $('.btnVerMas').click(function () {
        let idUsuario = $(this).data("id");
        let nombreUsuario = $(this).data("usuario");
        let rol = $(this).data("rol");
        let clave = $(this).data("clave");
        Swal.fire({
            title: "Información",
            icon: 'info',
            html: `
            <table class="table table-bordered">
                <tr>
                    <td><strong>ID</strong></td>
                    <td>${idUsuario}</td>
                </tr>
                <tr>
                    <td><strong>Usuario</strong></td>
                    <td>${nombreUsuario}</td>
                </tr>
                <tr>
                    <td><strong>Rol</strong></td>
                    <td>${rol}</td>
                </tr>
                <tr>
                    <td><strong>Clave</strong></td>
                    <td>${clave}</td>
                </tr>
            </table>
        `
        });
    });
});