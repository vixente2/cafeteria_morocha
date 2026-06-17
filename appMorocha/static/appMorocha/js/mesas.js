const enviarForm = (action, campos) => {
    const form = $('<form>', { method: 'POST', action });

    form.append($('<input>', {
        type: 'hidden',
        name: 'csrfmiddlewaretoken',
        value: CSRF_TOKEN
    }));

    $.each(campos, (name, value) => {
        form.append($('<input>', { type: 'hidden', name, value }));
    });

    $('body').append(form);
    form.submit();
};

// Botones de estado
$('.btnOcupado').on('click', function () {
    enviarForm(URLS.editarMesa, { id_mesa: $(this).data('id'), estado: 1 });
});
$('.btnLibre').on('click', function () {
    enviarForm(URLS.editarMesa, { id_mesa: $(this).data('id'), estado: 2 });
});
$('.btnMantenimiento').on('click', function () {
    enviarForm(URLS.editarMesa, { id_mesa: $(this).data('id'), estado: 3 });
});

// Botón eliminar
$('.btnEliminar').on('click', function () {
    const id_mesa = $(this).data('id');

    Swal.fire({
        title: '¿Eliminar mesa?',
        text: 'Esta acción no se puede deshacer.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            enviarForm(URLS.eliminarMesa, { id_mesa });
        }
    });
});