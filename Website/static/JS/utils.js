// static/js/utils.js

// Utility functions
class Utils {
    // Format numbers with proper locale
    static formatNumber(num, locale = 'ms-MY') {
        return new Intl.NumberFormat(locale).format(num);
    }

    // Format currency
    static formatCurrency(amount, currency = 'MYR', locale = 'ms-MY') {
        return new Intl.NumberFormat(locale, {
            style: 'currency',
            currency: currency
        }).format(amount);
    }

    // Debounce function
    static debounce(func, wait, immediate) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    }

    // Download data as CSV
    static downloadCSV(data, filename) {
        const csv = this.convertToCSV(data);
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
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

    // Convert array of objects to CSV
    static convertToCSV(objArray) {
        const array = typeof objArray !== 'object' ? JSON.parse(objArray) : objArray;
        let str = '';
        
        // Header
        const headers = Object.keys(array[0]);
        str += headers.join(',') + '\r\n';
        
        // Data
        for (let i = 0; i < array.length; i++) {
            let line = '';
            for (let index in array[i]) {
                if (line !== '') line += ',';
                line += array[i][index];
            }
            str += line + '\r\n';
        }
        return str;
    }

    // Generate random colors
    static generateColors(count) {
        const colors = [
            '#074e7e', '#c92427', '#16a34a', '#f59e0b', '#8b5cf6',
            '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
        ];
        
        const result = [];
        for (let i = 0; i < count; i++) {
            result.push(colors[i % colors.length]);
        }
        return result;
    }

    // Animate counter
    static animateCounter(element, target, duration = 2000, suffix = '') {
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current * 10) / 10 + suffix;
        }, 16);
    }
}

// Export manager
class ExportManager {
    static async exportChartAsImage(chartId, filename) {
        const canvas = document.getElementById(chartId);
        if (canvas) {
            const url = canvas.toDataURL('image/png');
            const link = document.createElement('a');
            link.download = filename + '.png';
            link.href = url;
            link.click();
        }
    }

    static async exportDashboardAsPDF() {
        // This would require a library like jsPDF
        // Implementation depends on specific requirements
        console.log('PDF export functionality to be implemented');
    }

    static async exportAllData(dashboard) {
        const allData = {};
        
        // Collect all chart data
        Object.keys(dashboard.charts).forEach(chartName => {
            const chart = dashboard.charts[chartName];
            allData[chartName] = {
                labels: chart.data.labels,
                datasets: chart.data.datasets
            };
        });

        // Download as JSON
        const dataStr = JSON.stringify(allData, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'dashboard_data.json';
        link.click();
        URL.revokeObjectURL(url);
    }
}

// Performance monitor
class PerformanceMonitor {
    static startTimer(name) {
        performance.mark(`${name}-start`);
    }

    static endTimer(name) {
        performance.mark(`${name}-end`);
        performance.measure(name, `${name}-start`, `${name}-end`);
        
        const measure = performance.getEntriesByName(name)[0];
        console.log(`${name} took ${measure.duration.toFixed(2)}ms`);
        
        // Clean up
        performance.clearMarks(`${name}-start`);
        performance.clearMarks(`${name}-end`);
        performance.clearMeasures(name);
    }
}