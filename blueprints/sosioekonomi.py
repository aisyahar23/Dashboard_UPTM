from flask import Blueprint, render_template, request, jsonify, send_file
from models.data_processor import DataProcessor, load_excel_data
import io
import os
import pandas as pd

sosioekonomi_bp = Blueprint('sosioekonomi', __name__)

# Load data from Excel file
EXCEL_FILE_PATH = 'data/Questionnaire.xlsx'
df = load_excel_data(EXCEL_FILE_PATH)
data_processor = DataProcessor(df)

@sosioekonomi_bp.route('/')
def index():
    """Main sosioekonomi dashboard page"""
    return render_template('sosioekonomi.html')

@sosioekonomi_bp.route('/table')
def table_view():
    """Table view for sosioekonomi data"""
    return render_template('data_table.html', 
                         page_title='Sosioekonomi Data Table',
                         api_endpoint='/sosioekonomi/api/table-data')

@sosioekonomi_bp.route('/api/summary')
def api_summary():
    """Get summary statistics for sosioekonomi data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        stats = filtered_processor.get_summary_stats()
        filtered_df = filtered_processor.filtered_df
        
        total_records = len(filtered_df)
        
        # Calculate real KPIs from actual data
        financing_stats = {}
        income_stats = {}
        parent_employment = {}
        
        if total_records > 0:
            # Financing method analysis
            if 'Bagaimana anda membiayai pendidikan anda?' in filtered_df.columns:
                financing_counts = filtered_df['Bagaimana anda membiayai pendidikan anda?'].value_counts()
                total_financing = financing_counts.sum()
                
                for method, count in financing_counts.items():
                    method_lower = str(method).lower()
                    percentage = (count / total_financing) * 100 if total_financing > 0 else 0
                    
                    if any(word in method_lower for word in ['biasiswa', 'scholarship', 'grant']):
                        financing_stats['scholarship'] = financing_stats.get('scholarship', 0) + percentage
                    elif any(word in method_lower for word in ['pinjaman', 'loan', 'ptptn']):
                        financing_stats['loan'] = financing_stats.get('loan', 0) + percentage
                    elif any(word in method_lower for word in ['keluarga', 'family', 'parents', 'ibu bapa']):
                        financing_stats['family'] = financing_stats.get('family', 0) + percentage
                    elif any(word in method_lower for word in ['sendiri', 'self', 'own']):
                        financing_stats['self'] = financing_stats.get('self', 0) + percentage
            
            # Income analysis
            if 'Pendapatan isi rumah bulanan keluarga anda?' in filtered_df.columns:
                income_counts = filtered_df['Pendapatan isi rumah bulanan keluarga anda?'].value_counts()
                most_common_income = income_counts.index[0] if len(income_counts) > 0 else 'N/A'
                
                # Categorize income levels
                high_income_count = 0
                medium_income_count = 0
                low_income_count = 0
                
                for income, count in income_counts.items():
                    income_str = str(income).lower()
                    if any(num in income_str for num in ['6000', '7000', '8000', '9000', '10000']):
                        high_income_count += count
                    elif any(num in income_str for num in ['4000', '5000']):
                        medium_income_count += count
                    else:
                        low_income_count += count
                
                income_stats = {
                    'high_income_rate': (high_income_count / total_records) * 100,
                    'medium_income_rate': (medium_income_count / total_records) * 100,
                    'low_income_rate': (low_income_count / total_records) * 100,
                    'most_common': most_common_income
                }
            
            # Parent employment analysis
            father_employed = 0
            mother_employed = 0
            
            if 'Pekerjaan bapa anda' in filtered_df.columns:
                father_jobs = filtered_df['Pekerjaan bapa anda'].value_counts()
                for job, count in father_jobs.items():
                    job_lower = str(job).lower()
                    if not any(word in job_lower for word in ['pencen', 'retired', 'tiada', 'none', 'meninggal']):
                        father_employed += count
            
            if 'Pekerjaan ibu anda?' in filtered_df.columns:
                mother_jobs = filtered_df['Pekerjaan ibu anda?'].value_counts()
                for job, count in mother_jobs.items():
                    job_lower = str(job).lower()
                    if not any(word in job_lower for word in ['suri rumah', 'housewife', 'pencen', 'retired', 'tiada', 'none', 'meninggal']):
                        mother_employed += count
            
            parent_employment = {
                'father_employment_rate': (father_employed / total_records) * 100,
                'mother_employment_rate': (mother_employed / total_records) * 100,
                'dual_income_potential': min((father_employed / total_records) * 100, (mother_employed / total_records) * 100)
            }
        
        # Update stats with real calculations
        stats.update({
            'total_records': total_records,
            'scholarship_rate': round(financing_stats.get('scholarship', 0), 1),
            'loan_rate': round(financing_stats.get('loan', 0), 1),
            'family_funding_rate': round(financing_stats.get('family', 0), 1),
            'self_funding_rate': round(financing_stats.get('self', 0), 1),
            'high_income_families': round(income_stats.get('high_income_rate', 0), 1),
            'medium_income_families': round(income_stats.get('medium_income_rate', 0), 1),
            'low_income_families': round(income_stats.get('low_income_rate', 0), 1),
            'most_common_income': income_stats.get('most_common', 'N/A'),
            'father_employment_rate': round(parent_employment.get('father_employment_rate', 0), 1),
            'mother_employment_rate': round(parent_employment.get('mother_employment_rate', 0), 1)
        })
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'total_records': 0,
            'scholarship_rate': 0,
            'loan_rate': 0,
            'family_funding_rate': 0,
            'self_funding_rate': 0
        }), 500

@sosioekonomi_bp.route('/api/income-distribution')
def api_income_distribution():
    """Get household income distribution data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        income_column = 'Pendapatan isi rumah bulanan keluarga anda?'
        if income_column not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 2,
                    'borderRadius': 8
                }]
            })
        
        data = filtered_processor.get_chart_data('bar', income_column)
        return jsonify(data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'labels': ['Error Loading Data'],
            'datasets': [{
                'data': [1],
                'backgroundColor': ['#ef4444'],
                'borderColor': '#dc2626',
                'borderWidth': 2,
                'borderRadius': 8
            }]
        }), 500

@sosioekonomi_bp.route('/api/financing-methods')
def api_financing_methods():
    """Get education financing methods data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        financing_column = 'Bagaimana anda membiayai pendidikan anda?'
        if financing_column not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderWidth': 3,
                    'borderColor': '#ffffff'
                }]
            })
        
        data = filtered_processor.get_chart_data('pie', financing_column)
        return jsonify(data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'labels': ['Error Loading Data'],
            'datasets': [{
                'data': [1],
                'backgroundColor': ['#ef4444'],
                'borderWidth': 3,
                'borderColor': '#ffffff'
            }]
        }), 500

@sosioekonomi_bp.route('/api/parent-occupation')
def api_parent_occupation():
    """Get parent occupation distribution"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        income_column = 'Pendapatan isi rumah bulanan keluarga anda?'
        father_column = 'Pekerjaan bapa anda'
        
        if income_column not in filtered_processor.filtered_df.columns or father_column not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1],
                    'backgroundColor': '#6b7280',
                    'borderWidth': 0
                }]
            })
        
        data = filtered_processor.get_chart_data('stacked_bar', income_column, group_by=father_column)
        return jsonify(data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'labels': ['Error Loading Data'],
            'datasets': [{
                'label': 'Error',
                'data': [1],
                'backgroundColor': '#ef4444',
                'borderWidth': 0
            }]
        }), 500

@sosioekonomi_bp.route('/api/table-data')
def api_table_data():
    """Get paginated table data for sosioekonomi"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() 
                   if k not in ['page', 'per_page', 'search']}
        filtered_processor = data_processor.apply_filters(filters)
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        
        # Define relevant columns for sosioekonomi
        relevant_columns = [
            'Pendapatan isi rumah bulanan keluarga anda?',
            'Pekerjaan bapa anda',
            'Pekerjaan ibu anda?',
            'Bagaimana anda membiayai pendidikan anda?',
            'Tahun graduasi anda?',
            'Jantina anda?'
        ]
        
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

@sosioekonomi_bp.route('/api/export')
def api_export():
    """Export sosioekonomi data in various formats"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() if k != 'format'}
        filtered_processor = data_processor.apply_filters(filters)
        
        format_type = request.args.get('format', 'csv')
        
        relevant_columns = [
            'Timestamp',
            'Pendapatan isi rumah bulanan keluarga anda?',
            'Pekerjaan bapa anda',
            'Pekerjaan ibu anda?',
            'Bagaimana anda membiayai pendidikan anda?',
            'Adakah jenis pembiayaan ini memberi kelebihan dalam mencari kerja?',
            'Jika anda mempunyai pinjaman pendidikan, adakah beban hutang mempengaruhi pilihan kerjaya anda?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Umur anda?'
        ]
        
        available_columns = [col for col in relevant_columns if col in filtered_processor.filtered_df.columns]
        
        data = filtered_processor.export_data(format_type, available_columns)
        
        if format_type == 'csv':
            mimetype = 'text/csv'
            filename = 'sosioekonomi_data.csv'
        elif format_type == 'excel':
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = 'sosioekonomi_data.xlsx'
        else:
            mimetype = 'application/json'
            filename = 'sosioekonomi_data.json'
        
        return send_file(
            io.BytesIO(data),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sosioekonomi_bp.route('/api/filters/available')
def api_available_filters():
    """Get available filter options for sosioekonomi data"""
    try:
        sample_df = data_processor.df
        filters = {}
        
        filter_columns = [
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Pendapatan isi rumah bulanan keluarga anda?',
            'Bagaimana anda membiayai pendidikan anda?',
            'Institusi pendidikan MARA yang anda hadiri?'
        ]
        
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