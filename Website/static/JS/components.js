// static/js/components.js

// Global Chart Management
window.globalCharts = {};

// Safe chart destruction function
function safeDestroyChart(chartId) {
    if (window.globalCharts[chartId]) {
        window.globalCharts[chartId].destroy();
        delete window.globalCharts[chartId];
    }
}

// Global Chart Factory
class ChartFactory {
    static defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false,
                position: 'bottom',
                labels: {
                    padding: 20,
                    usePointStyle: true,
                    font: {
                        size: 12,
                        weight: '500'
                    }
                }
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.9)',
                titleColor: 'white',
                bodyColor: 'white',
                cornerRadius: 12,
                padding: 16,
                titleFont: {
                    size: 14,
                    weight: 'bold'
                },
                bodyFont: {
                    size: 13
                }
            }
        }
    };

    static createBarChart(ctx, data, options = {}) {
        // Brand-focused color palette
        const theme = options.theme || 'brand';
        const colorPalettes = {
            default: [
                '#1e40af', '#dc2626', '#059669', '#d97706', '#7c3aed',
                '#be185d', '#0891b2', '#65a30d', '#c2410c', '#7c2d12'
            ],
            corporate: [
                '#074e7e', '#c92427', '#0369a1', '#dc2626', '#0891b2'
            ],
            brand: [
                '#074e7e', '#c92427', '#0ea5e9', '#ef4444', '#06b6d4',
                '#f97316', '#10b981', '#8b5cf6', '#ec4899', '#84cc16'
            ],
            minimal: [
                '#374151', '#6b7280', '#9ca3af', '#d1d5db', '#e5e7eb'
            ]
        };

        const colors = colorPalettes[theme] || colorPalettes.brand;

        // Apply colors to dataset if not already set
        if (data.datasets && data.datasets[0] && !data.datasets[0].backgroundColor) {
            if (options.singleColor) {
                // Use primary brand color for single color charts
                data.datasets[0].backgroundColor = colors[0];
                data.datasets[0].borderColor = colors[0];
            } else {
                data.datasets[0].backgroundColor = colors.slice(0, data.labels?.length || 10);
                data.datasets[0].borderColor = colors.slice(0, data.labels?.length || 10);
            }
            data.datasets[0].borderWidth = 1;
            data.datasets[0].borderRadius = 6;
            data.datasets[0].borderSkipped = false;
        }

        return new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                ...this.defaultOptions,
                ...options,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { 
                            color: 'rgba(7, 78, 126, 0.08)', 
                            drawBorder: false 
                        },
                        ticks: { 
                            font: { size: 11, weight: '500' },
                            color: '#374151'
                        }
                    },
                    x: { 
                        grid: { display: false },
                        ticks: { 
                            font: { size: 11, weight: '500' },
                            color: '#374151',
                            maxRotation: options.indexAxis === 'y' ? 0 : 45
                        }
                    },
                    ...options.scales
                },
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: {
                        display: false,
                        ...this.defaultOptions.plugins.legend
                    },
                    ...options.plugins
                }
            }
        });
    }

    static createStackedBarChart(ctx, data, options = {}) {
        // Professional color palette for stacked charts
        const colors = [
            '#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', 
            '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#f59e0b'
        ];

        // Apply colors to datasets
        if (data.datasets) {
            data.datasets.forEach((dataset, index) => {
                if (!dataset.backgroundColor) {
                    dataset.backgroundColor = colors[index % colors.length];
                    dataset.borderWidth = 0;
                }
            });
        }

        return new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                ...this.defaultOptions,
                ...options,
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12,
                                weight: '500'
                            }
                        }
                    },
                    ...options.plugins
                },
                scales: {
                    x: { 
                        stacked: true,
                        grid: { display: false },
                        ticks: { 
                            font: { size: 11, weight: '500' },
                            color: '#374151',
                            maxRotation: 45
                        }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        grid: { 
                            color: 'rgba(0,0,0,0.05)', 
                            drawBorder: false 
                        },
                        ticks: { 
                            font: { size: 12, weight: '500' },
                            color: '#374151'
                        }
                    },
                    ...options.scales
                }
            }
        });
    }

    static createPieChart(ctx, data, options = {}) {
        // Brand color palette for pie charts
        const theme = options.theme || 'brand';
        const colorPalettes = {
            default: [
                '#1e40af', '#dc2626', '#059669', '#d97706', '#7c3aed',
                '#be185d', '#0891b2', '#65a30d', '#c2410c', '#7c2d12'
            ],
            brand: [
                '#074e7e', '#c92427', '#0ea5e9', '#ef4444', '#06b6d4',
                '#f97316', '#10b981', '#8b5cf6', '#ec4899', '#84cc16'
            ]
        };

        const colors = colorPalettes[theme] || colorPalettes.brand;

        // Apply colors to dataset if not already set
        if (data.datasets && data.datasets[0] && !data.datasets[0].backgroundColor) {
            data.datasets[0].backgroundColor = colors.slice(0, data.labels?.length || 10);
            data.datasets[0].borderColor = '#ffffff';
            data.datasets[0].borderWidth = 3;
        }

        return new Chart(ctx, {
            type: 'pie',
            data: data,
            options: {
                ...this.defaultOptions,
                ...options,
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12,
                                weight: '500'
                            },
                            generateLabels: function(chart) {
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {
                                    return data.labels.map((label, i) => {
                                        const dataset = data.datasets[0];
                                        const value = dataset.data[i];
                                        const total = dataset.data.reduce((a, b) => a + b, 0);
                                        const percentage = ((value / total) * 100).toFixed(1);
                                        
                                        return {
                                            text: `${label} (${percentage}%)`,
                                            fillStyle: dataset.backgroundColor[i],
                                            strokeStyle: dataset.borderColor,
                                            lineWidth: dataset.borderWidth,
                                            hidden: false,
                                            index: i
                                        };
                                    });
                                }
                                return [];
                            }
                        }
                    },
                    ...options.plugins
                }
            }
        });
    }

    static createLineChart(ctx, data, options = {}) {
        // Professional styling for line charts
        const colors = [
            '#1e40af', '#dc2626', '#059669', '#d97706', '#7c3aed'
        ];

        if (data.datasets) {
            data.datasets.forEach((dataset, index) => {
                if (!dataset.borderColor) {
                    dataset.borderColor = colors[index % colors.length];
                    dataset.backgroundColor = colors[index % colors.length] + '20';
                    dataset.borderWidth = 3;
                    dataset.fill = false;
                    dataset.tension = 0.4;
                }
            });
        }

        return new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                ...this.defaultOptions,
                ...options,
                scales: {
                    x: { 
                        grid: { 
                            color: 'rgba(0,0,0,0.05)',
                            drawBorder: false
                        },
                        ticks: { 
                            font: { size: 12, weight: '500' },
                            color: '#374151'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { 
                            color: 'rgba(0,0,0,0.05)', 
                            drawBorder: false 
                        },
                        ticks: { 
                            font: { size: 12, weight: '500' },
                            color: '#374151'
                        }
                    },
                    ...options.scales
                }
            }
        });
    }
}

// Utility Functions
class DashboardUtils {
    // Toast notification system
    static showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        const colors = {
            success: 'bg-emerald-500 border-emerald-600',
            error: 'bg-red-500 border-red-600',
            info: 'bg-blue-500 border-blue-600',
            warning: 'bg-amber-500 border-amber-600'
        };
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle',
            warning: 'fas fa-exclamation-triangle'
        };
        
        toast.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-4 rounded-lg shadow-2xl z-50 transition-all duration-300 transform translate-x-0 border-l-4 max-w-sm`;
        toast.innerHTML = `
            <div class="flex items-center space-x-3">
                <i class="${icons[type]} text-lg"></i>
                <div class="flex-1">
                    <div class="font-semibold">${message}</div>
                </div>
                <button onclick="this.parentElement.parentElement.style.transform = 'translateX(100%)'; setTimeout(() => this.parentElement.parentElement.remove(), 300);" class="text-white/80 hover:text-white">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove
        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.transform = 'translateX(100%)';
                setTimeout(() => toast.remove(), 300);
            }
        }, duration);
    }

    // Loading overlay
    static showLoading(container) {
        const overlay = document.createElement('div');
        overlay.className = 'absolute inset-0 bg-white/90 backdrop-blur-sm flex items-center justify-center z-40';
        overlay.innerHTML = `
            <div class="text-center">
                <div class="animate-spin rounded-full h-12 w-12 border-b-4 border-blue-600 mx-auto mb-4"></div>
                <div class="text-gray-700 font-medium">Loading data...</div>
            </div>
        `;
        container.appendChild(overlay);
        return overlay;
    }

    static hideLoading(overlay) {
        if (overlay && overlay.parentElement) {
            overlay.remove();
        }
    }

    // Format numbers with proper separators
    static formatNumber(num) {
        if (typeof num !== 'number') return num;
        return new Intl.NumberFormat().format(num);
    }

    // Format percentages
    static formatPercentage(num, decimals = 1) {
        if (typeof num !== 'number') return '0%';
        return `${num.toFixed(decimals)}%`;
    }

    // Debounce function for search inputs
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Color generator for charts with corporate minimal palette
    static generateColors(count, theme = 'default') {
        const themes = {
            default: [
                '#1e40af', '#dc2626', '#059669', '#d97706', '#7c3aed',
                '#be185d', '#0891b2', '#65a30d', '#c2410c', '#7c2d12'
            ],
            corporate: [
                '#074e7e', '#c92427', '#0369a1', '#dc2626', '#0891b2',
                '#be185d', '#059669', '#d97706', '#7c3aed', '#65a30d'
            ],
            minimal: [
                '#374151', '#6b7280', '#9ca3af', '#d1d5db', '#e5e7eb'
            ],
            brand: [
                '#074e7e', '#c92427', '#0ea5e9', '#ef4444', '#06b6d4',
                '#f97316', '#10b981', '#8b5cf6', '#ec4899', '#84cc16'
            ]
        };
        
        const baseColors = themes[theme] || themes.default;
        const colors = [];
        for (let i = 0; i < count; i++) {
            colors.push(baseColors[i % baseColors.length]);
        }
        return colors;
    }

    // CSV export helper
    static exportToCSV(data, filename) {
        if (!data || data.length === 0) {
            this.showToast('No data to export', 'warning');
            return;
        }

        const csvContent = this.convertToCSV(data);
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', filename);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }

    static convertToCSV(data) {
        if (!data || data.length === 0) return '';
        
        const headers = Object.keys(data[0]);
        const csvHeaders = headers.join(',');
        
        const csvRows = data.map(row => 
            headers.map(header => {
                const value = row[header];
                // Escape commas and quotes
                if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                    return `"${value.replace(/"/g, '""')}"`;
                }
                return value;
            }).join(',')
        );
        
        return [csvHeaders, ...csvRows].join('\n');
    }
}

// Modal Management
class ModalManager {
    static openModal(title, endpoint, additionalParams = {}) {
        const existingModal = document.getElementById('dataModal');
        if (existingModal) {
            existingModal.remove();
        }

        const modal = this.createModal(title);
        document.body.appendChild(modal);
        
        this.loadModalData(endpoint, additionalParams);
        modal.classList.add('show');
    }

    static createModal(title) {
        const modal = document.createElement('div');
        modal.id = 'dataModal';
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 opacity-0 transition-opacity duration-300';
        modal.innerHTML = `
            <div class="bg-white rounded-2xl shadow-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden transform scale-95 transition-transform duration-300">
                <div class="bg-gradient-to-r from-slate-700 to-slate-800 px-8 py-6 text-white">
                    <div class="flex items-center justify-between">
                        <h3 class="text-xl font-bold">${title}</h3>
                        <button onclick="ModalManager.closeModal()" class="text-white/80 hover:text-white text-2xl">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                <div id="modalContent" class="p-8">
                    <div class="flex items-center justify-center py-12">
                        <div class="animate-spin rounded-full h-12 w-12 border-b-4 border-slate-600"></div>
                        <span class="ml-4 text-gray-600">Loading data...</span>
                    </div>
                </div>
            </div>
        `;
        
        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        });

        return modal;
    }

    static async loadModalData(endpoint, params = {}) {
        try {
            const url = new URL(endpoint, window.location.origin);
            Object.keys(params).forEach(key => {
                if (Array.isArray(params[key])) {
                    params[key].forEach(value => url.searchParams.append(key, value));
                } else {
                    url.searchParams.append(key, params[key]);
                }
            });

            const response = await fetch(url);
            const data = await response.json();

            const modalContent = document.getElementById('modalContent');
            if (!modalContent) return;

            if (data.error) {
                modalContent.innerHTML = `
                    <div class="text-center py-12">
                        <i class="fas fa-exclamation-triangle text-red-500 text-4xl mb-4"></i>
                        <p class="text-red-600 font-medium">Error loading data: ${data.error}</p>
                    </div>
                `;
                return;
            }

            if (!data.data || data.data.length === 0) {
                modalContent.innerHTML = `
                    <div class="text-center py-12">
                        <i class="fas fa-database text-gray-400 text-4xl mb-4"></i>
                        <p class="text-gray-600 font-medium">No data available</p>
                    </div>
                `;
                return;
            }

            // Create table
            const headers = Object.keys(data.data[0]);
            const tableHTML = `
                <div class="overflow-x-auto">
                    <div class="mb-4 flex items-center justify-between">
                        <div class="text-sm text-gray-600">
                            Showing ${data.data.length} records
                        </div>
                        <button onclick="DashboardUtils.exportToCSV(${JSON.stringify(data.data).replace(/"/g, '&quot;')}, 'modal_data.csv')" 
                                class="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors">
                            <i class="fas fa-download mr-2"></i>Export CSV
                        </button>
                    </div>
                    <table class="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg overflow-hidden">
                        <thead class="bg-gray-50">
                            <tr>
                                ${headers.map(header => `
                                    <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                                        ${header}
                                    </th>
                                `).join('')}
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            ${data.data.map((row, index) => `
                                <tr class="${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-blue-50 transition-colors">
                                    ${headers.map(header => `
                                        <td class="px-6 py-4 text-sm text-gray-900 border-b border-gray-100">
                                            ${this.formatCellValue(row[header])}
                                        </td>
                                    `).join('')}
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;

            modalContent.innerHTML = tableHTML;

        } catch (error) {
            console.error('Error loading modal data:', error);
            const modalContent = document.getElementById('modalContent');
            if (modalContent) {
                modalContent.innerHTML = `
                    <div class="text-center py-12">
                        <i class="fas fa-exclamation-triangle text-red-500 text-4xl mb-4"></i>
                        <p class="text-red-600 font-medium">Error loading data: ${error.message}</p>
                    </div>
                `;
            }
        }
    }

    static formatCellValue(value) {
        if (value === null || value === undefined) return '-';
        if (typeof value === 'string' && value.length > 100) {
            return value.substring(0, 100) + '...';
        }
        return String(value);
    }

    static closeModal() {
        const modal = document.getElementById('dataModal');
        if (modal) {
            modal.classList.remove('show');
            modal.style.opacity = '0';
            setTimeout(() => {
                if (modal.parentElement) {
                    modal.remove();
                }
            }, 300);
        }
    }
}

// Global utility functions for backward compatibility
function showToast(message, type = 'info') {
    DashboardUtils.showToast(message, type);
}

function openModal(title, endpoint, params = {}) {
    ModalManager.openModal(title, endpoint, params);
}

function closeModal() {
    ModalManager.closeModal();
}

// Enhanced Dashboard Base Class
class Dashboard {
    constructor(apiBase = '/api') {
        this.charts = {};
        this.filters = {};
        this.apiBase = apiBase;
        this.loadingOverlays = {};
    }

    // Initialize dashboard
    init() {
        this.setupEventListeners();
        this.loadData();
    }

    // Setup common event listeners
    setupEventListeners() {
        // Filter controls
        const filterBtn = document.getElementById('filterBtn');
        if (filterBtn) {
            filterBtn.addEventListener('click', () => {
                document.getElementById('filterDropdown')?.classList.toggle('show');
            });
        }

        // Close filter dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#filterBtn') && !e.target.closest('#filterDropdown')) {
                const dropdown = document.getElementById('filterDropdown');
                if (dropdown) dropdown.classList.remove('show');
            }
        });

        // Refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }

        // Export buttons
        document.querySelectorAll('[data-export]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const format = e.target.closest('[data-export]').dataset.export;
                this.exportData(format);
            });
        });

        // Apply filters button
        const applyFiltersBtn = document.getElementById('applyFilters');
        if (applyFiltersBtn) {
            applyFiltersBtn.addEventListener('click', () => this.applyFilters());
        }

        // Clear filters button
        const clearFiltersBtn = document.getElementById('clearAllFilters');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => this.clearFilters());
        }
    }

    // Fetch data from API with error handling
    async fetchData(endpoint, params = {}) {
        try {
            const url = new URL(`${this.apiBase}${endpoint}`, window.location.origin);
            Object.keys(params).forEach(key => {
                if (Array.isArray(params[key])) {
                    params[key].forEach(value => url.searchParams.append(key, value));
                } else {
                    url.searchParams.append(key, params[key]);
                }
            });

            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Fetch error:', error);
            DashboardUtils.showToast(`Error loading data: ${error.message}`, 'error');
            return null;
        }
    }

    // Apply filters with loading state
    applyFilters() {
        this.updateActiveFiltersDisplay();
        this.loadData();
        DashboardUtils.showToast('Filters applied successfully', 'success');
    }

    // Clear all filters
    clearFilters() {
        this.filters = {};
        document.querySelectorAll('#filterDropdown input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
        });
        this.updateActiveFiltersDisplay();
        this.loadData();
        DashboardUtils.showToast('All filters cleared', 'info');
    }

    // Update active filters display
    updateActiveFiltersDisplay() {
        const container = document.getElementById('activeFilters');
        const filterCount = document.getElementById('filterCount');
        
        if (container) {
            container.innerHTML = '';
            let count = 0;
            
            Object.entries(this.filters).forEach(([key, values]) => {
                if (Array.isArray(values)) {
                    values.forEach(value => {
                        count++;
                        const tag = document.createElement('div');
                        tag.className = 'inline-flex items-center px-3 py-1 rounded-full text-sm bg-slate-600 text-white mr-2 mb-2';
                        tag.innerHTML = `
                            ${value}
                            <button onclick="dashboard.removeFilter('${key}', '${value}')" class="ml-2 p-1 rounded-full hover:bg-white/20">
                                <i class="fas fa-times text-xs"></i>
                            </button>
                        `;
                        container.appendChild(tag);
                    });
                }
            });
            
            if (filterCount) {
                if (count > 0) {
                    filterCount.textContent = count;
                    filterCount.classList.remove('hidden');
                } else {
                    filterCount.classList.add('hidden');
                }
            }
        }
    }

    // Remove specific filter
    removeFilter(key, value) {
        if (Array.isArray(this.filters[key])) {
            this.filters[key] = this.filters[key].filter(v => v !== value);
            if (this.filters[key].length === 0) {
                delete this.filters[key];
            }
        } else {
            delete this.filters[key];
        }
        
        // Update checkbox state
        const checkbox = document.querySelector(`input[value="${value}"]`);
        if (checkbox) checkbox.checked = false;
        
        this.updateActiveFiltersDisplay();
        this.loadData();
    }

    // Refresh data with visual feedback
    async refreshData() {
        const btn = document.getElementById('refreshBtn');
        if (btn) {
            const originalContent = btn.innerHTML;
            btn.innerHTML = `
                <i class="fas fa-spinner fa-spin"></i>
                <span class="text-sm font-semibold">Refreshing...</span>
            `;
            btn.disabled = true;
            
            await this.loadData();
            
            setTimeout(() => {
                btn.innerHTML = originalContent;
                btn.disabled = false;
                DashboardUtils.showToast('Data refreshed successfully', 'success');
            }, 1000);
        }
    }

    // Export data with loading state
    async exportData(format = 'csv') {
        const params = this.buildFilterParams();
        const url = `${this.apiBase}/export?format=${format}&${params}`;
        
        try {
            // Open in new tab for download
            window.open(url, '_blank');
            DashboardUtils.showToast(`Exporting data as ${format.toUpperCase()}...`, 'info');
        } catch (error) {
            console.error('Export error:', error);
            DashboardUtils.showToast('Export failed', 'error');
        }
    }

    // Build filter parameters string
    buildFilterParams() {
        const params = new URLSearchParams();
        Object.entries(this.filters).forEach(([key, values]) => {
            if (Array.isArray(values) && values.length > 0) {
                values.forEach(value => params.append(key, value));
            }
        });
        return params.toString();
    }

    // Show table modal
    showTableModal(title, endpoint) {
        const params = this.buildFilterParams();
        const fullEndpoint = `${this.apiBase}${endpoint}`;
        ModalManager.openModal(title, fullEndpoint, this.filters);
    }

    // Override in child classes
    async loadData() {
        console.log('Override loadData method in child class');
    }
}

// CSS for modals and components (inject into head)
const componentStyles = `
<style>
    .modal {
        display: flex !important;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.3s ease;
    }
    
    .modal.show {
        opacity: 1;
        pointer-events: auto;
    }
    
    .modal.show > div {
        transform: scale(1);
    }
    
    .modal > div {
        transform: scale(0.95);
        transition: transform 0.3s ease;
    }
    
    /* Custom scrollbar for tables */
    .table-container {
        scrollbar-width: thin;
        scrollbar-color: #cbd5e1 #f1f5f9;
    }
    
    .table-container::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    .table-container::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    .table-container::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    .table-container::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* Loading animation */
    .loading-pulse {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
</style>
`;

// Inject styles into head
if (!document.getElementById('component-styles')) {
    const styleElement = document.createElement('div');
    styleElement.id = 'component-styles';
    styleElement.innerHTML = componentStyles;
    document.head.appendChild(styleElement);
}

// Global dashboard instance placeholder
let dashboard;