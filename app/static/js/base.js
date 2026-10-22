(function () {
    const darkModeQuery = window.matchMedia("(prefers-color-scheme: dark)");
    document.documentElement.setAttribute("data-bs-theme", darkModeQuery.matches ? "dark" : "light");
})();

document.addEventListener("DOMContentLoaded", function () {
    const darkModeQuery = window.matchMedia("(prefers-color-scheme: dark)");

    function applyDarkModePreference() {
        document.body.setAttribute("data-bs-theme", darkModeQuery.matches ? "dark" : "light");
    }

    darkModeQuery.addEventListener("change", applyDarkModePreference);
});

document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("usuarios-sidebar");
    const toggleButton = document.getElementById("toggle-usuarios-sidebar");
    const closeButton = document.getElementById("cerrar-usuarios-sidebar");

    if (!sidebar || !toggleButton) {
        return;
    }

    function setSidebarOpen(open) {
        sidebar.classList.toggle("is-open", open);
        toggleButton.setAttribute("aria-expanded", String(open));
    }

    toggleButton.addEventListener("click", function () {
        setSidebarOpen(!sidebar.classList.contains("is-open"));
    });

    closeButton?.addEventListener("click", function () {
        setSidebarOpen(false);
        toggleButton.focus();
    });

    document.addEventListener("keydown", function (event) {
        if (
            event.key === "Escape" &&
            sidebar.classList.contains("is-open") &&
            window.matchMedia("(max-width: 991.98px)").matches
        ) {
            setSidebarOpen(false);
            toggleButton.focus();
        }
    });

    window.addEventListener("resize", function () {
        if (window.matchMedia("(min-width: 992px)").matches) {
            setSidebarOpen(false);
        }
    });
});