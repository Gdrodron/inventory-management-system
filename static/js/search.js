document.addEventListener("DOMContentLoaded", () => {

    const searchInput = document.getElementById("searchInput");
    const table = document.getElementById("productTable");

    if (!searchInput || !table) return;

    searchInput.addEventListener("keyup", function () {

        const keyword = this.value.toLowerCase();

        table.querySelectorAll("tbody tr").forEach(row => {

            row.style.display = row.innerText.toLowerCase().includes(keyword)
                ? ""
                : "none";

        });

    });

});