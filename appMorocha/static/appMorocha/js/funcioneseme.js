$(document).ready(function () {

    $('.btnEliminar').click(function () {
        let id_pedido = $(this).data('id_pedido');

        Swal.fire({
            title: "Eliminar Pedido",
            text: "¿Estás seguro que quieres eliminar el pedido #" + id_pedido + "?",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            cancelButtonText: "No",
            confirmButtonText: "Sí, Eliminar"
        }).then((result) => {
            if (result.isConfirmed)
                window.location.href = "/eliminarPedido/" + id_pedido + "/";
                window.location.href = "/eliminarPedido/" + id_pedido;
        });
    });
    
    $('.btnVerMas').click(function(){
    let id_pedido = $(this).data('id_pedido');
    let fecha     = $(this).data('fecha');
    let mesa      = $(this).data('mesa');
    let cliente   = $(this).data('cliente');
    let estado    = $(this).data('estado');

    Swal.fire({
        title: "Información del Pedido",
        icon: 'info',
        html: (() => {
            const escapeHtml = (v) => String(v ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
            return `
                <table class="table table-bordered">
                    <thead class="table-dark"><tr><th colspan="2" class="text-center">Vista Previa</th></tr></thead>
                    <tbody>
                        <tr><td><strong># Pedido</strong></td><td>${escapeHtml(id_pedido)}</td></tr>
                        <tr><td><strong>Fecha</strong></td><td>${escapeHtml(fecha)}</td></tr>
                        <tr><td><strong>Mesa</strong></td><td>${escapeHtml(mesa)}</td></tr>
                        <tr><td><strong>Cliente</strong></td><td>${escapeHtml(cliente)}</td></tr>
                        <tr><td><strong>Estado</strong></td><td>${escapeHtml(estado)}</td></tr>
                    </tbody>
                </table>`;
        })(),
        html: `
            <table class="table table-bordered">
                <thead class="table-dark">
                    <th colspan="2" class="text-center">Vista Previa</th>
                </thead>
                <tbody>
                    <tr><td><strong># Pedido</strong></td><td>${id_pedido}</td></tr>
                    <tr><td><strong>Fecha</strong></td><td>${fecha}</td></tr>
                    <tr><td><strong>Mesa</strong></td><td>${mesa}</td></tr>
                    <tr><td><strong>Cliente</strong></td><td>${cliente}</td></tr>
                    <tr><td><strong>Estado</strong></td><td>${estado}</td></tr>
                </tbody>
            </table>
        `,
        confirmButtonText: "Cerrar Vista Previa",
        confirmButtonColor: '#0AA34A'
    });
});
});