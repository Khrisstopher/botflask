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

