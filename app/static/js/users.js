$(document).ready(function () {
    const csrfToken = $('meta[name="csrf-token"]').attr("content");

    // DataTables: se conserva temporalmente porque depende de jQuery.
    let table = $("#tablaUsuarios").DataTable({
        paging: true,
        autoWidth: true,
        responsive: true,
        language: {
            lengthMenu: "Mostrar _MENU_ registros por página",
            zeroRecords: "No se encontraron registros",
            info: "Mostrando página _PAGE_ de _PAGES_",
            infoEmpty: "No hay registros disponibles",
            infoFiltered: "(filtrado de _MAX_ registros en total)",
            search: "Buscar:",
            paginate: {
                next: "Siguiente",
                previous: "Anterior"
            }
        },
        lengthMenu: [5, 10, 25, 50],
        order: [[1, "asc"]]
    });

    // Abrir el modal para editar un usuario.
    $(document).on("click", ".actualizar-btn", function () {
        const userId = $(this).data("id");
        const username = $(this).data("username");
        const email = $(this).data("email");

        $("#editUserId").val(userId);
        $("#editUsername").val(username);
        $("#editEmail").val(email);
        $("#editPassword").val("");

        const modalElement = document.getElementById("modalEditarUsuario");
        bootstrap.Modal.getOrCreateInstance(modalElement).show();
    });

    // Editar usuario usando fetch.
    $("#formEditarUsuario").on("submit", async function (event) {
        event.preventDefault();

        const userId = $("#editUserId").val();

        const updatedData = {
            username: $("#editUsername").val(),
            email: $("#editEmail").val(),
            password: $("#editPassword").val() || null
        };

        try {
            const response = await fetch(`/usuarios/editar/${userId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify(updatedData)
            });

            const result = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error(
                    result.error || `Error HTTP: ${response.status}`
                );
            }

            alert(result.message || "Usuario actualizado correctamente");
            location.reload();

        } catch (error) {
            alert(error.message || "Error al actualizar usuario");
        }
    });

    // Eliminar usuario usando fetch.
    $(document).on("click", ".eliminar-btn", async function () {
        const userId = $(this).data("id");

        if (!confirm("¿Seguro que quieres eliminar este usuario?")) {
            return;
        }

        try {
            const response = await fetch(`/usuarios/eliminar/${userId}`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            const result = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error(
                    result.error || `Error HTTP: ${response.status}`
                );
            }

            alert(result.message || "Usuario eliminado correctamente");
            location.reload();

        } catch (error) {
            alert(error.message || "Error al eliminar usuario");
        }
    });
});
