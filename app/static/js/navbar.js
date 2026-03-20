document.addEventListener("DOMContentLoaded", function () {

    const menuToggle = document.getElementById("menuToggle");
    const navLinks   = document.querySelector(".nav-links");

    // ── MOBILE HAMBURGER ──────────────────────────────────────
    if (menuToggle && navLinks) {

        menuToggle.addEventListener("click", function (e) {
            e.stopPropagation();
            const isOpen = navLinks.classList.toggle("open");
            menuToggle.classList.toggle("open", isOpen);
            document.body.style.overflow = isOpen ? "hidden" : "";
        });

        // Close when a regular nav link is clicked
        navLinks.querySelectorAll("a").forEach(function (link) {
            link.addEventListener("click", function () {
                if (link.id === "loginToggle" || link.id === "profileToggle") return;
                if (link.closest(".dropdown-menu")) return;
                navLinks.classList.remove("open");
                menuToggle.classList.remove("open");
                document.body.style.overflow = "";
            });
        });

        // Close on resize to desktop
        window.addEventListener("resize", function () {
            if (window.innerWidth > 768) {
                navLinks.classList.remove("open");
                menuToggle.classList.remove("open");
                document.body.style.overflow = "";
            }
        });
    }

    // ── LOGIN / PROFILE DROPDOWN ──────────────────────────────
    const loginDropdown = document.querySelector(".login-dropdown");
    const toggleBtn     = document.getElementById("loginToggle") 
                       || document.getElementById("profileToggle");

    if (loginDropdown && toggleBtn) {

        toggleBtn.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation(); // CRITICAL: stops the document click from firing
            loginDropdown.classList.toggle("active");
        });

        // Close when clicking anywhere outside the dropdown
        document.addEventListener("click", function (e) {
            if (!loginDropdown.contains(e.target)) {
                loginDropdown.classList.remove("active");
            }
        });

        // Close when clicking outside on mobile (when menu is open)
        document.addEventListener("click", function (e) {
            if (!e.target.closest("header")) {
                navLinks && navLinks.classList.remove("open");
                menuToggle && menuToggle.classList.remove("open");
                document.body.style.overflow = "";
            }
        });
    }

    // ── SCROLL SHRINK ─────────────────────────────────────────
    const header = document.querySelector("header");
    if (header) {
        window.addEventListener("scroll", function () {
            header.classList.toggle("scrolled", window.scrollY > 50);
        });
    }

});