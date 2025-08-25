from flask import Blueprint, render_template, request, jsonify, send_file
from models.data_processor import DataProcessor, load_excel_data
import io
import os
import pandas as pd
from collections import Counter
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

@demografi_bp.route('/api/test')
def api_test():
    """Test endpoint to verify the blueprint is working"""
    try:
        # Debug column names
        all_columns = list(df.columns) if not df.empty else []
        
        # Check for similar column names
        relevant_patterns = ['Tahun', 'Umur', 'Jantina', 'Institusi', 'Bidang']
        matching_columns = {}
        
        for pattern in relevant_patterns:
            matching_columns[pattern] = [col for col in all_columns if pattern.lower() in col.lower()]
        
        return jsonify({
            'status': 'success',
            'message': 'Demografi API is working',
            'total_records': len(df),
            'all_columns': all_columns,
            'matching_columns': matching_columns,
            'sample_data': df.head(2).to_dict('records') if not df.empty else []
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'total_records': 0
        }), 500

@demografi_bp.route('/api/summary')
def api_summary():
    """Get enhanced summary statistics for demografi data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        total_records = len(filtered_df)
        
        # Gender analysis
        gender_column = 'Jantina anda? '
        male_rate = 0
        female_rate = 0
        
        if gender_column in filtered_df.columns:
            gender_counts = filtered_df[gender_column].value_counts()
            total_gender_responses = gender_counts.sum()
            
            if total_gender_responses > 0:
                male_count = gender_counts.get('Lelaki', 0)
                female_count = gender_counts.get('Perempuan', 0)
                
                male_rate = (male_count / total_gender_responses) * 100
                female_rate = (female_count / total_gender_responses) * 100
        
        # Age analysis
        age_column = 'Umur anda? '
        most_common_age = "N/A"
        young_graduates_rate = 0
        
        if age_column in filtered_df.columns:
            age_counts = filtered_df[age_column].value_counts()
            if len(age_counts) > 0:
                most_common_age = age_counts.index[0]
                
                # Calculate young graduates rate (under 25)
                young_responses = age_counts[
                    age_counts.index.str.contains('20-24|18-24', na=False)
                ].sum()
                
                total_age_responses = age_counts.sum()
                if total_age_responses > 0:
                    young_graduates_rate = (young_responses / total_age_responses) * 100
        
        # Institution analysis
        institution_column = 'Institusi pendidikan MARA yang anda hadiri? '
        uptm_rate = 0
        most_common_institution = "N/A"
        
        if institution_column in filtered_df.columns:
            # Apply categorization function
            def categorize_institution(cell):
                if pd.isnull(cell):
                    return None
                if 'Universiti Poly-Tech Malaysia (UPTM)' in cell:
                    return 'Universiti Poly-Tech Malaysia (UPTM)'
                elif 'Kolej Poly-Tech MARA' in cell:
                    return 'Kolej Poly-Tech MARA'
                else:
                    return 'Other'
            
            institution_categories = filtered_df[institution_column].apply(categorize_institution)
            institution_counts = institution_categories.value_counts()
            
            if len(institution_counts) > 0:
                most_common_institution = institution_counts.index[0]
                uptm_count = institution_counts.get('Universiti Poly-Tech Malaysia (UPTM)', 0)
                total_institution_responses = institution_counts.sum()
                
                if total_institution_responses > 0:
                    uptm_rate = (uptm_count / total_institution_responses) * 100
        
        # Field of study analysis
        field_column = 'Bidang pengajian utama anda? '
        most_common_field = "N/A"
        engineering_rate = 0
        
        if field_column in filtered_df.columns:
            # Define the mapping for grouping fields of study
            field_of_study_mapping = {
                'Kejuruteraan & Teknologi': 'Engineering Environment',
                'Teknologi Elektrik, Elektronik & Pembinaan': 'Engineering Environment',
                'Sains Komputer & Kecerdasan Buatan': 'IT & Computer Science',
                'Sains Data & Analitik': 'IT & Computer Science',
                'Fizik, Kimia & Bioteknologi': 'Natural Science Medical Science / Specialist',
                'Perubatan, Farmasi & Sains Kesihatan': 'Natural Science Medical Science / Specialist',
                'Pemakanan, Dietetik & Fisioterapi': 'Natural Science Medical Science / Specialist',
                'Kewangan, Perbankan & Perakaunan': 'Accounting & Finance',
                'Matematik & Sains Aktuari': 'Accounting & Finance',
                'Pemasaran & Pengurusan Sumber Manusia': 'Economy, Business & Management',
                'Pengurusan Perniagaan & Keusahawanan': 'Economy, Business & Management',
                'Logistik, Pengangkutan & Rantaian Bekalan': 'Economy, Business & Management',
                'Komunikasi, Media & Hubungan Antarabangsa': 'Economy, Business & Management',
                'Psikologi, Sosiologi & Kajian Kemanusiaan': 'Economy, Business & Management',
                'Pelancongan, Hospitaliti & Pengurusan Acara': 'Economy, Business & Management',
                'Seni Kulinari & Pengurusan Perkhidmatan Makanan': 'Economy, Business & Management',
                'Undang-Undang & Pengajian Perundangan': 'Economy, Business & Management',
                'Pengajian Islam & Syariah': 'Economy, Business & Management',
                'Teknologi Automotif & Mekatronik': 'Transport - Vehicle Design & Engineering',
                'Kimpalan, Fabrikasi & Pembuatan': 'Transport - Vehicle Design & Engineering',
                'Senibina & Reka Bentuk': 'Build Professionals',
                'Animasi, Multimedia & Kreativiti Digital': 'Creative Design',
                'Pendidikan & Latihan': 'Other',
                'Information Security': 'IT & Computer Science',
                'Cyber Security': 'IT & Computer Science',
                'Information Security (IT)': 'IT & Computer Science'
            }
            
            def group_field_of_study(cell):
                if pd.isnull(cell):
                    return None
                return field_of_study_mapping.get(cell, 'Other')
            
            field_categories = filtered_df[field_column].apply(group_field_of_study)
            field_counts = field_categories.value_counts()
            
            if len(field_counts) > 0:
                most_common_field = field_counts.index[0]
                engineering_count = field_counts.get('Engineering Environment', 0)
                total_field_responses = field_counts.sum()
                
                if total_field_responses > 0:
                    engineering_rate = (engineering_count / total_field_responses) * 100
        
        enhanced_stats = {
            'total_records': total_records,
            'male_rate': round(male_rate, 1),
            'female_rate': round(female_rate, 1),
            'most_common_age': most_common_age,
            'young_graduates_rate': round(young_graduates_rate, 1),
            'uptm_rate': round(uptm_rate, 1),
            'most_common_institution': most_common_institution,
            'most_common_field': most_common_field,
            'engineering_rate': round(engineering_rate, 1),
            'filter_applied': len([f for f in filters.values() if f]) > 0
        }
        
        return jsonify(enhanced_stats)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'total_records': 0,
            'male_rate': 0,
            'female_rate': 0,
            'most_common_age': 'N/A',
            'young_graduates_rate': 0,
            'uptm_rate': 0,
            'most_common_institution': 'N/A',
            'most_common_field': 'N/A',
            'engineering_rate': 0
        }), 500

@demografi_bp.route('/api/age-by-graduation-year')
def api_age_by_graduation_year():
    """Get age distribution by graduation year - enhanced-stacked-bar (STANDARDIZED)"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        # Try multiple possible column names
        year_columns = ['Tahun graduasi anda?', 'Tahun graduasi anda? ', 'Tahun graduasi anda']
        age_columns = ['Umur anda?', 'Umur anda? ', 'Umur anda']
        
        year_column = None
        age_column = None
        
        # Find the correct column names
        for col in year_columns:
            if col in filtered_df.columns:
                year_column = col
                break
                
        for col in age_columns:
            if col in filtered_df.columns:
                age_column = col
                break
        
        print(f"Available columns: {list(filtered_df.columns)}")
        print(f"Year column found: {year_column}")
        print(f"Age column found: {age_column}")
        
        if year_column is None or age_column is None:
            print("Column not found - available columns:", list(filtered_df.columns))
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1]
                }]
            })
        
        # Group by graduation year and age (EXACT COLAB REPLICATION)
        grouped_data = filtered_df.groupby([year_column, age_column]).size().unstack(fill_value=0)
        
        print(f"Grouped data shape: {grouped_data.shape}")
        print(f"Grouped data:\n{grouped_data}")
        
        if grouped_data.empty:
            return jsonify({
                'labels': ['No Data'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1]
                }]
            })
        
        # Prepare datasets for stacked bar chart (STANDARDIZED FORMAT)
        datasets = []
        for age_group in grouped_data.columns:
            datasets.append({
                'label': str(age_group),
                'data': [int(val) for val in grouped_data[age_group].values.tolist()]
            })
        
        chart_data = {
            'labels': [str(label) for label in grouped_data.index.tolist()],
            'datasets': datasets
        }
        
        print(f"Chart data: {chart_data}")
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in age by graduation year endpoint: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

@demografi_bp.route('/api/gender-distribution')
def api_gender_distribution():
    """Get gender distribution - enhanced-pie (STANDARDIZED)"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        # Try multiple possible column names
        gender_columns = ['Jantina anda?', 'Jantina anda? ', 'Jantina anda']
        gender_column = None
        
        # Find the correct column name
        for col in gender_columns:
            if col in filtered_df.columns:
                gender_column = col
                break
        
        print(f"Available columns: {list(filtered_df.columns)}")
        print(f"Gender column found: {gender_column}")
        
        if gender_column is None:
            print("Gender column not found - available columns:", list(filtered_df.columns))
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Jantina',
                    'data': [1]
                }]
            })
        
        # Get gender distribution counts (EXACT COLAB REPLICATION)
        gender_counts = filtered_df[gender_column].value_counts()
        
        print(f"Gender counts: {gender_counts}")
        
        if gender_counts.empty:
            return jsonify({
                'labels': ['No Gender Data'],
                'datasets': [{
                    'label': 'Jantina',
                    'data': [1]
                }]
            })
        
        # STANDARDIZED PIE CHART FORMAT
        chart_data = {
            'labels': [str(label) for label in gender_counts.index.tolist()],
            'datasets': [{
                'label': 'Taburan Jantina',
                'data': [int(val) for val in gender_counts.values.tolist()]
            }]
        }
        
        print(f"Chart data: {chart_data}")
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in gender distribution endpoint: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

@demografi_bp.route('/api/institution-category')
def api_institution_category():
    """Get institution category distribution - vertical-bar (STANDARDIZED)"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        # Try multiple possible column names
        institution_columns = [
            'Institusi pendidikan MARA yang anda hadiri?',
            'Institusi pendidikan MARA yang anda hadiri? ', 
            'Institusi pendidikan MARA yang anda hadiri'
        ]
        institution_column = None
        
        # Find the correct column name
        for col in institution_columns:
            if col in filtered_df.columns:
                institution_column = col
                break
        
        print(f"Available columns: {list(filtered_df.columns)}")
        print(f"Institution column found: {institution_column}")
        
        if institution_column is None:
            print("Institution column not found - available columns:", list(filtered_df.columns))
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Institusi',
                    'data': [1]
                }]
            })
        
        # Apply categorization function (EXACT COLAB REPLICATION)
        def categorize_institution(cell):
            if pd.isnull(cell):
                return None
            if 'Universiti Poly-Tech Malaysia (UPTM)' in str(cell):
                return 'Universiti Poly-Tech Malaysia (UPTM)'
            elif 'Kolej Poly-Tech MARA' in str(cell):
                return 'Kolej Poly-Tech MARA'
            else:
                return 'Other'
        
        # Apply categorization to the filtered data
        filtered_df_copy = filtered_df.copy()
        filtered_df_copy['Institution_Category'] = filtered_df_copy[institution_column].apply(categorize_institution)
        
        # Get institution category counts
        institution_counts = filtered_df_copy['Institution_Category'].value_counts()
        
        print(f"Institution counts: {institution_counts}")
        
        if institution_counts.empty:
            return jsonify({
                'labels': ['No Institution Data'],
                'datasets': [{
                    'label': 'Institusi',
                    'data': [1]
                }]
            })
        
        # STANDARDIZED VERTICAL BAR CHART FORMAT
        chart_data = {
            'labels': [str(label) for label in institution_counts.index.tolist()],
            'datasets': [{
                'label': 'Bilangan Responden',
                'data': [int(val) for val in institution_counts.values.tolist()]
            }]
        }
        
        print(f"Chart data: {chart_data}")
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in institution category endpoint: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

@demografi_bp.route('/api/field-of-study')
def api_field_of_study():
    """Get field of study distribution (grouped) - vertical-bar (STANDARDIZED)"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        # Try multiple possible column names
        field_columns = [
            'Bidang pengajian utama anda?',
            'Bidang pengajian utama anda? ', 
            'Bidang pengajian utama anda'
        ]
        field_column = None
        
        # Find the correct column name
        for col in field_columns:
            if col in filtered_df.columns:
                field_column = col
                break
        
        print(f"Available columns: {list(filtered_df.columns)}")
        print(f"Field column found: {field_column}")
        
        if field_column is None:
            print("Field column not found - available columns:", list(filtered_df.columns))
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Bidang Pengajian',
                    'data': [1]
                }]
            })
        
        # EXACT COLAB REPLICATION - Field of study mapping
        field_of_study_mapping = {
            'Kejuruteraan & Teknologi': 'Engineering Environment',
            'Teknologi Elektrik, Elektronik & Pembinaan': 'Engineering Environment',
            'Sains Komputer & Kecerdasan Buatan': 'IT & Computer Science',
            'Sains Data & Analitik': 'IT & Computer Science',
            'Fizik, Kimia & Bioteknologi': 'Natural Science Medical Science / Specialist',
            'Perubatan, Farmasi & Sains Kesihatan': 'Natural Science Medical Science / Specialist',
            'Pemakanan, Dietetik & Fisioterapi': 'Natural Science Medical Science / Specialist',
            'Kewangan, Perbankan & Perakaunan': 'Accounting & Finance',
            'Matematik & Sains Aktuari': 'Accounting & Finance',
            'Pemasaran & Pengurusan Sumber Manusia': 'Economy, Business & Management',
            'Pengurusan Perniagaan & Keusahawanan': 'Economy, Business & Management',
            'Logistik, Pengangkutan & Rantaian Bekalan': 'Economy, Business & Management',
            'Komunikasi, Media & Hubungan Antarabangsa': 'Economy, Business & Management',
            'Psikologi, Sosiologi & Kajian Kemanusiaan': 'Economy, Business & Management',
            'Pelancongan, Hospitaliti & Pengurusan Acara': 'Economy, Business & Management',
            'Seni Kulinari & Pengurusan Perkhidmatan Makanan': 'Economy, Business & Management',
            'Undang-Undang & Pengajian Perundangan': 'Economy, Business & Management',
            'Pengajian Islam & Syariah': 'Economy, Business & Management',
            'Teknologi Automotif & Mekatronik': 'Transport - Vehicle Design & Engineering',
            'Kimpalan, Fabrikasi & Pembuatan': 'Transport - Vehicle Design & Engineering',
            'Senibina & Reka Bentuk': 'Build Professionals',
            'Animasi, Multimedia & Kreativiti Digital': 'Creative Design',
            'Pendidikan & Latihan': 'Other',
            'Information Security': 'IT & Computer Science',
            'Cyber Security': 'IT & Computer Science',
            'Information Security (IT)': 'IT & Computer Science'
        }
        
        # EXACT COLAB REPLICATION - Apply the mapping function
        def group_field_of_study(cell):
            if pd.isnull(cell):
                return None
            # Assuming a single field of study per cell, apply the mapping directly
            return field_of_study_mapping.get(str(cell), 'Other') # Use 'Other' for any unmapped values
        
        # Create a copy and apply grouping
        filtered_df_copy = filtered_df.copy()
        filtered_df_copy['Bidang_pengajian'] = filtered_df_copy[field_column].apply(group_field_of_study)
        
        # Get field of study counts
        field_counts = filtered_df_copy['Bidang_pengajian'].value_counts()
        
        print(f"Field of study sample values: {filtered_df_copy[field_column].head()}")
        print(f"Field counts: {field_counts}")
        
        if field_counts.empty:
            return jsonify({
                'labels': ['No Field Data'],
                'datasets': [{
                    'label': 'Bidang Pengajian',
                    'data': [1]
                }]
            })
        
        # STANDARDIZED VERTICAL BAR CHART FORMAT
        chart_data = {
            'labels': [str(label) for label in field_counts.index.tolist()],
            'datasets': [{
                'label': 'Bilangan Responden',
                'data': [int(val) for val in field_counts.values.tolist()]
            }]
        }
        
        print(f"Chart data: {chart_data}")
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in field of study endpoint: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'labels': ['Error Loading Field Data'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

# Keep existing endpoints (table, export, filters)
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
            'Tahun graduasi anda? ',
            'Umur anda? ',
            'Jantina anda? ',
            'Institusi pendidikan MARA yang anda hadiri? ',
            'Bidang pengajian utama anda? ',
            'Program pengajian yang anda ikuti? '
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

@demografi_bp.route('/api/export')
def api_export():
    """Export demografi data in various formats"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() if k != 'format'}
        filtered_processor = data_processor.apply_filters(filters)
        
        format_type = request.args.get('format', 'csv')
        
        relevant_columns = [
            'Timestamp',
            'Tahun graduasi anda? ',
            'Umur anda? ',
            'Jantina anda? ',
            'Institusi pendidikan MARA yang anda hadiri? ',
            'Bidang pengajian utama anda? ',
            'Program pengajian yang anda ikuti? '
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
        return jsonify({'error': str(e)}), 500

@demografi_bp.route('/api/filters/available')
def api_available_filters():
    """Get available filter options for demografi data"""
    try:
        sample_df = data_processor.df
        filters = {}
        
        print(f"All available columns: {list(sample_df.columns)}")
        
        # Define multiple possible column names for each filter
        filter_mappings = {
            'graduation_years': ['Tahun graduasi anda?', 'Tahun graduasi anda? ', 'Tahun graduasi anda'],
            'genders': ['Jantina anda?', 'Jantina anda? ', 'Jantina anda'],
            'age_groups': ['Umur anda?', 'Umur anda? ', 'Umur anda'],
            'institutions': ['Institusi pendidikan MARA yang anda hadiri?', 'Institusi pendidikan MARA yang anda hadiri? ', 'Institusi pendidikan MARA yang anda hadiri'],
            'fields_of_study': ['Bidang pengajian utama anda?', 'Bidang pengajian utama anda? ', 'Bidang pengajian utama anda'],
            'programs': ['Program pengajian yang anda ikuti?', 'Program pengajian yang anda ikuti? ', 'Program pengajian yang anda ikuti']
        }
        
        for filter_key, possible_columns in filter_mappings.items():
            found_column = None
            for col in possible_columns:
                if col in sample_df.columns:
                    found_column = col
                    break
            
            if found_column:
                unique_values = sample_df[found_column].dropna().unique().tolist()
                if isinstance(unique_values[0] if unique_values else None, (int, float)):
                    unique_values = sorted(unique_values)
                else:
                    unique_values = sorted([str(val) for val in unique_values])
                filters[filter_key] = unique_values
                print(f"Found {filter_key} in column '{found_column}': {len(unique_values)} values")
            else:
                print(f"Column not found for {filter_key}")
                filters[filter_key] = []
        
        return jsonify(filters)
        
    except Exception as e:
        print(f"Error loading filters: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e), 'filters': {}}), 500