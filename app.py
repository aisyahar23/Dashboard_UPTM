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

# Create comprehensive sample data with proper column names
def create_sample_data():
    np.random.seed(42)
    sample_size = 1000  # Increased sample size for better analysis
    
    return pd.DataFrame({
        # Employment Status
        'Adakah anda kini bekerja?': np.random.choice([
            'Ya, bekerja sepenuh masa', 
            'Tidak, sedang mencari pekerjaan', 
            'Ya, bekerja separuh masa'
        ], sample_size, p=[0.72, 0.18, 0.1]),
        
        # Job Types
        'Apakah jenis pekerjaan anda sekarang': np.random.choice([
            'Bekerja dalam bidang pengajian',
            'Bekerja di luar bidang pengajian', 
            'Pekerja ekonomi gig (Grab, Shopee, freelancer, dsb.)',
            'Tidak bekerja',
            'Mengusahakan perniagaan sendiri'
        ], sample_size, p=[0.45, 0.25, 0.15, 0.1, 0.05]),
        
        # Time to Employment
        'Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?': np.random.choice([
            'Kurang dari 3 bulan',
            '3-6 bulan', 
            '6-12 bulan',
            'Lebih dari 1 tahun'
        ], sample_size, p=[0.4, 0.3, 0.2, 0.1]),
        
        # Study Fields
        'Bidang pengajian utama anda? ': np.random.choice([
            'Teknologi Maklumat', 'Perniagaan', 'Kejuruteraan', 
            'Perakaunan', 'Pemasaran', 'Sains Komputer',
            'Pengurusan', 'Kewangan'
        ], sample_size),
        
        # Graduation Years
        'Tahun graduasi anda? ': np.random.choice([2020, 2021, 2022, 2023, 2024], sample_size),
        
        # Current Salary
        'Berapakah julat gaji bulanan anda sekarang?': np.random.choice([
            'RM1000-RM1999', 'RM2000-RM2999', 'RM3000-RM3999', 
            'RM4000-RM4999', 'RM5000-RM5999', 'RM6000 ke atas'
        ], sample_size, p=[0.15, 0.25, 0.25, 0.2, 0.1, 0.05]),
        
        # Expected Salary
        'Apakah jangkaan gaji permulaan yang anda anggap sesuai dengan kelulusan anda?': np.random.choice([
            'RM1000-RM1999', 'RM2000-RM2999', 'RM3000-RM3999', 
            'RM4000-RM4999', 'RM5000 ke atas'
        ], sample_size, p=[0.3, 0.35, 0.2, 0.1, 0.05]),
        
        # Out of field reasons
        'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?': np.random.choice([
            'Tiada peluang dalam bidang',
            'Gaji lebih tinggi di luar bidang',
            'Minat peribadi',
            'Peluang kerjaya lebih baik',
            'Lokasi kerja sesuai'
        ], sample_size),
        
        # Academic skills requirement
        'Jika anda bekerja di luar bidang pengajian, adakah pekerjaan tersebut masih memerlukan kemahiran akademik anda?': np.random.choice([
            'Ya', 'Tidak', 'Sebahagiannya'
        ], sample_size, p=[0.6, 0.2, 0.2]),
        
        # Job Challenges - Updated with 12 options
        'Apakah cabaran utama yang anda hadapi dalam mendapatkan pekerjaan?': np.random.choice([
            'Kekurangan pengalaman kerja',
            'Persaingan yang tinggi', 
            'Kemahiran tidak sesuai dengan keperluan industri',
            'Tiada peluang pekerjaan dalam bidang',
            'Gaji yang ditawarkan terlalu rendah',
            'Lokasi kerja tidak sesuai',
            'Kekurangan kemahiran soft skills',
            'Tiada networking yang kuat',
            'Proses temuduga yang sukar',
            'Kekurangan sijil profesional',
            'Masalah komunikasi',
            'Tiada pengalaman praktikal'
        ], sample_size),
        
        # Success Factors
        'Apakah faktor utama yang membantu anda mendapat pekerjaan tersebut?': np.random.choice([
            'Kemahiran komunikasi yang baik',
            'Pengalaman praktikal/internship',
            'Networking yang kuat',
            'Sijil profesional',
            'Prestasi akademik yang cemerlang',
            'Kemahiran teknikal yang relevan',
            'Kemahiran bahasa',
            'Sikap yang positif'
        ], sample_size),
        
        # Employment Sectors
        'Apakah sektor pekerjaan anda?': np.random.choice([
            'Sektor Swasta',
            'Sektor Kerajaan',
            'GLC (Government-Linked Companies)',
            'Syarikat Multinasional',
            'Startup/SME',
            'NGO/Nonprofit'
        ], sample_size, p=[0.4, 0.25, 0.15, 0.1, 0.08, 0.02]),
        
        # Professional Certifications
        'Adakah anda memiliki sijil profesional tambahan selain ijazah/diploma?': np.random.choice([
            'Ya', 'Tidak'
        ], sample_size, p=[0.3, 0.7]),
        
        # Internship
        'Adakah anda menjalani internship/praktikal sebelum tamat pengajian?': np.random.choice([
            'Ya', 'Tidak'
        ], sample_size, p=[0.65, 0.35]),
        
        # University Preparation
        'Sejauh mana anda bersetuju bahawa universiti telah menyediakan anda untuk pasaran kerja?': np.random.choice([
            'Sangat setuju', 'Setuju', 'Neutral', 'Tidak setuju', 'Sangat tidak setuju'
        ], sample_size, p=[0.2, 0.4, 0.25, 0.1, 0.05]),
        
        # Gig Economy
        'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?': np.random.choice([
            'Ya, aktif terlibat', 'Kadang-kadang', 'Tidak terlibat'
        ], sample_size, p=[0.25, 0.35, 0.4]),
        
        # Support Needed
        'Apakah bantuan atau sokongan yang anda rasa perlu untuk berjaya dalam keusahawanan dan ekonomi gig?': np.random.choice([
            'Latihan kemahiran',
            'Bantuan kewangan',
            'Bimbingan kerjaya',
            'Peluang networking',
            'Akses kepada peluang kerja',
            'Pembangunan keusahawanan'
        ], sample_size),
        
        # Gender
        'Jantina anda? ': np.random.choice(['Lelaki', 'Perempuan'], sample_size),
        
        # Age
        'Umur anda? ': np.random.randint(22, 35, sample_size),
        
        # Institution
        'Institusi pendidikan MARA yang anda hadiri? ': np.random.choice([
            'MARA Professional College',
            'MARA University of Technology',
            'MARA Skills Institute'
        ], sample_size)
    })

# Load data
try:
    df = pd.read_csv('SOAL_SELIDIK_GRADUATE.csv')
    logger.info("✅ CSV file loaded successfully!")
    logger.info(f"Data shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)}")
except FileNotFoundError:
    logger.warning("📁 CSV file not found. Creating sample data...")
    df = create_sample_data()
    logger.info(f"Sample data created with shape: {df.shape}")

def clean_data():
    global df
    df = df.fillna('Tidak Dinyatakan')
    logger.info(f"✅ Data processed successfully. Shape: {df.shape}")
    return df

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

# Enhanced column mapping
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
    'institution': 'Institusi pendidikan MARA yang anda hadiri? '
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

@app.route('/')
def index():
    return render_template('dashboard.html')

# 1. Enhanced Employment Status API
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
        
        # Create table data
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'status', 'count')
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'total_graduates': total,
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

# 2. Enhanced Job Types API
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

# 3. Enhanced Time to Employment API
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
                'quick_employment_rate': round((data.iloc[0] / len(employed_df)) * 100, 1) if len(data) > 0 else 0
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in time_to_employment: {str(e)}")
        return safe_api_response(str(e), False)

# 4. Enhanced Graduates by Field and Year API
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
        
        colors_list = ['#283E56', '#970747', '#1989AC', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#84cc16']
        
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
        
        result = {
            'chart_data': chart_data,
            'table_data': table_data,
            'analysis': {
                'total_years_covered': len(cross_tab.index),
                'total_fields': len(cross_tab.columns),
                'peak_year': str(cross_tab.sum(axis=1).idxmax()) if len(cross_tab) > 0 else 'N/A',
                'most_popular_field': str(cross_tab.sum(axis=0).idxmax()) if len(cross_tab.columns) > 0 else 'N/A'
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in graduates_by_field_year: {str(e)}")
        return safe_api_response(str(e), False)

# 5. Enhanced Current Salary by Field API
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
                'fields_analyzed': len(cross_tab.index)
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in current_salary_by_field: {str(e)}")
        return safe_api_response(str(e), False)

# 6. Enhanced Salary Comparison API
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
        
        result = {
            'chart_data': {
                'labels': all_labels,
                'datasets': [
                    {
                        'label': 'Current Salary',
                        'data': current_values,
                        'backgroundColor': '#1989AC',
                        'borderColor': '#1989AC',
                        'borderWidth': 1
                    },
                    {
                        'label': 'Expected Salary',
                        'data': expected_values,
                        'backgroundColor': '#970747',
                        'borderColor': '#970747',
                        'borderWidth': 1
                    }
                ]
            },
            'table_data': table_data,
            'analysis': {
                'current_responses': len(filtered_df[current_salary_col].dropna()),
                'expected_responses': len(filtered_df[expected_salary_col].dropna())
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in salary_comparison: {str(e)}")
        return safe_api_response(str(e), False)

# 7. Enhanced Out-of-Field Analysis API
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
                'total_graduates': len(filtered_df)
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

# 8. Enhanced Job Challenges API
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
        
        data = clean_data.value_counts()
        total = len(clean_data)
        
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'challenge', 'count')
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'top_challenge': str(data.idxmax()) if len(data) > 0 else 'N/A',
                'top_challenge_percentage': round((data.max() / total) * 100, 1) if len(data) > 0 else 0,
                'total_responses': total,
                'diversity_of_challenges': len(data)
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in job_challenges: {str(e)}")
        return safe_api_response(str(e), False)

# Enhanced Support APIs
@app.route('/api/certifications')
def certifications():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        cert_col = find_column_smart(filtered_df, ['professional_cert'])
        
        if cert_col is None:
            return safe_api_response('Certifications column not found', False)
        
        clean_data = filtered_df[cert_col].dropna()
        clean_data = clean_data[clean_data != 'Tidak Dinyatakan']
        
        if len(clean_data) == 0:
            return safe_api_response('No certifications data available after filtering', False)
        
        data = clean_data.value_counts()
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'certification_status', 'count')
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'certification_rate': round((data.get('Ya', 0) / len(clean_data)) * 100, 1),
                'total_responses': len(clean_data)
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in certifications: {str(e)}")
        return safe_api_response(str(e), False)

@app.route('/api/internship-impact')
def internship_impact():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        internship_col = find_column_smart(filtered_df, ['internship'])
        
        if internship_col is None:
            return safe_api_response('Internship column not found', False)
        
        clean_data = filtered_df[internship_col].dropna()
        clean_data = clean_data[clean_data != 'Tidak Dinyatakan']
        
        if len(clean_data) == 0:
            return safe_api_response('No internship data available after filtering', False)
        
        data = clean_data.value_counts()
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'internship_status', 'count')
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'internship_rate': round((data.get('Ya', 0) / len(clean_data)) * 100, 1),
                'total_responses': len(clean_data)
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in internship_impact: {str(e)}")
        return safe_api_response(str(e), False)

@app.route('/api/gig-economy')
def gig_economy():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        gig_col = find_column_smart(filtered_df, ['gig_economy'])
        
        if gig_col is None:
            return safe_api_response('Gig economy column not found', False)
        
        clean_data = filtered_df[gig_col].dropna()
        clean_data = clean_data[clean_data != 'Tidak Dinyatakan']
        
        if len(clean_data) == 0:
            return safe_api_response('No gig economy data available after filtering', False)
        
        data = clean_data.value_counts()
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'gig_participation', 'count')
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'active_participation': round((data.get('Ya, aktif terlibat', 0) / len(clean_data)) * 100, 1),
                'total_responses': len(clean_data)
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in gig_economy: {str(e)}")
        return safe_api_response(str(e), False)

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
        support_col = find_column_smart(filtered_df, ['support_needed'])
        
        if support_col is None:
            return safe_api_response('Support needed column not found', False)
        
        clean_data = filtered_df[support_col].dropna()
        clean_data = clean_data[clean_data != 'Tidak Dinyatakan']
        
        if len(clean_data) == 0:
            return safe_api_response('No support needed data available after filtering', False)
        
        data = clean_data.value_counts()
        table_data = create_table_data(data.index.tolist(), data.values.tolist(), 'support_type', 'count')
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': table_data,
            'analysis': {
                'top_need': str(data.idxmax()) if len(data) > 0 else 'N/A',
                'top_need_percentage': round((data.max() / len(clean_data)) * 100, 1) if len(data) > 0 else 0,
                'total_responses': len(clean_data)
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in support_needed: {str(e)}")
        return safe_api_response(str(e), False)

# Enhanced Summary Statistics API
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

# Additional utility endpoints
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
    logger.info("🚀 Starting Enhanced Graduate Analytics Dashboard...")
    logger.info("🔗 Dashboard URL: http://localhost:5000")
    logger.info("📊 All 8 required graphs supported with filtering:")
    logger.info("   1. ✅ Employment Status (Pie Chart)")
    logger.info("   2. ✅ Job Types (Bar Chart)")
    logger.info("   3. ✅ Time to Employment (Area Chart)")
    logger.info("   4. ✅ Graduates by Field & Year (Stacked Bar)")
    logger.info("   5. ✅ Current Salary by Field (Stacked Bar)")
    logger.info("   6. ✅ Salary Expectations vs Reality (Bar Chart)")
    logger.info("   7. ✅ Out-of-Field Analysis (Multiple Charts)")
    logger.info("   8. ✅ Job Search Challenges (Bar Chart)")
    logger.info("🔍 Enhanced filtering affects ALL graphs")
    logger.info("📊 Enhanced comparison mode available")
    logger.info("📋 Comprehensive table views for all charts")
    
    app.run(debug=True, port=5000, host='0.0.0.0')