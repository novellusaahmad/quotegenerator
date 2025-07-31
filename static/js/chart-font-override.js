/**
 * Chart Font Size Override for Better Data Marker Visibility
 * This script ensures all chart data labels are large and readable
 */

// Force bigger data label fonts with CSS override
const chartFontStyle = document.createElement('style');
chartFontStyle.textContent = `
    /* Force bigger data label fonts */
    .chartjs-datalabels {
        font-size: 18px !important;
        font-weight: bold !important;
        color: #333 !important;
        text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8) !important;
    }
    
    /* Chart legend fonts */
    .chartjs-legend {
        font-size: 16px !important;
    }
    
    /* Chart title fonts */
    .chartjs-title {
        font-size: 20px !important;
        font-weight: bold !important;
    }
    
    /* Tooltip fonts */
    .chartjs-tooltip {
        font-size: 14px !important;
    }
    
    /* Axis label fonts */
    .chartjs-axis-label {
        font-size: 14px !important;
    }
`;
document.head.appendChild(chartFontStyle);

// Global Chart.js configuration override for data labels
window.ChartDataLabelDefaults = {
    display: true,
    anchor: 'end',
    align: 'top',
    color: '#333',
    backgroundColor: 'rgba(255, 255, 255, 0.8)',
    borderRadius: 4,
    padding: 6,
    font: {
        weight: 'bold',
        size: 18 // Large default size
    },
    formatter: function(value, context) {
        const currency = '£';
        if (value === 0 || value === null || value === undefined) return '';
        
        // Format large numbers with K/M suffixes for space
        if (value >= 1000000) {
            return currency + (value / 1000000).toFixed(1) + 'M';
        } else if (value >= 1000) {
            return currency + (value / 1000).toFixed(0) + 'K';
        } else {
            return currency + value.toLocaleString('en-GB', {
                minimumFractionDigits: 0, 
                maximumFractionDigits: 0
            });
        }
    }
};

// Apply bigger fonts when Chart.js is ready
document.addEventListener('DOMContentLoaded', function() {
    // Override Chart.js defaults after library loads
    if (typeof Chart !== 'undefined') {
        console.log('Applying big font overrides to Chart.js');
        
        // Force register the datalabels plugin
        if (typeof ChartDataLabels !== 'undefined') {
            Chart.register(ChartDataLabels);
        }
        
        // Set global defaults for bigger fonts
        Chart.defaults.font.size = 16;
        Chart.defaults.plugins = Chart.defaults.plugins || {};
        Chart.defaults.plugins.datalabels = window.ChartDataLabelDefaults;
        
        console.log('Chart.js big font configuration applied');
    }
});

console.log('Chart font override script loaded - data markers will be bigger!');