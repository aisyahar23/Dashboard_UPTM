// Enhanced Chart Configuration with improved area chart support and sosioekonomi chart types

// Enhanced Global Chart Configuration
const ChartConfig = {
    // Corporate Color Schemes - Designed for accessibility and professional appearance
// Optimized for older audiences with high contrast and clear differentiation
colorSchemes: {
    
    // 1. PROFESSIONAL NAVY & STEEL - Classic corporate look
    corporateNavy: {
        colors: [
            '#1a365d', // Deep navy blue
            '#2d5a87', // Medium navy
            '#4a90b8', // Steel blue
            '#6ba3d0', // Light steel
            '#8bb8d8', // Very light steel
            '#a8cde8'  // Pale steel
        ],
        name: 'Corporate Navy & Steel'
    },

    // 2. EXECUTIVE BURGUNDY & GRAY - Sophisticated and authoritative
    executiveBurgundy: {
        colors: [
            '#722f37', // Deep burgundy
            '#8b4513', // Rich brown
            '#5d5d5d', // Charcoal gray
            '#787878', // Medium gray
            '#9d9d9d', // Light gray
            '#b8b8b8'  // Very light gray
        ],
        name: 'Executive Burgundy & Gray'
    },

    // 3. FOREST GREEN CORPORATE - Trustworthy and stable
    forestCorporate: {
        colors: [
            '#2d5016', // Deep forest green
            '#3d6b1f', // Forest green
            '#4a7c28', // Medium green
            '#689842', // Lighter green
            '#87b35c', // Light olive
            '#a6c878'  // Pale green
        ],
        name: 'Forest Green Corporate'
    },

    // 4. SLATE & COPPER - Modern yet conservative
    slateCopper: {
        colors: [
            '#334155', // Dark slate
            '#475569', // Medium slate
            '#64748b', // Light slate
            '#94a3b8', // Very light slate
            '#b45309', // Copper
            '#d97706'  // Light copper
        ],
        name: 'Slate & Copper Professional'
    },

    // 5. DEEP BLUE CORPORATE - Traditional and reliable
    deepBlueCorp: {
        colors: [
            '#0f172a', // Very dark blue
            '#1e293b', // Dark blue
            '#334155', // Medium blue-gray
            '#475569', // Lighter blue-gray
            '#64748b', // Light blue-gray
            '#94a3b8'  // Very light blue-gray
        ],
        name: 'Deep Blue Corporate'
    },

    // 6. WARM EARTH TONES - Approachable yet professional
    warmEarth: {
        colors: [
            '#451a03', // Dark brown
            '#78350f', // Rich brown
            '#92400e', // Medium brown
            '#c2410c', // Orange-brown
            '#ea580c', // Light orange
            '#fb923c'  // Pale orange
        ],
        name: 'Warm Earth Professional'
    },

    // UPDATED ORIGINAL SCHEMES with better accessibility:
    
    // Enhanced colors for horizontal bar charts
    horizontalBar: {
        colors: [
            '#1a365d', // Deep navy (high contrast)
            '#722f37', // Deep burgundy  
            '#2d5016', // Deep forest green
            '#451a03', // Dark brown
            '#334155', // Dark slate
            '#0f172a', // Very dark blue
            '#78350f', // Rich brown
            '#3d6b1f'  // Forest green
        ],
        name: 'Horizontal Bar Colors - Corporate'
    },
    
    // Enhanced colors for stacked bar charts
    stackedBar: {
        colors: [
            '#1a365d', // Deep navy
            '#722f37', // Deep burgundy
            '#2d5016', // Deep forest green
            '#334155', // Dark slate
            '#451a03', // Dark brown
            '#78350f', // Rich brown
            '#0f172a'  // Very dark blue
        ],
        name: 'Stacked Bar Colors - Corporate'
    },
    
    // Enhanced colors for vertical bar charts
    verticalBar: {
        colors: [
            '#1a365d', // Deep navy
            '#2d5a87', // Medium navy
            '#4a90b8', // Steel blue
            '#334155', // Dark slate
            '#475569', // Medium slate
            '#64748b'  // Light slate
        ],
        name: 'Vertical Bar Colors - Corporate'
    },
    
    // Enhanced colors for pie charts
    enhancedPie: {
        colors: [
            '#1a365d', // Deep navy
            '#722f37', // Deep burgundy
            '#2d5016', // Deep forest green
            '#451a03', // Dark brown
            '#334155'  // Dark slate
        ],
        name: 'Enhanced Pie Colors - Corporate'
    },
    
    // Enhanced colors for area charts
    area: {
        colors: [
            '#1a365d', '#2d5a87', '#4a90b8', '#722f37', '#8b4513',
            '#2d5016', '#3d6b1f', '#451a03', '#334155', '#475569'
        ],
        gradients: [
            ['#1a365d', '#4a90b8'], ['#722f37', '#a8787e'], ['#2d5016', '#689842'],
            ['#451a03', '#d97706'], ['#334155', '#94a3b8']
        ],
        name: 'Area Chart Colors - Corporate'
    },
    
    // Enhanced colors for line charts
    line: {
        colors: [
            '#1a365d', '#722f37', '#2d5016', '#451a03', '#334155',
            '#78350f', '#0f172a', '#3d6b1f', '#2d5a87', '#8b4513'
        ],
        name: 'Line Chart Colors - Corporate'
    },
    
    // Enhanced colors for multiple bar charts
    multipleBar: {
        colors: [
            '#0f172a', // Very dark blue
            '#1a365d', // Deep navy
            '#2d5a87', // Medium navy
            '#4a90b8', // Steel blue
            '#6ba3d0', // Light steel
            '#8bb8d8', // Very light steel
            '#a8cde8', // Pale steel
            '#dbeafe'  // Very pale blue
        ],
        name: 'Multiple Bar Colors - Corporate'
    },
    
    // Enhanced Sosioekonomi color schemes
    sosioekonomiIncome: {
        colors: [
            '#2d5016', '#3d6b1f', '#4a7c28', '#689842', '#87b35c',
            '#1f5f1f', '#2d7d2d', '#3d8b3d', '#4d9a4d', '#5da85d'
        ],
        name: 'Sosioekonomi Income - Corporate Green'
    },
    
    sosioekonomiFinancing: {
        colors: [
            '#0f172a', '#1a365d', '#2d5a87', '#4a90b8', '#6ba3d0',
            '#1e293b', '#334155', '#475569', '#64748b', '#94a3b8'
        ],
        name: 'Sosioekonomi Financing - Corporate Blue'
    },
    
    sosioekonomiOccupation: {
        colors: [
            '#451a03', '#78350f', '#92400e', '#c2410c', '#ea580c',
            '#fb923c', '#fdba74', '#fed7aa', '#ffedd5', '#451a03',
            '#78350f', '#92400e', '#c2410c'
        ],
        name: 'Sosioekonomi Occupation - Corporate Earth'
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
            maxBarThickness: 50,
            categoryPercentage: 0.95,
            barPercentage: 0.9,
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
            maxBarThickness: 40,
            categoryPercentage: 0.6,
            barPercentage: 0.7
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
            intersect: true,
            mode: 'nearest'
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
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        left: isHorizontal ? 50 : 20,
                        right: 20,
                        top: 20,
                        bottom: 20
                    }
                },
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
                                size: 8,
                                weight: '500',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#1f2937',
                            maxRotation: 0,
                            minRotation: 0,
                            padding: isHorizontal ? 15 : 10,
                            maxTicksLimit: undefined,
                            autoSkip: false
                        },
                        border: {
                            display: false
                        },
                        beforeFit: function(scale) {
                            if (isHorizontal) {
                                scale.width = 800;
                            }
                        },
                        afterFit: function(scale) {
                            if (isHorizontal) {
                                scale.width = 800;
                            }
                        }
                    },
                    ...options.scales
                },
                plugins: {
                    ...ChartConfig.globalOptions.plugins,
                    tooltip: {
                        ...ChartConfig.globalOptions.plugins.tooltip,
                        enabled: true,
                        mode: 'nearest',
                        intersect: true,
                        callbacks: {
                            title: function(context) {
                                if (isHorizontal && context[0]) {
                                    return context[0].label;
                                }
                                return context[0]?.label || '';
                            },
                            label: function (context)
                            {
                                return `${context.dataset.label || 'Nilai'}: ${context.parsed[ isHorizontal ? 'x' : 'y' ].toLocaleString()}`;
                            }
                        }
                    },
                    customLabels: isHorizontal ? {
                        afterDraw: function(chart) {
                            const ctx = chart.ctx;
                            const yScale = chart.scales.y;
                            const originalLabels = chart.data.labels;
                            
                            if (!originalLabels || !yScale) return;
                            
                            // Hide original labels by making them transparent
                            yScale.options.ticks.color = 'transparent';
                            
                            ctx.save();
                            ctx.font = '9px Inter, sans-serif';
                            ctx.fillStyle = '#1f2937';
                            ctx.textAlign = 'right';
                            ctx.textBaseline = 'middle';
                            
                            originalLabels.forEach((label, index) => {
                                const y = yScale.getPixelForValue(index);
                                const x = yScale.left - 20;
                                
                                // Draw full text without truncation
                                ctx.fillText(label.toString(), x, y);
                            });
                            
                            ctx.restore();
                        }
                    } : {},
                    ...options.plugins
                },
                interaction: {
                    intersect: true,
                    mode: 'nearest'
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
                            padding: 15,
                            font: {
                                size: 9,
                                weight: '500',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#374151',
                            boxWidth: 10,
                            boxHeight: 10,
                            maxWidth: 180,

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

        // Check if this is a horizontal stacked bar with multiple datasets
        // Disabled: Use standard stacked bar chart instead
        // if (isHorizontal && data.datasets.length > 1) {
        //     return this.createMultipleStackedHorizontalBarChart(ctx, enhancedData, options);
        // }

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
                    customStackedLabels: isHorizontal ? {
                        id: 'customStackedLabels',
                        afterDatasetsDraw(chart) {
                            const { ctx: canvasCtx, scales: { y: yScale }, data } = chart;
                            
                            if (!yScale) return;
                            
                            canvasCtx.save();
                            canvasCtx.font = '8px Inter, sans-serif';
                            canvasCtx.fillStyle = '#1f2937';
                            canvasCtx.textAlign = 'right';
                            canvasCtx.textBaseline = 'middle';
                            
                            const maxWidth = 170;
                            const lineHeight = 12;
                            
                            data.labels.forEach((label, index) => {
                                const y = yScale.getPixelForValue(index);
                                const x = yScale.left - 10;
                                
                                // Wrap text to multiple lines
                                const words = label.toString().split(' ');
                                let lines = [];
                                let currentLine = '';
                                
                                words.forEach(word => {
                                    const testLine = currentLine ? currentLine + ' ' + word : word;
                                    const metrics = canvasCtx.measureText(testLine);
                                    
                                    if (metrics.width > maxWidth && currentLine) {
                                        lines.push(currentLine);
                                        currentLine = word;
                                    } else {
                                        currentLine = testLine;
                                    }
                                });
                                
                                if (currentLine) {
                                    lines.push(currentLine);
                                }
                                
                                // Draw wrapped text
                                const totalHeight = lines.length * lineHeight;
                                let startY = y - (totalHeight / 2);
                                
                                lines.forEach((line, lineIndex) => {
                                    canvasCtx.fillText(line, x, startY + (lineIndex * lineHeight));
                                });
                            });
                            
                            canvasCtx.restore();
                        }
                    } : {},
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
                                size: 7,
                                weight: '600',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#1f2937',
                            maxRotation: 0,
                            minRotation: 0,
                            padding: 10,
                            align: 'end',
                            autoSkip: false
                        },
                        border: {
                            display: false
                        },
                        afterFit: function(scale) {
                            if (isHorizontal) {
                                scale.width = 280;
                            }
                        }
                    },
                    ...options.scales
                }
            }
        });
    }

    // NEW: Multiple Stacked Horizontal Bar Chart (for charts with multiple datasets)
    static createMultipleStackedHorizontalBarChart(ctx, data, options = {})
    {
        return new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                ...ChartConfig.globalOptions,
                responsive: true,
                indexAxis: 'y',
                layout: {
                    padding: {
                        left: 250,
                        right: 20,
                        top: 20,
                        bottom: 20
                    }
                },
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
                                return `${context.dataset.label}: ${context.parsed.x.toLocaleString()}`;
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
                                const percentage = ((context.parsed.x / total) * 100).toFixed(1);
                                return `Peratus: ${percentage}%`;
                            }
                        }
                    },
                    ...options.plugins
                },
                scales: {
                    x: {
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
                    y: {
                        stacked: true,
                        grid: { display: false },
                        ticks: {
                            font: {
                                size: 9,
                                weight: '600',
                                family: "'Inter', 'Segoe UI', sans-serif"
                            },
                            color: '#1f2937',
                            maxRotation: 0,
                            minRotation: 0,
                            padding: 15,
                            align: 'end'
                        },
                        border: {
                            display: false
                        },
                        afterFit: function(scale) {
                            scale.width = 250;
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