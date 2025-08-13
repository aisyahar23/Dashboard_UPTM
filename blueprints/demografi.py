from flask import Blueprint, render_template, request, jsonify, send_file
from models.data_processor import DataProcessor, load_excel_data
import io
import os
import pandas as pd
import numpy as np

demografi_bp = Blueprint('demografi', __name__)

# Load data from Excel file
EXCEL_FILE_PATH = 'data/Questionnaire.xlsx'
df = load_excel_data(EXCEL_FILE_PATH)
data_processor = DataProcessor(df)

@demografi_bp.route('/')
def index():
    """Main demografi dashboard page"""
    return render_template('demografi.html')

@demografi_bp.route('/table')
def table_view():
    """Table view for demografi data"""
    return render_template('data_table.html', 
                         page_title='Demografi Data Table',
                         api_endpoint='/demografi/api/table-data')

@demografi_bp.route('/api/summary')
def api_summary():
    """Get summary statistics for demografi data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        filtered_df = filtered_processor.filtered_df
        total_records = len(filtered_df)
        
        # Initialize default stats
        demo_stats = {
            'total_records': total_records,
            'avg_age': 0,
            'min_age': 0,
            'max_age': 0,
            'male_percentage': 0,
            'female_percentage': 0,
            'gender_diversity_index': 0,
            'total_institutions': 0,
            'graduation_year_span': 0,
            'recent_graduates_rate': 0,
            'field_diversity': 0
        }
        
        if total_records > 0:
            # Age analysis
            age_column = 'Umur anda?'
            if age_column in filtered_df.columns:
                ages = pd.to_numeric(filtered_df[age_column], errors='coerce').dropna()
                if len(ages) > 0:
                    demo_stats.update({
                        'avg_age': round(float(ages.mean()), 1),
                        'min_age': int(ages.min()),
                        'max_age': int(ages.max())
                    })
            
            # Gender distribution
            gender_column = 'Jantina anda?'
            if gender_column in filtered_df.columns:
                gender_counts = filtered_df[gender_column].value_counts()
                total_gender = gender_counts.sum()
                
                if total_gender > 0:
                    male_count = 0
                    female_count = 0
                    
                    for gender, count in gender_counts.items():
                        gender_str = str(gender).lower()
                        if any(word in gender_str for word in ['lelaki', 'male', 'laki']):
                            male_count = count
                        elif any(word in gender_str for word in ['perempuan', 'female', 'wanita']):
                            female_count = count
                    
                    male_percentage = round((male_count / total_gender) * 100, 1)
                    female_percentage = round((female_count / total_gender) * 100, 1)
                    
                    # Calculate gender diversity index (how balanced the distribution is)
                    if male_count > 0 and female_count > 0:
                        min_count = min(male_count, female_count)
                        max_count = max(male_count, female_count)
                        gender_diversity_index = round((min_count / max_count) * 100, 1)
                    else:
                        gender_diversity_index = 0
                    
                    demo_stats.update({
                        'male_percentage': male_percentage,
                        'female_percentage': female_percentage,
                        'gender_diversity_index': gender_diversity_index
                    })
            
            # Institution analysis
            institution_column = 'Institusi pendidikan MARA yang anda hadiri?'
            if institution_column in filtered_df.columns:
                institutions = filtered_df[institution_column].dropna().nunique()
                demo_stats['total_institutions'] = institutions
            
            # Graduation year analysis
            grad_column = 'Tahun graduasi anda?'
            if grad_column in filtered_df.columns:
                grad_years = pd.to_numeric(filtered_df[grad_column], errors='coerce').dropna()
                if len(grad_years) > 0:
                    grad_year_span = grad_years.nunique()
                    current_year = pd.Timestamp.now().year
                    recent_grads = len(grad_years[grad_years >= (current_year - 3)])  # Last 3 years
                    recent_graduates_rate = round((recent_grads / total_records) * 100, 1)
                    
                    demo_stats.update({
                        'graduation_year_span': grad_year_span,
                        'recent_graduates_rate': recent_graduates_rate
                    })
            
            # Field of study diversity
            field_column = 'Bidang pengajian utama anda?'
            if field_column in filtered_df.columns:
                fields = filtered_df[field_column].dropna().nunique()
                demo_stats['field_diversity'] = fields
        
        return jsonify(demo_stats)
        
    except Exception as e:
        print(f"Error in api_summary: {str(e)}")
        return jsonify({
            'error': str(e),
            'total_records': 0,
            'avg_age': 0,
            'min_age': 0,
            'max_age': 0,
            'male_percentage': 0,
            'female_percentage': 0,
            'gender_diversity_index': 0,
            'total_institutions': 0,
            'graduation_year_span': 0,
            'recent_graduates_rate': 0,
            'field_diversity': 0
        }), 500

@demografi_bp.route('/api/gender-distribution')
def api_gender_distribution():
    """Get gender distribution data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        gender_column = 'Jantina anda?'
        if gender_column not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderWidth': 3,
                    'borderColor': '#ffffff'
                }]
            })
        
        data = filtered_processor.get_chart_data('pie', gender_column)
        return jsonify(data)
        
    except Exception as e:
        print(f"Error in api_gender_distribution: {str(e)}")
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

@demografi_bp.route('/api/age-distribution')
def api_age_distribution():
    """Get age distribution data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        age_column = 'Umur anda?'
        if age_column not in filtered_processor.filtered_df.columns:
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
        
        # Create age groups from the data
        filtered_df = filtered_processor.filtered_df.copy()
        
        # Convert age to numeric and handle errors
        ages = pd.to_numeric(filtered_df[age_column], errors='coerce')
        valid_ages = ages.dropna()
        
        if len(valid_ages) == 0:
            return jsonify({
                'labels': ['No Valid Age Data'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': '#6b7280',
                    'borderColor': '#374151',
                    'borderWidth': 2,
                    'borderRadius': 8
                }]
            })
        
        # Create age groups
        def categorize_age(age):
            if pd.isna(age):
                return 'Unknown'
            age = int(age)
            if age <= 22:
                return '≤22'
            elif age <= 24:
                return '23-24'
            elif age <= 26:
                return '25-26'
            elif age <= 28:
                return '27-28'
            elif age <= 30:
                return '29-30'
            else:
                return '30+'
        
        filtered_df['Age_Group'] = ages.apply(categorize_age)
        
        # Count age groups
        age_group_counts = filtered_df['Age_Group'].value_counts()
        
        # Define the order for age groups
        age_group_order = ['≤22', '23-24', '25-26', '27-28', '29-30', '30+', 'Unknown']
        
        # Reorder the data
        ordered_labels = []
        ordered_data = []
        
        for age_group in age_group_order:
            if age_group in age_group_counts.index:
                ordered_labels.append(age_group)
                ordered_data.append(int(age_group_counts[age_group]))
        
        # Create color scheme
        colors = ['#3b82f6', '#1d4ed8', '#1e40af', '#1e3a8a', '#312e81', '#3730a3']
        
        return jsonify({
            'labels': ordered_labels,
            'datasets': [{
                'label': 'Number of Graduates',
                'data': ordered_data,
                'backgroundColor': colors[:len(ordered_data)],
                'borderColor': '#ffffff',
                'borderWidth': 2,
                'borderRadius': 8
            }]
        })
        
    except Exception as e:
        print(f"Error in api_age_distribution: {str(e)}")
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

@demografi_bp.route('/api/institution-distribution')
def api_institution_distribution():
    """Get institution distribution data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        institution_column = 'Institusi pendidikan MARA yang anda hadiri?'
        if institution_column not in filtered_processor.filtered_df.columns:
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
        
        data = filtered_processor.get_chart_data('bar', institution_column)
        return jsonify(data)
        
    except Exception as e:
        print(f"Error in api_institution_distribution: {str(e)}")
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

@demografi_bp.route('/api/field-graduation')
def api_field_graduation():
    """Get field of study vs graduation year data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        field_column = 'Bidang pengajian utama anda?'
        grad_column = 'Tahun graduasi anda?'
        
        if field_column not in filtered_processor.filtered_df.columns or grad_column not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1],
                    'backgroundColor': '#6b7280',
                    'borderWidth': 0
                }]
            })
        
        data = filtered_processor.get_chart_data('stacked_bar', grad_column, group_by=field_column)
        return jsonify(data)
        
    except Exception as e:
        print(f"Error in api_field_graduation: {str(e)}")
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

@demografi_bp.route('/api/table-data')
def api_table_data():
    """Get paginated table data for demografi"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() 
                   if k not in ['page', 'per_page', 'search']}
        filtered_processor = data_processor.apply_filters(filters)
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        
        # Define relevant columns for demografi
        relevant_columns = [
            'Timestamp',
            'Umur anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Bidang pengajian utama anda?',
            'Tahap pendidikan tertinggi anda?',
            'Tahun graduasi anda?'
        ]
        
        available_columns = [col for col in relevant_columns if col in filtered_processor.filtered_df.columns]
        
        data = filtered_processor.get_table_data(page, per_page, search, available_columns)
        return jsonify(data)
        
    except Exception as e:
        print(f"Error in api_table_data: {str(e)}")
        return jsonify({
            'error': str(e),
            'data': [],
            'pagination': {'page': 1, 'per_page': 50, 'total': 0, 'pages': 0},
            'columns': []
        }), 500

@demografi_bp.route('/api/export')
def api_export():
    """Export demografi data in various formats"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() if k != 'format'}
        filtered_processor = data_processor.apply_filters(filters)
        
        format_type = request.args.get('format', 'csv')
        
        relevant_columns = [
            'Timestamp',
            'Umur anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Bidang pengajian utama anda?',
            'Tahap pendidikan tertinggi anda?',
            'Tahun graduasi anda?'
        ]
        
        available_columns = [col for col in relevant_columns if col in filtered_processor.filtered_df.columns]
        
        data = filtered_processor.export_data(format_type, available_columns)
        
        if format_type == 'csv':
            mimetype = 'text/csv'
            filename = 'demografi_data.csv'
        elif format_type == 'excel':
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = 'demografi_data.xlsx'
        else:
            mimetype = 'application/json'
            filename = 'demografi_data.json'
        
        return send_file(
            io.BytesIO(data),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Error in api_export: {str(e)}")
        return jsonify({'error': str(e)}), 500

@demografi_bp.route('/api/filters/available')
def api_available_filters():
    """Get available filter options for demografi data"""
    try:
        sample_df = data_processor.df
        filters = {}
        
        filter_columns = [
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Bidang pengajian utama anda?',
            'Tahap pendidikan tertinggi anda?'
        ]
        
        for column in filter_columns:
            if column in sample_df.columns:
                unique_values = sample_df[column].dropna().unique().tolist()
                if len(unique_values) > 0:
                    # Handle numeric values
                    if isinstance(unique_values[0], (int, float, np.number)):
                        unique_values = sorted([int(val) for val in unique_values if not pd.isna(val)])
                    else:
                        unique_values = sorted([str(val) for val in unique_values if str(val) != 'nan'])
                    filters[column] = unique_values
                else:
                    filters[column] = []
        
        return jsonify(filters)
        
    except Exception as e:
        print(f"Error in api_available_filters: {str(e)}")
        return jsonify({'error': str(e), 'filters': {}}), 500