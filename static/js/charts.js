/**
 * Novellus Loan Management - Chart Utilities
 * Chart.js configurations and helpers for loan visualizations
 */

class ChartManager {
    constructor() {
        this.charts = new Map();
        this.defaultColors = {
            primary: '#0d6efd',
            secondary: '#6c757d',
            success: '#198754',
            danger: '#dc3545',
            warning: '#ffc107',
            info: '#0dcaf0',
            light: '#f8f9fa',
            dark: '#212529'
        };
    }

    /**
     * Create payment schedule chart
     */
    createPaymentScheduleChart(canvasId, schedule, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !schedule || schedule.length === 0) return null;

        // Destroy existing chart if it exists
        if (this.charts.has(canvasId)) {
            this.charts.get(canvasId).destroy();
        }

        const labels = schedule.map((_, index) => index + 1);
        const principalData = schedule.map(payment => payment.principal || 0);
        const interestData = schedule.map(payment => payment.interest || 0);
        const balanceData = schedule.map(payment => payment.balance || 0);

        let config = {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Principal Payment',
                        data: principalData,
                        backgroundColor: this.addTransparency(this.defaultColors.primary, 0.7),
                        borderColor: this.defaultColors.primary,
                        borderWidth: 1,
                        stack: 'payments'
                    },
                    {
                        label: 'Interest Payment',
                        data: interestData,
                        backgroundColor: this.addTransparency(this.defaultColors.danger, 0.7),
                        borderColor: this.defaultColors.danger,
                        borderWidth: 1,
                        stack: 'payments'
                    },
                    {
                        label: 'Remaining Balance',
                        data: balanceData,
                        type: 'line',
                        backgroundColor: this.addTransparency(this.defaultColors.success, 0.2),
                        borderColor: this.defaultColors.success,
                        borderWidth: 3,
                        yAxisID: 'y1',
                        fill: false,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    title: {
                        display: true,
                        text: options.title || 'Payment Schedule Breakdown',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.dataset.label || '';
                                const value = context.parsed.y;
                                const currency = options.currency || '£';
                                return `${label}: ${currency}${value.toLocaleString('en-GB', {minimumFractionDigits: 2})}`;
                            }
                        }
                    },
                    datalabels: {
                        display: true,
                        anchor: 'end',
                        align: 'top',
                        color: '#333',
                        font: {
                            weight: 'bold',
                            size: function(context) {
                                // Increase font size when in fullscreen mode
                                const isFullscreen = document.fullscreenElement !== null;
                                return isFullscreen ? 16 : 12;
                            }
                        },
                        formatter: function(value, context) {
                            const currency = context.chart.options.plugins.currency || '£';
                            if (value === 0) return '';
                            return currency + value.toLocaleString('en-GB', {minimumFractionDigits: 0, maximumFractionDigits: 0});
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Payment Period'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Payment Amount'
                        },
                        ticks: {
                            callback: function(value) {
                                const currency = options.currency || '£';
                                return currency + value.toLocaleString('en-GB');
                            }
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Outstanding Balance'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                        ticks: {
                            callback: function(value) {
                                const currency = options.currency || '£';
                                return currency + value.toLocaleString('en-GB');
                            }
                        }
                    }
                },
                ...options.chartOptions
            }
        };

        // Add data labels if ChartEnhancer is available
        if (typeof window.ChartEnhancer !== 'undefined' && config.type === 'pie') {
            config = window.ChartEnhancer.enhancePieChart(config, {});
        } else if (typeof window.ChartEnhancer !== 'undefined' && config.type === 'bar') {
            config = window.ChartEnhancer.enhanceBarChart(config, {});
        } else if (typeof window.ChartEnhancer !== 'undefined' && config.type === 'line') {
            config = window.ChartEnhancer.enhanceLineChart(config, {});
        }

        const chart = new Chart(ctx, config);
        this.charts.set(canvasId, chart);
        return chart;
    }

    /**
     * Create loan balance over time chart
     */
    createLoanBalanceChart(canvasId, schedule, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !schedule || schedule.length === 0) return null;

        if (this.charts.has(canvasId)) {
            this.charts.get(canvasId).destroy();
        }

        const labels = schedule.map((_, index) => index + 1);
        const balanceData = schedule.map(payment => payment.balance || 0);
        // Helper to parse currency strings or numbers
        const parseValue = (val) => {
            if (typeof val === 'string') {
                const cleaned = val.replace(/[^0-9.-]/g, '');
                return parseFloat(cleaned) || 0;
            }
            return val || 0;
        };
        // Build running sum for interest accrued
        let cumulativeAccrued = 0;
        const interestAccruedData = schedule.map(payment => {
            const val = parseValue(payment.interest_accrued_raw ?? payment.interest_accrued);
            cumulativeAccrued += val;
            return cumulativeAccrued;
        });

        let config = {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Outstanding Balance',
                        data: balanceData,
                        type: 'bar',
                        backgroundColor: this.addTransparency(this.defaultColors.primary, 0.6),
                        borderColor: this.defaultColors.primary,
                        borderWidth: 1,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Interest Accrued',
                        data: interestAccruedData,
                        type: 'line',
                        backgroundColor: this.addTransparency(this.defaultColors.secondary, 0.1),
                        borderColor: this.defaultColors.secondary,
                        borderWidth: 3,
                        fill: false,
                        tension: 0.4,
                        pointBackgroundColor: this.defaultColors.secondary,
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true
                    },
                    title: {
                        display: true,
                        text: options.title || 'Loan Balance & Interest Over Time',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.parsed.y;
                                const currency = options.currency || '£';
                                return `${context.dataset.label}: ${currency}${value.toLocaleString('en-GB', {minimumFractionDigits: 2})}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Payment Period'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Outstanding Balance'
                        },
                        ticks: {
                            callback: function(value) {
                                const currency = options.currency || '£';
                                return currency + value.toLocaleString('en-GB');
                            }
                        }
                    },
                    y1: {
                        title: {
                            display: true,
                            text: 'Interest'
                        },
                        position: 'right',
                        grid: {
                            drawOnChartArea: false
                        },
                        ticks: {
                            callback: function(value) {
                                const currency = options.currency || '£';
                                return currency + value.toLocaleString('en-GB');
                            }
                        }
                    }
                },
                ...options.chartOptions
            }
        };

        // Add data labels if ChartEnhancer is available
        if (typeof window.ChartEnhancer !== 'undefined' && config.type === 'pie') {
            config = window.ChartEnhancer.enhancePieChart(config, {});
        } else if (typeof window.ChartEnhancer !== 'undefined' && config.type === 'bar') {
            config = window.ChartEnhancer.enhanceBarChart(config, {});
        } else if (typeof window.ChartEnhancer !== 'undefined' && config.type === 'line') {
            config = window.ChartEnhancer.enhanceLineChart(config, {});
        }

        const chart = new Chart(ctx, config);
        this.charts.set(canvasId, chart);
        return chart;
    }

    /**
     * Create interest vs principal breakdown chart
     */
    createInterestBreakdownChart(canvasId, schedule, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !schedule || schedule.length === 0) return null;

        if (this.charts.has(canvasId)) {
            this.charts.get(canvasId).destroy();
        }

        const totalInterest = schedule.reduce((sum, payment) => sum + (payment.interest || 0), 0);
        const totalPrincipal = schedule.reduce((sum, payment) => sum + (payment.principal || 0), 0);

        let config = {
            type: 'doughnut',
            data: {
                labels: ['Total Interest', 'Total Principal'],
                datasets: [{
                    data: [totalInterest, totalPrincipal],
                    backgroundColor: [
                        this.defaultColors.danger,
                        this.defaultColors.primary
                    ],
                    borderColor: [
                        this.defaultColors.danger,
                        this.defaultColors.primary
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    title: {
                        display: true,
                        text: options.title || 'Interest vs Principal Breakdown',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = totalInterest + totalPrincipal;
                                const percentage = ((value / total) * 100).toFixed(1);
                                const currency = options.currency || '£';
                                return `${label}: ${currency}${value.toLocaleString('en-GB', {minimumFractionDigits: 2})} (${percentage}%)`;
                            }
                        }
                    }
                },
                ...options.chartOptions
            }
        };

        // Add data labels if ChartEnhancer is available
        if (typeof window.ChartEnhancer !== 'undefined' && config.type === 'pie') {
            config = window.ChartEnhancer.enhancePieChart(config, {});
        } else if (typeof window.ChartEnhancer !== 'undefined' && config.type === 'bar') {
            config = window.ChartEnhancer.enhanceBarChart(config, {});
        } else if (typeof window.ChartEnhancer !== 'undefined' && config.type === 'line') {
            config = window.ChartEnhancer.enhanceLineChart(config, {});
        }

        const chart = new Chart(ctx, config);
        this.charts.set(canvasId, chart);
        return chart;
    }

    /**
     * Create LTV comparison chart
     */
    createLTVChart(canvasId, currentLTV, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        if (this.charts.has(canvasId)) {
            this.charts.get(canvasId).destroy();
        }

        const maxLTV = 100;
        const remainingLTV = maxLTV - currentLTV;

        let config = {
            type: 'doughnut',
            data: {
                labels: ['Current LTV', 'Available'],
                datasets: [{
                    data: [currentLTV, remainingLTV],
                    backgroundColor: [
                        this.getLTVColor(currentLTV),
                        this.addTransparency('#e9ecef', 0.7)
                    ],
                    borderColor: [
                        this.getLTVColor(currentLTV),
                        '#e9ecef'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: options.title || 'Loan to Value Ratio',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                return `${label}: ${value.toFixed(1)}%`;
                            }
                        }
                    }
                },
                ...options.chartOptions
            },
            plugins: [{
                id: 'centerText',
                beforeDraw: function(chart) {
                    const width = chart.width;
                    const height = chart.height;
                    const ctx = chart.ctx;
                    
                    ctx.restore();
                    const fontSize = (height / 114).toFixed(2);
                    ctx.font = `bold ${fontSize}em sans-serif`;
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = chart.config.options.plugins.centerTextColor || '#333';
                    
                    const text = `${currentLTV.toFixed(1)}%`;
                    const textX = Math.round((width - ctx.measureText(text).width) / 2);
                    const textY = height / 2;
                    
                    ctx.fillText(text, textX, textY);
                    ctx.save();
                }
            }]
        };

        // Add data labels if ChartEnhancer is available (skip for LTV chart with custom plugins)
        if (typeof window.ChartEnhancer !== 'undefined' && config.type === 'pie' && !config.plugins) {
            config = window.ChartEnhancer.enhancePieChart(config, {});
        } else if (typeof window.ChartEnhancer !== 'undefined' && config.type === 'bar') {
            config = window.ChartEnhancer.enhanceBarChart(config, {});
        } else if (typeof window.ChartEnhancer !== 'undefined' && config.type === 'line') {
            config = window.ChartEnhancer.enhanceLineChart(config, {});
        }

        const chart = new Chart(ctx, config);
        this.charts.set(canvasId, chart);
        return chart;
    }

    /**
     * Get color based on LTV value
     */
    getLTVColor(ltv) {
        if (ltv <= 70) return this.defaultColors.success;
        if (ltv <= 80) return this.defaultColors.warning;
        if (ltv <= 90) return '#fd7e14'; // orange
        return this.defaultColors.danger;
    }

    /**
     * Add transparency to a color
     */
    addTransparency(color, alpha) {
        // Convert hex to rgba
        const hex = color.replace('#', '');
        const r = parseInt(hex.substr(0, 2), 16);
        const g = parseInt(hex.substr(2, 2), 16);
        const b = parseInt(hex.substr(4, 2), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    /**
     * Destroy a specific chart
     */
    destroyChart(canvasId) {
        if (this.charts.has(canvasId)) {
            this.charts.get(canvasId).destroy();
            this.charts.delete(canvasId);
        }
    }

    /**
     * Destroy all charts
     */
    destroyAllCharts() {
        this.charts.forEach(chart => chart.destroy());
        this.charts.clear();
    }

    /**
     * Update chart data
     */
    updateChart(canvasId, newData) {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.data = newData;
            chart.update();
        }
    }

    /**
     * Export chart as image
     */
    exportChart(canvasId, filename = 'chart') {
        const chart = this.charts.get(canvasId);
        if (chart) {
            const url = chart.toBase64Image();
            const link = document.createElement('a');
            link.download = `${filename}.png`;
            link.href = url;
            link.click();
        }
    }
}

// Global chart manager instance
window.chartManager = new ChartManager();

// Chart.js default configuration
Chart.defaults.font.family = "'Brother 1816', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.color = '#495057';
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0, 0, 0, 0.8)';
Chart.defaults.plugins.tooltip.titleColor = '#fff';
Chart.defaults.plugins.tooltip.bodyColor = '#fff';
Chart.defaults.plugins.tooltip.cornerRadius = 6;

// Helper functions for common chart operations
window.createPaymentChart = function(canvasId, schedule, options = {}) {
    return window.chartManager.createPaymentScheduleChart(canvasId, schedule, options);
};

window.createBalanceChart = function(canvasId, schedule, options = {}) {
    return window.chartManager.createLoanBalanceChart(canvasId, schedule, options);
};

window.createInterestChart = function(canvasId, schedule, options = {}) {
    return window.chartManager.createInterestBreakdownChart(canvasId, schedule, options);
};

window.createLTVChart = function(canvasId, ltv, options = {}) {
    return window.chartManager.createLTVChart(canvasId, ltv, options);
};

// Export functions for ES6 modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChartManager;
}
