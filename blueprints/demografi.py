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
        # Get filters properly
        filters = {}
        for key in request.args.keys():
            values = request.args.getlist(key)
            if values:  # Only include non-empty filters
                filters[key] = values
                print(f"Filter applied in summary: {key} = {values}")
        
        print(f"All filters for summary: {filters}")
        
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        total_records = len(filtered_df)
        print(f"Total records after filtering: {total_records}")
        print(f"Available columns: {list(filtered_df.columns)}")
        
        # Initialize default values
        male_rate = 0
        female_rate = 0
        most_common_age = "N/A"
        young_graduates_rate = 0
        uptm_rate = 0
        most_common_institution = "N/A"
        most_common_field = "N/A"
        engineering_rate = 0
        
        if total_records == 0:
            print("No data found - returning default values")
            return jsonify({
                'total_records': 0,
                'male_rate': 0,
                'female_rate': 0,
                'most_common_age': 'N/A',
                'young_graduates_rate': 0,
                'uptm_rate': 0,
                'most_common_institution': 'N/A',
                'most_common_field': 'N/A',
                'engineering_rate': 0,
                'filter_applied': len(filters) > 0
            })
        
        # Gender analysis - try multiple column variations
        gender_columns = ['Jantina anda?', 'Jantina anda? ', 'Jantina anda']
        gender_column = None
        
        for col in gender_columns:
            if col in filtered_df.columns:
                gender_column = col
                print(f"Found gender column: '{gender_column}'")
                break
        
        if gender_column and gender_column in filtered_df.columns:
            # Clean and standardize gender data
            gender_data = filtered_df[gender_column].dropna().astype(str).str.strip()
            gender_counts = gender_data.value_counts()
            print(f"Gender counts: {gender_counts.to_dict()}")
            
            total_gender_responses = gender_counts.sum()
            
            if total_gender_responses > 0:
                # Try different variations of gender values
                male_variations = ['Lelaki', 'lelaki', 'Male', 'male', 'LELAKI']
                female_variations = ['Perempuan', 'perempuan', 'Female', 'female', 'PEREMPUAN']
                
                male_count = 0
                female_count = 0
                
                for variation in male_variations:
                    male_count += gender_counts.get(variation, 0)
                
                for variation in female_variations:
                    female_count += gender_counts.get(variation, 0)
                
                print(f"Male count: {male_count}, Female count: {female_count}")
                
                male_rate = (male_count / total_gender_responses) * 100
                female_rate = (female_count / total_gender_responses) * 100
        else:
            print("Gender column not found")
        
        # Age analysis - try multiple column variations
        age_columns = ['Umur anda?', 'Umur anda? ', 'Umur anda']
        age_column = None
        
        for col in age_columns:
            if col in filtered_df.columns:
                age_column = col
                print(f"Found age column: '{age_column}'")
                break
        
        if age_column and age_column in filtered_df.columns:
            age_data = filtered_df[age_column].dropna().astype(str).str.strip()
            age_counts = age_data.value_counts()
            print(f"Age counts: {age_counts.to_dict()}")
            
            if len(age_counts) > 0:
                most_common_age = age_counts.index[0]
                
                # Calculate young graduates rate (under 25)
                young_age_patterns = ['20-24', '18-24', '20 - 24', '18 - 24', '18-19', '20-21', '22-23', '24']
                young_responses = 0
                
                for pattern in young_age_patterns:
                    for age_value in age_counts.index:
                        if pattern in str(age_value).lower():
                            young_responses += age_counts[age_value]
                
                total_age_responses = age_counts.sum()
                if total_age_responses > 0:
                    young_graduates_rate = (young_responses / total_age_responses) * 100
        else:
            print("Age column not found")
        
        # Institution analysis - try multiple column variations
        institution_columns = [
            'Institusi pendidikan MARA yang anda hadiri?',
            'Institusi pendidikan MARA yang anda hadiri? ', 
            'Institusi pendidikan MARA yang anda hadiri'
        ]
        institution_column = None
        
        for col in institution_columns:
            if col in filtered_df.columns:
                institution_column = col
                print(f"Found institution column: '{institution_column}'")
                break
        
        if institution_column and institution_column in filtered_df.columns:
            def categorize_institution(cell):
                if pd.isnull(cell):
                    return None
                cell_str = str(cell).strip()
                if 'Universiti Poly-Tech Malaysia' in cell_str or 'UPTM' in cell_str:
                    return 'Universiti Poly-Tech Malaysia (UPTM)'
                elif 'Kolej Poly-Tech MARA' in cell_str or 'KPTM' in cell_str:
                    return 'Kolej Poly-Tech MARA'
                else:
                    return 'Other'
            
            institution_categories = filtered_df[institution_column].apply(categorize_institution)
            institution_counts = institution_categories.value_counts()
            print(f"Institution counts: {institution_counts.to_dict()}")
            
            if len(institution_counts) > 0:
                most_common_institution = institution_counts.index[0]
                uptm_count = institution_counts.get('Universiti Poly-Tech Malaysia (UPTM)', 0)
                total_institution_responses = institution_counts.sum()
                
                if total_institution_responses > 0:
                    uptm_rate = (uptm_count / total_institution_responses) * 100
        else:
            print("Institution column not found")
        
        # Field of study analysis - try multiple column variations
        field_columns = [
            'Bidang pengajian utama anda?',
            'Bidang pengajian utama anda? ', 
            'Bidang pengajian utama anda'
        ]
        field_column = None
        
        for col in field_columns:
            if col in filtered_df.columns:
                field_column = col
                print(f"Found field column: '{field_column}'")
                break
        
        if field_column and field_column in filtered_df.columns:
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
                cell_str = str(cell).strip()
                return field_of_study_mapping.get(cell_str, 'Other')
            
            field_categories = filtered_df[field_column].apply(group_field_of_study)
            field_counts = field_categories.value_counts()
            print(f"Field counts: {field_counts.to_dict()}")
            
            if len(field_counts) > 0:
                most_common_field = field_counts.index[0]
                engineering_count = field_counts.get('Engineering Environment', 0)
                total_field_responses = field_counts.sum()
                
                if total_field_responses > 0:
                    engineering_rate = (engineering_count / total_field_responses) * 100
        else:
            print("Field column not found")
        
        # Print final results for debugging
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
            'filter_applied': len(filters) > 0
        }
        
        print(f"Final enhanced stats: {enhanced_stats}")
        return jsonify(enhanced_stats)
        
    except Exception as e:
        print(f"Error in summary endpoint: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
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
        # Get filters properly
        filters = {}
        for key in request.args.keys():
            values = request.args.getlist(key)
            if values:  # Only include non-empty filters
                filters[key] = values
        
        print(f"Age-by-year filters: {filters}")
        
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        print(f"Age-by-year filtered data shape: {filtered_df.shape}")
        
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
        
        # Clean data first
        clean_df = filtered_df[[year_column, age_column]].copy()
        clean_df = clean_df.dropna()
        
        if clean_df.empty:
            return jsonify({
                'labels': ['No Data'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1]
                }]
            })
        
        # Group by graduation year and age (EXACT COLAB REPLICATION)
        grouped_data = clean_df.groupby([year_column, age_column]).size().unstack(fill_value=0)
        
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
        # Get filters properly
        filters = {}
        for key in request.args.keys():
            values = request.args.getlist(key)
            if values:  # Only include non-empty filters
                filters[key] = values
        
        print(f"Gender distribution filters: {filters}")
        
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        print(f"Gender distribution filtered data shape: {filtered_df.shape}")
        
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
        
        # Clean data first
        gender_data = filtered_df[gender_column].dropna()
        
        if gender_data.empty:
            return jsonify({
                'labels': ['No Gender Data'],
                'datasets': [{
                    'label': 'Jantina',
                    'data': [1]
                }]
            })
        
        # Get gender distribution counts (EXACT COLAB REPLICATION)
        gender_counts = gender_data.value_counts()
        
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
        # Get filters properly
        filters = {}
        for key in request.args.keys():
            values = request.args.getlist(key)
            if values:  # Only include non-empty filters
                filters[key] = values
        
        print(f"Institution category filters: {filters}")
        
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        print(f"Institution category filtered data shape: {filtered_df.shape}")
        
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
            cell_str = str(cell).strip()
            if 'Universiti Poly-Tech Malaysia' in cell_str or 'UPTM' in cell_str:
                return 'Universiti Poly-Tech Malaysia (UPTM)'
            elif 'Kolej Poly-Tech MARA' in cell_str or 'KPTM' in cell_str:
                return 'Kolej Poly-Tech MARA'
            else:
                return 'Other'
        
        # Apply categorization to the filtered data
        filtered_df_copy = filtered_df.copy()
        filtered_df_copy['Institution_Category'] = filtered_df_copy[institution_column].apply(categorize_institution)
        
        # Get institution category counts
        institution_counts = filtered_df_copy['Institution_Category'].dropna().value_counts()
        
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
        # Get filters properly
        filters = {}
        for key in request.args.keys():
            values = request.args.getlist(key)
            if values:  # Only include non-empty filters
                filters[key] = values
        
        print(f"Field of study filters: {filters}")
        
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        print(f"Field of study filtered data shape: {filtered_df.shape}")
        
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
            cell_str = str(cell).strip()
            # Use mapping directly
            return field_of_study_mapping.get(cell_str, 'Other')
        
        # Create a copy and apply grouping
        filtered_df_copy = filtered_df.copy()
        filtered_df_copy['Bidang_pengajian'] = filtered_df_copy[field_column].apply(group_field_of_study)
        
        # Get field of study counts
        field_counts = filtered_df_copy['Bidang_pengajian'].dropna().value_counts()
        
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

@demografi_bp.route('/api/table-data')
def api_table_data():
    """Get paginated table data for demografi"""
    try:
        # Get filters properly
        filters = {}
        for key in request.args.keys():
            if key not in ['page', 'per_page', 'search']:
                values = request.args.getlist(key)
                if values:  # Only include non-empty filters
                    filters[key] = values
        
        print(f"Table data filters: {filters}")
        
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
        # Get format first
        format_type = request.args.get('format', 'csv')
        print(f"Export format requested: {format_type}")
        
        # Get filters (exclude 'format' parameter)
        filters = {}
        for key in request.args.keys():
            if key != 'format':
                values = request.args.getlist(key)
                if values:  # Only include non-empty filters
                    filters[key] = values
                    print(f"Filter applied: {key} = {values}")
        
        print(f"All filters for export: {filters}")
        
        # Apply filters to get filtered data
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        print(f"Filtered data shape: {filtered_df.shape}")
        
        if filtered_df.empty:
            print("No data after filtering")
            return jsonify({'error': 'No data available for export'}), 400
        
        # Define relevant columns for export
        relevant_columns = [
            'Timestamp',
            'Tahun graduasi anda? ',
            'Umur anda? ',
            'Jantina anda? ',
            'Institusi pendidikan MARA yang anda hadiri? ',
            'Bidang pengajian utama anda? ',
            'Program pengajian yang anda ikuti? '
        ]
        
        # Get only available columns
        available_columns = []
        for col in relevant_columns:
            if col in filtered_df.columns:
                available_columns.append(col)
        
        print(f"Available columns for export: {available_columns}")
        
        if not available_columns:
            return jsonify({'error': 'No relevant columns found for export'}), 400
        
        # Select only relevant columns
        export_df = filtered_df[available_columns].copy()
        
        # Generate export data based on format
        if format_type == 'csv':
            output = io.StringIO()
            export_df.to_csv(output, index=False, encoding='utf-8')
            data = output.getvalue().encode('utf-8')
            mimetype = 'text/csv'
            filename = f'demografi_data_{len(export_df)}_records.csv'
            
        elif format_type == 'excel':
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                export_df.to_excel(writer, sheet_name='Demografi Data', index=False)
            data = output.getvalue()
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f'demografi_data_{len(export_df)}_records.xlsx'
            
        else:
            # JSON format
            data = export_df.to_json(orient='records', indent=2).encode('utf-8')
            mimetype = 'application/json'
            filename = f'demografi_data_{len(export_df)}_records.json'
        
        print(f"Export successful: {format_type}, {len(export_df)} records, {len(data)} bytes")
        
        return send_file(
            io.BytesIO(data),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Error in export endpoint: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@demografi_bp.route('/api/filters/available')
def api_available_filters():
    """Get available filter options for demografi data"""
    try:
        sample_df = data_processor.df
        filters = {}
        
        print(f"All available columns: {list(sample_df.columns)}")
        
        # Define the exact column names that should be used for filtering
        # These should match what the frontend sends
        filter_mappings = {
            'Tahun graduasi anda? ': ['Tahun graduasi anda?', 'Tahun graduasi anda? ', 'Tahun graduasi anda'],
            'Jantina anda? ': ['Jantina anda?', 'Jantina anda? ', 'Jantina anda'],
            'Umur anda? ': ['Umur anda?', 'Umur anda? ', 'Umur anda'],
            'Institusi pendidikan MARA yang anda hadiri? ': ['Institusi pendidikan MARA yang anda hadiri?', 'Institusi pendidikan MARA yang anda hadiri? ', 'Institusi pendidikan MARA yang anda hadiri'],
            'Bidang pengajian utama anda? ': ['Bidang pengajian utama anda?', 'Bidang pengajian utama anda? ', 'Bidang pengajian utama anda'],
        }
        
        for expected_key, possible_columns in filter_mappings.items():
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
                filters[expected_key] = unique_values
                print(f"Found filter '{expected_key}' in column '{found_column}': {len(unique_values)} values")
            else:
                print(f"Column not found for filter '{expected_key}'")
                filters[expected_key] = []
        
        return jsonify(filters)
        
    except Exception as e:
        print(f"Error loading filters: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500