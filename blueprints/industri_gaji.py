from flask import Blueprint, render_template, request, jsonify, send_file
from models.data_processor import DataProcessor, load_excel_data
import io
import os
import pandas as pd
from collections import Counter
import numpy as np

# Global Color Palette Configuration
class ColorPalette:
    """Centralized color palette management for consistent theming across charts"""
    
    # Primary color scheme for general charts
    PRIMARY = [
        '#2066a8',  # Dark Blue
        '#3594cc',  # Med Blue  
        '#8cc5e3',  # Light Blue
        '#a00000',  # Dark Red
        '#c46666',  # Med Red
        '#d8a6a6'   # Light Red
    ]
    
    # Extended palette for pie charts and complex visualizations
    EXTENDED = [
        '#296899',
        '#274754', 
        '#cc7700',
        '#e8c468',
        '#ba454d',
        '#2066a8',
        '#cdecec',
        '#8eclda',
        '#f6d6c2',
        '#ededed',
        '#d47264',
        '#ae282c'
    ]
    
    # Secondary/Accent colors (red scheme)
    SECONDARY = {
        50: '#fef2f2',
        100: '#fde2e2', 
        200: '#fbc6c6',
        300: '#f59898',
        400: '#ee6b6b',
        500: '#c92427',  # Main secondary
        600: '#b91c1c',
        700: '#991b1b',
        800: '#7f1d1d',
        900: '#651515'
    }
    
    # Neutral colors for backgrounds and borders
    NEUTRAL = [
        '#374151', '#6b7280', '#9ca3af', '#d1d5db',
        '#e5e7eb', '#f3f4f6', '#f9fafb'
    ]
    
    # Status colors
    STATUS = {
        'success': '#059669',
        'warning': '#d97706', 
        'danger': '#c92427',
        'info': '#2066a8'
    }
    
    @classmethod
    def get_colors(cls, chart_type='primary', count=8):
        """Get colors based on chart type and required count"""
        if chart_type == 'pie' or chart_type == 'doughnut':
            colors = cls.EXTENDED.copy()
        elif chart_type == 'secondary':
            colors = [cls.SECONDARY[key] for key in [200, 300, 400, 500, 600, 700, 800, 900]]
        else:  # primary or default
            colors = cls.PRIMARY.copy()
        
        # Extend colors if needed
        while len(colors) < count:
            colors.extend(cls.EXTENDED)
        
        return colors[:count]
    
    @classmethod
    def get_gradient_colors(cls, start_color, end_color, steps):
        """Generate gradient colors between two hex colors"""
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        
        start_rgb = hex_to_rgb(start_color)
        end_rgb = hex_to_rgb(end_color)
        
        colors = []
        for i in range(steps):
            factor = i / (steps - 1) if steps > 1 else 0
            rgb = tuple(
                start_rgb[j] + factor * (end_rgb[j] - start_rgb[j])
                for j in range(3)
            )
            colors.append(rgb_to_hex(rgb))
        
        return colors

industri_gaji_bp = Blueprint('industri_gaji', __name__)

# Load data from Excel file
EXCEL_FILE_PATH = 'data/Questionnaire.xlsx'
df = load_excel_data(EXCEL_FILE_PATH)
data_processor = DataProcessor(df)

# Job factor grouping mapping
JOB_FACTOR_GROUPING = {
    'Permohonan terus kepada syarikat (JobStreet, LinkedIn, laman web syarikat)': 'Saluran Rasmi',
    'Program kerajaan (contoh: MySTEP, Protege, SL1M)': 'Saluran Rasmi',
    'Melalui pameran kerjaya atau job fair': 'Saluran Rasmi',
    'Rangkaian peribadi / kenalan (pensyarah, alumni, keluarga, rakan)': 'Saluran Informal / Sosial',
    'Dihubungi oleh perekrut atau headhunter': 'Saluran Informal / Sosial',
    'Melalui latihan industri / praktikal': 'Laluan Berasaskan Institusi Pendidikan',
    'Tawaran daripada syarikat sebelum tamat pengajian': 'Laluan Berasaskan Institusi Pendidikan',
    'Memulakan perniagaan sendiri / bekerja dalam ekonomi gig': 'Laluan Kendiri / Keusahawanan'
}

def group_job_factors(cell):
    """Group job finding factors according to mapping"""
    if pd.isnull(cell):
        return ''
    raw_factors = [x.strip() for x in str(cell).split(';')]
    mapped = [JOB_FACTOR_GROUPING.get(factor, factor) for factor in raw_factors]
    return '; '.join(dict.fromkeys(mapped))

def create_chart_data(chart_type, labels, values, dataset_label='Data'):
    """Create standardized chart data with consistent color scheme"""
    color_count = len(labels) if labels else len(values) if isinstance(values, list) else 1
    colors = ColorPalette.get_colors(chart_type, color_count)
    
    if chart_type in ['pie', 'doughnut']:
        return {
            'labels': labels,
            'datasets': [{
                'data': values,
                'backgroundColor': colors,
                'borderColor': '#ffffff',
                'borderWidth': 3,
                'hoverBorderWidth': 4,
                'hoverOffset': 8
            }]
        }
    elif chart_type == 'bar':
        return {
            'labels': labels,
            'datasets': [{
                'label': dataset_label,
                'data': values,
                'backgroundColor': colors,
                'borderColor': colors,
                'borderWidth': 0,
                'borderRadius': 8,
                'borderSkipped': False
            }]
        }
    elif chart_type == 'line':
        return {
            'labels': labels,
            'datasets': [{
                'label': dataset_label,
                'data': values,
                'backgroundColor': f'{colors[0]}20',  # 20% opacity
                'borderColor': colors[0],
                'borderWidth': 3,
                'tension': 0.4,
                'fill': False,
                'pointBackgroundColor': '#ffffff',
                'pointBorderColor': colors[0],
                'pointBorderWidth': 2,
                'pointRadius': 4
            }]
        }
    else:
        return {
            'labels': labels,
            'datasets': [{
                'label': dataset_label,
                'data': values,
                'backgroundColor': colors,
                'borderColor': colors,
                'borderWidth': 1
            }]
        }

def create_stacked_chart_data(labels, datasets_info):
    """Create stacked chart data with consistent color scheme"""
    colors = ColorPalette.get_colors('primary', len(datasets_info))
    
    datasets = []
    for i, (label, data) in enumerate(datasets_info):
        datasets.append({
            'label': label,
            'data': data,
            'backgroundColor': colors[i % len(colors)],
            'borderColor': colors[i % len(colors)],
            'borderWidth': 0,
            'borderRadius': 6,
            'borderSkipped': False
        })
    
    return {
        'labels': labels,
        'datasets': datasets
    }

@industri_gaji_bp.route('/')
def index():
    """Main industri gaji dashboard page"""
    return render_template('industri_gaji.html')

@industri_gaji_bp.route('/table')
def table_view():
    """Table view for industri gaji data"""
    return render_template('data_table.html', 
                         page_title='Employment & Industry Data Table',
                         api_endpoint='/industri-gaji/api/table-data')

@industri_gaji_bp.route('/api/summary')
def api_summary():
    """Get summary statistics"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        total_records = len(filtered_df)
        
        if total_records == 0:
            return jsonify({
                'total_records': 0,
                'full_time_employment_rate': 0,
                'private_sector_rate': 0,
                'quick_employment_rate': 0,
                'average_salary': 0
            })
        
        # Employment Rate Analysis
        employment_col = 'Adakah anda kini bekerja?'
        employment_stats = {}
        
        if employment_col in filtered_df.columns:
            employment_counts = filtered_df[employment_col].value_counts()
            total_employment = employment_counts.sum()
            
            full_time_count = 0
            for status, count in employment_counts.items():
                if 'sepenuh masa' in str(status).lower():
                    full_time_count += count
            
            employment_stats['full_time_employment_rate'] = round((full_time_count / total_employment) * 100, 1) if total_employment > 0 else 0
        
        # Private Sector Analysis
        job_status_col = 'Apakah status pekerjaan anda sekarang?'
        private_sector_rate = 0
        
        df_working = filtered_df[filtered_df[employment_col].isin(['Ya, bekerja sepenuh masa', 'Ya, bekerja separuh masa'])].copy()
        
        if not df_working.empty and job_status_col in df_working.columns:
            job_status_counts = df_working[job_status_col].value_counts()
            total_working = job_status_counts.sum()
            
            private_count = 0
            for status, count in job_status_counts.items():
                if any(word in str(status).lower() for word in ['swasta', 'private']):
                    private_count += count
            
            private_sector_rate = round((private_count / total_working) * 100, 1) if total_working > 0 else 0
        
        # Quick Employment Analysis
        time_col = 'Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?'
        quick_employment_rate = 0
        
        if time_col in filtered_df.columns:
            time_counts = filtered_df[time_col].value_counts()
            total_time_responses = time_counts.sum()
            
            quick_count = 0
            for time_period, count in time_counts.items():
                time_str = str(time_period).lower()
                if any(word in time_str for word in ['sebelum', 'before', '1 bulan', '2 bulan', '3 bulan', 'kurang']):
                    quick_count += count
            
            quick_employment_rate = round((quick_count / total_time_responses) * 100, 1) if total_time_responses > 0 else 0
        
        # Average Salary (mock calculation - adjust based on your salary columns)
        average_salary = 4500  # Default placeholder
        
        return jsonify({
            'total_records': total_records,
            'full_time_employment_rate': employment_stats.get('full_time_employment_rate', 0),
            'private_sector_rate': private_sector_rate,
            'quick_employment_rate': quick_employment_rate,
            'average_salary': average_salary
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'total_records': 0,
            'full_time_employment_rate': 0,
            'private_sector_rate': 0,
            'quick_employment_rate': 0,
            'average_salary': 0
        }), 500

@industri_gaji_bp.route('/api/employment-status')
def api_employment_status():
    """Get employment status pie chart data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        employment_column = 'Adakah anda kini bekerja?'
        if employment_column not in filtered_processor.filtered_df.columns:
            return jsonify(create_chart_data('pie', ['No Data Available'], [1]))
        
        employment_counts = filtered_processor.filtered_df[employment_column].value_counts()
        labels = employment_counts.index.tolist()
        values = employment_counts.values.tolist()
        
        return jsonify(create_chart_data('pie', labels, values))
        
    except Exception as e:
        return jsonify(create_chart_data('pie', ['Error Loading Data'], [1])), 500

@industri_gaji_bp.route('/api/job-types')
def api_job_types():
    """Get current job types bar chart"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        employment_col = 'Adakah anda kini bekerja?'
        working_df = filtered_processor.filtered_df[
            filtered_processor.filtered_df[employment_col].isin([
                'Ya, bekerja sepenuh masa',
                'Ya, bekerja separuh masa'
            ])
        ]
        
        if working_df.empty:
            return jsonify(create_chart_data('bar', ['No working respondents'], [1], 'Respondents'))
        
        job_status_col = 'Apakah status pekerjaan anda sekarang?'
        if job_status_col not in working_df.columns:
            return jsonify(create_chart_data('bar', ['No Data Available'], [1], 'Respondents'))
        
        job_counts = working_df[job_status_col].value_counts()
        labels = job_counts.index.tolist()
        values = job_counts.values.tolist()
        
        return jsonify(create_chart_data('bar', labels, values, 'Number of Employees'))
        
    except Exception as e:
        print(f"Error in api_job_types: {str(e)}")
        return jsonify(create_chart_data('bar', ['Error Loading Data'], [1], 'Error')), 500

@industri_gaji_bp.route('/api/salary-distribution')
def api_salary_distribution():
    """Get salary distribution data - using time to employment as proxy"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        time_col = 'Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?'
        
        if time_col not in filtered_processor.filtered_df.columns:
            return jsonify(create_chart_data('line', ['No Data Available'], [1], 'Salary Range'))
        
        tempoh_counts = filtered_processor.filtered_df[time_col].value_counts().sort_index()
        labels = tempoh_counts.index.tolist()
        
        # Mock salary data based on employment timing (for demo purposes)
        # In real implementation, use actual salary columns
        salary_data = []
        for i, label in enumerate(labels):
            base_salary = 3000 + (i * 500)  # Mock progression
            salary_data.append(base_salary)
        
        return jsonify(create_chart_data('line', labels, salary_data, 'Average Salary (RM)'))
        
    except Exception as e:
        return jsonify(create_chart_data('line', ['Error Loading Data'], [1], 'Error')), 500

@industri_gaji_bp.route('/api/job-finding-factors')
def api_job_finding_factors():
    """Get job finding factors with salary correlation (stacked bar)"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        factors_column = 'Apakah faktor utama yang membantu anda mendapat pekerjaan tersebut?'
        
        if factors_column not in filtered_processor.filtered_df.columns:
            return jsonify(create_chart_data('bar', ['No Data Available'], [1], 'No Data'))
        
        df_copy = filtered_processor.filtered_df.copy()
        df_copy['Faktor_Pekerjaan_Grouped'] = df_copy[factors_column].apply(group_job_factors)
        
        split_factors = df_copy['Faktor_Pekerjaan_Grouped'].dropna().apply(
            lambda x: [i.strip() for i in str(x).split(';') if i.strip()]
        )
        
        all_factors = [item for sublist in split_factors for item in sublist if item]
        factor_counts = pd.Series(Counter(all_factors)).sort_values(ascending=False)
        
        if factor_counts.empty:
            return jsonify(create_chart_data('bar', ['No Factors Available'], [1], 'Count'))
        
        labels = factor_counts.index.tolist()
        values = factor_counts.values.tolist()
        
        # Mock salary ranges for different job finding methods
        entry_level = [v * 0.4 for v in values]  # 40% entry level
        mid_level = [v * 0.4 for v in values]    # 40% mid level  
        senior_level = [v * 0.2 for v in values] # 20% senior level
        
        datasets_info = [
            ('Entry Level (RM 2,000-3,500)', entry_level),
            ('Mid Level (RM 3,500-6,000)', mid_level),
            ('Senior Level (RM 6,000+)', senior_level)
        ]
        
        return jsonify(create_stacked_chart_data(labels, datasets_info))
        
    except Exception as e:
        return jsonify(create_chart_data('bar', ['Error Loading Data'], [1], 'Error')), 500

@industri_gaji_bp.route('/api/current-job-types')
def api_current_job_types():
    """Get current job types distribution"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        job_type_column = 'Apakah jenis pekerjaan anda sekarang'
        
        if job_type_column not in filtered_processor.filtered_df.columns:
            return jsonify(create_chart_data('bar', ['No Data Available'], [1], 'Respondents'))
        
        pekerjaan_counts = filtered_processor.filtered_df[job_type_column].value_counts()
        labels = pekerjaan_counts.index.tolist()
        values = pekerjaan_counts.values.tolist()
        
        return jsonify(create_chart_data('bar', labels, values, 'Number of Respondents'))
        
    except Exception as e:
        return jsonify(create_chart_data('bar', ['Error Loading Data'], [1], 'Error')), 500

# Keep existing table data, export, and filter routes unchanged
@industri_gaji_bp.route('/api/table-data')
def api_table_data():
    """Get paginated table data for industri gaji"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() 
                   if k not in ['page', 'per_page', 'search']}
        filtered_processor = data_processor.apply_filters(filters)
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        
        relevant_columns = [
            'Adakah anda kini bekerja?',
            'Apakah status pekerjaan anda sekarang?',
            'Apakah jenis pekerjaan anda sekarang',
            'Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?',
            'Apakah faktor utama yang membantu anda mendapat pekerjaan tersebut?',
            'Tahun graduasi anda?',
            'Jantina anda?'
        ]
        
        salary_columns = [col for col in filtered_processor.filtered_df.columns 
                         if any(keyword in col.lower() for keyword in ['gaji', 'salary', 'pendapatan kerja'])]
        relevant_columns.extend(salary_columns)
        
        available_columns = [col for col in relevant_columns if col in filtered_processor.filtered_df.columns]
        
        data = filtered_processor.get_table_data(page, per_page, search, available_columns)
        return jsonify(data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'data': [],
            'pagination': {'page': 1, 'per_page': 50, 'total': 0, 'pages': 0},
            'columns': []
        }), 500

@industri_gaji_bp.route('/api/export/<format>')
def api_export(format):
    """Export industri gaji data in various formats"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        relevant_columns = [
            'Timestamp',
            'Adakah anda kini bekerja?',
            'Apakah status pekerjaan anda sekarang?',
            'Apakah jenis pekerjaan anda sekarang',
            'Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?',
            'Apakah faktor utama yang membantu anda mendapat pekerjaan tersebut?',
            'Adakah pekerjaan anda berkaitan dengan bidang pengajian anda?',
            'Jika tidak berkaitan, mengapa anda memilih pekerjaan tersebut?',
            'Adakah anda berpuas hati dengan pekerjaan semasa?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Umur anda?',
            'Institusi pendidikan MARA yang anda hadiri?'
        ]
        
        salary_columns = [col for col in filtered_processor.filtered_df.columns 
                         if any(keyword in col.lower() for keyword in ['gaji', 'salary', 'pendapatan kerja'])]
        relevant_columns.extend(salary_columns)
        
        available_columns = [col for col in relevant_columns if col in filtered_processor.filtered_df.columns]
        
        data = filtered_processor.export_data(format, available_columns)
        
        if format == 'csv':
            mimetype = 'text/csv'
            filename = 'employment_analytics_data.csv'
        elif format == 'excel':
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = 'employment_analytics_data.xlsx'
        else:
            mimetype = 'application/json'
            filename = 'employment_analytics_data.json'
        
        return send_file(
            io.BytesIO(data),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@industri_gaji_bp.route('/api/filters/available')
def api_available_filters():
    """Get available filter options for industri gaji data"""
    try:
        sample_df = data_processor.df
        filters = {}
        
        filter_columns = [
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Adakah anda kini bekerja?',
            'Apakah status pekerjaan anda sekarang?',
            'Apakah jenis pekerjaan anda sekarang',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?'
        ]
        
        salary_columns = [col for col in sample_df.columns 
                         if any(keyword in col.lower() for keyword in ['gaji', 'salary', 'pendapatan kerja'])]
        filter_columns.extend(salary_columns)
        
        for column in filter_columns:
            if column in sample_df.columns:
                unique_values = sample_df[column].dropna().unique().tolist()
                if isinstance(unique_values[0] if unique_values else None, (int, float)):
                    unique_values = sorted(unique_values)
                else:
                    unique_values = sorted([str(val) for val in unique_values])
                filters[column] = unique_values
        
        return jsonify(filters)
        
    except Exception as e:
        return jsonify({'error': str(e), 'filters': {}}), 500

# Color palette endpoint for frontend synchronization
@industri_gaji_bp.route('/api/color-palette')
def api_color_palette():
    """Get the current color palette configuration"""
    return jsonify({
        'primary': ColorPalette.PRIMARY,
        'extended': ColorPalette.EXTENDED,
        'secondary': ColorPalette.SECONDARY,
        'neutral': ColorPalette.NEUTRAL,
        'status': ColorPalette.STATUS
    })