from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
from collections import Counter
import json
import logging
from flask_cors import CORS

app = Flask(__name__, template_folder='Website/templates', static_folder='Website/static')
CORS(app)  # Enable CORS for all routes

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FIXED: Load real CSV data instead of creating sample data
try:
    df = pd.read_csv('latest_soal_selidk.csv', encoding='utf-8')
    logger.info(f"✅ Real CSV file loaded successfully! Shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)}")
except FileNotFoundError:
    logger.error("❌ CSV file 'latest_soal_selidk.csv' not found!")
    # Create minimal sample data as fallback
    df = pd.DataFrame({
        'Adakah anda kini bekerja?': ['Ya'] * 39,
        'Bidang pengajian utama anda? ': ['IT'] * 39
    })
    logger.warning("⚠️ Using minimal fallback data")
except Exception as e:
    logger.error(f"❌ Error loading CSV: {str(e)}")
    df = pd.DataFrame()

def clean_data():
    global df
    df = df.fillna('Tidak Dinyatakan')
    logger.info(f"✅ Data processed successfully. Shape: {df.shape}")

clean_data()

def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

def safe_api_response(data, success=True):
    """Standardize API response format with proper JSON serialization"""
    try:
        if success and data:
            data = convert_numpy_types(data)
        
        return jsonify({
            'success': success,
            'data': data if success else None,
            'error': None if success else data
        })
    except Exception as e:
        logger.error(f"Error in API response: {str(e)}")
        return jsonify({
            'success': False,
            'data': None,
            'error': str(e)
        })

def find_column_fuzzy(df, target_columns):
    """Find column using fuzzy matching"""
    for target in target_columns:
        for col in df.columns:
            if target.lower() in col.lower() or col.lower() in target.lower():
                return col
    return None

# Enhanced column mapping with REAL column names from CSV
COLUMN_MAPPING = {
    'employment_status': 'Adakah anda kini bekerja?',
    'job_type': 'Apakah jenis pekerjaan anda sekarang',
    'time_to_employment': 'Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?',
    'field_of_study': 'Bidang pengajian utama anda? ',
    'graduation_year': 'Tahun graduasi anda? ',
    'current_salary': 'Berapakah julat gaji bulanan anda sekarang?',
    'expected_salary': 'Apakah jangkaan gaji permulaan yang anda anggap sesuai dengan kelulusan anda?',
    'out_of_field_reason': 'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?',
    'academic_skills_needed': 'Jika anda bekerja di luar bidang pengajian, adakah pekerjaan tersebut masih memerlukan kemahiran akademik anda?',
    'job_challenges': 'Apakah cabaran utama yang anda hadapi dalam mendapatkan pekerjaan?',
    'success_factors': 'Apakah faktor utama yang membantu anda mendapat pekerjaan tersebut?',
    'employment_sectors': 'Apakah sektor pekerjaan anda?',
    'professional_cert': 'Adakah anda memiliki sijil profesional tambahan selain ijazah/diploma?',
    'internship': 'Adakah anda menjalani internship/praktikal sebelum tamat pengajian?',
    'university_preparation': 'Sejauh mana anda bersetuju bahawa universiti telah menyediakan anda untuk pasaran kerja?',
    'gig_economy': 'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?',
    'support_needed': 'Apakah bantuan atau sokongan yang anda rasa perlu untuk berjaya dalam keusahawanan dan ekonomi gig?',
    'gender': 'Jantina anda? ',
    'age': 'Umur anda? ',
    'institution': 'Institusi pendidikan MARA yang anda hadiri? ',
    # NEW: Added missing mappings
    'financing_advantage': 'Adakah jenis pembiayaan ini memberi kelebihan dalam mencari kerja?',
    'li_impact': 'Sejauh mana latihan industri/praktikal mempengaruhi kebolehpasaran anda?',
    'communication_impact': 'Sejauh mana Kemahiran Komunikasi  mempengaruhi kebolehpasaran anda?',
    'technical_impact': 'Sejauh mana kemahiran teknikal mempengaruhi kebolehpasaran anda?',
    'networking_impact': 'Sejauh mana rangkaian peribadi (networking) mempengaruhi kebolehpasaran anda?',
    'academic_impact': 'Sejauh mana kelayakan akademik mempengaruhi kebolehpasaran anda?',
    'entrepreneurship_training': 'Adakah universiti anda menawarkan kursus atau latihan berkaitan keusahawanan?',
    'uni_gig_programs': 'Adakah universiti anda pernah menganjurkan program berkaitan perniagaan atau ekonomi gig seperti hackathon, bootcamp, atau geran permulaan perniagaan?',
    'program_helpful': 'Adakah program berkaitan perniagaan atau ekonomi gig di universiti membantu anda dalam memulakan atau mengembangkan pekerjaan bebas anda?',
    'gig_reasons': 'Apakah sebab utama anda memilih untuk bekerja dalam ekonomi gig? ',
    'gig_skills_source': 'Bagaimanakah anda memperoleh kemahiran untuk bekerja dalam ekonomi gig?',
    'gig_challenges': 'Apakah cabaran utama yang anda hadapi dalam keusahawanan atau ekonomi gig?',
    'gig_income': 'Berapakah purata pendapatan bulan anda daripada ekonomi gig?',
    'gig_vs_permanent': 'Jika diberikan peluang pekerjaan tetap dengan gaji setanding ekonomi gig, adakah anda akan menerimanya?'
}

def get_column(key):
    """Get column name from mapping"""
    return COLUMN_MAPPING.get(key)

def find_column_smart(df, possible_keys):
    """Smart column finder that uses both mapping and fuzzy matching"""
    for key in possible_keys:
        col = get_column(key)
        if col and col in df.columns:
            return col
    
    all_possible_names = []
    for key in possible_keys:
        if key in COLUMN_MAPPING:
            all_possible_names.append(COLUMN_MAPPING[key])
        all_possible_names.append(key.replace('_', ' ').title())
    
    return find_column_fuzzy(df, all_possible_names)

def apply_filters(data_df, filters):
    """Enhanced filter application with better error handling"""
    filtered_df = data_df.copy()
    initial_count = len(filtered_df)
    
    try:
        if filters.get('year'):
            year_col = find_column_smart(filtered_df, ['graduation_year'])
            if year_col and year_col in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[year_col].astype(str) == str(filters['year'])]
                logger.info(f"Year filter applied: {len(filtered_df)} rows remaining")
        
        if filters.get('field'):
            field_col = find_column_smart(filtered_df, ['field_of_study'])
            if field_col and field_col in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[field_col] == filters['field']]
                logger.info(f"Field filter applied: {len(filtered_df)} rows remaining")
        
        if filters.get('employment'):
            emp_col = find_column_smart(filtered_df, ['employment_status'])
            if emp_col and emp_col in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[emp_col] == filters['employment']]
                logger.info(f"Employment filter applied: {len(filtered_df)} rows remaining")
        
        if filters.get('gender'):
            gender_col = find_column_smart(filtered_df, ['gender'])
            if gender_col and gender_col in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[gender_col] == filters['gender']]
                logger.info(f"Gender filter applied: {len(filtered_df)} rows remaining")
        
        if filters.get('institution'):
            inst_col = find_column_smart(filtered_df, ['institution'])
            if inst_col and inst_col in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[inst_col] == filters['institution']]
                logger.info(f"Institution filter applied: {len(filtered_df)} rows remaining")
        
        logger.info(f"Total filtering: {initial_count} -> {len(filtered_df)} rows")
        return filtered_df
        
    except Exception as e:
        logger.error(f"Error applying filters: {str(e)}")
        return data_df

def create_table_data(labels, data, label_key='label', count_key='count'):
    """Helper function to create standardized table data"""
    total = sum(data) if data else 1
    table_data = []
    
    for i, (label, count) in enumerate(zip(labels, data)):
        percentage = round((count / total) * 100, 1) if total > 0 else 0
        table_data.append({
            label_key: str(label),
            count_key: int(count),
            'percentage': percentage
        })
    
    return table_data

def process_checkbox_data(responses, predefined_options=None):
    """Process checkbox-style responses where multiple options can be selected"""
    if responses is None or len(responses) == 0:
        return [], [], 0
    
    # Convert to list if it's a pandas Series
    if hasattr(responses, 'tolist'):
        responses = responses.tolist()
    elif hasattr(responses, 'values'):
        responses = responses.values.tolist()
    
    # Clean responses and split by comma
    all_selections = []
    total_responses = len(responses)
    valid_responses = 0
    
    for response in responses:
        if response is None or pd.isna(response) or str(response).strip() == '' or str(response) == 'Tidak Dinyatakan':
            continue
        valid_responses += 1
        # Split by comma and clean each selection
        selections = [sel.strip() for sel in str(response).split(',') if sel.strip()]
        all_selections.extend(selections)
    
    # Count occurrences
    selection_counts = Counter(all_selections)
    
    # If predefined options are provided, ensure they're all included
    if predefined_options:
        labels = predefined_options
        data = [selection_counts.get(option, 0) for option in predefined_options]
        # Only include options that have at least one response
        filtered_data = [(label, count) for label, count in zip(labels, data) if count > 0]
        if filtered_data:
            labels, data = zip(*filtered_data)
        else:
            labels, data = [], []
    else:
        # Use most common selections
        most_common = selection_counts.most_common()
        labels, data = zip(*most_common) if most_common else ([], [])
    
    return list(labels), list(data), valid_responses

def filter_employed_only(filtered_df):
    """Filter to exclude 'Tidak, sedang mencari pekerjaan' from employment status"""
    employment_col = find_column_smart(filtered_df, ['employment_status'])
    if employment_col and employment_col in filtered_df.columns:
        # FIXED: Exclude unemployed people
        employed_df = filtered_df[filtered_df[employment_col] != 'Tidak, sedang mencari pekerjaan'].copy()
        logger.info(f"🔄 Employed filter: {len(filtered_df)} -> {len(employed_df)} (excluded 'Tidak, sedang mencari pekerjaan')")
        return employed_df
    return filtered_df

def filter_gig_interested_only(filtered_df):
    """Filter to exclude 'Tidak berminat' from gig economy questions"""
    gig_col = find_column_smart(filtered_df, ['gig_economy'])
    if gig_col and gig_col in filtered_df.columns:
        # FIXED: Exclude not interested in gig economy
        gig_interested_df = filtered_df[~filtered_df[gig_col].str.contains('Tidak berminat', case=False, na=False)].copy()
        logger.info(f"🔄 Gig interested filter: {len(filtered_df)} -> {len(gig_interested_df)} (excluded 'Tidak berminat')")
        return gig_interested_df
    return filtered_df

def createApp():
    """Factory function that returns the existing app instance"""
    return app

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/dashboard') 
def dashboard():
    return render_template('dashboard.html')

# ===== EXISTING GRAPHS (1-8) =====

# 1. Employment Status API
@app.route('/api/employment-status')
def employment_status():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        employment_col = find_column_smart(filtered_df, ['employment_status'])
        
        if employment_col is None:
            logger.error(f"Employment status column not found")
            return safe_api_response('Employment status column not found', False)
        
        data = filtered_df[employment_col].value_counts()
        total = len(filtered_df)
        
        if total == 0:
            return safe_api_response('No data available after filtering', False)
        
        # Calculate employment metrics
        employed_keywords = ['ya', 'bekerja', 'employed', 'working']
        unemployed_keywords = ['tidak', 'mencari', 'unemployed', 'jobless']
        
        employed_count = 0
        unemployed_count = 0
        
        for status, count in data.items():
            status_lower = str(status).lower()
            if any(keyword in status_lower for keyword in employed_keywords):
                employed_count += count
            elif any(keyword in status_lower for keyword in unemployed_keywords):
                unemployed_count += count
        
        employment_rate = round((employed_count / total) * 100, 1) if total > 0 else 0
        unemployment_rate = round((unemployed_count / total) * 100, 1) if total > 0 else 0
        
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'status', 'count')
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'total_graduates': total,
                'total_responses': total,
                'employment_rate': employment_rate,
                'unemployment_rate': unemployment_rate,
                'employed_count': employed_count,
                'unemployed_count': unemployed_count
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in employment_status: {str(e)}")
        return safe_api_response(str(e), False)

# 2. Job Types API
@app.route('/api/job-types')
def job_types():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        job_type_col = find_column_smart(filtered_df, ['job_type'])
        
        if job_type_col is None:
            return safe_api_response('Job type column not found', False)
        
        clean_data = filtered_df[job_type_col].dropna()
        clean_data = clean_data[clean_data != 'Tidak Dinyatakan']
        
        if len(clean_data) == 0:
            return safe_api_response('No job type data available after filtering', False)
            
        data = clean_data.value_counts()
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'job_type', 'count')
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'total_responses': len(clean_data),
                'most_common_type': str(data.idxmax()) if len(data) > 0 else 'N/A'
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in job_types: {str(e)}")
        return safe_api_response(str(e), False)

# 3. Time to Employment API
@app.route('/api/time-to-employment')
def time_to_employment():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        time_col = find_column_smart(filtered_df, ['time_to_employment'])
        
        if time_col is None:
            return safe_api_response('Time to employment column not found', False)
        
        employed_df = filtered_df[filtered_df[time_col].notna() & (filtered_df[time_col] != 'Tidak Dinyatakan')]
        
        if len(employed_df) == 0:
            return safe_api_response('No employment time data available after filtering', False)
        
        data = employed_df[time_col].value_counts()
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'period', 'count')
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'total_employed_surveyed': len(employed_df),
                'total_responses': len(employed_df),
                'quick_employment_rate': round((data.iloc[0] / len(employed_df)) * 100, 1) if len(data) > 0 else 0
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in time_to_employment: {str(e)}")
        return safe_api_response(str(e), False)

# 4. Graduates by Field and Year API
@app.route('/api/graduates-by-field-year')
def graduates_by_field_year():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        # For field-year analysis, we don't filter by year since that's what we're analyzing
        temp_filters = filters.copy()
        temp_filters['year'] = None
        filtered_df = apply_filters(df, temp_filters)
        
        field_col = find_column_smart(filtered_df, ['field_of_study'])
        year_col = find_column_smart(filtered_df, ['graduation_year'])
        
        if field_col is None or year_col is None:
            return safe_api_response('Required columns not found', False)
        
        clean_df = filtered_df[[field_col, year_col]].dropna()
        clean_df = clean_df[clean_df[field_col] != 'Tidak Dinyatakan']
        clean_df = clean_df[clean_df[year_col] != 'Tidak Dinyatakan']
        
        if len(clean_df) == 0:
            return safe_api_response('No field-year data available after filtering', False)
        
        cross_tab = pd.crosstab(clean_df[year_col], clean_df[field_col])
        
        chart_data = {
            'labels': [str(year) for year in sorted(cross_tab.index)],
            'datasets': []
        }
        
        colors_list = ['#30475E', '#F05454', '#10b981', '#3B82F6', '#8B5CF6', '#F59E0B', '#06b6d4', '#84cc16']
        
        for i, field in enumerate(cross_tab.columns):
            chart_data['datasets'].append({
                'label': str(field),
                'data': [int(val) for val in cross_tab[field].tolist()],
                'backgroundColor': colors_list[i % len(colors_list)],
                'borderColor': colors_list[i % len(colors_list)],
                'borderWidth': 1
            })
        
        # Enhanced table data
        table_data = []
        for year in sorted(cross_tab.index):
            row = {'year': str(year)}
            total_year = cross_tab.loc[year].sum()
            for field in cross_tab.columns:
                row[str(field)] = {
                    'count': int(cross_tab.loc[year, field]),
                    'percentage': round((cross_tab.loc[year, field] / total_year) * 100, 1) if total_year > 0 else 0
                }
            row['total'] = int(total_year)
            table_data.append(row)
        
        total_graduates = len(clean_df)
        
        result = {
            'chart_data': chart_data,
            'table_data': table_data,
            'analysis': {
                'total_years_covered': len(cross_tab.index),
                'total_fields': len(cross_tab.columns),
                'total_graduates': total_graduates,
                'total_responses': total_graduates,
                'peak_year': str(cross_tab.sum(axis=1).idxmax()) if len(cross_tab) > 0 else 'N/A',
                'most_popular_field': str(cross_tab.sum(axis=0).idxmax()) if len(cross_tab.columns) > 0 else 'N/A'
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in graduates_by_field_year: {str(e)}")
        return safe_api_response(str(e), False)

# 5. Current Salary by Field API
@app.route('/api/current-salary-by-field')
def current_salary_by_field():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        
        salary_col = find_column_smart(filtered_df, ['current_salary'])
        field_col = find_column_smart(filtered_df, ['field_of_study'])
        
        if salary_col is None or field_col is None:
            return safe_api_response('Required columns not found', False)
        
        working_df = filtered_df[[salary_col, field_col]].dropna()
        working_df = working_df[working_df[salary_col] != 'Tidak Dinyatakan']
        working_df = working_df[working_df[field_col] != 'Tidak Dinyatakan']
        
        if len(working_df) == 0:
            return safe_api_response('No salary data available after filtering', False)
        
        cross_tab = pd.crosstab(working_df[field_col], working_df[salary_col])
        
        chart_data = {
            'labels': [str(field) for field in cross_tab.index.tolist()],
            'datasets': []
        }
        
        salary_colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6']
        
        for i, salary_range in enumerate(cross_tab.columns):
            chart_data['datasets'].append({
                'label': str(salary_range),
                'data': [int(val) for val in cross_tab[salary_range].tolist()],
                'backgroundColor': salary_colors[i % len(salary_colors)],
                'borderColor': salary_colors[i % len(salary_colors)],
                'borderWidth': 1
            })
        
        # Enhanced table data
        table_data = []
        for field in cross_tab.index:
            row = {'field': str(field)}
            total_field = cross_tab.loc[field].sum()
            for salary_range in cross_tab.columns:
                row[str(salary_range)] = {
                    'count': int(cross_tab.loc[field, salary_range]),
                    'percentage': round((cross_tab.loc[field, salary_range] / total_field) * 100, 1) if total_field > 0 else 0
                }
            row['total'] = int(total_field)
            table_data.append(row)
        
        result = {
            'chart_data': chart_data,
            'table_data': table_data,
            'analysis': {
                'total_working_graduates': len(working_df),
                'total_responses': len(working_df),
                'fields_analyzed': len(cross_tab.index)
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in current_salary_by_field: {str(e)}")
        return safe_api_response(str(e), False)

# 6. Salary Comparison API
@app.route('/api/salary-comparison')
def salary_comparison():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        
        current_salary_col = find_column_smart(filtered_df, ['current_salary'])
        expected_salary_col = find_column_smart(filtered_df, ['expected_salary'])
        
        if not current_salary_col or not expected_salary_col:
            return safe_api_response('Salary comparison columns not found', False)
        
        # Get salary data
        current_data = filtered_df[current_salary_col].dropna().value_counts()
        expected_data = filtered_df[expected_salary_col].dropna().value_counts()
        
        # Combine labels and ensure consistent ordering
        all_labels = sorted(list(set(current_data.index.tolist() + expected_data.index.tolist())))
        
        current_values = [int(current_data.get(label, 0)) for label in all_labels]
        expected_values = [int(expected_data.get(label, 0)) for label in all_labels]
        
        # Create table data for comparison
        table_data = []
        for i, label in enumerate(all_labels):
            table_data.append({
                'salary_range': str(label),
                'current_count': current_values[i],
                'expected_count': expected_values[i],
                'difference': current_values[i] - expected_values[i]
            })
        
        current_responses = len(filtered_df[current_salary_col].dropna())
        expected_responses = len(filtered_df[expected_salary_col].dropna())
        
        result = {
            'chart_data': {
                'labels': all_labels,
                'datasets': [
                    {
                        'label': 'Gaji Semasa',
                        'data': current_values,
                        'backgroundColor': '#30475E',
                        'borderColor': '#30475E',
                        'borderWidth': 1
                    },
                    {
                        'label': 'Gaji Jangkaan',
                        'data': expected_values,
                        'backgroundColor': '#F05454',
                        'borderColor': '#F05454',
                        'borderWidth': 1
                    }
                ]
            },
            'table_data': table_data,
            'analysis': {
                'current_responses': current_responses,
                'expected_responses': expected_responses,
                'total_responses': max(current_responses, expected_responses)
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in salary_comparison: {str(e)}")
        return safe_api_response(str(e), False)

# 7. Out-of-Field Analysis API
@app.route('/api/out-of-field-analysis')
def out_of_field_analysis():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        
        job_type_col = find_column_smart(filtered_df, ['job_type'])
        reason_col = find_column_smart(filtered_df, ['out_of_field_reason'])
        academic_skills_col = find_column_smart(filtered_df, ['academic_skills_needed'])
        
        if not job_type_col:
            return safe_api_response('Job type column not found', False)
        
        # Filter for out-of-field workers
        out_of_field_mask = filtered_df[job_type_col].str.contains('luar bidang', case=False, na=False)
        out_of_field_df = filtered_df[out_of_field_mask]
        
        result = {
            'job_types': {},
            'reasons': {},
            'academic_skills': {},
            'summary': {
                'total_out_of_field': len(out_of_field_df),
                'percentage_of_total': round((len(out_of_field_df) / len(filtered_df)) * 100, 1) if len(filtered_df) > 0 else 0,
                'total_graduates': len(filtered_df),
                'total_responses': len(filtered_df)
            }
        }
        
        # Job types data (focus on out-of-field types)
        if len(out_of_field_df) > 0:
            job_types_data = out_of_field_df[job_type_col].value_counts()
            result['job_types'] = {
                'labels': [str(label) for label in job_types_data.index.tolist()],
                'data': [int(val) for val in job_types_data.values.tolist()],
                'table_data': create_table_data(
                    job_types_data.index.tolist(), 
                    job_types_data.values.tolist(), 
                    'job_type', 'count'
                )
            }
        
        # Reasons data
        if reason_col and reason_col in filtered_df.columns:
            reasons_clean = filtered_df[reason_col].dropna()
            reasons_clean = reasons_clean[reasons_clean != 'Tidak Dinyatakan']
            if len(reasons_clean) > 0:
                reasons_data = reasons_clean.value_counts()
                result['reasons'] = {
                    'labels': [str(label) for label in reasons_data.index.tolist()],
                    'data': [int(val) for val in reasons_data.values.tolist()],
                    'table_data': create_table_data(
                        reasons_data.index.tolist(), 
                        reasons_data.values.tolist(), 
                        'reason', 'count'
                    )
                }
        
        # Academic skills needed
        if academic_skills_col and academic_skills_col in filtered_df.columns:
            skills_clean = filtered_df[academic_skills_col].dropna()
            skills_clean = skills_clean[skills_clean != 'Tidak Dinyatakan']
            if len(skills_clean) > 0:
                skills_data = skills_clean.value_counts()
                result['academic_skills'] = {
                    'labels': [str(label) for label in skills_data.index.tolist()],
                    'data': [int(val) for val in skills_data.values.tolist()],
                    'table_data': create_table_data(
                        skills_data.index.tolist(), 
                        skills_data.values.tolist(), 
                        'academic_skills_needed', 'count'
                    )
                }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in out_of_field_analysis: {str(e)}")
        return safe_api_response(str(e), False)

# 8. Job Challenges API
@app.route('/api/job-challenges')
def job_challenges():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        challenges_col = find_column_smart(filtered_df, ['job_challenges'])
        
        if challenges_col is None:
            return safe_api_response('Challenges column not found', False)
        
        clean_data = filtered_df[challenges_col].dropna()
        clean_data = clean_data[clean_data != 'Tidak Dinyatakan']
        
        if len(clean_data) == 0:
            return safe_api_response('No challenges data available after filtering', False)
        
        # Process checkbox data
        labels, data, total_responses = process_checkbox_data(clean_data)
        
        # Sort by count (highest first)
        if labels and data:
            sorted_data = sorted(zip(labels, data), key=lambda x: x[1], reverse=True)
            labels, data = zip(*sorted_data)
            labels, data = list(labels), list(data)
        
        total_individual_challenges = sum(data) if data else 0
        
        table_data = create_table_data(labels, data, 'challenge', 'count')
        
        result = {
            'chart_data': {
                'labels': labels,
                'data': data
            },
            'table_data': table_data,
            'analysis': {
                'top_challenge': labels[0] if labels else 'N/A',
                'top_challenge_count': data[0] if data else 0,
                'total_survey_responses': total_responses,
                'total_responses': total_responses,
                'total_individual_challenges': total_individual_challenges,
                'average_challenges_per_person': round(total_individual_challenges / total_responses, 1) if total_responses > 0 else 0,
                'diversity_of_challenges': len(labels)
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in job_challenges: {str(e)}")
        return safe_api_response(str(e), False)

# ===== NEW GRAPHS (9-19) - MISSING FROM ORIGINAL =====

# 9. NEW: Financing Advantage (#11)
@app.route('/api/financing-advantage')
def financing_advantage():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        financing_col = find_column_smart(filtered_df, ['financing_advantage'])
        
        if financing_col is None:
            return safe_api_response('Financing advantage column not found', False)
        
        clean_data = filtered_df[financing_col].dropna()
        clean_data = clean_data[clean_data != 'Tidak Dinyatakan']
        
        if len(clean_data) == 0:
            return safe_api_response('No financing advantage data available after filtering', False)
        
        data = clean_data.value_counts()
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'advantage', 'count')
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'total_responses': len(clean_data),
                'positive_response_rate': round((data.get('Ya', 0) / len(clean_data)) * 100, 1) if len(clean_data) > 0 else 0
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in financing_advantage: {str(e)}")
        return safe_api_response(str(e), False)

# 10. NEW: Success Factors with Employment Filter (#16)
@app.route('/api/success-factors')
def success_factors():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        # FIXED: Filter out unemployed people as requested
        filtered_df = filter_employed_only(filtered_df)
        
        success_col = find_column_smart(filtered_df, ['success_factors'])
        
        if success_col is None:
            return safe_api_response('Success factors column not found', False)
        
        clean_data = filtered_df[success_col].dropna()
        clean_data_list = []
        for item in clean_data:
            if item != 'Tidak Dinyatakan' and str(item).strip() != '':
                clean_data_list.append(item)
        
        if len(clean_data_list) == 0:
            return safe_api_response('No success factors data available after filtering', False)
        
        # Process checkbox data
        labels, data, total_responses = process_checkbox_data(clean_data_list)
        
        # Sort by count (highest first)
        if labels and data:
            sorted_data = sorted(zip(labels, data), key=lambda x: x[1], reverse=True)
            labels, data = zip(*sorted_data)
            labels, data = list(labels), list(data)
        
        table_data = create_table_data(labels, data, 'success_factor', 'count')
        
        result = {
            'chart_data': {
                'labels': labels,
                'data': data
            },
            'table_data': table_data,
            'analysis': {
                'total_responses': total_responses,
                'top_factor': labels[0] if labels else 'N/A',
                'total_individual_factors': sum(data) if data else 0,
                'note': 'Excluded unemployed respondents'
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in success_factors: {str(e)}")
        return safe_api_response(str(e), False)

# 11-15. NEW: Employability Impact Factors (#25-29)
@app.route('/api/li-impact')
def li_impact():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        li_col = find_column_smart(filtered_df, ['li_impact'])
        
        if li_col is None:
            return safe_api_response('LI impact column not found', False)
        
        clean_data = filtered_df[li_col].dropna()
        
        if len(clean_data) == 0:
            return safe_api_response('No LI impact data available after filtering', False)
        
        data = clean_data.value_counts().sort_index()
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'scale', 'count')
        
        # Calculate average impact
        numeric_data = pd.to_numeric(clean_data, errors='coerce').dropna()
        avg_impact = round(numeric_data.mean(), 2) if len(numeric_data) > 0 else 0
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'total_responses': len(clean_data),
                'average_impact': avg_impact,
                'scale_description': '1=Very Low, 5=Very High'
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in li_impact: {str(e)}")
        return safe_api_response(str(e), False)

@app.route('/api/communication-impact')
def communication_impact():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        comm_col = find_column_smart(filtered_df, ['communication_impact'])
        
        if comm_col is None:
            return safe_api_response('Communication impact column not found', False)
        
        clean_data = filtered_df[comm_col].dropna()
        
        if len(clean_data) == 0:
            return safe_api_response('No communication impact data available after filtering', False)
        
        data = clean_data.value_counts().sort_index()
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'scale', 'count')
        
        # Calculate average impact
        numeric_data = pd.to_numeric(clean_data, errors='coerce').dropna()
        avg_impact = round(numeric_data.mean(), 2) if len(numeric_data) > 0 else 0
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'total_responses': len(clean_data),
                'average_impact': avg_impact,
                'scale_description': '1=Very Low, 5=Very High'
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in communication_impact: {str(e)}")
        return safe_api_response(str(e), False)

@app.route('/api/technical-impact')
def technical_impact():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        tech_col = find_column_smart(filtered_df, ['technical_impact'])
        
        if tech_col is None:
            return safe_api_response('Technical impact column not found', False)
        
        clean_data = filtered_df[tech_col].dropna()
        
        if len(clean_data) == 0:
            return safe_api_response('No technical impact data available after filtering', False)
        
        data = clean_data.value_counts().sort_index()
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'scale', 'count')
        
        # Calculate average impact
        numeric_data = pd.to_numeric(clean_data, errors='coerce').dropna()
        avg_impact = round(numeric_data.mean(), 2) if len(numeric_data) > 0 else 0
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'total_responses': len(clean_data),
                'average_impact': avg_impact,
                'scale_description': '1=Very Low, 5=Very High'
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in technical_impact: {str(e)}")
        return safe_api_response(str(e), False)

@app.route('/api/networking-impact')
def networking_impact():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        network_col = find_column_smart(filtered_df, ['networking_impact'])
        
        if network_col is None:
            return safe_api_response('Networking impact column not found', False)
        
        clean_data = filtered_df[network_col].dropna()
        
        if len(clean_data) == 0:
            return safe_api_response('No networking impact data available after filtering', False)
        
        data = clean_data.value_counts().sort_index()
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'scale', 'count')
        
        # Calculate average impact
        numeric_data = pd.to_numeric(clean_data, errors='coerce').dropna()
        avg_impact = round(numeric_data.mean(), 2) if len(numeric_data) > 0 else 0
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'total_responses': len(clean_data),
                'average_impact': avg_impact,
                'scale_description': '1=Very Low, 5=Very High'
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in networking_impact: {str(e)}")
        return safe_api_response(str(e), False)

@app.route('/api/academic-impact')
def academic_impact():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        academic_col = find_column_smart(filtered_df, ['academic_impact'])
        
        if academic_col is None:
            return safe_api_response('Academic impact column not found', False)
        
        clean_data = filtered_df[academic_col].dropna()
        
        if len(clean_data) == 0:
            return safe_api_response('No academic impact data available after filtering', False)
        
        data = clean_data.value_counts().sort_index()
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'scale', 'count')
        
        # Calculate average impact
        numeric_data = pd.to_numeric(clean_data, errors='coerce').dropna()
        avg_impact = round(numeric_data.mean(), 2) if len(numeric_data) > 0 else 0
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'total_responses': len(clean_data),
                'average_impact': avg_impact,
                'scale_description': '1=Very Low, 5=Very High'
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in academic_impact: {str(e)}")
        return safe_api_response(str(e), False)

# ===== GIG ECONOMY GRAPHS (#40-48) =====

# 16. NEW: Entrepreneurship Training (#40)
@app.route('/api/entrepreneurship-training')
def entrepreneurship_training():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        training_col = find_column_smart(filtered_df, ['entrepreneurship_training'])
        
        if training_col is None:
            return safe_api_response('Entrepreneurship training column not found', False)
        
        clean_data = filtered_df[training_col].dropna()
        clean_data = clean_data[clean_data != 'Tidak Dinyatakan']
        
        if len(clean_data) == 0:
            return safe_api_response('No entrepreneurship training data available after filtering', False)
        
        data = clean_data.value_counts()
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'training_available', 'count')
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'total_responses': len(clean_data),
                'training_availability_rate': round((data.get('Ya', 0) / len(clean_data)) * 100, 1) if len(clean_data) > 0 else 0
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in entrepreneurship_training: {str(e)}")
        return safe_api_response(str(e), False)

# 17. NEW: University Gig Programs (#41)
@app.route('/api/uni-gig-programs')
def uni_gig_programs():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        programs_col = find_column_smart(filtered_df, ['uni_gig_programs'])
        
        if programs_col is None:
            return safe_api_response('University gig programs column not found', False)
        
        clean_data = filtered_df[programs_col].dropna()
        clean_data = clean_data[clean_data != 'Tidak Dinyatakan']
        
        if len(clean_data) == 0:
            return safe_api_response('No university gig programs data available after filtering', False)
        
        data = clean_data.value_counts()
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'program_status', 'count')
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'total_responses': len(clean_data),
                'program_awareness_rate': round((1 - data.get('Tidak, saya tidak pernah dengar tentang program seperti ini.', 0) / len(clean_data)) * 100, 1) if len(clean_data) > 0 else 0
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in uni_gig_programs: {str(e)}")
        return safe_api_response(str(e), False)

# 18. NEW: Program Helpful (#42)
@app.route('/api/program-helpful')
def program_helpful():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        
        # Filter out those who said they never heard of programs
        uni_programs_col = find_column_smart(filtered_df, ['uni_gig_programs'])
        if uni_programs_col:
            filtered_df = filtered_df[filtered_df[uni_programs_col] != 'Tidak, saya tidak pernah dengar tentang program seperti ini.']
        
        helpful_col = find_column_smart(filtered_df, ['program_helpful'])
        
        if helpful_col is None:
            return safe_api_response('Program helpful column not found', False)
        
        clean_data = filtered_df[helpful_col].dropna()
        clean_data = clean_data[clean_data != 'Tidak Dinyatakan']
        
        if len(clean_data) == 0:
            return safe_api_response('No program helpful data available after filtering', False)
        
        data = clean_data.value_counts()
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'helpful_status', 'count')
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'total_responses': len(clean_data),
                'helpfulness_rate': round((data.get('Ya', 0) / len(clean_data)) * 100, 1) if len(clean_data) > 0 else 0,
                'note': 'Excludes those who never heard of programs'
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in program_helpful: {str(e)}")
        return safe_api_response(str(e), False)

# 19. NEW: Gig Reasons (#43) - WITH GIG FILTER
@app.route('/api/gig-reasons')
def gig_reasons():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        # FIXED: Filter out those not interested in gig economy
        filtered_df = filter_gig_interested_only(filtered_df)
        
        reasons_col = find_column_smart(filtered_df, ['gig_reasons'])
        
        if reasons_col is None:
            return safe_api_response('Gig reasons column not found', False)
        
        clean_data = filtered_df[reasons_col].dropna()
        clean_data_list = []
        for item in clean_data:
            if item != 'Tidak Dinyatakan' and str(item).strip() != '' and 'Tidak relevan' not in str(item):
                clean_data_list.append(item)
        
        if len(clean_data_list) == 0:
            return safe_api_response('No gig reasons data available after filtering', False)
        
        # Process checkbox data
        labels, data, total_responses = process_checkbox_data(clean_data_list)
        
        # Sort by count (highest first)
        if labels and data:
            sorted_data = sorted(zip(labels, data), key=lambda x: x[1], reverse=True)
            labels, data = zip(*sorted_data)
            labels, data = list(labels), list(data)
        
        table_data = create_table_data(labels, data, 'reason', 'count')
        
        result = {
            'chart_data': {
                'labels': labels,
                'data': data
            },
            'table_data': table_data,
            'analysis': {
                'total_responses': total_responses,
                'top_reason': labels[0] if labels else 'N/A',
                'total_individual_reasons': sum(data) if data else 0,
                'note': 'Excludes those not interested in gig economy'
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in gig_reasons: {str(e)}")
        return safe_api_response(str(e), False)

# 20. NEW: Gig Skills Source (#44) - WITH GIG FILTER
@app.route('/api/gig-skills-source')
def gig_skills_source():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        # FIXED: Filter out those not interested in gig economy
        filtered_df = filter_gig_interested_only(filtered_df)
        
        skills_col = find_column_smart(filtered_df, ['gig_skills_source'])
        
        if skills_col is None:
            return safe_api_response('Gig skills source column not found', False)
        
        clean_data = filtered_df[skills_col].dropna()
        clean_data_list = []
        for item in clean_data:
            if item != 'Tidak Dinyatakan' and str(item).strip() != '':
                clean_data_list.append(item)
        
        if len(clean_data_list) == 0:
            return safe_api_response('No gig skills source data available after filtering', False)
        
        # Process checkbox data
        labels, data, total_responses = process_checkbox_data(clean_data_list)
        
        # Sort by count (highest first)
        if labels and data:
            sorted_data = sorted(zip(labels, data), key=lambda x: x[1], reverse=True)
            labels, data = zip(*sorted_data)
            labels, data = list(labels), list(data)
        
        table_data = create_table_data(labels, data, 'skills_source', 'count')
        
        result = {
            'chart_data': {
                'labels': labels,
                'data': data
            },
            'table_data': table_data,
            'analysis': {
                'total_responses': total_responses,
                'top_source': labels[0] if labels else 'N/A',
                'total_individual_sources': sum(data) if data else 0,
                'note': 'Excludes those not interested in gig economy'
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in gig_skills_source: {str(e)}")
        return safe_api_response(str(e), False)

# 21. NEW: Gig Challenges (#45) - WITH GIG FILTER
@app.route('/api/gig-challenges')
def gig_challenges():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        # FIXED: Filter out those not interested in gig economy
        filtered_df = filter_gig_interested_only(filtered_df)
        
        challenges_col = find_column_smart(filtered_df, ['gig_challenges'])
        
        if challenges_col is None:
            return safe_api_response('Gig challenges column not found', False)
        
        clean_data = filtered_df[challenges_col].dropna()
        clean_data_list = []
        for item in clean_data:
            if item != 'Tidak Dinyatakan' and str(item).strip() != '':
                clean_data_list.append(item)
        
        if len(clean_data_list) == 0:
            return safe_api_response('No gig challenges data available after filtering', False)
        
        # Process checkbox data
        labels, data, total_responses = process_checkbox_data(clean_data_list)
        
        # Sort by count (highest first)
        if labels and data:
            sorted_data = sorted(zip(labels, data), key=lambda x: x[1], reverse=True)
            labels, data = zip(*sorted_data)
            labels, data = list(labels), list(data)
        
        table_data = create_table_data(labels, data, 'challenge', 'count')
        
        result = {
            'chart_data': {
                'labels': labels,
                'data': data
            },
            'table_data': table_data,
            'analysis': {
                'total_responses': total_responses,
                'top_challenge': labels[0] if labels else 'N/A',
                'total_individual_challenges': sum(data) if data else 0,
                'note': 'Excludes those not interested in gig economy'
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in gig_challenges: {str(e)}")
        return safe_api_response(str(e), False)

# 22. NEW: Support Needed (#46) - WITH GIG FILTER
@app.route('/api/support-needed')
def support_needed():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        # FIXED: Filter out those not interested in gig economy
        filtered_df = filter_gig_interested_only(filtered_df)
        
        support_col = find_column_smart(filtered_df, ['support_needed'])
        
        if support_col is None:
            return safe_api_response('Support needed column not found', False)
        
        clean_data = filtered_df[support_col].dropna()
        clean_data_list = []
        for item in clean_data:
            if item != 'Tidak Dinyatakan' and str(item).strip() != '' and 'Tidak relevan' not in str(item):
                clean_data_list.append(item)
        
        if len(clean_data_list) == 0:
            return safe_api_response('No support needed data available after filtering', False)
        
        # Process checkbox data
        labels, data, total_responses = process_checkbox_data(clean_data_list)
        
        # Sort by count (highest first)
        if labels and data:
            sorted_data = sorted(zip(labels, data), key=lambda x: x[1], reverse=True)
            labels, data = zip(*sorted_data)
            labels, data = list(labels), list(data)
        
        table_data = create_table_data(labels, data, 'support_type', 'count')
        
        result = {
            'chart_data': {
                'labels': labels,
                'data': data
            },
            'table_data': table_data,
            'analysis': {
                'total_responses': total_responses,
                'top_need': labels[0] if labels else 'N/A',
                'total_individual_support': sum(data) if data else 0,
                'note': 'Excludes those not interested in gig economy'
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in support_needed: {str(e)}")
        return safe_api_response(str(e), False)

# 23. NEW: Gig Income (#47) - WITH GIG FILTER
@app.route('/api/gig-income')
def gig_income():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        # FIXED: Filter out those not interested in gig economy
        filtered_df = filter_gig_interested_only(filtered_df)
        
        income_col = find_column_smart(filtered_df, ['gig_income'])
        
        if income_col is None:
            return safe_api_response('Gig income column not found', False)
        
        clean_data = filtered_df[income_col].dropna()
        clean_data = clean_data[clean_data != 'Tidak Dinyatakan']
        clean_data = clean_data[~clean_data.str.contains('Tidak relevan', case=False, na=False)]
        
        if len(clean_data) == 0:
            return safe_api_response('No gig income data available after filtering', False)
        
        data = clean_data.value_counts()
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'income_range', 'count')
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'total_responses': len(clean_data),
                'most_common_range': str(data.idxmax()) if len(data) > 0 else 'N/A',
                'note': 'Excludes those not interested in gig economy'
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in gig_income: {str(e)}")
        return safe_api_response(str(e), False)

# 24. NEW: Gig vs Permanent Job (#48) - WITH GIG FILTER
@app.route('/api/gig-vs-permanent')
def gig_vs_permanent():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        # FIXED: Filter out those not interested in gig economy
        filtered_df = filter_gig_interested_only(filtered_df)
        
        preference_col = find_column_smart(filtered_df, ['gig_vs_permanent'])
        
        if preference_col is None:
            return safe_api_response('Gig vs permanent preference column not found', False)
        
        clean_data = filtered_df[preference_col].dropna()
        clean_data = clean_data[clean_data != 'Tidak Dinyatakan']
        clean_data = clean_data[~clean_data.str.contains('Tidak relevan', case=False, na=False)]
        
        if len(clean_data) == 0:
            return safe_api_response('No gig vs permanent data available after filtering', False)
        
        data = clean_data.value_counts()
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'preference', 'count')
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'total_responses': len(clean_data),
                'permanent_job_preference_rate': round((data.get('Ya', 0) / len(clean_data)) * 100, 1) if len(clean_data) > 0 else 0,
                'note': 'Excludes those not interested in gig economy'
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in gig_vs_permanent: {str(e)}")
        return safe_api_response(str(e), False)

# ===== EXISTING UTILITY ENDPOINTS =====

@app.route('/api/employment-sectors')
def employment_sectors():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        sectors_col = find_column_smart(filtered_df, ['employment_sectors'])
        
        if sectors_col is None:
            return safe_api_response('Employment sectors column not found', False)
        
        clean_data = filtered_df[sectors_col].dropna()
        clean_data = clean_data[clean_data != 'Tidak Dinyatakan']
        
        if len(clean_data) == 0:
            return safe_api_response('No employment sectors data available after filtering', False)
        
        data = clean_data.value_counts()
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'sector', 'count')
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'total_responses': len(clean_data),
                'dominant_sector': str(data.idxmax()) if len(data) > 0 else 'N/A'
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in employment_sectors: {str(e)}")
        return safe_api_response(str(e), False)

@app.route('/api/summary-stats')
def summary_stats():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        total_graduates = len(filtered_df)
        
        if total_graduates == 0:
            return safe_api_response('No data available after filtering', False)
        
        # Employment rate calculation
        employment_col = find_column_smart(filtered_df, ['employment_status'])
        
        employed = 0
        if employment_col:
            employed_keywords = ['bekerja', 'employed', 'working', 'ya']
            for status in filtered_df[employment_col].dropna():
                if any(keyword in str(status).lower() for keyword in employed_keywords):
                    employed += 1
        
        employment_rate = (employed / total_graduates * 100) if total_graduates > 0 else 0
        
        # Other statistics
        field_col = find_column_smart(filtered_df, ['field_of_study'])
        fields_count = len(filtered_df[field_col].unique()) if field_col else 0
        
        year_col = find_column_smart(filtered_df, ['graduation_year'])
        year_range = ""
        if year_col:
            try:
                years = pd.to_numeric(filtered_df[year_col], errors='coerce').dropna()
                if len(years) > 0:
                    min_year = int(years.min())
                    max_year = int(years.max())
                    year_range = f"{min_year}-{max_year}" if min_year != max_year else str(min_year)
            except:
                year_range = "N/A"
        
        # Calculate data quality metrics
        completeness = round((filtered_df.count().sum() / (len(filtered_df) * len(filtered_df.columns))) * 100, 1) if len(filtered_df) > 0 else 0
        
        result = {
            'total_graduates': total_graduates,
            'employment_rate': round(employment_rate, 1),
            'fields_count': fields_count,
            'year_range': year_range,
            'employed_count': employed,
            'data_quality': {
                'completeness': completeness,
                'response_rate': 100,
                'filters_applied': sum(1 for v in filters.values() if v)
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in summary_stats: {str(e)}")
        return safe_api_response(str(e), False)

@app.route('/api/filter-options')
def filter_options():
    """Get available filter options"""
    try:
        field_col = find_column_smart(df, ['field_of_study'])
        year_col = find_column_smart(df, ['graduation_year'])
        employment_col = find_column_smart(df, ['employment_status'])
        institution_col = find_column_smart(df, ['institution'])
        
        options = {
            'fields': sorted(df[field_col].unique().tolist()) if field_col else [],
            'years': sorted(df[year_col].unique().tolist()) if year_col else [],
            'employment_types': sorted(df[employment_col].unique().tolist()) if employment_col else [],
            'institutions': sorted(df[institution_col].unique().tolist()) if institution_col else [],
            'genders': ['Lelaki', 'Perempuan']
        }
        
        return safe_api_response(options)
    except Exception as e:
        logger.error(f"❌ Error in filter_options: {str(e)}")
        return safe_api_response(str(e), False)

@app.route('/api/data-health')
def data_health():
    """Get data health and quality metrics"""
    try:
        health_metrics = {
            'total_records': len(df),
            'columns_count': len(df.columns),
            'missing_data_percentage': round((df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100, 2),
            'duplicate_records': df.duplicated().sum(),
            'data_types': df.dtypes.astype(str).to_dict(),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
            'last_updated': pd.Timestamp.now().isoformat()
        }
        
        return safe_api_response(health_metrics)
    except Exception as e:
        logger.error(f"❌ Error in data_health: {str(e)}")
        return safe_api_response(str(e), False)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return safe_api_response('Endpoint not found', False), 404

@app.errorhandler(500)
def internal_error(error):
    return safe_api_response('Internal server error', False), 500

if __name__ == '__main__':
    logger.info("🚀 Starting COMPLETE Graduate Analytics Dashboard with ALL 24 GRAPHS!")
    logger.info("🔗 Dashboard URL: http://localhost:5000")
    logger.info("📊 ALL REQUIRED GRAPHS SUPPORTED:")
    
    logger.info("   === ORIGINAL 8 GRAPHS ===")
    logger.info("   1. ✅ Employment Status - /api/employment-status")
    logger.info("   2. ✅ Job Types - /api/job-types")
    logger.info("   3. ✅ Time to Employment - /api/time-to-employment")
    logger.info("   4. ✅ Graduates by Field & Year - /api/graduates-by-field-year")
    logger.info("   5. ✅ Current Salary by Field - /api/current-salary-by-field")
    logger.info("   6. ✅ Salary Comparison - /api/salary-comparison")
    logger.info("   7. ✅ Out-of-Field Analysis - /api/out-of-field-analysis")
    logger.info("   8. ✅ Job Challenges - /api/job-challenges")
    
    logger.info("   === NEW REQUIRED GRAPHS ===")
    logger.info("   9. ✅ Financing Advantage (#11) - /api/financing-advantage")
    logger.info("   10. ✅ Success Factors (Employment Filter) (#16) - /api/success-factors")
    logger.info("   11. ✅ LI Impact (#25) - /api/li-impact")
    logger.info("   12. ✅ Communication Impact (#26) - /api/communication-impact")
    logger.info("   13. ✅ Technical Impact (#27) - /api/technical-impact")
    logger.info("   14. ✅ Networking Impact (#28) - /api/networking-impact")
    logger.info("   15. ✅ Academic Impact (#29) - /api/academic-impact")
    
    logger.info("   === GIG ECONOMY GRAPHS (WITH FILTERS) ===")
    logger.info("   16. ✅ Entrepreneurship Training (#40) - /api/entrepreneurship-training")
    logger.info("   17. ✅ University Gig Programs (#41) - /api/uni-gig-programs")
    logger.info("   18. ✅ Program Helpful (#42) - /api/program-helpful")
    logger.info("   19. ✅ Gig Reasons (#43) - /api/gig-reasons [EXCLUDES 'Tidak berminat']")
    logger.info("   20. ✅ Gig Skills Source (#44) - /api/gig-skills-source [EXCLUDES 'Tidak berminat']")
    logger.info("   21. ✅ Gig Challenges (#45) - /api/gig-challenges [EXCLUDES 'Tidak berminat']")
    logger.info("   22. ✅ Support Needed (#46) - /api/support-needed [EXCLUDES 'Tidak berminat']")
    logger.info("   23. ✅ Gig Income (#47) - /api/gig-income [EXCLUDES 'Tidak berminat']")
    logger.info("   24. ✅ Gig vs Permanent (#48) - /api/gig-vs-permanent [EXCLUDES 'Tidak berminat']")
    
    logger.info("\n🔄 SPECIAL FILTERS:")
    logger.info("   - Success Factors: EXCLUDES 'Tidak, sedang mencari pekerjaan'")
    logger.info("   - All Gig Economy graphs: EXCLUDES 'Tidak berminat' from gig participation")
    
    logger.info(f"\n📈 Real Data: Using CSV with {len(df)} rows and {len(df.columns)} columns")
    
    app.run(debug=True, port=5000, host='0.0.0.0')