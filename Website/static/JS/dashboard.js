// Simple Toast notification function
function showToast(message, type = 'info')
{
    const container = document.getElementById('toastContainer') || createToastContainer();
    const toast = document.createElement('div');

    const colors = {
        success: 'bg-green-500 text-white',
        error: 'bg-red-500 text-white',
        info: 'bg-blue-500 text-white'
    };

    toast.className = `${colors[ type ]} px-4 py-3 rounded-lg shadow-lg transform transition-all duration-300 translate-x-full opacity-0 flex items-center space-x-3 min-w-80`;
    toast.innerHTML = `
        <span class="font-medium">${message}</span>
        <button onclick="this.parentElement.remove()" class="text-white/80 hover:text-white">
            <i class="fas fa-times"></i>
        </button>
    `;

    container.appendChild(toast);

    requestAnimationFrame(() =>
    {
        toast.classList.remove('translate-x-full', 'opacity-0');
    });

    setTimeout(() =>
    {
        toast.classList.add('translate-x-full', 'opacity-0');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function createToastContainer()
{
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'fixed top-4 right-4 z-50 space-y-2';
    document.body.appendChild(container);
    return container;
}

// Modal functions
async function openModal(title, endpoint)
{
    const modal = document.getElementById('tableModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');

    modalTitle.textContent = title;
    modalBody.innerHTML = '<div class="flex items-center justify-center py-8"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div></div>';

    modal.classList.remove('hidden');
    modal.classList.add('flex');

    try
    {
        const response = await fetch(endpoint);
        const data = await response.json();

        if (data.data && data.data.length > 0)
        {
            const headers = Object.keys(data.data[ 0 ]);
            modalBody.innerHTML = `
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-primary-600">
                            <tr>
                                ${headers.map(header => `
                                    <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase">
                                        ${header}
                                    </th>
                                `).join('')}
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            ${data.data.slice(0, 50).map((row, index) => `
                                <tr class="hover:bg-gray-50 ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}">
                                    ${headers.map(header => `
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            ${row[ header ] || ''}
                                        </td>
                                    `).join('')}
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                <div class="mt-4 text-sm text-gray-700">
                    Showing first 50 of ${data.data.length} records
                </div>
            `;
        } else
        {
            modalBody.innerHTML = '<div class="text-center py-8 text-gray-500">No data available</div>';
        }
    } catch (error)
    {
        modalBody.innerHTML = '<div class="text-center py-8 text-red-500">Error loading data</div>';
        console.error('Error loading table data:', error);
    }
}

function closeModal()
{
    const modal = document.getElementById('tableModal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}

// Chart Factory Class - More robust version
class ChartFactory
{
    static createBarChart(ctx, data, options = {})
    {
        if (typeof Chart === 'undefined')
        {
            console.error('Chart.js is not loaded');
            return null;
        }

        if (!ctx)
        {
            console.error('Canvas context is null');
            return null;
        }

        try
        {
            return new Chart(ctx, {
                type: 'bar',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: 'white',
                            bodyColor: 'white',
                            cornerRadius: 8
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0,0,0,0.1)'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    },
                    animation: {
                        duration: 800
                    },
                    ...options
                }
            });
        } catch (error)
        {
            console.error('Error creating bar chart:', error);
            return null;
        }
    }

    static createPieChart(ctx, data, options = {})
    {
        if (typeof Chart === 'undefined')
        {
            console.error('Chart.js is not loaded');
            return null;
        }

        if (!ctx)
        {
            console.error('Canvas context is null');
            return null;
        }

        try
        {
            return new Chart(ctx, {
                type: 'doughnut',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '60%',
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: 'white',
                            bodyColor: 'white',
                            cornerRadius: 8
                        }
                    },
                    animation: {
                        duration: 800
                    },
                    ...options
                }
            });
        } catch (error)
        {
            console.error('Error creating pie chart:', error);
            return null;
        }
    }

    static createStackedBarChart(ctx, data, options = {})
    {
        if (typeof Chart === 'undefined')
        {
            console.error('Chart.js is not loaded');
            return null;
        }

        if (!ctx)
        {
            console.error('Canvas context is null');
            return null;
        }

        try
        {
            return new Chart(ctx, {
                type: 'bar',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            stacked: true,
                            grid: {
                                display: false
                            }
                        },
                        y: {
                            stacked: true,
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0,0,0,0.1)'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                padding: 20,
                                usePointStyle: true
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: 'white',
                            bodyColor: 'white',
                            cornerRadius: 8
                        }
                    },
                    animation: {
                        duration: 800
                    },
                    ...options
                }
            });
        } catch (error)
        {
            console.error('Error creating stacked bar chart:', error);
            return null;
        }
    }
}

// Global Chart Store to prevent duplicates
window.globalCharts = {};

// Utility function to safely destroy and recreate charts
function safeDestroyChart(chartId)
{
    if (window.globalCharts[ chartId ])
    {
        try
        {
            window.globalCharts[ chartId ].destroy();
        } catch (e)
        {
            console.warn(`Warning destroying chart ${chartId}:`, e);
        }
        delete window.globalCharts[ chartId ];
    }
}

// Highlight active navigation item based on current URL
document.addEventListener('DOMContentLoaded', function ()
{
    const navItems = document.querySelectorAll('.nav-item');
    const currentPath = window.location.pathname;

    navItems.forEach(item =>
    {
        const itemHref = item.getAttribute('href');

        console.log(`Checking nav item: ${itemHref} against current path: ${currentPath}`);

        // Special handling for root path
        if (itemHref === '/' && currentPath === '/')
        {
            item.classList.add('bg-white');
            item.classList.add('text-primary-700');
        }
        // For other paths, check if current path starts with the item href
        else if (itemHref !== '/' && currentPath.startsWith(itemHref))
        {
            item.classList.add('bg-white');
            item.classList.add('text-primary-700');
        }
    });
});

// Make functions globally available
window.showToast = showToast;
window.openModal = openModal;
window.closeModal = closeModal;
window.ChartFactory = ChartFactory;
window.safeDestroyChart = safeDestroyChart;