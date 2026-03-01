document.addEventListener("DOMContentLoaded", function () {

    /* ========================= */
    /* CATEGORY FILTER */
    /* ========================= */

    const buttons = document.querySelectorAll(".filter-btn");
    const cards = document.querySelectorAll(".menu-card");

    buttons.forEach(button => {
        button.addEventListener("click", () => {

            const category = button.getAttribute("data-category");

            buttons.forEach(btn => btn.classList.remove("active"));
            button.classList.add("active");

            cards.forEach(card => {
                const itemCategory = card.getAttribute("data-category");

                if (category === "all" || itemCategory === category) {
                    card.style.display = "block";
                } else {
                    card.style.display = "none";
                }
            });

        });
    });

    /* ========================= */
    /* PAYMENT MODAL */
    /* ========================= */

    const buyButtons = document.querySelectorAll(".buy-btn");
    const modal = document.getElementById("paymentModal");
    const closeBtn = document.querySelector(".close-payment");
    const paymentOptions = document.querySelectorAll(".payment-option");

    buyButtons.forEach(button => {
        button.addEventListener("click", function () {
            modal.classList.add("active");
        });
    });

    if (closeBtn) {
        closeBtn.addEventListener("click", function () {
            modal.classList.remove("active");
        });
    }

    paymentOptions.forEach(option => {
        option.addEventListener("click", function () {
            const method = this.getAttribute("data-method");

            if (method === "cash") {
                alert("Cash Payment Selected");
            } else {
                alert("Online Payment Selected");
            }

            modal.classList.remove("active");
        });
    });

});