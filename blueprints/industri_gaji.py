from flask import Blueprint, render_template, request, jsonify, send_file
from models.data_processor import DataProcessor, load_excel_data
import io
import os
import pandas as pd
from collections import Counter
import numpy as np

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
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6B7280'],
                    'borderWidth': 0,
                    'hoverBackgroundColor': ['#6B7280']
                }]
            })
        
        data = filtered_processor.get_chart_data('pie', employment_column)
        return jsonify(data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'labels': ['Error Loading Data'],
            'datasets': [{
                'data': [1],
                'backgroundColor': ['#DC2626'],
                'borderWidth': 0
            }]
        }), 500

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
            return jsonify({
                'labels': ['No working respondents'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': '#6b7280',
                    'borderColor': '#374151',
                    'borderWidth': 2,
                    'borderRadius': 8
                }]
            })
        
        job_status_col = 'Apakah status pekerjaan anda sekarang?'
        if job_status_col not in working_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': '#6b7280',
                    'borderColor': '#374151',
                    'borderWidth': 2,
                    'borderRadius': 8
                }]
            })
        
        # Let your processor handle the chart creation
        filtered_processor.filtered_df = working_df
        data = filtered_processor.get_chart_data('bar', job_status_col)
        return jsonify(data)
        
    except Exception as e:
        print(f"Error in api_job_types: {str(e)}")
        return jsonify({
            'error': str(e),
            'labels': ['Error Loading Data'],
            'datasets': [{
                'data': [1],
                'backgroundColor': '#ef4444',
                'borderColor': '#dc2626',
                'borderWidth': 2,
                'borderRadius': 8
            }]
        }), 500

@industri_gaji_bp.route('/api/salary-distribution')
def api_salary_distribution():
    """Get salary distribution data - using time to employment as proxy"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        time_col = 'Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?'
        
        if time_col not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Salary Range',
                    'data': [1],
                    'backgroundColor': 'rgba(31, 41, 55, 0.1)',
                    'borderColor': '#1F2937',
                    'borderWidth': 2,
                    'fill': True
                }]
            })
        
        tempoh_counts = filtered_processor.filtered_df[time_col].value_counts().sort_index()
        labels = tempoh_counts.index.tolist()
        
        # Mock salary data based on employment timing (for demo purposes)
        # In real implementation, use actual salary columns
        salary_data = []
        for i, label in enumerate(labels):
            base_salary = 3000 + (i * 500)  # Mock progression
            salary_data.append(base_salary)
        
        chart_data = {
            'labels': labels,
            'datasets': [{
                'label': 'Average Salary (RM)',
                'data': salary_data,
                'backgroundColor': 'rgba(31, 41, 55, 0.1)',
                'borderColor': '#1F2937',
                'borderWidth': 2,
                'fill': True,
                'tension': 0.4,
                'pointBackgroundColor': '#1F2937',
                'pointBorderColor': '#1F2937',
                'pointBorderWidth': 2,
                'pointRadius': 4
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'labels': ['Error Loading Data'],
            'datasets': [{
                'label': 'Error',
                'data': [1],
                'backgroundColor': 'rgba(220, 38, 38, 0.1)',
                'borderColor': '#DC2626',
                'borderWidth': 2,
                'fill': True
            }]
        }), 500

@industri_gaji_bp.route('/api/job-finding-factors')
def api_job_finding_factors():
    """Get job finding factors with salary correlation (stacked bar)"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        factors_column = 'Apakah faktor utama yang membantu anda mendapat pekerjaan tersebut?'
        
        if factors_column not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1],
                    'backgroundColor': '#6B7280',
                    'borderWidth': 0
                }]
            })
        
        df_copy = filtered_processor.filtered_df.copy()
        df_copy['Faktor_Pekerjaan_Grouped'] = df_copy[factors_column].apply(group_job_factors)
        
        split_factors = df_copy['Faktor_Pekerjaan_Grouped'].dropna().apply(
            lambda x: [i.strip() for i in str(x).split(';') if i.strip()]
        )
        
        all_factors = [item for sublist in split_factors for item in sublist if item]
        factor_counts = pd.Series(Counter(all_factors)).sort_values(ascending=False)
        
        if factor_counts.empty:
            return jsonify({
                'labels': ['No Factors Available'],
                'datasets': [{
                    'label': 'Count',
                    'data': [1],
                    'backgroundColor': '#6B7280',
                    'borderWidth': 0
                }]
            })
        
        labels = factor_counts.index.tolist()
        values = factor_counts.values.tolist()
        
        # Mock salary ranges for different job finding methods
        entry_level = [v * 0.4 for v in values]  # 40% entry level
        mid_level = [v * 0.4 for v in values]    # 40% mid level  
        senior_level = [v * 0.2 for v in values] # 20% senior level
        
        chart_data = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Entry Level (RM 2,000-3,500)',
                    'data': entry_level,
                    'backgroundColor': '#6B7280',
                    'borderWidth': 0
                },
                {
                    'label': 'Mid Level (RM 3,500-6,000)', 
                    'data': mid_level,
                    'backgroundColor': '#374151',
                    'borderWidth': 0
                },
                {
                    'label': 'Senior Level (RM 6,000+)',
                    'data': senior_level,
                    'backgroundColor': '#1F2937',
                    'borderWidth': 0
                }
            ]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'labels': ['Error Loading Data'],
            'datasets': [{
                'label': 'Error',
                'data': [1],
                'backgroundColor': '#DC2626',
                'borderWidth': 0
            }]
        }), 500

@industri_gaji_bp.route('/api/current-job-types')
def api_current_job_types():
    """Get current job types distribution"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        job_type_column = 'Apakah jenis pekerjaan anda sekarang'
        
        if job_type_column not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Respondents',
                    'data': [1],
                    'backgroundColor': '#6B7280',
                    'borderColor': '#6B7280',
                    'borderWidth': 0
                }]
            })
        
        pekerjaan_counts = filtered_processor.filtered_df[job_type_column].value_counts()
        labels = pekerjaan_counts.index.tolist()
        values = pekerjaan_counts.values.tolist()
        
        chart_data = {
            'labels': labels,
            'datasets': [{
                'label': 'Number of Respondents',
                'data': values,
                'backgroundColor': '#1F2937',
                'borderColor': '#1F2937',
                'borderWidth': 0,
                'borderRadius': 4
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'labels': ['Error Loading Data'],
            'datasets': [{
                'label': 'Error',
                'data': [1],
                'backgroundColor': '#DC2626',
                'borderColor': '#DC2626',
                'borderWidth': 0
            }]
        }), 500

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