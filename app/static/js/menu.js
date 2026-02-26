const buttons = document.querySelectorAll(".filter-btn");
const cards = document.querySelectorAll(".menu-card");

buttons.forEach(button => {
    button.addEventListener("click", () => {
        const category = button.getAttribute("data-category");

        cards.forEach(card => {
            const itemCategory = card.getAttribute("data-category");

            if (category === "all" || itemCategory.includes(category)) {
                card.style.display = "block";
            } else {
                card.style.display = "none";
            }
        });
    });
});