let detalles = [];

const opcionesSelect = productos.map(p =>
    `<option value="${p.id}">${p.nombre} — $${p.precio}</option>`
).join('');

function tablaHTML() {
    if (detalles.length === 0) {
        return `<p class="text-muted text-center mt-2">Sin productos aún.</p>`;
    }
    let total = 0;
    let filas = detalles.map(d => {
        total += d.subtotal;
        return `
            <tr>
                <td>${d.nombre_producto}</td>
                <td>${d.cantidad}</td>
                <td>$${d.precio_producto}</td>
                <td>$${d.subtotal}</td>
            </tr>`;
    }).join('');

    return `
        <table class="table table-sm table-bordered mt-3">
            <thead class="table-dark">
                <tr>
                    <th>Producto</th>
                    <th>Cant.</th>
                    <th>Precio</th>
                    <th>Subtotal</th>
                </tr>
            </thead>
            <tbody>${filas}</tbody>
            <tfoot>
                <tr class="table-success fw-bold">
                    <td colspan="3" class="text-end">Total:</td>
                    <td>$${total}</td>
                </tr>
            </tfoot>
        </table>`;
}

function contenidoSwal() {
    return `
        <div class="mb-3 text-start">
            <label class="form-label fw-semibold">Producto</label>
            <select id="swal_producto" class="form-select">
                ${opcionesSelect}
            </select>
        </div>
        <div class="mb-3 text-start">
            <label class="form-label fw-semibold">Cantidad</label>
            <input type="number" id="swal_cantidad" class="form-control" value="1" min="1"/>
        </div>
        <div id="swal_tabla">${tablaHTML()}</div>
    `;
}

function abrirSwal() {
    Swal.fire({
        title: `Pedido #${ID_PEDIDO} — Agregar Productos`,
        html: contenidoSwal(),
        width: 600,
        showCancelButton: true,
        confirmButtonText: '+ Agregar',
        confirmButtonColor: '#198754',
        cancelButtonText: 'Finalizar Pedido',
        cancelButtonColor: '#0d6efd',
        allowOutsideClick: false,
        preConfirm: () => {
            const cantidad = parseInt(document.getElementById('swal_cantidad').value);
            const id_producto = document.getElementById('swal_producto').value;

            if (!cantidad || cantidad < 1) {
                Swal.showValidationMessage('La cantidad debe ser mayor a 0');
                return false;
            }

            Swal.showLoading();

            return fetch(URL_REGISTRAR, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': CSRF_TOKEN,
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify({
                    id_pedido: ID_PEDIDO,
                    id_producto: id_producto,
                    cantidad: cantidad,
                })
            })
            .then(r => r.json())
            .then(data => {
                if (data.ok) {
                    detalles = data.detalles;
                    return true;
                }
                Swal.showValidationMessage('Error al guardar el producto');
                return false;
            });
        }
    }).then(result => {
        if (result.isConfirmed) {
            abrirSwal();
        } else {
            if (detalles.length === 0) {
                Swal.fire('Atención', 'El pedido quedó sin productos.', 'warning');
            } else {
                Swal.fire({
                    icon: 'success',
                    title: '¡Pedido registrado!',
                    text: `Pedido #${ID_PEDIDO} guardado con ${detalles.length} producto(s).`,
                    confirmButtonText: 'Ver pedidos',
                    confirmButtonColor: '#198754',
                }).then(() => {
                    window.location.href = URL_ESTADO;
                });
            }
        }
    });
}

abrirSwal();