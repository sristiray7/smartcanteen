document.addEventListener("DOMContentLoaded", function () {

    const loginDropdown = document.querySelector(".login-dropdown");
    const loginToggle = document.getElementById("loginToggle");

    if (!loginDropdown || !loginToggle) return;

    // Toggle dropdown
    loginToggle.addEventListener("click", function (e) {
        e.preventDefault();
        loginDropdown.classList.toggle("active");
    });

    // Close when clicking outside
    document.addEventListener("click", function (e) {
        if (!loginDropdown.contains(e.target)) {
            loginDropdown.classList.remove("active");
        }
    });

});