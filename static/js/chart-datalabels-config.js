/**
 * Chart.js Data Labels Configuration
 * Adds permanent value display to all charts
 */

// Register the datalabels plugin globally for all charts
if (typeof Chart !== 'undefined' && typeof ChartDataLabels !== 'undefined') {
    Chart.register(ChartDataLabels);
    
    // Set global defaults for data labels
    Chart.defaults.plugins.datalabels = {
        display: false, // Disable by default, enable per chart
        color: 'white',
        font: {
            weight: 'bold',
            size: 11
        },
        textAlign: 'center'
    };
}

// Enhanced chart creation functions with data labels
window.ChartEnhancer = {
    // Add data labels to pie/doughnut charts
    enhancePieChart: function(chartConfig, results) {
        if (!chartConfig.options) chartConfig.options = {};
        if (!chartConfig.options.plugins) chartConfig.options.plugins = {};
        
        chartConfig.options.plugins.datalabels = {
            display: true,
            color: 'white',
            font: {
                weight: 'bold',
                size: 11
            },
            formatter: function(value, context) {
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = ((value / total) * 100).toFixed(1);
                const currency = results && results.currencySymbol ? results.currencySymbol : '£';
                if (percentage < 3) return ''; // Hide very small percentages
                return `${percentage}%\n${currency}${(value/1000).toFixed(0)}k`;
            },
            textAlign: 'center'
        };
        
        if (!chartConfig.plugins) chartConfig.plugins = [];
        if (!chartConfig.plugins.includes(ChartDataLabels)) {
            chartConfig.plugins.push(ChartDataLabels);
        }
        
        return chartConfig;
    },
    
    // Add data labels to bar charts
    enhanceBarChart: function(chartConfig, results) {
        if (!chartConfig.options) chartConfig.options = {};
        if (!chartConfig.options.plugins) chartConfig.options.plugins = {};
        
        chartConfig.options.plugins.datalabels = {
            display: true,
            color: 'black',
            font: {
                weight: 'bold',
                size: 10
            },
            anchor: 'end',
            align: 'top',
            formatter: function(value, context) {
                const currency = results && results.currencySymbol ? results.currencySymbol : '£';
                if (value === 0) return '';
                return `${currency}${(value/1000).toFixed(0)}k`;
            }
        };
        
        if (!chartConfig.plugins) chartConfig.plugins = [];
        if (!chartConfig.plugins.includes(ChartDataLabels)) {
            chartConfig.plugins.push(ChartDataLabels);
        }
        
        return chartConfig;
    },
    
    // Add data labels to line charts
    enhanceLineChart: function(chartConfig, results) {
        if (!chartConfig.options) chartConfig.options = {};
        if (!chartConfig.options.plugins) chartConfig.options.plugins = {};
        
        chartConfig.options.plugins.datalabels = {
            display: true,
            color: 'black',
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            borderColor: 'rgba(0, 0, 0, 0.1)',
            borderRadius: 4,
            borderWidth: 1,
            font: {
                weight: 'bold',
                size: 9
            },
            padding: 4,
            formatter: function(value, context) {
                const currency = results && results.currencySymbol ? results.currencySymbol : '£';
                if (value === 0) return '';
                return `${currency}${(value/1000).toFixed(0)}k`;
            }
        };
        
        if (!chartConfig.plugins) chartConfig.plugins = [];
        if (!chartConfig.plugins.includes(ChartDataLabels)) {
            chartConfig.plugins.push(ChartDataLabels);
        }
        
        return chartConfig;
    }
};

console.log('Chart Data Labels configuration loaded');