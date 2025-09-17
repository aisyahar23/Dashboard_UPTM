from flask import Blueprint, render_template, request, jsonify, send_file
from models.data_processor import DataProcessor, load_excel_data
import io
import os
import pandas as pd
from collections import Counter
import numpy as np
import re

demografi_bp = Blueprint('demografi', __name__)

# Load data from Excel file
EXCEL_FILE_PATH = 'data/Questionnaire.xlsx'
df = load_excel_data(EXCEL_FILE_PATH)
data_processor = DataProcessor(df)


# Check key columns for demografi
key_columns = [
    'Tahun graduasi anda?',
    'Umur anda?',
    'Jantina anda?',
    'Institusi pendidikan MARA yang anda hadiri?',
    'Bidang pengajian utama anda?'
]

for col in key_columns:
    if col in df.columns:
        non_null = df[col].notna().sum()
        print(f"✓ {col}: {non_null}/{len(df)} non-null values")
        # Show sample values
        sample_values = df[col].dropna().unique()[:3]
        print(f"    Sample values: {list(sample_values)}")
    else:
        print(f"✗ {col}: NOT FOUND")

print("="*50)

def debug_filter_application(df_original, filters):
    """Debug filter application step by step for demografi"""
    print(f"\n=== DEMOGRAFI FILTER DEBUG ===")
    print(f"Original data shape: {df_original.shape}")
    print(f"Filters received: {filters}")
    
    df_result = df_original.copy()
    
    for column, values in filters.items():
        if not values or len(values) == 0:
            continue
            
        print(f"\nApplying filter: {column} = {values}")
        print(f"Column exists: {column in df_result.columns}")
        
        if column in df_result.columns:
            print(f"Before filter - rows: {len(df_result)}")
            print(f"Column data type: {df_result[column].dtype}")
            print(f"Unique values in column: {list(df_result[column].unique())[:5]}...")
            print(f"Looking for values: {values}")
            
            # Convert filter values to match column data type
            if df_result[column].dtype in ['int64', 'float64']:
                try:
                    converted_values = []
                    for v in values:
                        if isinstance(v, (int, float)):
                            converted_values.append(v)
                        else:
                            converted_values.append(int(float(v)))
                    print(f"Converted filter values to numbers: {converted_values}")
                    df_result = df_result[df_result[column].isin(converted_values)]
                except Exception as e:
                    print(f"Number conversion failed: {e}, using string matching")
                    df_result = df_result[df_result[column].astype(str).isin([str(v) for v in values])]
            else:
                # String matching
                df_result = df_result[df_result[column].isin(values)]
            
            print(f"After filter - rows: {len(df_result)}")
            
            if len(df_result) == 0:
                print("WARNING: Filter eliminated all rows!")
                break
        else:
            print(f"WARNING: Column {column} not found!")
    
    print(f"Final filtered shape: {df_result.shape}")
    print("=== END DEMOGRAFI FILTER DEBUG ===\n")
    
    return df_result

@demografi_bp.route('/')
def index():
    """Main demografi dashboard page"""
    return render_template('demografi.html')

@demografi_bp.route('/table')
def table_view():
    return render_template('data_table.html', 
                         page_title='Demographics & Academic Background Data Table',
                         api_endpoint='/demografi/api/table-data')

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
        
        # Use debug filter application
        df_filtered = debug_filter_application(data_processor.df, filters)
        total_records = len(df_filtered)
        
        print(f"Total records after filtering: {total_records}")
        print(f"Available columns: {list(df_filtered.columns)}")
        
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
            if col in df_filtered.columns:
                gender_column = col
                print(f"Found gender column: '{gender_column}'")
                break
        
        if gender_column and gender_column in df_filtered.columns:
            # Clean and standardize gender data
            gender_data = df_filtered[gender_column].dropna().astype(str).str.strip()
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
            if col in df_filtered.columns:
                age_column = col
                print(f"Found age column: '{age_column}'")
                break
        
        if age_column and age_column in df_filtered.columns:
            age_data = df_filtered[age_column].dropna().astype(str).str.strip()
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
            if col in df_filtered.columns:
                institution_column = col
                print(f"Found institution column: '{institution_column}'")
                break
        
        if institution_column and institution_column in df_filtered.columns:
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
            
            institution_categories = df_filtered[institution_column].apply(categorize_institution)
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
            if col in df_filtered.columns:
                field_column = col
                print(f"Found field column: '{field_column}'")
                break
        
        if field_column and field_column in df_filtered.columns:
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
            
            field_categories = df_filtered[field_column].apply(group_field_of_study)
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

# Centralized Chart Data Formatter
class ChartDataFormatter:
    @staticmethod
    def format_pie_chart(data_series, title="Distribution"):
        return {
            'labels': data_series.index.tolist(),
            'datasets': [{
                'label': title,
                'data': data_series.values.tolist()
            }]
        }
    
    @staticmethod  
    def format_bar_chart(data_series, title="Chart", sort_desc=True):
        if sort_desc:
            data_series = data_series.sort_values(ascending=False)
        
        return {
            'labels': data_series.index.tolist(),
            'datasets': [{
                'label': title,
                'data': data_series.values.tolist()
            }]
        }
        
    @staticmethod
    def format_stacked_bar_chart(grouped_data, title="Stacked Chart"):
        datasets = []
        for column in grouped_data.columns:
            datasets.append({
                'label': str(column),
                'data': [int(val) for val in grouped_data[column].values.tolist()]
            })
        
        return {
            'labels': [str(label) for label in grouped_data.index.tolist()],
            'datasets': datasets
        }

formatter = ChartDataFormatter()

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
        
        # Use debug filter application
        df_filtered = debug_filter_application(data_processor.df, filters)
        
        print(f"Age-by-year filtered data shape: {df_filtered.shape}")
        
        # Try multiple possible column names
        year_columns = ['Tahun graduasi anda?', 'Tahun graduasi anda? ', 'Tahun graduasi anda']
        age_columns = ['Umur anda?', 'Umur anda? ', 'Umur anda']
        
        year_column = None
        age_column = None
        
        # Find the correct column names
        for col in year_columns:
            if col in df_filtered.columns:
                year_column = col
                break
                
        for col in age_columns:
            if col in df_filtered.columns:
                age_column = col
                break
        
        print(f"Available columns: {list(df_filtered.columns)}")
        print(f"Year column found: {year_column}")
        print(f"Age column found: {age_column}")
        
        if year_column is None or age_column is None:
            print("Column not found - available columns:", list(df_filtered.columns))
            return jsonify(formatter.format_stacked_bar_chart(
                pd.DataFrame([1], index=['No Data'], columns=['No Data']),
                "Age by Graduation Year"
            ))
        
        # Clean data first
        clean_df = df_filtered[[year_column, age_column]].copy()
        clean_df = clean_df.dropna()
        
        if clean_df.empty:
            return jsonify(formatter.format_stacked_bar_chart(
                pd.DataFrame([1], index=['No Data'], columns=['No Data']),
                "Age by Graduation Year"
            ))
        
        # Group by graduation year and age (EXACT COLAB REPLICATION)
        grouped_data = clean_df.groupby([year_column, age_column]).size().unstack(fill_value=0)
        
        print(f"Grouped data shape: {grouped_data.shape}")
        print(f"Grouped data:\n{grouped_data}")
        
        if grouped_data.empty:
            return jsonify(formatter.format_stacked_bar_chart(
                pd.DataFrame([1], index=['No Data'], columns=['No Data']),
                "Age by Graduation Year"
            ))
        
        chart_data = formatter.format_stacked_bar_chart(grouped_data, "Age by Graduation Year")
        print(f"Chart data: {chart_data}")
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in age by graduation year endpoint: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify(formatter.format_stacked_bar_chart(
            pd.DataFrame([1], index=['Error'], columns=['Error']),
            "Error"
        )), 500

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
        
        # Use debug filter application
        df_filtered = debug_filter_application(data_processor.df, filters)
        
        print(f"Gender distribution filtered data shape: {df_filtered.shape}")
        
        # Try multiple possible column names
        gender_columns = ['Jantina anda?', 'Jantina anda? ', 'Jantina anda']
        gender_column = None
        
        # Find the correct column name
        for col in gender_columns:
            if col in df_filtered.columns:
                gender_column = col
                break
        
        print(f"Available columns: {list(df_filtered.columns)}")
        print(f"Gender column found: {gender_column}")
        
        if gender_column is None:
            print("Gender column not found - available columns:", list(df_filtered.columns))
            return jsonify(formatter.format_pie_chart(
                pd.Series([1], index=['No Data Available']),
                "Gender Distribution"
            ))
        
        # Clean data first
        gender_data = df_filtered[gender_column].dropna()
        
        if gender_data.empty:
            return jsonify(formatter.format_pie_chart(
                pd.Series([1], index=['No Gender Data']),
                "Gender Distribution"
            ))
        
        # Get gender distribution counts (EXACT COLAB REPLICATION)
        gender_counts = gender_data.value_counts()
        
        print(f"Gender counts: {gender_counts}")
        
        if gender_counts.empty:
            return jsonify(formatter.format_pie_chart(
                pd.Series([1], index=['No Gender Data']),
                "Gender Distribution"
            ))
        
        chart_data = formatter.format_pie_chart(gender_counts, "Gender Distribution")
        print(f"Chart data: {chart_data}")
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in gender distribution endpoint: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify(formatter.format_pie_chart(
            pd.Series([1], index=['Error']),
            "Error"
        )), 500

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
        
        # Use debug filter application
        df_filtered = debug_filter_application(data_processor.df, filters)
        
        print(f"Institution category filtered data shape: {df_filtered.shape}")
        
        # Try multiple possible column names
        institution_columns = [
            'Institusi pendidikan MARA yang anda hadiri?',
            'Institusi pendidikan MARA yang anda hadiri? ', 
            'Institusi pendidikan MARA yang anda hadiri'
        ]
        institution_column = None
        
        # Find the correct column name
        for col in institution_columns:
            if col in df_filtered.columns:
                institution_column = col
                break
        
        print(f"Available columns: {list(df_filtered.columns)}")
        print(f"Institution column found: {institution_column}")
        
        if institution_column is None:
            print("Institution column not found - available columns:", list(df_filtered.columns))
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Data Available']),
                "Institution Categories"
            ))
        
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
        df_filtered_copy = df_filtered.copy()
        df_filtered_copy['Institution_Category'] = df_filtered_copy[institution_column].apply(categorize_institution)
        
        # Get institution category counts
        institution_counts = df_filtered_copy['Institution_Category'].dropna().value_counts()
        
        print(f"Institution counts: {institution_counts}")
        
        if institution_counts.empty:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Institution Data']),
                "Institution Categories"
            ))
        
        chart_data = formatter.format_bar_chart(institution_counts, "Institution Categories", sort_desc=True)
        print(f"Chart data: {chart_data}")
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in institution category endpoint: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify(formatter.format_bar_chart(
            pd.Series([1], index=['Error']),
            "Error"
        )), 500

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
        
        # Use debug filter application
        df_filtered = debug_filter_application(data_processor.df, filters)
        
        print(f"Field of study filtered data shape: {df_filtered.shape}")
        
        # Try multiple possible column names
        field_columns = [
            'Bidang pengajian utama anda?',
            'Bidang pengajian utama anda? ', 
            'Bidang pengajian utama anda'
        ]
        field_column = None
        
        # Find the correct column name
        for col in field_columns:
            if col in df_filtered.columns:
                field_column = col
                break
        
        print(f"Available columns: {list(df_filtered.columns)}")
        print(f"Field column found: {field_column}")
        
        if field_column is None:
            print("Field column not found - available columns:", list(df_filtered.columns))
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Data Available']),
                "Field of Study"
            ))
        
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
        df_filtered_copy = df_filtered.copy()
        df_filtered_copy['Bidang_pengajian'] = df_filtered_copy[field_column].apply(group_field_of_study)
        
        # Get field of study counts
        field_counts = df_filtered_copy['Bidang_pengajian'].dropna().value_counts()
        
        print(f"Field of study sample values: {df_filtered_copy[field_column].head()}")
        print(f"Field counts: {field_counts}")
        
        if field_counts.empty:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Field Data']),
                "Field of Study"
            ))
        
        chart_data = formatter.format_bar_chart(field_counts, "Field of Study", sort_desc=True)
        print(f"Chart data: {chart_data}")
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in field of study endpoint: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify(formatter.format_bar_chart(
            pd.Series([1], index=['Error Loading Field Data']),
            "Error"
        )), 500

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
        
        # Use debug filter application
        df_filtered = debug_filter_application(data_processor.df, filters)
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        
        # Define relevant columns for demografi
        relevant_columns = [
            'Tahun graduasi anda?',
            'Umur anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Bidang pengajian utama anda?',
            'Program pengajian yang anda ikuti?'
        ]
        
        available_columns = [col for col in relevant_columns if col in df_filtered.columns]
        
        # Manual pagination and search implementation
        if search:
            search_mask = df_filtered[available_columns].astype(str).apply(
                lambda x: x.str.contains(search, case=False, na=False)
            ).any(axis=1)
            df_filtered = df_filtered[search_mask]
        
        total_records = len(df_filtered)
        total_pages = (total_records + per_page - 1) // per_page
        
        # Apply pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        df_page = df_filtered[available_columns].iloc[start_idx:end_idx]
        
        # Convert to records
        records = df_page.to_dict('records')
        
        data = {
            'data': records,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_records,
                'pages': total_pages
            },
            'columns': available_columns
        }
        
        return jsonify(data)
        
    except Exception as e:
        print(f"TABLE DATA ERROR: {e}")
        import traceback
        traceback.print_exc()
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
        
        # Use debug filter application
        df_filtered = debug_filter_application(data_processor.df, filters)
        
        print(f"Filtered data shape: {df_filtered.shape}")
        
        if df_filtered.empty:
            print("No data after filtering")
            return jsonify({'error': 'No data available for export'}), 400
        
        # Define relevant columns for export
        relevant_columns = [
            'Timestamp',
            'Tahun graduasi anda?',
            'Umur anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Bidang pengajian utama anda?',
            'Program pengajian yang anda ikuti?'
        ]
        
        # Get only available columns
        available_columns = [col for col in relevant_columns if col in df_filtered.columns]
        
        print(f"Available columns for export: {available_columns}")
        
        if not available_columns:
            return jsonify({'error': 'No relevant columns found for export'}), 400
        
        # Select only relevant columns
        export_df = df_filtered[available_columns].copy()
        
        # Generate export data based on format
        buffer = io.BytesIO()
        
        if format_type == 'csv':
            export_df.to_csv(buffer, index=False, encoding='utf-8')
            mimetype = 'text/csv'
            filename = f'demografi_data_{len(export_df)}_records.csv'
            
        elif format_type == 'excel':
            export_df.to_excel(buffer, index=False, engine='openpyxl')
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f'demografi_data_{len(export_df)}_records.xlsx'
            
        else:
            export_df.to_json(buffer, orient='records', indent=2)
            mimetype = 'application/json'
            filename = f'demografi_data_{len(export_df)}_records.json'
        
        buffer.seek(0)
        
        print(f"Export successful: {format_type}, {len(export_df)} records, {len(buffer.getvalue())} bytes")
        
        return send_file(
            buffer,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Error in export endpoint: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

def extract_graduation_year(val):
    """Enhanced graduation year extraction"""
    if pd.isna(val):
        return None
    
    val_str = str(val).strip()
    
    # Method 1: Direct number
    try:
        clean_val = val_str.replace(',', '').replace('.0', '')
        if clean_val.isdigit():
            year = int(clean_val)
            if 1990 <= year <= 2030:
                return year
    except:
        pass
    
    # Method 2: Extract 4-digit years using regex
    year_pattern = r'\b(19|20)\d{2}\b'
    matches = re.findall(year_pattern, val_str)
    if matches:
        for match in matches:
            year = int(match)
            if 1990 <= year <= 2030:
                return year
    
    return None

@demografi_bp.route('/api/filters/available')
def api_available_filters():
    """Get available filter options for demografi data with enhanced debugging"""
    try:
        sample_df = data_processor.df
        filters = {}
        
        print(f"\n=== DEMOGRAFI FILTERS DEBUG ===")
        print(f"All available columns: {list(sample_df.columns)}")
        
        # Define the exact column names that should be used for filtering
        filter_mappings = {
            'Tahun graduasi anda?': ['Tahun graduasi anda?', 'Tahun graduasi anda? ', 'Tahun graduasi anda'],
            'Jantina anda?': ['Jantina anda?', 'Jantina anda? ', 'Jantina anda'],
            'Umur anda?': ['Umur anda?', 'Umur anda? ', 'Umur anda'],
            'Institusi pendidikan MARA yang anda hadiri?': ['Institusi pendidikan MARA yang anda hadiri?', 'Institusi pendidikan MARA yang anda hadiri? ', 'Institusi pendidikan MARA yang anda hadiri'],
            'Bidang pengajian utama anda?': ['Bidang pengajian utama anda?', 'Bidang pengajian utama anda? ', 'Bidang pengajian utama anda'],
        }
        
        for expected_key, possible_columns in filter_mappings.items():
            found_column = None
            for col in possible_columns:
                if col in sample_df.columns:
                    found_column = col
                    break
            
            if found_column:
                non_null_data = sample_df[found_column].dropna()
                print(f"\nProcessing filter '{expected_key}' from column '{found_column}':")
                print(f"  Non-null values: {len(non_null_data)}/{len(sample_df)}")
                
                if len(non_null_data) == 0:
                    filters[expected_key] = []
                    continue
                
                unique_values = non_null_data.unique()
                print(f"  Unique values: {len(unique_values)}")
                
                # Special handling for graduation year
                if 'Tahun graduasi' in expected_key or 'graduasi' in expected_key.lower():
                    processed_years = set()
                    for val in unique_values:
                        if pd.notna(val):
                            year = extract_graduation_year(val)
                            if year:
                                processed_years.add(year)
                    
                    final_years = sorted(list(processed_years))
                    filters[expected_key] = final_years
                    print(f"  Graduation years processed: {final_years}")
                    
                elif isinstance(unique_values[0] if len(unique_values) > 0 else None, (int, float)):
                    # Other numeric columns
                    unique_values = sorted([val for val in unique_values if pd.notna(val)])
                    filters[expected_key] = unique_values
                    print(f"  Numeric values: {len(unique_values)} items")
                else:
                    # String columns
                    unique_values = sorted([str(val) for val in unique_values if pd.notna(val) and str(val).strip()])
                    filters[expected_key] = unique_values
                    print(f"  String values: {len(unique_values)} items")
                    print(f"  Sample: {unique_values[:3]}...")
                    
            else:
                print(f"Column not found for filter '{expected_key}'")
                filters[expected_key] = []
        
        print(f"\n=== FINAL FILTER SUMMARY ===")
        for col, values in filters.items():
            print(f"  {col}: {len(values)} values")
        
        return jsonify(filters)
        
    except Exception as e:
        print(f"Error loading filters: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500