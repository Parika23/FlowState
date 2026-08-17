document.addEventListener("DOMContentLoaded", function () {

    /**
     * Generic function to create a line chart
     */
    function createLineChart(canvasId, chartData, label, color) {

        if (typeof chartData === "undefined") {
            return;
        }

        const canvas = document.getElementById(canvasId);

        if (!canvas) {
            return;
        }

        new Chart(canvas, {

            type: "line",

            data: {

                labels: chartData.labels,

                datasets: [

                    {

                        label: label,

                        data: chartData.values,

                        borderColor: color,

                        backgroundColor: color + "33",

                        borderWidth: 3,

                        pointRadius: 5,

                        pointHoverRadius: 7,

                        tension: 0.35,

                        fill: false

                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: true,

                plugins: {

                    legend: {

                        display: true,

                        position: "top"

                    },

                    tooltip: {

                        enabled: true

                    }

                },

                scales: {

                    y: {

                        min: 0,

                        max: 100

                    }

                }

            }

        });

    }

    // =====================================
    // Recovery Chart
    // =====================================

    createLineChart(

        "recoveryChart",

        recoveryChartData,

        "Recovery Score",

        "#198754"

    );

    // =====================================
    // Productivity Chart
    // =====================================

    createLineChart(

        "productivityChart",

        productivityChartData,

        "Productivity Score",

        "#6f42c1"

    );
 
    // =====================================
    // Flow State Chart
    // =====================================

    createLineChart(

        "flowstateChart",

        flowstateChartData,

        "FlowState Index",

        "#0d6efd"

    );
});
