// COMPLETE Modal Manager - Fixed version with chart integration and filter support
(function() {
    'use strict';
    
    // Prevent multiple initializations
    if (window.modalManagerLoaded) {
        return;
    }
    
    class ModalManager {
        constructor() {
            this.currentModal = null;
            this.isLoading = false;
            this.currentEndpoint = null;
            this.currentTitle = null;
            this.currentChartType = null;
            this.initialized = false;
        }

        init() {
            if (this.initialized) return;
            
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.createModal());
            } else {
                this.createModal();
            }
        }

        createModal() {
            if (document.getElementById('dataModal')) return;
            if (!document.body) {
                setTimeout(() => this.createModal(), 100);
                return;
            }

            const modalHTML = `
                <div id="dataModal" class="fixed inset-0 z-50 hidden">
                    <div class="fixed inset-0 bg-black bg-opacity-50" onclick="window.modalManagerInstance.closeModal()"></div>
                    <div class="fixed inset-0 flex items-center justify-center p-4">
                        <div class="bg-white rounded-2xl shadow-2xl max-w-6xl w-full max-h-[90vh] flex flex-col">
                            <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                                <div>
                                    <h2 id="modalTitle" class="text-xl font-bold text-gray-800">Data Table</h2>
                                    <p id="modalSubtitle" class="text-sm text-gray-600 mt-1 hidden"></p>
                                </div>
                                <button onclick="window.modalManagerInstance.closeModal()" class="text-gray-400 hover:text-gray-600 p-2 rounded-lg hover:bg-gray-100">
                                    <i class="fas fa-times text-lg"></i>
                                </button>
                            </div>
                            <div class="flex-1 overflow-hidden flex flex-col">
                                <div id="modalLoading" class="flex-1 flex items-center justify-center hidden">
                                    <div class="text-center">
                                        <div class="animate-spin rounded-full h-12 w-12 border-b-4 border-blue-600 mx-auto mb-4"></div>
                                        <div class="text-gray-600 font-medium">Memuatkan data...</div>
                                    </div>
                                </div>
                                <div id="modalContent" class="flex-1 overflow-auto p-6"></div>
                            </div>
                            <div class="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
                                <div id="modalInfo" class="text-sm text-gray-500"></div>
                                <div class="flex space-x-3">
                                    <button onclick="window.modalManagerInstance.exportModalData('csv')" class="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors">
                                        <i class="fas fa-file-csv mr-2"></i>Export CSV
                                    </button>
                                    <button onclick="window.modalManagerInstance.exportModalData('excel')" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                                        <i class="fas fa-file-excel mr-2"></i>Export Excel
                                    </button>
                                    <button onclick="window.modalManagerInstance.closeModal()" class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors">
                                        Tutup
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>`;

            document.body.insertAdjacentHTML('beforeend', modalHTML);
            this.initialized = true;
            console.log('Modal created successfully');
        }

        // Get current dashboard filters
        buildFilterParams() {
            try {
                // Try to get filters from the current dashboard instance
                if (window.currentDashboardInstance && typeof window.currentDashboardInstance.buildFilterParams === 'function') {
                    return window.currentDashboardInstance.buildFilterParams();
                }
                
                // Fallback: try to get from Alpine.js data
                const dashboardElement = document.querySelector('[x-data*="Dashboard"]');
                if (dashboardElement && dashboardElement._x_dataStack) {
                    const data = dashboardElement._x_dataStack[0];
                    if (data && data.buildFilterParams) {
                        return data.buildFilterParams();
                    }
                }
                
                return '';
            } catch (error) {
                console.warn('Could not get filter params:', error);
                return '';
            }
        }

        // Main function for chart table modals
        async openChartTableModal(chartType, title) {
            this.currentChartType = chartType;
            this.currentTitle = title;
            
            const params = this.buildFilterParams();
            const endpoint = `/sosioekonomi/api/chart-table-data/${chartType}?${params}`;
            
            console.log(`Opening chart modal for ${chartType} with params: ${params}`);
            await this.openModal(title, endpoint);
        }

        // Enhanced openModal with chart support
        async openModal(title, endpoint, columns = null) {
            this.currentEndpoint = endpoint;
            this.currentTitle = title;
            
            const modal = document.getElementById('dataModal');
            const modalTitle = document.getElementById('modalTitle');
            const modalSubtitle = document.getElementById('modalSubtitle');
            const modalLoading = document.getElementById('modalLoading');
            const modalContent = document.getElementById('modalContent');
            const modalInfo = document.getElementById('modalInfo');
            
            if (!modal) {
                console.error('Modal element not found');
                return;
            }

            // Set title and subtitle based on chart context
            let displayTitle = title;
            let subtitle = '';
            
            if (this.currentChartType) {
                displayTitle = `${title}`;
                subtitle = this.getChartDescription(this.currentChartType);
                modalSubtitle.textContent = subtitle;
                modalSubtitle.classList.remove('hidden');
            } else {
                modalSubtitle.classList.add('hidden');
            }

            modalTitle.textContent = displayTitle;
            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
            modalLoading.classList.remove('hidden');
            modalContent.innerHTML = '';
            modalInfo.textContent = '';

            try {
                console.log('Loading modal data from:', endpoint);
                const response = await fetch(endpoint);
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`Failed to load data: ${response.status} - ${errorText}`);
                }
                const data = await response.json();
                console.log('Modal data loaded:', data);

                modalLoading.classList.add('hidden');
                
                // Use chart-specific columns if we have a chart type
                let displayColumns = data.columns || [];
                let displayData = data.data || [];
                
                if (this.currentChartType) {
                    displayColumns = this.getChartSpecificColumns(this.currentChartType, data.columns || []);
                    
                    // Filter data to only show relevant columns
                    if (displayColumns.length > 0) {
                        displayData = data.data.map(row => {
                            const filteredRow = {};
                            displayColumns.forEach(col => {
                                if (row.hasOwnProperty(col)) {
                                    filteredRow[col] = row[col];
                                }
                            });
                            return filteredRow;
                        });
                    }
                } else if (columns && columns.length > 0) {
                    displayColumns = data.columns.filter(col => columns.includes(col));
                    displayData = data.data.map(row => {
                        const filteredRow = {};
                        columns.forEach(col => {
                            if (row.hasOwnProperty(col)) {
                                filteredRow[col] = row[col];
                            }
                        });
                        return filteredRow;
                    });
                }

                // Add chart information header if this is a chart modal
                let chartInfoHtml = '';
                if (this.currentChartType) {
                    chartInfoHtml = this.generateChartInfoHeader();
                }

                modalContent.innerHTML = chartInfoHtml + this.generateTableHTML(displayData, displayColumns);
                
                // Update modal info
                const hasFilters = this.buildFilterParams().length > 0;
                const filterText = hasFilters ? ' (ditapis)' : '';
                modalInfo.textContent = `${displayData.length} rekod ditunjukkan${filterText}`;
                
            } catch (error) {
                console.error('Error loading modal data:', error);
                modalLoading.classList.add('hidden');
                modalContent.innerHTML = `
                    <div class="text-center py-12">
                        <i class="fas fa-exclamation-triangle text-red-500 text-4xl mb-4"></i>
                        <h3 class="text-lg font-semibold text-gray-800 mb-2">Error Loading Data</h3>
                        <p class="text-gray-600">${error.message}</p>
                        <div class="mt-4">
                            <button onclick="window.modalManagerInstance.retryLoad()" 
                                class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                                Cuba Semula
                            </button>
                        </div>
                    </div>`;
            }
        }

        // Get chart-specific columns
        getChartSpecificColumns(chartType, allColumns) {
            const chartColumnMappings = {
                'household-income': [
                    'Pendapatan isi rumah bulanan keluarga anda?',
                    'Jantina anda?',
                    'Tahun graduasi anda?',
                    'Institusi pendidikan MARA yang anda hadiri?',
                    'Program pengajian yang anda ikuti?'
                ],
                'education-financing': [
                    'Bagaimana anda membiayai pendidikan anda?',
                    'Jantina anda?',
                    'Tahun graduasi anda?',
                    'Institusi pendidikan MARA yang anda hadiri?',
                    'Program pengajian yang anda ikuti?'
                ],
                'father-occupation': [
                    'Pekerjaan bapa anda',
                    'Pendapatan isi rumah bulanan keluarga anda?',
                    'Jantina anda?',
                    'Tahun graduasi anda?',
                    'Institusi pendidikan MARA yang anda hadiri?'
                ],
                'mother-occupation': [
                    'Pekerjaan ibu anda?',
                    'Pendapatan isi rumah bulanan keluarga anda?',
                    'Jantina anda?',
                    'Tahun graduasi anda?',
                    'Institusi pendidikan MARA yang anda hadiri?'
                ],
                'financing-advantage': [
                    'Bagaimana anda membiayai pendidikan anda?',
                    'Adakah jenis pembiayaan ini memberi kelebihan dalam mencari kerja?',
                    'Jantina anda?',
                    'Tahun graduasi anda?',
                    'Institusi pendidikan MARA yang anda hadiri?'
                ],
                'debt-impact': [
                    'Bagaimana anda membiayai pendidikan anda?',
                    'Jika anda mempunyai pinjaman pendidikan, adakah beban hutang mempengaruhi pilihan kerjaya anda?',
                    'Jantina anda?',
                    'Tahun graduasi anda?',
                    'Institusi pendidikan MARA yang anda hadiri?'
                ]
            };

            const specificColumns = chartColumnMappings[chartType] || this.getFaktorGraduanColumns(allColumns);
            return specificColumns.filter(col => allColumns.includes(col));
        }

        // Get chart description
        getChartDescription(chartType) {
            const descriptions = {
                'household-income': 'Data taburan pendapatan isi rumah mengikut kategori pendapatan bulanan',
                'education-financing': 'Data kaedah pembiayaan pendidikan yang digunakan oleh responden',
                'father-occupation': 'Data hubungan antara pekerjaan bapa dan tahap pendapatan keluarga',
                'mother-occupation': 'Data hubungan antara pekerjaan ibu dan tahap pendapatan keluarga',
                'financing-advantage': 'Data persepsi responden tentang kelebihan kaedah pembiayaan dalam mencari kerja',
                'debt-impact': 'Data kesan beban hutang pendidikan terhadap pilihan kerjaya graduan'
            };
            return descriptions[chartType] || 'Data yang berkaitan dengan graf ini';
        }

        // Generate chart information header
        generateChartInfoHeader() {
            if (!this.currentChartType) return '';

            const description = this.getChartDescription(this.currentChartType);
            const hasFilters = this.buildFilterParams().length > 0;

            return `
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                    <div class="flex items-start space-x-3">
                        <div class="flex-shrink-0">
                            <i class="fas fa-chart-bar text-blue-600 text-lg mt-1"></i>
                        </div>
                        <div class="flex-1">
                            <h4 class="text-sm font-semibold text-blue-900 mb-1">Maklumat Graf</h4>
                            <p class="text-sm text-blue-700 mb-2">${description}</p>
                            <div class="flex items-center space-x-4 text-xs text-blue-600">
                                <span class="inline-flex items-center">
                                    <i class="fas fa-database mr-1"></i>
                                    Jenis: ${this.currentChartType}
                                </span>
                                ${hasFilters ? `
                                    <span class="inline-flex items-center text-green-600">
                                        <i class="fas fa-filter mr-1"></i>
                                        Ditapis mengikut kriteria yang dipilih
                                    </span>
                                ` : `
                                    <span class="inline-flex items-center text-gray-600">
                                        <i class="fas fa-globe mr-1"></i>
                                        Semua data (tiada penapisan)
                                    </span>
                                `}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        getFaktorGraduanColumns(allColumns) {
            // Define priority columns for faktor graduan
            const priorityColumns = [
                'Sejauh mana latihan industri/praktikal mempengaruhi kebolehpasaran anda?',
                'Sejauh mana kemahiran komunikasi  mempengaruhi kebolehpasaran anda?',
                'Sejauh mana kemahiran teknikal mempengaruhi kebolehpasaran anda?',
                'Sejauh mana rangkaian peribadi (networking) mempengaruhi kebolehpasaran anda?',
                'Sejauh mana kelayakan akademik mempengaruhi kebolehpasaran anda?',
                'Adakah anda memiliki sijil profesional tambahan selain ijazah/diploma?',
                'Adakah sijil profesional ini membantu anda dalam mendapatkan pekerjaan?',
                'Adakah majikan anda meminta kelayakan tambahan selain daripada ijazah anda?',
                'Kemahiran tambahan manakah yang paling banyak diminta oleh majikan semasa temu duga? ',
                'Sejauh mana anda bersetuju bahawa universiti telah menyediakan anda untuk pasaran kerja?',
                'Tahun graduasi anda?',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?'
            ];

            // Return columns that exist in both priority list and data columns
            const availableColumns = priorityColumns.filter(col => allColumns.includes(col));
            
            // If no priority columns found, return first 10 columns
            return availableColumns.length > 0 ? availableColumns : allColumns.slice(0, 10);
        }

        generateTableHTML(data, columns) {
            if (!data || data.length === 0) {
                return `<div class="text-center py-12">
                    <i class="fas fa-inbox text-gray-400 text-4xl mb-4"></i>
                    <h3 class="text-lg font-semibold text-gray-800 mb-2">Tiada Data</h3>
                    <p class="text-gray-600">Tiada data tersedia untuk paparan semasa.</p>
                </div>`;
            }

            // Shorten column headers for better display
            const shortenHeader = (header) => {
                if (header.length > 50) {
                    return header.substring(0, 47) + '...';
                }
                return header;
            };

            const tableHeaders = columns.map(col => 
                `<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b sticky top-0 bg-gray-50" title="${col}">
                    ${shortenHeader(col)}
                </th>`
            ).join('');

            const tableRows = data.slice(0, 100).map((row, index) => {
                const cells = columns.map(col => {
                    const value = row[col] || '';
                    const cellValue = typeof value === 'string' && value.length > 100 
                        ? value.substring(0, 100) + '...' 
                        : value;
                    return `<td class="px-4 py-3 text-sm text-gray-900 border-b" title="${value}">
                        ${cellValue}
                    </td>`;
                }).join('');
                
                return `<tr class="${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-blue-50 transition-colors">
                    ${cells}
                </tr>`;
            }).join('');

            const totalRows = data.length;
            const displayedRows = Math.min(totalRows, 100);

            return `<div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
                <div class="px-4 py-3 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                    <p class="text-sm text-gray-700">
                        Menunjukkan ${displayedRows} daripada ${totalRows} hasil
                        ${totalRows > 100 ? ' (had 100 baris untuk prestasi optimum)' : ''}
                    </p>
                    <div class="text-xs text-gray-500">
                        ${columns.length} lajur ditunjukkan
                    </div>
                </div>
                <div class="overflow-x-auto max-h-96">
                    <table class="min-w-full">
                        <thead class="bg-gray-50">
                            <tr>${tableHeaders}</tr>
                        </thead>
                        <tbody>${tableRows}</tbody>
                    </table>
                </div>
                ${totalRows > 100 ? `
                    <div class="px-4 py-3 bg-yellow-50 border-t border-yellow-200">
                        <p class="text-sm text-yellow-800">
                            <i class="fas fa-info-circle mr-2"></i>
                            Hanya 100 baris pertama ditunjukkan. Gunakan fungsi eksport untuk mendapatkan data penuh.
                        </p>
                    </div>
                ` : ''}
            </div>`;
        }

        closeModal() {
            const modal = document.getElementById('dataModal');
            if (modal) {
                modal.classList.add('hidden');
                document.body.style.overflow = '';
            }
            
            // Reset chart context
            this.currentChartType = null;
        }

        async retryLoad() {
            if (this.currentEndpoint && this.currentTitle) {
                await this.openModal(this.currentTitle, this.currentEndpoint);
            }
        }

        async exportModalData(format) {
            if (!this.currentEndpoint) return;
            try {
                let exportEndpoint = this.currentEndpoint.replace('/table-data', '/export');
                
                // Handle chart table data endpoints
                if (this.currentEndpoint.includes('/chart-table-data/')) {
                    exportEndpoint = this.currentEndpoint.replace('/chart-table-data/', '/export?chart_type=');
                }
                
                // Add format parameter
                const separator = exportEndpoint.includes('?') ? '&' : '?';
                exportEndpoint += `${separator}format=${format}`;
                
                console.log('Exporting from:', exportEndpoint);
                
                window.open(exportEndpoint, '_blank');
                
                // Show success message with chart context
                const contextMessage = this.currentChartType ? ` (${this.currentTitle})` : '';
                if (typeof showToast !== 'undefined') {
                    showToast(`Mengeksport data${contextMessage} sebagai ${format.toUpperCase()}...`, 'info');
                }
            } catch (error) {
                console.error('Export error:', error);
                if (typeof showToast !== 'undefined') {
                    showToast('Ralat semasa eksport data', 'error');
                }
            }
        }
    }

    // Chart column mappings for different dashboard types
    const CHART_COLUMNS = {
        // Faktor Graduan columns
        'employability-factors': [
            'Sejauh mana latihan industri/praktikal mempengaruhi kebolehpasaran anda?',
            'Sejauh mana kemahiran komunikasi  mempengaruhi kebolehpasaran anda?',
            'Sejauh mana kemahiran teknikal mempengaruhi kebolehpasaran anda?',
            'Sejauh mana rangkaian peribadi (networking) mempengaruhi kebolehpasaran anda?',
            'Sejauh mana kelayakan akademik mempengaruhi kebolehpasaran anda?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?'
        ],
        'professional-certificates': [
            'Adakah anda memiliki sijil profesional tambahan selain ijazah/diploma?',
            'Adakah sijil profesional ini membantu anda dalam mendapatkan pekerjaan?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?'
        ],
        'employer-requirements': [
            'Adakah majikan anda meminta kelayakan tambahan selain daripada ijazah anda?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?'
        ],
        'university-preparedness': [
            'Sejauh mana anda bersetuju bahawa universiti telah menyediakan anda untuk pasaran kerja?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?'
        ],
        'additional-skills': [
            'Kemahiran tambahan manakah yang paling banyak diminta oleh majikan semasa temu duga? ',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?'
        ],
        // Sosioekonomi chart columns
        'household-income': [
            'Pendapatan isi rumah bulanan keluarga anda?',
            'Jantina anda?',
            'Tahun graduasi anda?',
            'Institusi pendidikan MARA yang anda hadiri?'
        ],
        'education-financing': [
            'Bagaimana anda membiayai pendidikan anda?',
            'Jantina anda?',
            'Tahun graduasi anda?',
            'Institusi pendidikan MARA yang anda hadiri?'
        ],
        'father-occupation': [
            'Pekerjaan bapa anda',
            'Pendapatan isi rumah bulanan keluarga anda?',
            'Jantina anda?',
            'Tahun graduasi anda?'
        ],
        'mother-occupation': [
            'Pekerjaan ibu anda?',
            'Pendapatan isi rumah bulanan keluarga anda?',
            'Jantina anda?',
            'Tahun graduasi anda?'
        ],
        'financing-advantage': [
            'Bagaimana anda membiayai pendidikan anda?',
            'Adakah jenis pembiayaan ini memberi kelebihan dalam mencari kerja?',
            'Jantina anda?',
            'Tahun graduasi anda?'
        ],
        'debt-impact': [
            'Bagaimana anda membiayai pendidikan anda?',
            'Jika anda mempunyai pinjaman pendidikan, adakah beban hutang mempengaruhi pilihan kerjaya anda?',
            'Jantina anda?',
            'Tahun graduasi anda?'
        ],
        // Gig Economy chart columns
    'gig-types': [
        'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?',
        'Tahun graduasi anda?',
        'Jantina anda?',
        'Institusi pendidikan MARA yang anda hadiri?',
        'Program pengajian yang anda ikuti?'
    ],
    'gig-motivations': [
        'Apakah sebab utama anda memilih untuk bekerja dalam ekonomi gig? ',
        'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?',
        'Tahun graduasi anda?',
        'Jantina anda?',
        'Institusi pendidikan MARA yang anda hadiri?'
    ],
    'university-support': [
        'Adakah universiti anda menawarkan kursus atau latihan berkaitan keusahawanan?',
        'Tahun graduasi anda?',
        'Jantina anda?',
        'Institusi pendidikan MARA yang anda hadiri?',
        'Program pengajian yang anda ikuti?'
    ],
    'university-programs': [
        'Adakah universiti anda pernah menganjurkan program berkaitan perniagaan atau ekonomi gig seperti hackathon, bootcamp, atau geran permulaan perniagaan?',
        'Tahun graduasi anda?',
        'Jantina anda?',
        'Institusi pendidikan MARA yang anda hadiri?'
    ],
    'program-effectiveness': [
        'Adakah program berkaitan perniagaan atau ekonomi gig di universiti membantu anda dalam memulakan atau mengembangkan pekerjaan bebas anda?',
        'Adakah universiti anda pernah menganjurkan program berkaitan perniagaan atau ekonomi gig seperti hackathon, bootcamp, atau geran permulaan perniagaan?',
        'Tahun graduasi anda?',
        'Jantina anda?',
        'Institusi pendidikan MARA yang anda hadiri?'
    ],
    'skill-acquisition': [
        'Bagaimanakah anda memperoleh kemahiran untuk bekerja dalam ekonomi gig?',
        'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?',
        'Tahun graduasi anda?',
        'Jantina anda?',
        'Institusi pendidikan MARA yang anda hadiri?'
    ],
    'gig-challenges': [
        'Apakah cabaran utama yang anda hadapi dalam keusahawanan atau ekonomi gig?',
        'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?',
        'Tahun graduasi anda?',
        'Jantina anda?',
        'Institusi pendidikan MARA yang anda hadiri?'
    ],
    'support-needed': [
        'Apakah bantuan atau sokongan yang anda rasa perlu untuk berjaya dalam keusahawanan dan ekonomi gig?',
        'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?',
        'Tahun graduasi anda?',
        'Jantina anda?',
        'Institusi pendidikan MARA yang anda hadiri?'
    ],
    'monthly-income': [
        'Berapakah purata pendapatan bulan anda daripada ekonomi gig?',
        'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?',
        'Tahun graduasi anda?',
        'Jantina anda?',
        'Institusi pendidikan MARA yang anda hadiri?'
    ],
    'job-preference': [
        'Jika diberikan peluang pekerjaan tetap dengan gaji setanding ekonomi gig, adakah anda akan menerimanya?',
        'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?',
        'Tahun graduasi anda?',
        'Jantina anda?',
        'Institusi pendidikan MARA yang anda hadiri?'
    ]
    };

    // Initialize manager
    function initModalManager() {
        try {
            if (!window.modalManagerInstance) {
                window.modalManagerInstance = new ModalManager();
                window.modalManagerInstance.init();
            }

            // Global function for chart modals
            window.openChartModal = function(chartType, title, endpoint) {
                if (!window.modalManagerInstance) {
                    console.error('Modal manager not ready');
                    return;
                }
                const columns = CHART_COLUMNS[chartType] || null;
                window.modalManagerInstance.openModal(title, endpoint, columns);
            };

            // Global function for simple modals (used by faktor graduan)
            window.openModal = function(title, endpoint) {
                if (!window.modalManagerInstance) {
                    console.error('Modal manager not ready');
                    return;
                }
                window.modalManagerInstance.openModal(title, endpoint);
            };

            // Global function for chart table modals (main function for sosioekonomi)
            window.openChartTableModal = function(chartType, title) {
                if (!window.modalManagerInstance) {
                    console.error('Modal manager not ready');
                    return;
                }
                window.modalManagerInstance.openChartTableModal(chartType, title);
            };

            window.modalManagerLoaded = true;
            console.log('Modal manager loaded successfully with chart integration');
        } catch (error) {
            console.error('Error initializing modal manager:', error);
        }
    }

    // Initialize when ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initModalManager);
    } else {
        initModalManager();
    }

})();