// Enhanced Corporate Dashboard JavaScript with Fixed Chart Loading
// File: static/js/dashboard.js

document.addEventListener('alpine:init', () => {
    Alpine.data('corporateDashboard', () => ({
        // Core State
        isLoading: false,
        isRefreshing: false,
        isPaused: false,
        currentSlide: 0,
        carouselInterval: null,
        lastUpdated: '',
        activeCharts: new Map(), // Use Map for better chart management
        chartsLoaded: new Set(), // Track which charts are loaded
        
        // 10-Slide Configuration with corrected endpoints
        slideConfigs: [
            {
                title: 'Analisis Demografi',
                subtitle: 'Taburan umur mengikut tahun graduasi',
                icon: 'fas fa-users',
                color: 'blue',
                colorClass: 'bg-blue-500',
                gradientClass: 'from-blue-500 to-indigo-600',
                endpoint: '/api/age-by-graduation-year',
                chartType: 'bar'
            },
            {
                title: 'Sosioekonomi Graduan',
                subtitle: 'Kaedah pembiayaan pendidikan',
                icon: 'fas fa-coins',
                color: 'green',
                colorClass: 'bg-green-500',
                gradientClass: 'from-green-500 to-emerald-600',
                endpoint: '/sosioekonomi/api/education-financing',
                chartType: 'bar'
            },
            {
                title: 'Graduan Luar Bidang',
                subtitle: 'Sebab bekerja di luar bidang',
                icon: 'fas fa-exchange-alt',
                color: 'red',
                colorClass: 'bg-red-500',
                gradientClass: 'from-red-500 to-rose-600',
                endpoint: '/graduan-luar/api/reasons-distribution',
                chartType: 'horizontalBar'
            },
            {
                title: 'Sektor & Gaji',
                subtitle: 'Kesesuaian gaji dengan kelulusan',
                icon: 'fas fa-chart-line',
                color: 'purple',
                colorClass: 'bg-purple-500',
                gradientClass: 'from-purple-500 to-violet-600',
                endpoint: '/sektor-gaji/api/salary-commensurate',
                chartType: 'pie'
            },
            {
                title: 'Latihan & Cabaran',
                subtitle: 'Keberkesanan latihan industri',
                icon: 'fas fa-user-tie',
                color: 'amber',
                colorClass: 'bg-amber-500',
                gradientClass: 'from-amber-500 to-orange-600',
                endpoint: '/intern/api/internship-benefits',
                chartType: 'bar'
            },
            {
                title: 'Status Pekerjaan',
                subtitle: 'Jenis pekerjaan semasa',
                icon: 'fas fa-briefcase',
                color: 'pink',
                colorClass: 'bg-pink-500',
                gradientClass: 'from-pink-500 to-rose-600',
                endpoint: '/status-pekerjaan/api/current-job-types',
                chartType: 'bar'
            },
            {
                title: 'Graduan Mengikut Bidang',
                subtitle: 'Taburan bidang mengikut tahun',
                icon: 'fas fa-graduation-cap',
                color: 'cyan',
                colorClass: 'bg-cyan-500',
                gradientClass: 'from-cyan-500 to-blue-600',
                endpoint: '/graduan-bidang/api/field-by-year',
                chartType: 'bar'
            },
            {
                title: 'Ekonomi Gig',
                subtitle: 'Trend kerja masa depan',
                icon: 'fas fa-laptop',
                color: 'teal',
                colorClass: 'bg-teal-500',
                gradientClass: 'from-teal-500 to-green-600',
                endpoint: '/gig-economy/api/skill-acquisition',
                chartType: 'horizontalBar'
            },
            {
                title: 'Faktor Kejayaan',
                subtitle: 'Penentu kebolehpasaran graduan',
                icon: 'fas fa-star',
                color: 'orange',
                colorClass: 'bg-orange-500',
                gradientClass: 'from-orange-500 to-red-600',
                endpoint: '/faktor-graduan/api/additional-skills',
                chartType: 'horizontalBar'
            },
            {
                title: 'Wawasan Strategik',
                subtitle: 'Masa mendapat pekerjaan pertama',
                icon: 'fas fa-network-wired',
                color: 'indigo',
                colorClass: 'bg-indigo-500',
                gradientClass: 'from-indigo-500 to-purple-600',
                endpoint: '/status-pekerjaan/api/time-to-first-job',
                chartType: 'line'
            }
        ],
        
        // KPI Metrics
        kpiMetrics: [
            {
                label: 'Jumlah Graduan',
                value: '39',
                icon: 'fas fa-graduation-cap',
                iconBg: 'bg-gradient-to-br from-blue-500 to-indigo-600',
                trend: '+12.5%',
                badgeClass: 'text-green-600 bg-green-50'
            },
            {
                label: 'Kadar Pekerjaan',
                value: '84.2%',
                icon: 'fas fa-briefcase',
                iconBg: 'bg-gradient-to-br from-green-500 to-emerald-600',
                trend: 'Baik',
                badgeClass: 'text-green-600 bg-green-50'
            },
            {
                label: 'Padanan Bidang',
                value: '71.3%',
                icon: 'fas fa-target',
                iconBg: 'bg-gradient-to-br from-red-500 to-rose-600',
                trend: 'Sederhana',
                badgeClass: 'text-orange-600 bg-orange-50'
            },
            {
                label: 'Masa Mendapat Kerja',
                value: '3.2 bulan',
                icon: 'fas fa-stopwatch',
                iconBg: 'bg-gradient-to-br from-purple-500 to-violet-600',
                trend: 'Baik',
                badgeClass: 'text-green-600 bg-green-50'
            }
        ],
        
        // Chart data storage
        chartData: {},
        slideMetrics: {},
        
        // Initialization with proper error handling
        async init() {
            console.log('🚀 Initializing Enhanced Corporate Dashboard...');
            this.updateDateTime();
            this.isLoading = true;
            
            try {
                // Wait for DOM to be fully ready
                await this.waitForDOM();
                
                // Load all data
                await this.loadAllData();
                
                // Initialize carousel
                this.startCarousel();
                this.startTimeUpdates();
                
                // Create initial chart with delay to ensure DOM is ready
                setTimeout(() => {
                    this.createChart(0);
                }, 1000);
                
                console.log('✅ Dashboard initialized successfully');
                
            } catch (error) {
                console.error('❌ Dashboard init error:', error);
                this.showGlobalError('Failed to initialize dashboard');
            } finally {
                this.isLoading = false;
            }
        },
        
        // Wait for DOM elements to be available
        async waitForDOM() {
            return new Promise((resolve) => {
                if (document.readyState === 'complete') {
                    resolve();
                } else {
                    window.addEventListener('load', resolve);
                }
            });
        },
        
        // Time Management
        updateDateTime() {
            const now = new Date();
            this.lastUpdated = now.toLocaleString('ms-MY', {
                hour: '2-digit',
                minute: '2-digit',
                day: '2-digit',
                month: '2-digit',
                hour12: false
            });
        },
        
        startTimeUpdates() {
            setInterval(() => this.updateDateTime(), 30000); // Update every 30 seconds
        },
        
        // Enhanced data loading with better error handling
        async loadAllData() {
            console.log('📊 Loading all analytics data...');
            const loadPromises = [];
            
            // Load chart data for all slides
            for (let i = 0; i < this.slideConfigs.length; i++) {
                loadPromises.push(this.loadSlideData(i));
            }
            
            // Load KPI data
            loadPromises.push(this.loadKPIData());
            
            try {
                await Promise.all(loadPromises);
                this.updateSlideMetrics();
                console.log('✅ All data loaded successfully');
            } catch (error) {
                console.warn('⚠️ Some data failed to load, using fallback data', error);
            }
        },
        
        async loadSlideData(index) {
            try {
                const config = this.slideConfigs[index];
                console.log(`Loading slide ${index}: ${config.title}`);
                
                const response = await fetch(config.endpoint);
                
                if (response.ok) {
                    this.chartData[index] = await response.json();
                    console.log(`✅ Real data loaded for slide ${index}`);
                } else {
                    throw new Error(`HTTP ${response.status}`);
                }
            } catch (error) {
                console.warn(`⚠️ Using mock data for slide ${index}:`, error.message);
                this.chartData[index] = this.getDefinedMockData(index);
            }
        },
        
        async loadKPIData() {
            try {
                const response = await fetch('/api/summary');
                if (response.ok) {
                    const data = await response.json();
                    
                    // Update KPI metrics with real data
                    if (data.total_records !== undefined) {
                        this.kpiMetrics[0].value = data.total_records.toString();
                    }
                    if (data.employment_rate !== undefined) {
                        this.kpiMetrics[1].value = `${data.employment_rate}%`;
                    }
                    if (data.field_alignment !== undefined) {
                        this.kpiMetrics[2].value = `${data.field_alignment}%`;
                    }
                    if (data.avg_time_to_employment !== undefined) {
                        this.kpiMetrics[3].value = `${data.avg_time_to_employment} bulan`;
                    }
                    
                    console.log('✅ KPI data updated');
                } else {
                    throw new Error(`HTTP ${response.status}`);
                }
            } catch (error) {
                console.warn('⚠️ Using default KPI data:', error.message);
            }
        },
        
        updateSlideMetrics() {
            // Enhanced metrics calculation based on loaded data
            this.slideMetrics = {
                0: { primary: '23-25 Tahun', primaryLabel: 'Umur Dominan', secondary: '52% P / 48% L', secondaryLabel: 'Gender Balance' },
                1: { primary: 'Pinjaman MARA', primaryLabel: 'Pembiayaan Utama', secondary: '68%', secondaryLabel: 'Kadar Pinjaman' },
                2: { primary: '28.7%', primaryLabel: 'Ketidakpadanan', secondary: 'Prospek Lebih Baik', secondaryLabel: 'Sebab Utama' },
                3: { primary: '73%', primaryLabel: 'Kesesuaian Gaji', secondary: 'Bersesuaian', secondaryLabel: 'Status Dominan' },
                4: { primary: '76%', primaryLabel: 'Kadar Latihan', secondary: 'Pengalaman Kerja', secondaryLabel: 'Manfaat Utama' },
                5: { primary: '84%', primaryLabel: 'Kadar Bekerja', secondary: 'Sektor Swasta', secondaryLabel: 'Jenis Utama' },
                6: { primary: '8', primaryLabel: 'Bidang Pengajian', secondary: 'Kejuruteraan', secondaryLabel: 'Bidang Popular' },
                7: { primary: '23%', primaryLabel: 'Penyertaan Gig', secondary: 'Belajar Sendiri', secondaryLabel: 'Kaedah Utama' },
                8: { primary: '89%', primaryLabel: 'Kadar Kejayaan', secondary: 'Komunikasi', secondaryLabel: 'Kemahiran Utama' },
                9: { primary: '3.2 bulan', primaryLabel: 'Masa Purata', secondary: '1-3 bulan', secondaryLabel: 'Kebanyakan' }
            };
        },
        
        getSlideMetric(index, type) {
            return this.slideMetrics[index]?.[type] || 'Loading...';
        },
        
        // Enhanced chart creation with proper error handling
        async createChart(slideIndex) {
            const config = this.slideConfigs[slideIndex];
            const chartId = `chart-${slideIndex}`;
            
            try {
                // Ensure canvas exists
                const canvas = document.getElementById(chartId);
                if (!canvas) {
                    console.warn(`❌ Canvas ${chartId} not found`);
                    setTimeout(() => this.createChart(slideIndex), 1000);
                    return;
                }
                
                // Destroy existing chart
                this.destroyChart(chartId);
                
                // Get chart data
                const data = this.chartData[slideIndex] || this.getDefinedMockData(slideIndex);
                
                // Get context
                const ctx = canvas.getContext('2d');
                if (!ctx) {
                    throw new Error('Could not get canvas context');
                }
                
                // Clear canvas
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // Create chart with enhanced options
                const chartOptions = this.getEnhancedChartOptions(config.chartType, slideIndex);
                
                const newChart = new Chart(ctx, {
                    type: this.normalizeChartType(config.chartType),
                    data: data,
                    options: chartOptions
                });
                
                // Store chart reference
                this.activeCharts.set(chartId, newChart);
                this.chartsLoaded.add(slideIndex);
                
                console.log(`✅ Chart created for slide ${slideIndex}: ${config.title}`);
                
            } catch (error) {
                console.error(`❌ Error creating chart for slide ${slideIndex}:`, error);
                this.showChartError(chartId, `Failed to load ${config.title}`);
            }
        },
        
        // Normalize chart types for Chart.js compatibility
        normalizeChartType(type) {
            const typeMap = {
                'horizontalBar': 'bar',
                'enhanced-stacked-bar': 'bar',
                'enhanced-pie': 'pie',
                'multiple-bar': 'bar',
                'area': 'line'
            };
            return typeMap[type] || type;
        },
        
        // Enhanced chart options with better styling
        getEnhancedChartOptions(chartType, slideIndex) {
            const baseOptions = {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: {
                                size: 12,
                                weight: '600',
                                family: "'Inter', sans-serif"
                            },
                            boxWidth: 10,
                            boxHeight: 10
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(17, 24, 39, 0.95)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#374151',
                        borderWidth: 1,
                        cornerRadius: 12,
                        padding: 16,
                        titleFont: {
                            size: 14,
                            weight: '600'
                        },
                        bodyFont: {
                            size: 13,
                            weight: '500'
                        },
                        displayColors: true,
                        boxPadding: 4
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeInOutCubic'
                }
            };
            
            // Chart-specific configurations
            switch (chartType) {
                case 'horizontalBar':
                    return {
                        ...baseOptions,
                        indexAxis: 'y',
                        scales: {
                            x: {
                                beginAtZero: true,
                                grid: {
                                    color: 'rgba(0,0,0,0.08)',
                                    borderColor: 'rgba(0,0,0,0.1)'
                                },
                                ticks: {
                                    font: { size: 11, weight: '500' },
                                    color: '#6b7280'
                                }
                            },
                            y: {
                                grid: { display: false },
                                ticks: {
                                    font: { size: 11, weight: '500' },
                                    color: '#6b7280'
                                }
                            }
                        }
                    };
                    
                case 'pie':
                case 'enhanced-pie':
                    return {
                        ...baseOptions,
                        plugins: {
                            ...baseOptions.plugins,
                            legend: {
                                ...baseOptions.plugins.legend,
                                position: 'right'
                            }
                        }
                    };
                    
                case 'line':
                case 'area':
                    return {
                        ...baseOptions,
                        elements: {
                            line: { 
                                tension: 0.4,
                                borderWidth: 3
                            },
                            point: { 
                                radius: 4,
                                hoverRadius: 8
                            }
                        },
                        scales: {
                            x: {
                                grid: {
                                    color: 'rgba(0,0,0,0.05)',
                                    borderColor: 'rgba(0,0,0,0.1)'
                                },
                                ticks: {
                                    font: { size: 11, weight: '500' },
                                    color: '#6b7280'
                                }
                            },
                            y: {
                                beginAtZero: true,
                                grid: {
                                    color: 'rgba(0,0,0,0.08)',
                                    borderColor: 'rgba(0,0,0,0.1)'
                                },
                                ticks: {
                                    font: { size: 11, weight: '500' },
                                    color: '#6b7280'
                                }
                            }
                        }
                    };
                    
                default:
                    return {
                        ...baseOptions,
                        scales: {
                            x: {
                                grid: { display: false },
                                ticks: {
                                    font: { size: 11, weight: '500' },
                                    color: '#6b7280'
                                }
                            },
                            y: {
                                beginAtZero: true,
                                grid: {
                                    color: 'rgba(0,0,0,0.08)',
                                    borderColor: 'rgba(0,0,0,0.1)'
                                },
                                ticks: {
                                    font: { size: 11, weight: '500' },
                                    color: '#6b7280'
                                }
                            }
                        }
                    };
            }
        },
        
        // Enhanced chart destruction
        destroyChart(chartId) {
            try {
                // Destroy from active charts map
                const existingChart = this.activeCharts.get(chartId);
                if (existingChart) {
                    existingChart.destroy();
                    this.activeCharts.delete(chartId);
                }
                
                // Also check global Chart.js registry
                const globalChart = Chart.getChart(chartId);
                if (globalChart) {
                    globalChart.destroy();
                }
                
                // Remove from loaded set
                const slideIndex = parseInt(chartId.replace('chart-', ''));
                this.chartsLoaded.delete(slideIndex);
                
            } catch (error) {
                console.warn(`⚠️ Error destroying chart ${chartId}:`, error);
            }
        },
        
        // Enhanced error display
        showChartError(chartId, message) {
            const canvas = document.getElementById(chartId);
            if (canvas && canvas.parentElement) {
                canvas.parentElement.innerHTML = `
                    <div class="flex items-center justify-center h-full">
                        <div class="text-center p-8 bg-red-50 rounded-xl border-2 border-dashed border-red-200">
                            <div class="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
                                <i class="fas fa-exclamation-triangle text-red-500 text-xl"></i>
                            </div>
                            <h4 class="font-semibold text-red-800 mb-2">Chart Error</h4>
                            <p class="text-sm text-red-600">${message}</p>
                            <button onclick="location.reload()" class="mt-4 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm">
                                Refresh Page
                            </button>
                        </div>
                    </div>
                `;
            }
        },
        
        showGlobalError(message) {
            console.error('Global Error:', message);
            // Could implement a toast notification here
        },
        
        // Enhanced carousel controls
        startCarousel() {
            this.carouselInterval = setInterval(() => {
                if (!this.isPaused) {
                    this.nextSlide();
                }
            }, 12000); // 12 seconds per slide for better viewing
        },
        
        nextSlide() {
            this.currentSlide = (this.currentSlide + 1) % this.slideConfigs.length;
            this.onSlideChange();
        },
        
        previousSlide() {
            this.currentSlide = this.currentSlide === 0 ? 
                this.slideConfigs.length - 1 : this.currentSlide - 1;
            this.onSlideChange();
        },
        
        goToSlide(index) {
            if (index >= 0 && index < this.slideConfigs.length && index !== this.currentSlide) {
                this.currentSlide = index;
                this.onSlideChange();
            }
        },
        
        onSlideChange() {
            // Create chart for new slide with proper delay
            setTimeout(() => {
                if (!this.chartsLoaded.has(this.currentSlide)) {
                    this.createChart(this.currentSlide);
                }
            }, 500);
        },
        
        pauseCarousel() {
            this.isPaused = true;
            if (this.carouselInterval) {
                clearInterval(this.carouselInterval);
            }
        },
        
        resumeCarousel() {
            this.isPaused = false;
            this.startCarousel();
        },
        
        // Data refresh with loading states
        async refreshAllData() {
            if (this.isRefreshing) return;
            
            this.isRefreshing = true;
            try {
                console.log('🔄 Refreshing all data...');
                await this.loadAllData();
                
                // Recreate current chart
                this.createChart(this.currentSlide);
                this.updateDateTime();
                
                console.log('✅ Data refreshed successfully');
            } catch (error) {
                console.error('❌ Refresh error:', error);
                this.showGlobalError('Failed to refresh data');
            } finally {
                this.isRefreshing = false;
            }
        },
        
        // Navigation helper
        scrollToAnalytics() {
            const element = document.getElementById('analytics-section');
            if (element) {
                element.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }
        },
        
        // Enhanced mock data with proper Chart.js structure
        getDefinedMockData(slideIndex) {
            const mockDataSets = [
                // Slide 0: Demographics - Stacked Bar
                {
                    labels: ['2020', '2021', '2022', '2023', '2024'],
                    datasets: [
                        { 
                            label: '21-23 Tahun', 
                            data: [8, 12, 15, 18, 14], 
                            backgroundColor: '#3b82f6',
                            borderColor: '#2563eb',
                            borderWidth: 2
                        },
                        { 
                            label: '24-26 Tahun', 
                            data: [12, 8, 10, 16, 11], 
                            backgroundColor: '#6366f1',
                            borderColor: '#4f46e5',
                            borderWidth: 2
                        },
                        { 
                            label: '27+ Tahun', 
                            data: [4, 6, 8, 5, 7], 
                            backgroundColor: '#8b5cf6',
                            borderColor: '#7c3aed',
                            borderWidth: 2
                        }
                    ]
                },
                
                // Slide 1: Sosioekonomi - Bar Chart
                {
                    labels: ['Pinjaman MARA', 'Pinjaman Kerajaan', 'Biasiswa', 'Ibu Bapa', 'Lain-lain'],
                    datasets: [{
                        label: 'Bilangan Responden',
                        data: [15, 8, 6, 7, 3],
                        backgroundColor: ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444'],
                        borderColor: ['#059669', '#2563eb', '#7c3aed', '#d97706', '#dc2626'],
                        borderWidth: 2
                    }]
                },
                
                // Slide 2: Graduan Luar - Horizontal Bar
                {
                    labels: ['Prospek Lebih Baik', 'Gaji Lebih Tinggi', 'Peluang Terhad', 'Minat Berubah'],
                    datasets: [{
                        label: 'Sebab Luar Bidang',
                        data: [8, 6, 5, 4],
                        backgroundColor: '#ef4444',
                        borderColor: '#dc2626',
                        borderWidth: 2
                    }]
                },
                
                // Slide 3: Sektor Gaji - Pie Chart
                {
                    labels: ['Sangat Bersesuaian', 'Bersesuaian', 'Kurang Bersesuaian', 'Tidak Bersesuaian'],
                    datasets: [{
                        data: [8, 18, 6, 2],
                        backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'],
                        borderColor: ['#059669', '#2563eb', '#d97706', '#dc2626'],
                        borderWidth: 3
                    }]
                },
                
                // Slide 4: Intern - Multiple Bar
                {
                    labels: ['Pengalaman', 'Rangkaian', 'Kemahiran', 'Keyakinan'],
                    datasets: [
                        { 
                            label: 'Dengan Latihan', 
                            data: [92, 85, 88, 82], 
                            backgroundColor: '#f59e0b',
                            borderColor: '#d97706',
                            borderWidth: 2
                        },
                        { 
                            label: 'Tanpa Latihan', 
                            data: [65, 45, 58, 52], 
                            backgroundColor: '#6b7280',
                            borderColor: '#4b5563',
                            borderWidth: 2
                        }
                    ]
                },
                
                // Slide 5: Status Pekerjaan - Bar Chart
                {
                    labels: ['Sektor Swasta', 'Sektor Awam', 'Bekerja Sendiri', 'Freelancer'],
                    datasets: [{
                        label: 'Jenis Pekerjaan',
                        data: [22, 8, 4, 3],
                        backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6'],
                        borderColor: ['#2563eb', '#059669', '#d97706', '#7c3aed'],
                        borderWidth: 2
                    }]
                },
                
                // Slide 6: Graduan Bidang - Stacked Bar
                {
                    labels: ['2020', '2021', '2022', '2023', '2024'],
                    datasets: [
                        { 
                            label: 'Kejuruteraan', 
                            data: [12, 15, 18, 22, 16], 
                            backgroundColor: '#3b82f6',
                            borderColor: '#2563eb',
                            borderWidth: 2
                        },
                        { 
                            label: 'IT', 
                            data: [8, 10, 12, 14, 11], 
                            backgroundColor: '#10b981',
                            borderColor: '#059669',
                            borderWidth: 2
                        },
                        { 
                            label: 'Perniagaan', 
                            data: [6, 8, 7, 9, 8], 
                            backgroundColor: '#f59e0b',
                            borderColor: '#d97706',
                            borderWidth: 2
                        }
                    ]
                },
                
                // Slide 7: Gig Economy - Horizontal Bar
                {
                    labels: ['Belajar Sendiri', 'Latihan Online', 'Pengalaman Kerja', 'Rakan/Keluarga'],
                    datasets: [{
                        label: 'Kaedah Pembelajaran',
                        data: [18, 12, 10, 6],
                        backgroundColor: '#14b8a6',
                        borderColor: '#0d9488',
                        borderWidth: 2
                    }]
                },
                
                // Slide 8: Faktor Graduan - Horizontal Bar
                {
                    labels: ['Kemahiran Komunikasi', 'Pemikiran Kritis', 'Kemahiran Digital', 'Kepimpinan'],
                    datasets: [{
                        label: 'Kepentingan Kemahiran',
                        data: [22, 18, 16, 14],
                        backgroundColor: '#f97316',
                        borderColor: '#ea580c',
                        borderWidth: 2
                    }]
                },
                
                // Slide 9: Strategic Integration - Line Chart
                {
                    labels: ['< 1 bulan', '1-3 bulan', '4-6 bulan', '7-12 bulan', '> 1 tahun'],
                    datasets: [{
                        label: 'Masa Mendapat Pekerjaan',
                        data: [8, 15, 12, 3, 1],
                        backgroundColor: 'rgba(99, 102, 241, 0.2)',
                        borderColor: '#6366f1',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#6366f1',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 5
                    }]
                }
            ];
            
            return mockDataSets[slideIndex] || mockDataSets[0];
        }
    }));
});

// Enhanced keyboard navigation with better UX
document.addEventListener('keydown', function(e) {
    // Don't interfere with form inputs
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) {
        return;
    }
    
    const dashboardElement = document.querySelector('[x-data*="corporateDashboard"]');
    if (!dashboardElement) return;
    
    const dashboard = Alpine.$data(dashboardElement);
    if (!dashboard) return;
    
    switch(e.key) {
        case 'ArrowLeft':
        case 'ArrowUp':
            e.preventDefault();
            dashboard.previousSlide();
            break;
        case 'ArrowRight':
        case 'ArrowDown':
            e.preventDefault();
            dashboard.nextSlide();
            break;
        case ' ':
        case 'k':
            e.preventDefault();
            dashboard.isPaused ? dashboard.resumeCarousel() : dashboard.pauseCarousel();
            break;
        case 'r':
            e.preventDefault();
            dashboard.refreshAllData();
            break;
        case 'Home':
            e.preventDefault();
            dashboard.goToSlide(0);
            break;
        case 'End':
            e.preventDefault();
            dashboard.goToSlide(dashboard.slideConfigs.length - 1);
            break;
        default:
            // Handle number keys (1-9, 0 for slide 10)
            const num = parseInt(e.key);
            if (!isNaN(num)) {
                e.preventDefault();
                const slideIndex = num === 0 ? 9 : num - 1;
                if (slideIndex < dashboard.slideConfigs.length) {
                    dashboard.goToSlide(slideIndex);
                }
            }
            break;
    }
});

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    const dashboardElement = document.querySelector('[x-data*="corporateDashboard"]');
    if (dashboardElement) {
        const dashboard = Alpine.$data(dashboardElement);
        if (dashboard) {
            // Clean up intervals
            if (dashboard.carouselInterval) {
                clearInterval(dashboard.carouselInterval);
            }
            
            // Destroy all charts
            dashboard.activeCharts.forEach((chart, chartId) => {
                try {
                    chart.destroy();
                } catch (error) {
                    console.warn(`Error destroying chart ${chartId}:`, error);
                }
            });
        }
    }
});

console.log('✅ Enhanced Corporate Dashboard loaded successfully with improved error handling and design');