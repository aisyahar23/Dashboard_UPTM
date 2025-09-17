// static/js/components.js - Extended Version with Missing Methods

// Global Chart Factory with Enhanced Styling
class ChartFactory {
    static defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            intersect: false,
            mode: 'index'
        },
        plugins: {
            legend: {
                display: false,
                position: 'top',
                labels: {
                    usePointStyle: true,
                    padding: 20,
                    font: {
                        size: 12,
                        weight: '500',
                        family: "'Inter', 'Segoe UI', sans-serif"
                    }
                }
            },
            tooltip: {
                backgroundColor: 'rgba(17, 24, 39, 0.95)',
                titleColor: '#ffffff',
                bodyColor: '#ffffff',
                cornerRadius: 12,
                padding: 16,
                titleFont: {
                    size: 14,
                    weight: '600',
                    family: "'Inter', 'Segoe UI', sans-serif"
                },
                bodyFont: {
                    size: 13,
                    family: "'Inter', 'Segoe UI', sans-serif"
                },
                displayColors: true,
                boxPadding: 6,
                usePointStyle: true
            }
        },
        elements: {
            point: {
                radius: 6,
                hoverRadius: 8,
                backgroundColor: '#ffffff',
                borderWidth: 3
            },
            line: {
                tension: 0.4,
                borderWidth: 3
            },
            bar: {
                borderRadius: 6,
                borderSkipped: false
            }
        }
    };

    static corporateColors = {
        primary: '#1e40af',     // Blue 700
        secondary: '#7c3aed',   // Violet 600
        success: '#059669',     // Emerald 600
        warning: '#d97706',     // Amber 600
        danger: '#dc2626',      // Red 600
        info: '#0891b2',        // Cyan 600
        gradient: [
            '#1e40af', '#3b82f6', '#6366f1', '#8b5cf6', 
            '#a855f7', '#d946ef', '#ec4899', '#f43f5e'
        ],
        neutral: [
            '#374151', '#6b7280', '#9ca3af', '#d1d5db',
            '#e5e7eb', '#f3f4f6', '#f9fafb'
        ]
    };

    static createBarChart(ctx, data, options = {}) {
        const enhancedData = {
            ...data,
            datasets: data.datasets.map((dataset, index) => ({
                ...dataset,
                backgroundColor: dataset.backgroundColor || this.corporateColors.gradient[index % this.corporateColors.gradient.length],
                borderColor: dataset.borderColor || this.corporateColors.gradient[index % this.corporateColors.gradient.length],
                borderWidth: 0,
                borderRadius: 8,
                borderSkipped: false
            }))
        };

        return new Chart(ctx, {
            type: 'bar',
            data: enhancedData,
            options: {
                ...this.defaultOptions,
                ...options,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { 
                            color: 'rgba(0,0,0,0.04)', 
                            drawBorder: false,
                            lineWidth: 1
                        },
                        ticks: { 
                            font: { 
                                size: 12, 
                                weight: '500',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#6b7280',
                            padding: 12
                        }
                    },
                    x: { 
                        grid: { display: false },
                        ticks: { 
                            font: { 
                                size: 12, 
                                weight: '500',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#6b7280',
                            maxRotation: 45,
                            padding: 8
                        }
                    },
                    ...options.scales
                },
                plugins: {
                    ...this.defaultOptions.plugins,
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label || 'Value'}: ${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    },
                    ...options.plugins
                }
            }
        });
    }

    static createMultipleBarChart(ctx, data, options = {}) {
        const enhancedData = {
            ...data,
            datasets: data.datasets.map((dataset, index) => ({
                ...dataset,
                backgroundColor: dataset.backgroundColor || this.corporateColors.gradient[index % this.corporateColors.gradient.length],
                borderColor: dataset.borderColor || this.corporateColors.gradient[index % this.corporateColors.gradient.length],
                borderWidth: 0,
                borderRadius: 6,
                borderSkipped: false,
                barThickness: 'flex',
                maxBarThickness: 40
            }))
        };

        return new Chart(ctx, {
            type: 'bar',
            data: enhancedData,
            options: {
                ...this.defaultOptions,
                ...options,
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: {
                        display: true,
                        position: 'top',
                        align: 'end',
                        labels: {
                            usePointStyle: true,
                            pointStyle: 'rect',
                            padding: 20,
                            font: {
                                size: 12,
                                weight: '500',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#374151'
                        }
                    },
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    },
                    ...options.plugins
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { 
                            color: 'rgba(0,0,0,0.04)', 
                            drawBorder: false,
                            lineWidth: 1
                        },
                        ticks: { 
                            font: { 
                                size: 12, 
                                weight: '500',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#6b7280',
                            padding: 12,
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    },
                    x: { 
                        grid: { display: false },
                        ticks: { 
                            font: { 
                                size: 12, 
                                weight: '500',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#6b7280',
                            maxRotation: 45,
                            padding: 8
                        }
                    },
                    ...options.scales
                }
            }
        });
    }

    static createStackedBarChart(ctx, data, options = {}) {
        const enhancedData = {
            ...data,
            datasets: data.datasets.map((dataset, index) => ({
                ...dataset,
                backgroundColor: dataset.backgroundColor || this.corporateColors.gradient[index % this.corporateColors.gradient.length],
                borderColor: dataset.borderColor || this.corporateColors.gradient[index % this.corporateColors.gradient.length],
                borderWidth: 0,
                borderRadius: 6,
                borderSkipped: false
            }))
        };

        return new Chart(ctx, {
            type: 'bar',
            data: enhancedData,
            options: {
                ...this.defaultOptions,
                ...options,
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: {
                        display: true,
                        position: 'top',
                        align: 'end',
                        labels: {
                            usePointStyle: true,
                            pointStyle: 'rect',
                            padding: 20,
                            font: {
                                size: 12,
                                weight: '500',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#374151'
                        }
                    },
                    ...options.plugins
                },
                scales: {
                    x: { 
                        stacked: true,
                        grid: { display: false },
                        ticks: { 
                            font: { 
                                size: 12, 
                                weight: '500',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#6b7280',
                            maxRotation: 45
                        }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        grid: { 
                            color: 'rgba(0,0,0,0.04)', 
                            drawBorder: false,
                            lineWidth: 1
                        },
                        ticks: { 
                            font: { 
                                size: 12, 
                                weight: '500',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#6b7280',
                            padding: 12
                        }
                    },
                    ...options.scales
                }
            }
        });
    }

    static createLineChart(ctx, data, options = {}) {
        const enhancedData = {
            ...data,
            datasets: data.datasets.map((dataset, index) => ({
                ...dataset,
                backgroundColor: dataset.backgroundColor || `${this.corporateColors.gradient[index % this.corporateColors.gradient.length]}20`,
                borderColor: dataset.borderColor || this.corporateColors.gradient[index % this.corporateColors.gradient.length],
                borderWidth: 3,
                tension: 0.4,
                fill: dataset.fill !== undefined ? dataset.fill : false,
                pointBackgroundColor: '#ffffff',
                pointBorderColor: dataset.borderColor || this.corporateColors.gradient[index % this.corporateColors.gradient.length],
                pointBorderWidth: 3,
                pointRadius: 6,
                pointHoverRadius: 8,
                pointHoverBackgroundColor: '#ffffff',
                pointHoverBorderWidth: 4
            }))
        };

        return new Chart(ctx, {
            type: 'line',
            data: enhancedData,
            options: {
                ...this.defaultOptions,
                ...options,
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: {
                        display: data.datasets.length > 1,
                        position: 'top',
                        align: 'end',
                        labels: {
                            usePointStyle: true,
                            pointStyle: 'circle',
                            padding: 20,
                            font: {
                                size: 12,
                                weight: '500',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#374151'
                        }
                    },
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label || 'Value'}: ${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    },
                    ...options.plugins
                },
                scales: {
                    x: { 
                        grid: { 
                            display: true,
                            color: 'rgba(0,0,0,0.04)',
                            drawBorder: false,
                            lineWidth: 1
                        },
                        ticks: { 
                            font: { 
                                size: 12, 
                                weight: '500',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#6b7280',
                            maxRotation: 45,
                            padding: 8
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { 
                            color: 'rgba(0,0,0,0.04)', 
                            drawBorder: false,
                            lineWidth: 1
                        },
                        ticks: { 
                            font: { 
                                size: 12, 
                                weight: '500',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#6b7280',
                            padding: 12,
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    },
                    ...options.scales
                }
            }
        });
    }

    static createAreaChart(ctx, data, options = {}) {
        const enhancedData = {
            ...data,
            datasets: data.datasets.map((dataset, index) => ({
                ...dataset,
                backgroundColor: dataset.backgroundColor || `${this.corporateColors.gradient[index % this.corporateColors.gradient.length]}30`,
                borderColor: dataset.borderColor || this.corporateColors.gradient[index % this.corporateColors.gradient.length],
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#ffffff',
                pointBorderColor: dataset.borderColor || this.corporateColors.gradient[index % this.corporateColors.gradient.length],
                pointBorderWidth: 3,
                pointRadius: 5,
                pointHoverRadius: 8,
                pointHoverBackgroundColor: '#ffffff',
                pointHoverBorderWidth: 4
            }))
        };

        return new Chart(ctx, {
            type: 'line',
            data: enhancedData,
            options: {
                ...this.defaultOptions,
                ...options,
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: {
                        display: data.datasets.length > 1,
                        position: 'top',
                        align: 'end',
                        labels: {
                            usePointStyle: true,
                            pointStyle: 'circle',
                            padding: 20,
                            font: {
                                size: 12,
                                weight: '500',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#374151'
                        }
                    },
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label || 'Value'}: ${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    },
                    ...options.plugins
                },
                scales: {
                    x: { 
                        grid: { 
                            display: true,
                            color: 'rgba(0,0,0,0.04)',
                            drawBorder: false,
                            lineWidth: 1
                        },
                        ticks: { 
                            font: { 
                                size: 12, 
                                weight: '500',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#6b7280',
                            maxRotation: 45,
                            padding: 8
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { 
                            color: 'rgba(0,0,0,0.04)', 
                            drawBorder: false,
                            lineWidth: 1
                        },
                        ticks: { 
                            font: { 
                                size: 12, 
                                weight: '500',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#6b7280',
                            padding: 12,
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    },
                    ...options.scales
                }
            }
        });
    }

    static createPieChart(ctx, data, options = {}) {
        const enhancedData = {
            ...data,
            datasets: data.datasets.map((dataset) => ({
                ...dataset,
                backgroundColor: dataset.backgroundColor || this.corporateColors.gradient,
                borderColor: '#ffffff',
                borderWidth: 3,
                hoverBorderWidth: 4,
                hoverOffset: 8
            }))
        };

        return new Chart(ctx, {
            type: 'pie',
            data: enhancedData,
            options: {
                ...this.defaultOptions,
                ...options,
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            pointStyle: 'circle',
                            padding: 15,
                            font: {
                                size: 11,
                                weight: '500',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#374151',
                            boxWidth: 12,
                            boxHeight: 12,
                            maxWidth: 300,
                            generateLabels: function(chart) {
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {
                                    return data.labels.map((label, index) => {
                                        const dataset = data.datasets[0];
                                        const value = dataset.data[index];
                                        const total = dataset.data.reduce((sum, val) => sum + val, 0);
                                        const percentage = ((value / total) * 100).toFixed(1);
                                        
                                        return {
                                            text: `${label} (${percentage}%)`,
                                            fillStyle: dataset.backgroundColor[index],
                                            strokeStyle: dataset.borderColor,
                                            lineWidth: dataset.borderWidth,
                                            hidden: false,
                                            index: index
                                        };
                                    });
                                }
                                return [];
                            }
                        }
                    },
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((sum, val) => sum + val, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed.toLocaleString()} (${percentage}%)`;
                            }
                        }
                    },
                    ...options.plugins
                }
            }
        });
    }

    // Utility method to create gradient backgrounds
    static createGradient(ctx, colorStart, colorEnd, direction = 'vertical') {
        const gradient = direction === 'vertical' 
            ? ctx.createLinearGradient(0, 0, 0, ctx.canvas.height)
            : ctx.createLinearGradient(0, 0, ctx.canvas.width, 0);
        
        gradient.addColorStop(0, colorStart);
        gradient.addColorStop(1, colorEnd);
        return gradient;
    }

    // Method to get consistent color palette
    static getColorPalette(count = 8) {
        const colors = [...this.corporateColors.gradient];
        while (colors.length < count) {
            colors.push(...this.corporateColors.gradient);
        }
        return colors.slice(0, count);
    }
}

// Enhanced Dashboard Class (keeping existing functionality)
class Dashboard {
    constructor() {
        this.charts = {};
        this.filters = {};
        this.apiBase = '/api';
    }

    // Initialize dashboard
    init() {
        this.setupEventListeners();
        this.loadData();
        this.addCustomStyles();
    }

    // Add custom CSS styles for professional look
    addCustomStyles() {
        if (!document.getElementById('dashboard-styles')) {
            const style = document.createElement('style');
            style.id = 'dashboard-styles';
            style.textContent = `
                .chart-container {
                    background: #ffffff;
                    border-radius: 12px;
                    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
                    border: 1px solid rgba(0, 0, 0, 0.05);
                    transition: all 0.2s ease-in-out;
                }

                .chart-container:hover {
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                }

                .chart-header {
                    padding: 20px 24px 16px 24px;
                    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
                }

                .chart-title {
                    font-size: 18px;
                    font-weight: 600;
                    color: #111827;
                    margin-bottom: 4px;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                }

                .chart-subtitle {
                    font-size: 14px;
                    color: #6b7280;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                }

                .chart-body {
                    padding: 20px 24px 24px 24px;
                    height: 300px;
                    position: relative;
                }

                .chart-loading {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 100%;
                    color: #6b7280;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                }

                .chart-actions {
                    position: absolute;
                    top: 20px;
                    right: 24px;
                    display: flex;
                    gap: 8px;
                }

                .chart-action-btn {
                    padding: 6px;
                    background: rgba(0, 0, 0, 0.05);
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    transition: all 0.2s ease-in-out;
                    color: #6b7280;
                }

                .chart-action-btn:hover {
                    background: rgba(0, 0, 0, 0.1);
                    color: #374151;
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Enhanced chart container creation
    createChartContainer(id, title, subtitle = '') {
        return `
            <div class="chart-container" id="${id}-container">
                <div class="chart-header">
                    <div class="chart-actions">
                        <button class="chart-action-btn" onclick="dashboard.refreshChart('${id}')" title="Refresh Chart">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                            </svg>
                        </button>
                        <button class="chart-action-btn" onclick="dashboard.exportChart('${id}')" title="Export Chart">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                            </svg>
                        </button>
                    </div>
                    <h3 class="chart-title">${title}</h3>
                    ${subtitle ? `<p class="chart-subtitle">${subtitle}</p>` : ''}
                </div>
                <div class="chart-body">
                    <div class="chart-loading" id="${id}-loading">
                        <svg class="w-6 h-6 animate-spin mr-2" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 0 1 4 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Loading chart...
                    </div>
                    <canvas id="${id}" style="display: none;"></canvas>
                </div>
            </div>
        `;
    }

    // Method to show chart and hide loading
    showChart(chartId) {
        const loading = document.getElementById(`${chartId}-loading`);
        const canvas = document.getElementById(chartId);
        
        if (loading) loading.style.display = 'none';
        if (canvas) canvas.style.display = 'block';
    }

    // Method to refresh individual chart
    async refreshChart(chartId) {
        if (this.charts[chartId]) {
            this.charts[chartId].destroy();
        }
        
        const loading = document.getElementById(`${chartId}-loading`);
        const canvas = document.getElementById(chartId);
        
        if (loading) loading.style.display = 'flex';
        if (canvas) canvas.style.display = 'none';
        
        // Reload chart data - override this method in child classes
        await this.loadChartData(chartId);
    }

    // Method to export individual chart
    exportChart(chartId) {
        if (this.charts[chartId]) {
            const url = this.charts[chartId].toBase64Image();
            const link = document.createElement('a');
            link.download = `${chartId}-chart.png`;
            link.href = url;
            link.click();
            
            this.showToast(`Chart exported successfully`, 'success');
        }
    }

    // Show toast notification (enhanced with better styling)
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        const colors = {
            success: 'bg-emerald-500 text-white border-emerald-600',
            error: 'bg-red-500 text-white border-red-600',
            info: 'bg-blue-500 text-white border-blue-600',
            warning: 'bg-amber-500 text-white border-amber-600'
        };
        
        const icons = {
            success: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>',
            error: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>',
            info: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg>',
            warning: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>'
        };
        
        toast.className = `fixed top-4 right-4 ${colors[type]} px-4 py-3 rounded-lg shadow-lg z-50 transition-all duration-300 border-l-4 font-medium`;
        toast.innerHTML = `
            <div class="flex items-center">
                <div class="flex-shrink-0 mr-3">
                    ${icons[type]}
                </div>
                <div class="text-sm font-medium">${message}</div>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Animate in
        setTimeout(() => toast.style.transform = 'translateX(0)', 10);
        
        // Animate out and remove
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    // Override in child classes
    async loadData() {
        console.log('Override loadData method in child class');
    }

    // Override in child classes for individual chart loading
    async loadChartData(chartId) {
        console.log(`Override loadChartData method for chart: ${chartId}`);
    }
}

// Global dashboard instance
let dashboard;

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the appropriate dashboard based on page
    if (typeof faktorGraduanDashboard === 'function') {
        dashboard = faktorGraduanDashboard();
        dashboard.init();
    } else if (typeof sosioekonomiDashboard === 'function') {
        dashboard = sosioekonomiDashboard();
        dashboard.init();
    }
});

console.log('ChartFactory with all methods loaded successfully');