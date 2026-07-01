document.addEventListener("DOMContentLoaded", () => {

    // ==========================
    // Table Search
    // ==========================
    function setupSearch(inputId, tableId) {

        const searchInput = document.getElementById(inputId);

        if (!searchInput) return;

        searchInput.addEventListener("keyup", () => {

            const value = searchInput.value.toLowerCase();
            const rows = document.querySelectorAll(`#${tableId} tbody tr`);

            rows.forEach(row => {

                row.style.display = row.textContent
                    .toLowerCase()
                    .includes(value)
                    ? ""
                    : "none";

            });

        });

    }

    setupSearch("productSearch", "productTable");
    setupSearch("transactionSearch", "transactionTable");


    // ==========================
    // Dashboard Charts
    // ==========================
    if (typeof Chart === "undefined" || !window.dashboardData) return;

    const {
        categoryLabels,
        categoryValues,
        stockLabels,
        stockValues
    } = window.dashboardData;


    // ==========================
    // Category Pie Chart
    // ==========================
    const categoryCanvas = document.getElementById("categoryChart");

    if (categoryCanvas) {

        new Chart(categoryCanvas, {

            type: "pie",

            data: {

                labels: categoryLabels,

                datasets: [{

                    data: categoryValues,

                    backgroundColor: [
                        "#3b82f6",
                        "#22c55e",
                        "#f59e0b",
                        "#ef4444",
                        "#8b5cf6",
                        "#06b6d4",
                        "#84cc16"
                    ]

                }]

            },

            options: {

                responsive: true,

                plugins: {

                    legend: {

                        position: "bottom"

                    }

                }

            }

        });

    }


    // ==========================
    // Stock Bar Chart
    // ==========================
    const stockCanvas = document.getElementById("stockChart");

    if (stockCanvas) {

        new Chart(stockCanvas, {

            type: "bar",

            data: {

                labels: stockLabels,

                datasets: [{

                    label: "Quantity",

                    data: stockValues,

                    backgroundColor: "#2563eb"

                }]

            },

            options: {

                responsive: true,

                scales: {

                    y: {

                        beginAtZero: true

                    }

                },

                plugins: {

                    legend: {

                        display: false

                    }

                }

            }

        });

    }

});