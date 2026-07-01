document.addEventListener("DOMContentLoaded", () => {

    const searchInput = document.getElementById("transactionSearch");
    const table = document.getElementById("transactionTable");

    if (!searchInput || !table) return;

    const rows = table.querySelectorAll("tbody tr");

    // =========================
    // Live Search
    // =========================

    searchInput.addEventListener("input", function () {

        const keyword = this.value.trim().toLowerCase();

        rows.forEach(row => {

            const text = row.textContent.toLowerCase();

            row.style.display = text.includes(keyword)
                ? ""
                : "none";

        });

    });

});