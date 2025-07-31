/**
 * Chart.js Data Labels Enhancement for Fullscreen Mode
 * Provides better visibility for data markers in fullscreen visualizations
 */

// Global Chart.js configurations with bigger fonts for better visibility
Chart.defaults.font.family = "'Brother1816', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.font.size = 16; // Increased from default 12 to 16
Chart.defaults.color = '#495057';

// Safely set font sizes with fallback for undefined properties
if (Chart.defaults.plugins && Chart.defaults.plugins.legend && Chart.defaults.plugins.legend.labels) {
    Chart.defaults.plugins.legend.labels.font = Chart.defaults.plugins.legend.labels.font || {};
    Chart.defaults.plugins.legend.labels.font.size = 16;
}

if (Chart.defaults.plugins && Chart.defaults.plugins.title) {
    Chart.defaults.plugins.title.font = Chart.defaults.plugins.title.font || {};
    Chart.defaults.plugins.title.font.size = 20;
}

if (Chart.defaults.plugins && Chart.defaults.plugins.tooltip) {
    Chart.defaults.plugins.tooltip.titleFont = Chart.defaults.plugins.tooltip.titleFont || {};
    Chart.defaults.plugins.tooltip.titleFont.size = 16;
    Chart.defaults.plugins.tooltip.bodyFont = Chart.defaults.plugins.tooltip.bodyFont || {};
    Chart.defaults.plugins.tooltip.bodyFont.size = 14;
}

// Register the datalabels plugin if available
if (typeof ChartDataLabels !== 'undefined') {
    Chart.register(ChartDataLabels);
}

// Enhanced Chart Configuration Helper
class ChartDataLabelsEnhancer {
    static enhanceChart(config, options = {}) {
        // Add fullscreen-aware data labels configuration
        if (!config.options.plugins) {
            config.options.plugins = {};
        }
        
        config.options.plugins.datalabels = {
            display: true,
            anchor: 'end',
            align: 'top',
            color: '#333',
            font: {
                weight: 'bold',
                size: function(context) {
                    // Use much bigger font sizes for better visibility
                    const isFullscreen = document.fullscreenElement !== null;
                    const baseSize = options.baseFontSize || 20; // Increased from 16 to 20
                    return isFullscreen ? baseSize + 10 : baseSize; // Increased fullscreen bonus to 10
                }
            },
            formatter: function(value, context) {
                const currency = options.currency || '£';
                if (value === 0 || value === null || value === undefined) return '';
                
                // Format numbers based on value size
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
        
        // Enhanced tooltip configuration
        if (!config.options.plugins.tooltip) {
            config.options.plugins.tooltip = {};
        }
        
        config.options.plugins.tooltip.backgroundColor = 'rgba(0, 0, 0, 0.8)';
        config.options.plugins.tooltip.titleColor = '#fff';
        config.options.plugins.tooltip.bodyColor = '#fff';
        config.options.plugins.tooltip.cornerRadius = 6;
        config.options.plugins.tooltip.titleFont = {
            size: 14,
            weight: 'bold'
        };
        config.options.plugins.tooltip.bodyFont = {
            size: 12
        };
        
        return config;
    }
    
    static enhancePieChart(config, options = {}) {
        config = this.enhanceChart(config, options);
        
        // Pie chart specific data label positioning
        config.options.plugins.datalabels.align = 'end';
        config.options.plugins.datalabels.anchor = 'end';
        config.options.plugins.datalabels.offset = 10;
        
        return config;
    }
    
    static enhanceBarChart(config, options = {}) {
        config = this.enhanceChart(config, options);
        
        // Bar chart specific data label positioning
        config.options.plugins.datalabels.align = 'top';
        config.options.plugins.datalabels.anchor = 'end';
        
        return config;
    }
    
    static enhanceLineChart(config, options = {}) {
        config = this.enhanceChart(config, options);
        
        // Line chart specific data label positioning with bigger fonts
        config.options.plugins.datalabels.backgroundColor = 'rgba(255, 255, 255, 0.9)';
        config.options.plugins.datalabels.borderColor = '#333';
        config.options.plugins.datalabels.borderRadius = 6;
        config.options.plugins.datalabels.borderWidth = 2;
        config.options.plugins.datalabels.padding = 6;
        
        return config;
    }
}

// Make the enhancer available globally
window.ChartDataLabelsEnhancer = ChartDataLabelsEnhancer;

// Add fullscreen event listeners to update charts when entering/exiting fullscreen
document.addEventListener('fullscreenchange', function() {
    // Trigger chart updates when fullscreen mode changes
    setTimeout(() => {
        if (window.calculator && window.calculator.charts) {
            Object.values(window.calculator.charts).forEach(chart => {
                if (chart && typeof chart.update === 'function') {
                    chart.update('resize');
                }
            });
        }
        
        // Also update chartManager charts if available
        if (window.chartManager && window.chartManager.charts) {
            window.chartManager.charts.forEach(chart => {
                if (chart && typeof chart.update === 'function') {
                    chart.update('resize');
                }
            });
        }
    }, 100);
});

console.log('Chart Data Labels Enhancement loaded with fullscreen support');