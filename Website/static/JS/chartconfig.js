// Enhanced Chart Configuration with improved area chart support and sosioekonomi chart types

// Enhanced Global Chart Configuration
const ChartConfig = {
    // Enhanced Color Schemes with better gradients and contrast
    colorSchemes: {
        // Enhanced colors for horizontal bar charts
        horizontalBar: {
            colors: [
                '#ed1c24',
                '#9c354d',
                '#56423e',
                '#bea6a1',
                '#3a001e',
                '#a5378b',
                '#cc0068',
                '#9c4f00',
                '#d28433'


                // '#00606d',
                // '#0097a1',
                // '#2d8b00',
                // '#005800',

            ],
            name: 'Horizontal Bar Colors'
        },

        // Enhanced colors for stacked bar charts
        stackedBar: {
            colors: [
                // '#ED1C24', '#D80164', '#A5378B', '#664C92',
                // '#354F7C ', '#2F4858', '#009096', '#00904E',
                // '#198A00', '#7D7C00', '#BE5E00', 
                '#ed1c24',
                '#d80164',
                '#9c354d',
                '#bea6a1',
                '#664c92',
            ],
            // backgrounds: [
            //     'rgba(37, 99, 235, 0.1)', 'rgba(220, 38, 38, 0.1)', 'rgba(22, 163, 74, 0.1)',
            //     'rgba(234, 88, 12, 0.1)', 'rgba(147, 51, 234, 0.1)', 'rgba(8, 145, 178, 0.1)'
            // ],
            name: 'Stacked Bar Colors'
        },

        // Enhanced colors for vertical bar charts
        verticalBar: {
            colors: [
                '#ed1c24', '#56423e', '#bea6a1', '#0097a1', '#00606d', '#4993a1' , '#627b81'
            ],
            name: 'Vertical Bar Colors'
        },

        // Enhanced colors for pie charts
        enhancedPie: {
            colors: [
                '#2159a2', '#a6abbd', '#9c354d', '#d6697e', '#727787' ],
            name: 'Enhanced Pie Colors'
        },

        // Enhanced colors for area charts
        area: {
            colors: [
                '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
                '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1'
            ],
            gradients: [
                [ '#3b82f6', '#93c5fd' ], [ '#10b981', '#6ee7b7' ], [ '#f59e0b', '#fcd34d' ],
                [ '#ef4444', '#f87171' ], [ '#8b5cf6', '#c4b5fd' ]
            ],
            name: 'Area Chart Colors'
        },

        // Enhanced colors for line charts
        line: {
            colors: [
                '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
                '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1'
            ],
            name: 'Line Chart Colors'
        },

        // Enhanced colors for multiple bar charts (employability factors)
        multipleBar: {
            colors: [
                '#1d4f90', '#2066a8', '#8ec1da', '#cde1ec',
                '#f6d6c2', '#d47264', '#ae282c', '#7f1d1d'
            ],
            name: 'Multiple Bar Colors'
        },

        // NEW: Sosioekonomi specific color schemes
        sosioekonomiIncome: {
            colors: [
                '#10b981', '#22c55e', '#4ade80', '#86efac', '#bbf7d0',
                '#065f46', '#047857', '#059669', '#0d9488', '#14b8a6'
            ],
            name: 'Sosioekonomi Income Colors'
        },

        sosioekonomiFinancing: {
            colors: [
                '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe',
                '#1e40af', '#2563eb', '#1d4ed8', '#1e3a8a', '#312e81'
            ],
            name: 'Sosioekonomi Financing Colors'
        },

        sosioekonomiOccupation: {
            colors: [
                '#f59e0b', '#fbbf24', '#fcd34d', '#fde68a', '#fef3c7',
                '#d97706', '#f59e0b', '#eab308', '#ca8a04', '#a16207',
                '#92400e', '#78350f', '#451a03'
            ],
            name: 'Sosioekonomi Occupation Colors'
        }
    },

    // Enhanced Style Templates
    styleTemplates: {
        // Enhanced horizontal bar template
        enhancedHorizontalBar: {
            borderRadius: 12,
            borderWidth: 0,
            borderSkipped: false,
            barThickness: 'flex',
            maxBarThickness: 35,
            categoryPercentage: 0.8,
            barPercentage: 0.85,
        },

        // Enhanced stacked bar template
        enhancedStackedBar: {
            borderRadius: {
                topLeft: 8,
                topRight: 8,
                bottomLeft: 8,
                bottomRight: 8
            },
            borderWidth: 1,
            borderColor: '#ffffff',
            borderSkipped: false,
            barThickness: 'flex',
            maxBarThickness: 40,
            categoryPercentage: 0.7,
            barPercentage: 0.9
        },

        // Enhanced vertical bar template
        enhancedVerticalBar: {
            borderRadius: {
                topLeft: 10,
                topRight: 10,
                bottomLeft: 0,
                bottomRight: 0
            },
            borderWidth: 0,
            borderSkipped: false,
            barThickness: 'flex',
            maxBarThickness: 45,
            categoryPercentage: 0.8,
            barPercentage: 0.75
        },

        // Enhanced pie template
        enhancedPie: {
            borderWidth: 3,
            borderColor: '#ffffff',
            hoverBorderWidth: 5,
            hoverOffset: 12,
            radius: '85%',
            cutout: '0%'
        },

        // Enhanced multiple bar template for employability factors
        enhancedMultipleBar: {
            borderRadius: 4,
            borderWidth: 1,
            borderSkipped: false,
            barThickness: 'flex',
            maxBarThickness: 30,
            categoryPercentage: 0.8,
            barPercentage: 0.9
        }
    },

    // Enhanced Global Options
    globalOptions: {
        responsive: true,
        maintainAspectRatio: false,
        devicePixelRatio: 2, // Better quality on high DPI displays
        interaction: {
            intersect: false,
            mode: 'index'
        },
        animation: {
            duration: 1200,
            easing: 'easeInOutQuart'
        },
        plugins: {
            legend: {
                display: false,
                position: 'top',
                align: 'start',
                labels: {
                    usePointStyle: true,
                    pointStyle: 'rectRounded',
                    padding: 20,
                    font: {
                        size: 12,
                        weight: '600',
                        family: "'Inter', 'Segoe UI', sans-serif"
                    },
                    color: '#374151',
                    boxWidth: 12,
                    boxHeight: 12
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
                    weight: '500',
                    family: "'Inter', 'Segoe UI', sans-serif"
                },
                displayColors: true,
                boxPadding: 8,
                usePointStyle: true,
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1,
                caretSize: 8
            }
        }
    }
};

// Enhanced Chart Factory with improved designs
class EnhancedChartFactory
{
    // Get enhanced colors with gradients for chart types
    static getColorsForChartType(chartType, dataLength = 6)
    {
        let scheme;

        switch (chartType.toLowerCase())
        {
            case 'horizontal-bar':
            case 'horizontal':
                scheme = ChartConfig.colorSchemes.horizontalBar;
                break;
            case 'enhanced-stacked-bar':
            case 'stacked-bar':
            case 'stacked':
                scheme = ChartConfig.colorSchemes.stackedBar;
                break;
            case 'vertical-bar':
            case 'bar':
                scheme = ChartConfig.colorSchemes.verticalBar;
                break;
            case 'enhanced-pie':
            case 'pie':
            case 'doughnut':
                scheme = ChartConfig.colorSchemes.enhancedPie;
                break;
            case 'multiple-bar':
            case 'multiple':
                scheme = ChartConfig.colorSchemes.multipleBar;
                break;
            case 'area':
                scheme = ChartConfig.colorSchemes.area;
                break;
            case 'line':
                scheme = ChartConfig.colorSchemes.line;
                break;
            // NEW: Sosioekonomi specific chart types
            case 'sosioekonomi-income':
                scheme = ChartConfig.colorSchemes.sosioekonomiIncome;
                break;
            case 'sosioekonomi-financing':
                scheme = ChartConfig.colorSchemes.sosioekonomiFinancing;
                break;
            case 'sosioekonomi-occupation':
                scheme = ChartConfig.colorSchemes.sosioekonomiOccupation;
                break;
            default:
                scheme = ChartConfig.colorSchemes.verticalBar;
        }

        // Extend colors if needed
        let colors = [ ...scheme.colors ];
        while (colors.length < dataLength)
        {
            colors = [ ...colors, ...scheme.colors ];
        }

        return colors.slice(0, dataLength);
    }

    // Create gradient colors for bars
    static createGradientColors(ctx, colors, direction = 'vertical')
    {
        return colors.map(color =>
        {
            const gradient = ctx.createLinearGradient(
                0, direction === 'vertical' ? 0 : ctx.canvas.height,
                direction === 'vertical' ? ctx.canvas.width : 0,
                direction === 'vertical' ? ctx.canvas.height : 0
            );

            // Create a lighter version of the color
            const lighterColor = this.lightenColor(color, 20);

            gradient.addColorStop(0, lighterColor);
            gradient.addColorStop(1, color);

            return gradient;
        });
    }

    // Create enhanced area gradient
    static createAreaGradient(ctx, color, chartArea)
    {
        const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);

        // Convert hex to rgba if needed
        let rgbaColor = color;
        if (color.startsWith('#'))
        {
            const r = parseInt(color.slice(1, 3), 16);
            const g = parseInt(color.slice(3, 5), 16);
            const b = parseInt(color.slice(5, 7), 16);
            rgbaColor = `rgba(${r}, ${g}, ${b}`;
        } else if (color.startsWith('rgb('))
        {
            rgbaColor = color.replace('rgb(', 'rgba(').replace(')', '');
        }

        gradient.addColorStop(0, rgbaColor + ', 0.8)');
        gradient.addColorStop(0.5, rgbaColor + ', 0.4)');
        gradient.addColorStop(1, rgbaColor + ', 0.05)');

        return gradient;
    }

    // Utility to lighten colors
    static lightenColor(color, percent)
    {
        const num = parseInt(color.replace("#", ""), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) + amt;
        const G = (num >> 8 & 0x00FF) + amt;
        const B = (num & 0x0000FF) + amt;
        return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
            (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
            (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
    }

    // Enhanced Horizontal Bar Chart
    static createBarChart(ctx, data, chartType = 'bar', options = {})
    {
        const isHorizontal = chartType === 'horizontal-bar' || options.indexAxis === 'y';
        const dataLength = data.datasets?.[ 0 ]?.data?.length || data.labels?.length || 6;
        const colors = this.getColorsForChartType(isHorizontal ? 'horizontal-bar' : 'vertical-bar', dataLength);
        const template = isHorizontal ?
            ChartConfig.styleTemplates.enhancedHorizontalBar :
            ChartConfig.styleTemplates.enhancedVerticalBar;

        // Create gradient backgrounds for better visual appeal
        const gradientColors = this.createGradientColors(ctx, colors, isHorizontal ? 'horizontal' : 'vertical');

        const enhancedData = {
            ...data,
            datasets: data.datasets.map((dataset) => ({
                ...dataset,
                backgroundColor: gradientColors,
                borderColor: colors,
                hoverBackgroundColor: colors.map(color => this.lightenColor(color, 10)),
                hoverBorderColor: colors.map(color => this.lightenColor(color, -10)),
                hoverBorderWidth: 2,
                ...template
            }))
        };

        return new Chart(ctx, {
            type: 'bar',
            data: enhancedData,
            options: {
                ...ChartConfig.globalOptions,
                indexAxis: isHorizontal ? 'y' : 'x',
                ...options,
                scales: {
                    [ isHorizontal ? 'x' : 'y' ]: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.05)',
                            drawBorder: false,
                            lineWidth: 1
                        },
                        ticks: {
                            font: {
                                size: 12,
                                weight: '600',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#4b5563',
                            padding: 12,
                            callback: function (value)
                            {
                                return value.toLocaleString();
                            }
                        },
                        border: {
                            display: false
                        }
                    },
                    [ isHorizontal ? 'y' : 'x' ]: {
                        grid: { display: false },
                        ticks: {
                            font: {
                                size: 11,
                                weight: '600',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#6b7280',
                            maxRotation: 0,
                            minRotation: 0,
                            padding: 10
                        },
                        border: {
                            display: false
                        }
                    },
                    ...options.scales
                },
                plugins: {
                    ...ChartConfig.globalOptions.plugins,
                    tooltip: {
                        ...ChartConfig.globalOptions.plugins.tooltip,
                        callbacks: {
                            label: function (context)
                            {
                                return `${context.dataset.label || 'Nilai'}: ${context.parsed[ isHorizontal ? 'x' : 'y' ].toLocaleString()}`;
                            }
                        }
                    },
                    ...options.plugins
                }
            }
        });
    }

    // Enhanced Pie Chart
    static createPieChart(ctx, data, chartType = 'pie', options = {})
    {
        const dataLength = data.labels?.length || data.datasets?.[ 0 ]?.data?.length || 6;
        const colors = this.getColorsForChartType('enhanced-pie', dataLength);
        const template = ChartConfig.styleTemplates.enhancedPie;

        const enhancedData = {
            ...data,
            datasets: data.datasets.map((dataset) => ({
                ...dataset,
                backgroundColor: colors.slice(0, dataLength),
                borderColor: Array(dataLength).fill('#ffffff'),
                hoverBackgroundColor: colors.slice(0, dataLength).map(color => this.lightenColor(color, 15)),
                hoverBorderColor: Array(dataLength).fill('#e5e7eb'),
                ...template
            }))
        };

        return new Chart(ctx, {
            type: 'pie',
            data: enhancedData,
            options: {
                ...ChartConfig.globalOptions,
                ...options,
                plugins: {
                    ...ChartConfig.globalOptions.plugins,
                    legend: {
                        display: true,
                        position: 'bottom',
                        align: 'center',
                        labels: {
                            usePointStyle: true,
                            pointStyle: 'circle',
                            padding: 20,
                            font: {
                                size: 12,
                                weight: '500',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#374151',
                            boxWidth: 15,
                            boxHeight: 15,
                            generateLabels: function (chart)
                            {
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length)
                                {
                                    return data.labels.map((label, index) =>
                                    {
                                        const dataset = data.datasets[ 0 ];
                                        const value = dataset.data[ index ];
                                        const total = dataset.data.reduce((sum, val) => sum + val, 0);
                                        const percentage = ((value / total) * 100).toFixed(1);

                                        return {
                                            text: `${label} (${percentage}%)`,
                                            fillStyle: dataset.backgroundColor[ index ],
                                            strokeStyle: '#ffffff',
                                            lineWidth: 3,
                                            hidden: false,
                                            index: index,
                                            fontColor: '#374151'
                                        };
                                    });
                                }
                                return [];
                            }
                        }
                    },
                    tooltip: {
                        ...ChartConfig.globalOptions.plugins.tooltip,
                        callbacks: {
                            label: function (context)
                            {
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

    // Enhanced Stacked Bar Chart
    static createStackedBarChart(ctx, data, chartType = 'stacked', options = {})
    {
        const isHorizontal = options.indexAxis === 'y';
        const colors = this.getColorsForChartType('enhanced-stacked-bar', data.datasets.length);
        const template = ChartConfig.styleTemplates.enhancedStackedBar;

        const enhancedData = {
            ...data,
            datasets: data.datasets.map((dataset, index) => ({
                ...dataset,
                backgroundColor: colors[ index % colors.length ],
                borderColor: '#ffffff',
                hoverBackgroundColor: this.lightenColor(colors[ index % colors.length ], 10),
                hoverBorderColor: '#f3f4f6',
                hoverBorderWidth: 2,
                ...template
            }))
        };

        return new Chart(ctx, {
            type: 'bar',
            data: enhancedData,
            options: {
                ...ChartConfig.globalOptions,
                responsive: true,
                indexAxis: isHorizontal ? 'y' : 'x',
                ...options,
                plugins: {
                    ...ChartConfig.globalOptions.plugins,
                    legend: {
                        display: true,
                        position: 'top',
                        align: 'start',
                        labels: {
                            usePointStyle: true,
                            pointStyle: 'rectRounded',
                            padding: 15,
                            font: {
                                size: 11,
                                weight: '600',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#374151',
                            boxWidth: 12,
                            boxHeight: 12
                        }
                    },
                    tooltip: {
                        ...ChartConfig.globalOptions.plugins.tooltip,
                        callbacks: {
                            label: function (context)
                            {
                                return `${context.dataset.label}: ${context.parsed[ isHorizontal ? 'x' : 'y' ].toLocaleString()}`;
                            },
                            afterLabel: function (context)
                            {
                                const datasetArray = [];
                                context.chart.data.datasets.forEach((dataset) =>
                                {
                                    if (dataset.data[ context.dataIndex ] != undefined)
                                    {
                                        datasetArray.push(dataset.data[ context.dataIndex ]);
                                    }
                                });
                                const total = datasetArray.reduce((total, dataItem) => total + dataItem, 0);
                                const percentage = ((context.parsed[ isHorizontal ? 'x' : 'y' ] / total) * 100).toFixed(1);
                                return `Peratus: ${percentage}%`;
                            }
                        }
                    },
                    ...options.plugins
                },
                scales: {
                    [ isHorizontal ? 'x' : 'y' ]: {
                        stacked: true,
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.04)',
                            drawBorder: false,
                            lineWidth: 1
                        },
                        ticks: {
                            font: {
                                size: 11,
                                weight: '600',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#4b5563',
                            padding: 12,
                            callback: function (value)
                            {
                                return value.toLocaleString();
                            }
                        },
                        border: {
                            display: false
                        }
                    },
                    [ isHorizontal ? 'y' : 'x' ]: {
                        stacked: true,
                        grid: { display: false },
                        ticks: {
                            font: {
                                size: 10,
                                weight: '600',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#6b7280',
                            maxRotation: 0,
                            minRotation: 0,
                            padding: 8
                        },
                        border: {
                            display: false
                        }
                    },
                    ...options.scales
                }
            }
        });
    }

    // Enhanced Multiple Bar Chart for employability factors
    static createMultipleBarChart(ctx, data, options = {})
    {
        const colors = this.getColorsForChartType('multiple-bar', data.datasets.length);
        const template = ChartConfig.styleTemplates.enhancedMultipleBar;

        // Enhanced data processing for multiple bar chart
        const enhancedData = {
            ...data,
            datasets: data.datasets.map((dataset, index) => ({
                ...dataset,
                backgroundColor: colors[ index % colors.length ],
                borderColor: this.lightenColor(colors[ index % colors.length ], -10),
                hoverBackgroundColor: this.lightenColor(colors[ index % colors.length ], 10),
                hoverBorderColor: this.lightenColor(colors[ index % colors.length ], -20),
                hoverBorderWidth: 2,
                ...template
            }))
        };

        return new Chart(ctx, {
            type: 'bar',
            data: enhancedData,
            options: {
                ...ChartConfig.globalOptions,
                responsive: true,
                maintainAspectRatio: false,
                ...options,
                plugins: {
                    ...ChartConfig.globalOptions.plugins,
                    legend: {
                        display: true,
                        position: 'top',
                        align: 'center',
                        labels: {
                            usePointStyle: true,
                            pointStyle: 'rectRounded',
                            padding: 20,
                            font: {
                                size: 12,
                                weight: '600',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#374151',
                            boxWidth: 12,
                            boxHeight: 12
                        }
                    },
                    tooltip: {
                        ...ChartConfig.globalOptions.plugins.tooltip,
                        callbacks: {
                            label: function (context)
                            {
                                return `${context.dataset.label}: ${context.parsed.y.toLocaleString()} responden`;
                            },
                            afterLabel: function (context)
                            {
                                const total = context.chart.data.datasets.reduce((sum, dataset) =>
                                {
                                    return sum + (dataset.data[ context.dataIndex ] || 0);
                                }, 0);
                                const percentage = total > 0 ? ((context.parsed.y / total) * 100).toFixed(1) : '0.0';
                                return `Peratus: ${percentage}%`;
                            }
                        }
                    },
                    ...options.plugins
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.05)',
                            drawBorder: false,
                            lineWidth: 1
                        },
                        ticks: {
                            font: {
                                size: 12,
                                weight: '600',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#4b5563',
                            padding: 12,
                            callback: function (value)
                            {
                                return value.toLocaleString();
                            }
                        },
                        border: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Bilangan Responden',
                            font: {
                                size: 13,
                                weight: '600',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#374151'
                        }
                    },
                    x: {
                        grid: { display: false },
                        ticks: {
                            font: {
                                size: 11,
                                weight: '600',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#6b7280',
                            maxRotation: 0,
                            minRotation: 0,
                            padding: 10
                        },
                        border: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Skala Kepentingan (1-5)',
                            font: {
                                size: 13,
                                weight: '600',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#374151'
                        }
                    },
                    ...options.scales
                }
            }
        });
    }

    // Enhanced Line Chart with Area Chart support (FIXED AND IMPROVED)
    static createLineChart(ctx, data, chartType = 'line', options = {})
    {
        const colors = this.getColorsForChartType(chartType === 'area' ? 'area' : 'line', data.datasets.length);

        const enhancedData = {
            ...data,
            datasets: data.datasets.map((dataset, index) =>
            {
                const color = colors[ index % colors.length ];
                const isAreaChart = dataset.fill !== undefined ? dataset.fill : (chartType === 'area');

                // Create gradient for area charts
                let backgroundColor = dataset.backgroundColor;
                if (isAreaChart && ctx.chart && ctx.chart.chartArea)
                {
                    backgroundColor = this.createAreaGradient(ctx, color, ctx.chart.chartArea);
                } else if (isAreaChart)
                {
                    // Fallback gradient creation
                    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
                    gradient.addColorStop(0, color.replace(')', ', 0.8)').replace('rgb', 'rgba'));
                    gradient.addColorStop(0.5, color.replace(')', ', 0.4)').replace('rgb', 'rgba'));
                    gradient.addColorStop(1, color.replace(')', ', 0.05)').replace('rgb', 'rgba'));
                    backgroundColor = gradient;
                }

                return {
                    ...dataset,
                    backgroundColor: backgroundColor,
                    borderColor: dataset.borderColor || color,
                    pointBorderColor: dataset.pointBorderColor || color,
                    pointHoverBorderColor: dataset.pointHoverBorderColor || color,
                    pointBackgroundColor: dataset.pointBackgroundColor || '#ffffff',
                    pointHoverBackgroundColor: dataset.pointHoverBackgroundColor || '#ffffff',
                    pointBorderWidth: 3,
                    pointHoverBorderWidth: 4,
                    fill: isAreaChart,
                    tension: dataset.tension !== undefined ? dataset.tension : 0.4,
                    pointRadius: dataset.pointRadius !== undefined ? dataset.pointRadius : 6,
                    pointHoverRadius: dataset.pointHoverRadius !== undefined ? dataset.pointHoverRadius : 8,
                    borderWidth: dataset.borderWidth !== undefined ? dataset.borderWidth : 4,
                    borderCapStyle: 'round',
                    borderJoinStyle: 'round'
                }
            })
        };

        return new Chart(ctx, {
            type: 'line',
            data: enhancedData,
            options: {
                ...ChartConfig.globalOptions,
                ...options,
                layout: {
                    padding: {
                        top: 20,
                        right: 20,
                        bottom: 20,
                        left: 20
                    }
                },
                elements: {
                    line: {
                        tension: 0.4
                    },
                    point: {
                        radius: 6,
                        hoverRadius: 8,
                        borderWidth: 3,
                        hoverBorderWidth: 4
                    }
                },
                plugins: {
                    ...ChartConfig.globalOptions.plugins,
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
                                weight: '600',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#374151'
                        }
                    },
                    tooltip: {
                        ...ChartConfig.globalOptions.plugins.tooltip,
                        backgroundColor: 'rgba(17, 24, 39, 0.95)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        cornerRadius: 15,
                        padding: 20,
                        displayColors: true,
                        boxPadding: 10,
                        usePointStyle: true,
                        callbacks: {
                            label: function (context)
                            {
                                return `${context.dataset.label || 'Bilangan'}: ${context.parsed.y.toLocaleString()} responden`;
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
                                size: 11,
                                weight: '600',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#6b7280',
                            maxRotation: 45,
                            minRotation: 0,
                            padding: 12
                        },
                        border: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grace: '10%',
                        grid: {
                            color: 'rgba(0,0,0,0.04)',
                            drawBorder: false,
                            lineWidth: 1
                        },
                        ticks: {
                            font: {
                                size: 11,
                                weight: '600',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#6b7280',
                            padding: 15,
                            callback: function (value)
                            {
                                return value.toLocaleString();
                            }
                        },
                        border: {
                            display: false
                        }
                    },
                    ...options.scales
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                animation: {
                    duration: 1500,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    // Universal chart creator method
    static createChart(ctx, type, data, endpoint, options = {})
    {
        switch (type.toLowerCase())
        {
            case 'multiple-bar':
            case 'multiple':
                return this.createMultipleBarChart(ctx, data, options);
            case 'horizontal-bar':
            case 'horizontal':
                return this.createBarChart(ctx, data, 'horizontal-bar', { indexAxis: 'y', ...options });
            case 'bar':
            case 'vertical-bar':
                return this.createBarChart(ctx, data, 'vertical-bar', options);
            case 'enhanced-pie':
            case 'pie':
            case 'doughnut':
                return this.createPieChart(ctx, data, 'enhanced-pie', options);
            case 'line':
                return this.createLineChart(ctx, data, 'line', options);
            case 'area':
                return this.createLineChart(ctx, data, 'area', { ...options, fill: true });
            case 'enhanced-stacked-bar':
            case 'stackedbar':
            case 'stacked':
                return this.createStackedBarChart(ctx, data, 'enhanced-stacked-bar', options);
            default:
                return this.createBarChart(ctx, data, type, options);
        }
    }

    // Method to update color schemes
    static updateColorScheme(chartType, colors)
    {
        if (ChartConfig.colorSchemes[ chartType ])
        {
            ChartConfig.colorSchemes[ chartType ].colors = colors;
            console.log(`Updated color scheme for ${chartType}`);
        }
    }

    // Preview all color schemes
    static previewColorSchemes()
    {
        console.log('Enhanced Chart Color Schemes:');
        Object.entries(ChartConfig.colorSchemes).forEach(([ key, scheme ]) =>
        {
            console.log(`${scheme.name}:`, scheme.colors.slice(0, 5));
        });
    }
}

// Enhanced Chart Factory Extension with Multiple Bar Chart Support
class ExtendedChartFactory extends EnhancedChartFactory
{

    // Override the getColorsForChartType method to include multiple-bar
    static getColorsForChartType(chartType, dataLength = 6)
    {
        if (chartType === 'multiple-bar' || chartType === 'multiple')
        {
            const scheme = ChartConfig.colorSchemes.multipleBar;
            let colors = [ ...scheme.colors ];
            while (colors.length < dataLength)
            {
                colors = [ ...colors, ...scheme.colors ];
            }
            return colors.slice(0, dataLength);
        }
        return super.getColorsForChartType(chartType, dataLength);
    }

    // Override createChart to handle multiple-bar type
    static createChart(ctx, type, data, endpoint, options = {})
    {
        switch (type.toLowerCase())
        {
            case 'multiple-bar':
            case 'multiple':
                return this.createMultipleBarChart(ctx, data, options);
            default:
                return super.createChart(ctx, type, data, endpoint, options);
        }
    }
}

// Export for global use
window.ChartConfig = ChartConfig;
window.EnhancedChartFactory = EnhancedChartFactory;
window.ExtendedChartFactory = ExtendedChartFactory;

// Compatibility alias for existing code
window.ChartFactory = ExtendedChartFactory;

// Enhanced Dashboard Integration
class EnhancedConfigurableDashboard
{
    constructor(apiBase = '/api')
    {
        this.charts = {};
        this.filters = {};
        this.apiBase = apiBase;
        this.loadingStates = {};
    }

    // Create enhanced chart with loading states
    async createEnhancedChart(canvasId, type, endpoint, options = {})
    {
        this.setLoadingState(canvasId, true);

        try
        {
            const response = await fetch(`${this.apiBase}/${endpoint}?${new URLSearchParams(this.filters)}`);
            const data = await response.json();

            if (data.error)
            {
                throw new Error(data.error);
            }

            const ctx = document.getElementById(canvasId);
            if (!ctx)
            {
                throw new Error(`Canvas element ${canvasId} not found`);
            }

            // Destroy existing chart
            this.destroyChart(canvasId);

            // Create enhanced chart
            this.charts[ canvasId ] = ExtendedChartFactory.createChart(
                ctx.getContext('2d'),
                type,
                data,
                endpoint,
                options
            );

            this.setLoadingState(canvasId, false);
            return this.charts[ canvasId ];

        } catch (error)
        {
            console.error(`Error creating chart ${canvasId}:`, error);
            this.showChartError(canvasId, error.message);
            this.setLoadingState(canvasId, false);
            return null;
        }
    }

    // Enhanced loading state management
    setLoadingState(chartId, isLoading)
    {
        this.loadingStates[ chartId ] = isLoading;
        const loadingEl = document.querySelector(`#${chartId}-loading`);
        const canvasEl = document.getElementById(chartId);

        if (loadingEl && canvasEl)
        {
            loadingEl.style.display = isLoading ? 'flex' : 'none';
            canvasEl.style.opacity = isLoading ? '0.3' : '1';
        }
    }

    // Enhanced chart destruction
    destroyChart(chartId)
    {
        if (this.charts[ chartId ])
        {
            try
            {
                this.charts[ chartId ].destroy();
                delete this.charts[ chartId ];
            } catch (error)
            {
                console.warn(`Error destroying chart ${chartId}:`, error);
            }
        }
    }

    // Enhanced error display
    showChartError(chartId, message)
    {
        const container = document.getElementById(chartId)?.parentElement;
        if (container)
        {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'flex items-center justify-center p-8 text-red-500 bg-red-50 rounded-lg';
            errorDiv.innerHTML = `
                <div class="text-center">
                    <i class="fas fa-exclamation-triangle text-2xl mb-2"></i>
                    <div class="font-medium">Error Loading Chart</div>
                    <div class="text-sm text-red-400 mt-1">${message}</div>
                </div>
            `;
            container.appendChild(errorDiv);
        }
    }

    // Method to refresh all charts with enhanced loading
    async refreshAllCharts()
    {
        const refreshPromises = Object.keys(this.charts).map(chartId =>
        {
            const chartType = this.charts[ chartId ].config.type;
            return this.refreshChart(chartId, chartType);
        });
        await Promise.all(refreshPromises);
    }

    // Enhanced filter updates
    async updateFilters(newFilters)
    {
        this.filters = { ...this.filters, ...newFilters };
        await this.refreshAllCharts();
    }
}

// Export enhanced dashboard
window.EnhancedConfigurableDashboard = EnhancedConfigurableDashboard;

// Initialize enhanced features
document.addEventListener('DOMContentLoaded', function ()
{
    // Add CSS for enhanced animations
    if (!document.querySelector('#enhanced-chart-styles'))
    {
        const style = document.createElement('style');
        style.id = 'enhanced-chart-styles';
        style.textContent = `
            .chart-container {
                position: relative;
                transition: all 0.3s ease;
            }
            
            .chart-container:hover {
                transform: translateY(-2px);
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            }
            
            canvas {
                transition: opacity 0.3s ease;
            }
            
            .chart-loading {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(255, 255, 255, 0.9);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10;
                border-radius: 12px;
            }
            
            @keyframes chartFadeIn {
                from { opacity: 0; transform: scale(0.95); }
                to { opacity: 1; transform: scale(1); }
            }
            
            .chart-fade-in {
                animation: chartFadeIn 0.6s ease-out;
            }
        `;
        document.head.appendChild(style);
    }
});

console.log('Enhanced Chart Configuration System with Sosioekonomi support loaded!'); a