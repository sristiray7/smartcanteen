document.addEventListener("DOMContentLoaded", function () {

    const buttons = document.querySelectorAll(".filter-btn");
    const cards = document.querySelectorAll(".menu-card");

    buttons.forEach(button => {
        button.addEventListener("click", () => {

            const category = button.getAttribute("data-category");

            // Optional: Active button styling
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

});