from flask import Blueprint, render_template, request, jsonify, send_file
from models.data_processor import DataProcessor, load_excel_data
import io
import os
import pandas as pd
from collections import Counter
import numpy as np

sosioekonomi_bp = Blueprint('sosioekonomi', __name__)

# Load data from Excel file
EXCEL_FILE_PATH = 'data/Questionnaire.xlsx'
df = load_excel_data(EXCEL_FILE_PATH)
data_processor = DataProcessor(df)

@sosioekonomi_bp.route('/')
def index():
    """Main sosioekonomi dashboard page"""
    return render_template('sosioekonomi.html')

@sosioekonomi_bp.route('/api/test')
def api_test():
    """Test endpoint to verify the blueprint is working"""
    return jsonify({
        'status': 'success',
        'message': 'Sosioekonomi API is working',
        'available_columns': list(df.columns) if not df.empty else [],
        'total_records': len(df)
    })

@sosioekonomi_bp.route('/api/summary')
def api_summary():
    """Get enhanced summary statistics for socioeconomic status"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        total_records = len(filtered_df)
        
        # Income analysis
        income_column = 'Pendapatan isi rumah bulanan keluarga anda?'
        avg_income_range = "N/A"
        high_income_rate = 0
        
        if income_column in filtered_df.columns:
            income_counts = filtered_df[income_column].value_counts()
            if len(income_counts) > 0:
                avg_income_range = income_counts.index[0]
                
                # Calculate high income rate (above RM5000)
                high_income_responses = income_counts[
                    income_counts.index.str.contains('RM5', na=False) |
                    income_counts.index.str.contains('RM6', na=False) |
                    income_counts.index.str.contains('RM7', na=False) |
                    income_counts.index.str.contains('RM8', na=False) |
                    income_counts.index.str.contains('RM9', na=False) |
                    income_counts.index.str.contains('RM10', na=False) |
                    income_counts.index.str.contains('lebih', na=False)
                ].sum()
                
                total_income_responses = income_counts.sum()
                if total_income_responses > 0:
                    high_income_rate = (high_income_responses / total_income_responses) * 100
        
        # Education financing analysis
        financing_column = 'Bagaimana anda membiayai pendidikan anda?'
        loan_financing_rate = 0
        most_common_financing = "N/A"
        
        if financing_column in filtered_df.columns:
            financing_counts = filtered_df[financing_column].value_counts()
            if len(financing_counts) > 0:
                most_common_financing = financing_counts.index[0]
                
                # Calculate loan financing rate
                loan_responses = financing_counts[
                    financing_counts.index.str.contains('Pinjaman', na=False)
                ].sum()
                
                total_financing_responses = financing_counts.sum()
                if total_financing_responses > 0:
                    loan_financing_rate = (loan_responses / total_financing_responses) * 100
        
        # Employment advantage analysis
        advantage_column = 'Adakah jenis pembiayaan ini memberi kelebihan dalam mencari kerja?'
        advantage_rate = 0
        
        if advantage_column in filtered_df.columns:
            advantage_counts = filtered_df[advantage_column].value_counts()
            if len(advantage_counts) > 0:
                yes_responses = advantage_counts.get('Ya', 0)
                total_advantage_responses = advantage_counts.sum()
                if total_advantage_responses > 0:
                    advantage_rate = (yes_responses / total_advantage_responses) * 100
        
        enhanced_stats = {
            'total_records': total_records,
            'avg_income_range': avg_income_range,
            'high_income_rate': round(high_income_rate, 1),
            'loan_financing_rate': round(loan_financing_rate, 1),
            'most_common_financing': most_common_financing,
            'advantage_rate': round(advantage_rate, 1),
            'filter_applied': len([f for f in filters.values() if f]) > 0
        }
        
        return jsonify(enhanced_stats)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'total_records': 0,
            'avg_income_range': 'N/A',
            'high_income_rate': 0,
            'loan_financing_rate': 0,
            'most_common_financing': 'N/A',
            'advantage_rate': 0
        }), 500

@sosioekonomi_bp.route('/api/household-income')
def api_household_income():
    """Get household income distribution - Bar Chart"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        income_column = 'Pendapatan isi rumah bulanan keluarga anda?'
        
        if income_column not in filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Pendapatan Isi Rumah',
                    'data': [1]
                }]
            })
        
        # Get income distribution counts
        income_counts = filtered_df[income_column].value_counts()
        
        # Define logical order for income ranges
        income_order = [
            'Kurang daripada RM1,000',
            'RM1,000 - RM2,999',
            'RM3,000 - RM4,999', 
            'RM5,000 - RM6,999',
            'RM7,000 - RM9,999',
            'RM10,000 dan lebih'
        ]
        
        # Sort according to logical order
        ordered_data = []
        ordered_labels = []
        for income_range in income_order:
            if income_range in income_counts.index:
                ordered_labels.append(income_range)
                ordered_data.append(int(income_counts[income_range]))
        
        # Add any remaining categories not in our predefined order
        for income_range in income_counts.index:
            if income_range not in income_order:
                ordered_labels.append(str(income_range))
                ordered_data.append(int(income_counts[income_range]))
        
        chart_data = {
            'labels': ordered_labels,
            'datasets': [{
                'label': 'Bilangan Responden',
                'data': ordered_data
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in household income endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

@sosioekonomi_bp.route('/api/father-occupation-by-income')
def api_father_occupation_by_income():
    """Get father occupation by income distribution - Stacked Bar Chart"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        income_column = 'Pendapatan isi rumah bulanan keluarga anda?'
        occupation_column = 'Pekerjaan bapa anda'
        
        if income_column not in filtered_df.columns or occupation_column not in filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1]
                }]
            })
        
        # Group by income and father occupation
        grouped_data = filtered_df.groupby([income_column, occupation_column]).size().unstack(fill_value=0)
        
        if grouped_data.empty:
            return jsonify({
                'labels': ['No Data'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1]
                }]
            })
        
        # Prepare datasets for stacked bar chart
        datasets = []
        for occupation in grouped_data.columns:
            datasets.append({
                'label': str(occupation),
                'data': [int(val) for val in grouped_data[occupation].values.tolist()]
            })
        
        chart_data = {
            'labels': [str(label) for label in grouped_data.index.tolist()],
            'datasets': datasets
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in father occupation by income endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

@sosioekonomi_bp.route('/api/mother-occupation-by-income')
def api_mother_occupation_by_income():
    """Get mother occupation by income distribution - Stacked Bar Chart"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        income_column = 'Pendapatan isi rumah bulanan keluarga anda?'
        occupation_column = 'Pekerjaan ibu anda?'
        
        if income_column not in filtered_df.columns or occupation_column not in filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1]
                }]
            })
        
        # Group by income and mother occupation
        grouped_data = filtered_df.groupby([income_column, occupation_column]).size().unstack(fill_value=0)
        
        if grouped_data.empty:
            return jsonify({
                'labels': ['No Data'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1]
                }]
            })
        
        # Prepare datasets for stacked bar chart
        datasets = []
        for occupation in grouped_data.columns:
            datasets.append({
                'label': str(occupation),
                'data': [int(val) for val in grouped_data[occupation].values.tolist()]
            })
        
        chart_data = {
            'labels': [str(label) for label in grouped_data.index.tolist()],
            'datasets': datasets
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in mother occupation by income endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

@sosioekonomi_bp.route('/api/education-financing')
def api_education_financing():
    """Get education financing methods - Bar Chart"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        financing_column = 'Bagaimana anda membiayai pendidikan anda?'
        
        if financing_column not in filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Jenis Pembiayaan',
                    'data': [1]
                }]
            })
        
        # Get financing methods counts
        financing_counts = filtered_df[financing_column].value_counts()
        
        chart_data = {
            'labels': [str(label) for label in financing_counts.index.tolist()],
            'datasets': [{
                'label': 'Bilangan Responden',
                'data': [int(val) for val in financing_counts.values.tolist()]
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in education financing endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

@sosioekonomi_bp.route('/api/financing-job-advantage')
def api_financing_job_advantage():
    """Get financing method vs job advantage - Stacked Bar Chart"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        financing_column = 'Bagaimana anda membiayai pendidikan anda?'
        advantage_column = 'Adakah jenis pembiayaan ini memberi kelebihan dalam mencari kerja?'
        
        if financing_column not in filtered_df.columns or advantage_column not in filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1]
                }]
            })
        
        # Group by financing method and job advantage
        grouped_data = filtered_df.groupby([financing_column, advantage_column]).size().unstack(fill_value=0)
        
        if grouped_data.empty:
            return jsonify({
                'labels': ['No Data'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1]
                }]
            })
        
        # Prepare datasets for stacked bar chart
        datasets = []
        for advantage in grouped_data.columns:
            datasets.append({
                'label': str(advantage),
                'data': [int(val) for val in grouped_data[advantage].values.tolist()]
            })
        
        chart_data = {
            'labels': [str(label) for label in grouped_data.index.tolist()],
            'datasets': datasets
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in financing job advantage endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

@sosioekonomi_bp.route('/api/debt-impact-career')
def api_debt_impact_career():
    """Get debt impact on career choices for loan-financed students - Bar Chart"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        financing_column = 'Bagaimana anda membiayai pendidikan anda?'
        debt_impact_column = 'Jika anda mempunyai pinjaman pendidikan, adakah beban hutang mempengaruhi pilihan kerjaya anda?'
        
        if financing_column not in filtered_df.columns or debt_impact_column not in filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Kesan Hutang',
                    'data': [1]
                }]
            })
        
        # Filter for loan-financed students only
        df_loan_financed = filtered_df[
            filtered_df[financing_column].str.contains('Pinjaman pendidikan', na=False)
        ].copy()
        
        if df_loan_financed.empty:
            return jsonify({
                'labels': ['Tiada responden dengan pinjaman pendidikan'],
                'datasets': [{
                    'label': 'Kesan Hutang',
                    'data': [1]
                }]
            })
        
        # Get debt impact counts
        debt_impact_counts = df_loan_financed[debt_impact_column].value_counts()
        
        chart_data = {
            'labels': [str(label) for label in debt_impact_counts.index.tolist()],
            'datasets': [{
                'label': 'Bilangan Responden',
                'data': [int(val) for val in debt_impact_counts.values.tolist()]
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in debt impact career endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

# Keep existing endpoints (table, export, filters)
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
            'Adakah jenis pembiayaan ini memberi kelebihan dalam mencari kerja?',
            'Jika anda mempunyai pinjaman pendidikan, adakah beban hutang mempengaruhi pilihan kerjaya anda?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?'
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
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?'
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
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?',
            'Pendapatan isi rumah bulanan keluarga anda?',
            'Bagaimana anda membiayai pendidikan anda?'
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