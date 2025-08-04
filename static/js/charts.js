function renderEquityCurve(chartData) {
    const ctx = document.getElementById('equityCurveChart').getContext('2d');
    const dates = chartData.map(d => d.Date);
    const portfolioValues = chartData.map(d => d.Portfolio_Value);

    new Chart(ctx, {
        type: 'line', data: { labels: dates, datasets: [{ label: 'Portfolio Value (₹)', data: portfolioValues, borderColor: '#1877f2', backgroundColor: 'rgba(24, 119, 242, 0.1)', fill: true, tension: 0.1, pointRadius: 0 }] },
        options: { responsive: true, maintainAspectRatio: false, scales: { x: { title: { display: true, text: 'Date' }}, y: { title: { display: true, text: 'Portfolio Value (₹)' }}}}
    });
}

// NEW: Function to render the drawdown chart
function renderDrawdownChart(chartData) {
    const ctx = document.getElementById('drawdownChart').getContext('2d');
    const dates = chartData.map(d => d.Date);
    const drawdownValues = chartData.map(d => d.Drawdown * 100); // Convert to percentage

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Drawdown (%)',
                data: drawdownValues,
                borderColor: '#fa383e',
                backgroundColor: 'rgba(250, 56, 62, 0.1)',
                fill: true,
                tension: 0.1,
                pointRadius: 0
            }]
        },
        options: { responsive: true, maintainAspectRatio: false, scales: { y: { ticks: { callback: function(value) { return value + '%' }}}}}
    });
}

// NEW: Function to render the returns histogram
function renderReturnsHistogram(returnsData) {
    const ctx = document.getElementById('returnsHistogram').getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            // We create bins for the histogram here
            labels: returnsData.map((_, i) => i), // dummy labels
            datasets: [{
                label: 'Daily Return Frequency',
                data: returnsData.map(r => r * 100), // Convert to percentage
                backgroundColor: 'rgba(24, 119, 242, 0.6)',
                barPercentage: 1.0,
                categoryPercentage: 1.0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    display: false // Hide x-axis labels for a clean histogram look
                },
                y: {
                    title: { display: true, text: 'Frequency' }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Return: ${context.raw.toFixed(2)}%`;
                        }
                    }
                }
            }
        }
    });
}