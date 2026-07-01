document.addEventListener("DOMContentLoaded", () => {

    const dashboardData = document.getElementById("dashboard-data");

    if (!dashboardData) return;

    const data = JSON.parse(dashboardData.textContent);

    // =========================
    // PIE CHART
    // =========================

    const categoryCanvas = document.getElementById("categoryChart");

    if (categoryCanvas) {

        new Chart(categoryCanvas, {

            type: "pie",

            data: {

                labels: data.categoryLabels,

                datasets: [{

                    data: data.categoryValues,

                    backgroundColor: [

                        "#2563eb",
                        "#22c55e",
                        "#f59e0b",
                        "#ef4444",
                        "#8b5cf6",
                        "#06b6d4",
                        "#ec4899",
                        "#14b8a6"

                    ],

                    borderColor: "#ffffff",

                    borderWidth: 3,

                    hoverOffset: 15

                }]

            },

            plugins: [ChartDataLabels],

            options: {

                responsive: true,

                maintainAspectRatio: false,

                animation: {

                    duration: 1000

                },

                plugins: {

                    legend: {

                        position: "bottom",

                        labels: {

                            usePointStyle: true,

                            pointStyle: "circle",

                            padding: 20,

                            font: {

                                size: 13,

                                weight: "bold"

                            }

                        }

                    },

                    tooltip: {

                        callbacks: {

                            label: function(context){

                                const value = context.raw;

                                const total = context.dataset.data.reduce((a,b)=>a+b,0);

                                const percent = ((value/total)*100).toFixed(1);

                                return `${context.label}: ${value} (${percent}%)`;

                            }

                        }

                    },

                    datalabels: {

                        color:"#fff",

                        font:{

                            weight:"bold",

                            size:14

                        },

                        formatter:(value,ctx)=>{

                            const total = ctx.dataset.data.reduce((a,b)=>a+b,0);

                            return ((value/total)*100).toFixed(1)+"%";

                        }

                    }

                }

            }

        });

    }

    // =========================
    // BAR CHART
    // =========================

    const stockCanvas = document.getElementById("stockChart");

    if(stockCanvas){

        new Chart(stockCanvas,{

            type:"bar",

            data:{

                labels:data.stockLabels,

                datasets:[{

                    label:"Available Stock",

                    data:data.stockValues,

                    backgroundColor:"#2563eb",

                    hoverBackgroundColor:"#1d4ed8",

                    borderRadius:10,

                    borderSkipped:false

                }]

            },

            plugins:[ChartDataLabels],

            options:{

                responsive:true,

                maintainAspectRatio:false,

                animation:{

                    duration:1000

                },

                scales:{

                    x:{

                        grid:{

                            display:false

                        }

                    },

                    y:{

                        beginAtZero:true,

                        ticks:{

                            precision:0

                        },

                        grid:{

                            color:"#e5e7eb"

                        }

                    }

                },

                plugins:{

                    legend:{

                        display:true,

                        labels:{

                            usePointStyle:true,

                            font:{

                                size:13,

                                weight:"bold"

                            }

                        }

                    },

                    datalabels:{

                        anchor:"end",

                        align:"top",

                        color:"#111827",

                        font:{

                            weight:"bold"

                        }

                    }

                }

            }

        });

    }

});