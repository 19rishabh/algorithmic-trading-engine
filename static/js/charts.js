// This function will be called from our HTML template
function renderEquityCurve(chartData) {
    const ctx = document.getElementById('equityCurveChart').getContext('2d');
    
    // The data is passed from our Flask app as a JSON string
    const dates = chartData.map(d => d.Date);
    const portfolioValues = chartData.map(d => d.Portfolio_Value);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Portfolio Value (₹)',
                data: portfolioValues,
                borderColor: '#1877f2',
                backgroundColor: 'rgba(24, 119, 242, 0.1)',
                fill: true,
                tension: 0.1,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Portfolio Value (₹)'
                    }
                }
            }
        }
    });
}