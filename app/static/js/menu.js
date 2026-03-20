// ================================================
// MENU.JS — filter, cart, wishlist, delete, modal
// ================================================

document.addEventListener("DOMContentLoaded", function () {

    // ── CATEGORY FILTER ──────────────────────────────────────
    const filterBtns = document.querySelectorAll(".filter-btn");
    const cards      = document.querySelectorAll(".menu-card");

    filterBtns.forEach(btn => {
        btn.addEventListener("click", function () {
            filterBtns.forEach(b => b.classList.remove("active"));
            this.classList.add("active");

            const category = this.dataset.category;

            cards.forEach(card => {
                if (category === "all" || card.dataset.category === category) {
                    card.style.display = "";
                } else {
                    card.style.display = "none";
                }
            });
        });
    });


    // ── ADD TO CART ──────────────────────────────────────────
    document.querySelectorAll(".cart-btn").forEach(btn => {
        btn.addEventListener("click", async function () {

            // Not logged in → go to login
            if (!isLoggedIn) {
                window.location.href = loginUrl;
                return;
            }

            const itemId = this.dataset.id;
            this.disabled = true;
            this.textContent = "Adding...";

            try {
                const res  = await fetch(`/cart/add/${itemId}`, { method: "POST" });
                const data = await res.json();

                if (data.success) {
                    // Redirect to cart page
                    window.location.href = cartUrl;
                } else if (data.redirect) {
                    window.location.href = data.redirect;
                }
            } catch (err) {
                console.error("Cart error:", err);
                this.disabled    = false;
                this.textContent = "Add to Cart";
            }
        });
    });


    // ── WISHLIST HEART ────────────────────────────────────────
    document.querySelectorAll(".wishlist-btn").forEach(btn => {
        btn.addEventListener("click", async function () {

            // Not logged in → go to login
            if (!isLoggedIn) {
                window.location.href = loginUrl;
                return;
            }

            const itemId = this.dataset.id;
            this.disabled = true;

            try {
                const res  = await fetch(`/wishlist/toggle/${itemId}`, { method: "POST" });
                const data = await res.json();

                if (data.success) {
                    if (data.added) {
                        // Item was added to wishlist
                        this.textContent = "❤️";
                        this.classList.add("wishlisted");
                        this.title = "Remove from Wishlist";
                        // Redirect to wishlist after brief visual feedback
                        setTimeout(() => {
                            window.location.href = wishUrl;
                        }, 300);
                    } else {
                        // Item was removed from wishlist (toggled off)
                        this.textContent = "🤍";
                        this.classList.remove("wishlisted");
                        this.title    = "Add to Wishlist";
                        this.disabled = false;
                    }
                } else if (data.redirect) {
                    window.location.href = data.redirect;
                }
            } catch (err) {
                console.error("Wishlist error:", err);
                this.disabled = false;
            }
        });
    });


    // ── ADMIN DELETE ──────────────────────────────────────────
    if (isAdmin) {
        document.querySelectorAll(".delete-btn").forEach(btn => {
            btn.addEventListener("click", async function () {
                if (!confirm("Delete this item?")) return;

                const itemId = this.dataset.id;

                try {
                    const res  = await fetch(`/api/admin/menu/delete/${itemId}`, { method: "DELETE" });
                    const data = await res.json();

                    if (data.success) {
                        // Remove card from DOM
                        this.closest(".menu-card").remove();
                    } else {
                        alert("Delete failed: " + (data.error || "Unknown error"));
                    }
                } catch (err) {
                    console.error("Delete error:", err);
                }
            });
        });
    }


    // ── BUY NOW / PAYMENT MODAL ───────────────────────────────
    const modal        = document.getElementById("paymentModal");
    const closePayment = document.querySelector(".close-payment");

    document.querySelectorAll(".buy-btn").forEach(btn => {
        btn.addEventListener("click", function () {
            if (!isLoggedIn) {
                window.location.href = loginUrl;
                return;
            }
            modal.style.display = "flex";
        });
    });

    if (closePayment) {
        closePayment.addEventListener("click", function () {
            modal.style.display = "none";
        });
    }

    document.querySelectorAll(".payment-option").forEach(btn => {
        btn.addEventListener("click", function () {
            const method = this.dataset.method;
            modal.style.display = "none";
            // TODO: handle payment method (cash / online)
            alert("Payment method selected: " + method);
        });
    });

    // Close modal on outside click
    if (modal) {
        modal.addEventListener("click", function (e) {
            if (e.target === modal) modal.style.display = "none";
        });
    }

});