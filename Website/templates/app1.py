from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
from collections import Counter
import json
import logging

app = Flask(__name__, template_folder='Website/templates', static_folder='Website/static')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create comprehensive sample data with proper column names
def create_sample_data():
    np.random.seed(42)
    sample_size = 500
    
    return pd.DataFrame({
        # Employment Status
        'Adakah anda kini bekerja?': np.random.choice([
            'Ya, bekerja sepenuh masa', 
            'Tidak, sedang mencari pekerjaan', 
            'Ya, bekerja separuh masa'
        ], sample_size, p=[0.7, 0.2, 0.1]),
        
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
        
        # Job Challenges - Updated with 12 options as checkbox items
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

@app.route('/')
def index():
    return render_template('dashboard.html')

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
            # Convert numpy types to Python native types
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

# Updated column mapping based on actual CSV structure
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
    # First try exact mapping
    for key in possible_keys:
        col = get_column(key)
        if col and col in df.columns:
            return col
    
    # Then try fuzzy matching
    all_possible_names = []
    for key in possible_keys:
        if key in COLUMN_MAPPING:
            all_possible_names.append(COLUMN_MAPPING[key])
        all_possible_names.append(key.replace('_', ' ').title())
    
    return find_column_fuzzy(df, all_possible_names)

# Apply global filters to dataframe
def apply_filters(data_df, filters):
    """Apply global filters to the dataframe"""
    filtered_df = data_df.copy()
    
    if filters.get('year'):
        year_col = find_column_smart(filtered_df, ['graduation_year'])
        if year_col:
            filtered_df = filtered_df[filtered_df[year_col].astype(str) == str(filters['year'])]
    
    if filters.get('field'):
        field_col = find_column_smart(filtered_df, ['field_of_study'])
        if field_col:
            filtered_df = filtered_df[filtered_df[field_col] == filters['field']]
    
    if filters.get('employment'):
        emp_col = find_column_smart(filtered_df, ['employment_status'])
        if emp_col:
            filtered_df = filtered_df[filtered_df[emp_col] == filters['employment']]
    
    if filters.get('gender'):
        gender_col = find_column_smart(filtered_df, ['gender'])
        if gender_col:
            filtered_df = filtered_df[filtered_df[gender_col] == filters['gender']]
    
    if filters.get('institution'):
        inst_col = find_column_smart(filtered_df, ['institution'])
        if inst_col:
            filtered_df = filtered_df[filtered_df[inst_col] == filters['institution']]
    
    return filtered_df

# 1. Employment Status API - Kadar Kebolehpasaran Graduan (Status Pekerjaan)
@app.route('/api/employment-status')
def employment_status():
    try:
        # Get filters from request
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        # Apply filters
        filtered_df = apply_filters(df, filters)
        
        employment_col = find_column_smart(filtered_df, ['employment_status'])
        
        if employment_col is None:
            logger.error(f"Employment status column not found. Available columns: {list(filtered_df.columns)}")
            return safe_api_response('Employment status column not found', False)
        
        logger.info(f"Using employment column: {employment_col}")
        data = filtered_df[employment_col].value_counts()
        total = len(filtered_df)
        
        detailed_data = []
        for status, count in data.items():
            percentage = (count / total) * 100 if total > 0 else 0
            detailed_data.append({
                'status': str(status),
                'count': int(count),
                'percentage': round(percentage, 1)
            })
        
        # Calculate metrics
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
        
        employment_rate = (employed_count / total) * 100 if total > 0 else 0
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': detailed_data,
            'analysis': {
                'total_graduates': total,
                'employment_rate': round(employment_rate, 1),
                'full_time_rate': round((employed_count / total) * 100, 1) if total > 0 else 0,
                'part_time_rate': 0,
                'unemployment_rate': round((unemployed_count / total) * 100, 1) if total > 0 else 0
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in employment_status: {str(e)}")
        return safe_api_response(str(e), False)

# 2. Job Types API - Kadar Kebolehpasaran Graduan (Jenis Pekerjaan)
@app.route('/api/job-types')
def job_types():
    try:
        # Get filters from request
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        # Apply filters
        filtered_df = apply_filters(df, filters)
        
        job_type_col = find_column_smart(filtered_df, ['job_type'])
        
        if job_type_col is None:
            logger.error(f"Job type column not found. Available columns: {list(filtered_df.columns)}")
            return safe_api_response('Job type column not found', False)
        
        logger.info(f"Using job type column: {job_type_col}")
        clean_data = filtered_df[job_type_col].dropna()
        clean_data = clean_data[clean_data != 'Tidak Dinyatakan']
        
        if len(clean_data) == 0:
            return safe_api_response('No job type data available', False)
            
        data = clean_data.value_counts()
        total = len(clean_data)
        
        detailed_data = []
        for job_type, count in data.items():
            percentage = (count / total) * 100
            detailed_data.append({
                'job_type': str(job_type),
                'count': int(count),
                'percentage': round(percentage, 1)
            })
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': detailed_data,
            'analysis': {
                'total_responses': total
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in job_types: {str(e)}")
        return safe_api_response(str(e), False)

# 3. Time to Employment API - Tempoh Mendapat Kerja
@app.route('/api/time-to-employment')
def time_to_employment():
    try:
        # Get filters from request
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        # Apply filters
        filtered_df = apply_filters(df, filters)
        
        time_col = find_column_smart(filtered_df, ['time_to_employment'])
        
        if time_col is None:
            logger.error(f"Time to employment column not found. Available columns: {list(filtered_df.columns)}")
            return safe_api_response('Time to employment column not found', False)
        
        logger.info(f"Using time column: {time_col}")
        employed_df = filtered_df[filtered_df[time_col].notna() & (filtered_df[time_col] != 'Tidak Dinyatakan')]
        
        if len(employed_df) == 0:
            return safe_api_response('No employment time data available', False)
        
        data = employed_df[time_col].value_counts()
        total_employed = len(employed_df)
        
        detailed_data = []
        for period, count in data.items():
            percentage = (count / total_employed) * 100
            detailed_data.append({
                'period': str(period),
                'count': int(count),
                'percentage': round(percentage, 1)
            })
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': detailed_data,
            'analysis': {
                'total_employed_surveyed': total_employed,
                'quick_employment_rate': round((data.iloc[0] / total_employed) * 100, 1) if len(data) > 0 else 0
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in time_to_employment: {str(e)}")
        return safe_api_response(str(e), False)

# 4. Field and Year API - Graduan Mengikut Bidang dan Tahun
@app.route('/api/graduates-by-field-year')
def graduates_by_field_year():
    try:
        # Get filters from request
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        # Apply filters (excluding year filter for this analysis)
        temp_filters = filters.copy()
        temp_filters['year'] = None  # Don't filter by year for year analysis
        filtered_df = apply_filters(df, temp_filters)
        
        field_col = find_column_smart(filtered_df, ['field_of_study'])
        year_col = find_column_smart(filtered_df, ['graduation_year'])
        
        if field_col is None or year_col is None:
            logger.error(f"Required columns not found. Field: {field_col}, Year: {year_col}")
            return safe_api_response('Required columns not found', False)
        
        logger.info(f"Using field column: {field_col}, year column: {year_col}")
        
        clean_df = filtered_df[[field_col, year_col]].dropna()
        clean_df = clean_df[clean_df[field_col] != 'Tidak Dinyatakan']
        clean_df = clean_df[clean_df[year_col] != 'Tidak Dinyatakan']
        
        if len(clean_df) == 0:
            return safe_api_response('No field-year data available', False)
        
        cross_tab = pd.crosstab(clean_df[year_col], clean_df[field_col])
        
        chart_data = {
            'labels': [str(year) for year in sorted(cross_tab.index)],
            'datasets': []
        }
        
        colors_list = ['#283E56', '#970747', '#1989AC', '#FEF4E8', '#667eea', '#764ba2', '#10b981', '#f59e0b']
        
        for i, field in enumerate(cross_tab.columns):
            chart_data['datasets'].append({
                'label': str(field),
                'data': [int(val) for val in cross_tab[field].tolist()],
                'backgroundColor': colors_list[i % len(colors_list)],
                'borderColor': colors_list[i % len(colors_list)],
                'borderWidth': 1
            })
        
        # Table data
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

# NEW: Out of Field Analysis API - Comprehensive Analysis
@app.route('/api/out-of-field-analysis')
def out_of_field_analysis():
    try:
        # Get filters from request
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        # Apply filters
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
        
        # Job types data
        if len(out_of_field_df) > 0:
            job_types_data = out_of_field_df[job_type_col].value_counts()
            result['job_types'] = {
                'labels': [str(label) for label in job_types_data.index.tolist()],
                'data': [int(val) for val in job_types_data.values.tolist()],
                'table_data': [
                    {
                        'job_type': str(job_type),
                        'count': int(count),
                        'percentage': round((count / len(out_of_field_df)) * 100, 1)
                    }
                    for job_type, count in job_types_data.items()
                ]
            }
        
        # Reasons data
        if reason_col and reason_col in out_of_field_df.columns and len(out_of_field_df) > 0:
            reasons_data = out_of_field_df[reason_col].dropna().value_counts()
            if len(reasons_data) > 0:
                result['reasons'] = {
                    'labels': [str(label) for label in reasons_data.index.tolist()],
                    'data': [int(val) for val in reasons_data.values.tolist()],
                    'table_data': [
                        {
                            'reason': str(reason),
                            'count': int(count),
                            'percentage': round((count / len(reasons_data)) * 100, 1)
                        }
                        for reason, count in reasons_data.items()
                    ]
                }
        
        # Academic skills needed
        if academic_skills_col and academic_skills_col in out_of_field_df.columns and len(out_of_field_df) > 0:
            skills_data = out_of_field_df[academic_skills_col].dropna().value_counts()
            if len(skills_data) > 0:
                result['academic_skills'] = {
                    'labels': [str(label) for label in skills_data.index.tolist()],
                    'data': [int(val) for val in skills_data.values.tolist()],
                    'table_data': [
                        {
                            'academic_skills_needed': str(skill),
                            'count': int(count),
                            'percentage': round((count / len(skills_data)) * 100, 1)
                        }
                        for skill, count in skills_data.items()
                    ]
                }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in out_of_field_analysis: {str(e)}")
        return safe_api_response(str(e), False)

# Job Challenges API - Updated with all 12 challenges
@app.route('/api/job-challenges')
def job_challenges():
    try:
        # Get filters from request
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        # Apply filters
        filtered_df = apply_filters(df, filters)
        
        challenges_col = find_column_smart(filtered_df, ['job_challenges'])
        
        if challenges_col is None:
            logger.error(f"Challenges column not found. Available columns: {list(filtered_df.columns)}")
            return safe_api_response('Challenges column not found', False)
        
        logger.info(f"Using challenges column: {challenges_col}")
        
        clean_data = filtered_df[challenges_col].dropna()
        clean_data = clean_data[clean_data != 'Tidak Dinyatakan']
        
        if len(clean_data) == 0:
            return safe_api_response('No challenges data available', False)
        
        data = clean_data.value_counts()
        total = len(clean_data)
        
        detailed_data = []
        for challenge, count in data.items():
            percentage = (count / total) * 100
            detailed_data.append({
                'challenge': str(challenge),
                'count': int(count),
                'percentage': round(percentage, 1)
            })
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': detailed_data,
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

# Continue with other existing APIs...
# (Include all the other API endpoints from the original code)

# Success Factors API
@app.route('/api/success-factors')
def success_factors():
    try:
        # Get filters from request
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        # Apply filters
        filtered_df = apply_filters(df, filters)
        
        factors_col = find_column_smart(filtered_df, ['success_factors'])
        
        if factors_col is None:
            return safe_api_response('Success factors column not found', False)
        
        clean_data = filtered_df[factors_col].dropna()
        clean_data = clean_data[clean_data != 'Tidak Dinyatakan']
        
        if len(clean_data) == 0:
            return safe_api_response('No success factors data available', False)
        
        data = clean_data.value_counts()
        total = len(clean_data)
        
        detailed_data = []
        for factor, count in data.items():
            percentage = (count / total) * 100
            detailed_data.append({
                'factor': str(factor),
                'count': int(count),
                'percentage': round(percentage, 1)
            })
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': detailed_data,
            'analysis': {
                'top_factor': str(data.idxmax()) if len(data) > 0 else 'N/A',
                'top_factor_percentage': round((data.max() / total) * 100, 1) if len(data) > 0 else 0,
                'total_responses': total
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in success_factors: {str(e)}")
        return safe_api_response(str(e), False)

# Other existing APIs...
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
        sector_col = find_column_smart(filtered_df, ['employment_sectors'])
        
        if sector_col is None:
            return safe_api_response('Employment sectors column not found', False)
        
        clean_data = filtered_df[sector_col].dropna()
        clean_data = clean_data[clean_data != 'Tidak Dinyatakan']
        
        if len(clean_data) == 0:
            return safe_api_response('No sector data available', False)
        
        data = clean_data.value_counts()
        total = len(clean_data)
        
        detailed_data = []
        for sector, count in data.items():
            percentage = (count / total) * 100
            detailed_data.append({
                'sector': str(sector),
                'count': int(count),
                'percentage': round(percentage, 1)
            })
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'table_data': detailed_data,
            'analysis': {
                'total_responses': total
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in employment_sectors: {str(e)}")
        return safe_api_response(str(e), False)

# Continue with other existing APIs (salary, certifications, etc.)...
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
            logger.error(f"Required columns not found. Salary: {salary_col}, Field: {field_col}")
            return safe_api_response('Required columns not found', False)
        
        working_df = filtered_df[[salary_col, field_col]].dropna()
        working_df = working_df[working_df[salary_col] != 'Tidak Dinyatakan']
        working_df = working_df[working_df[field_col] != 'Tidak Dinyatakan']
        
        if len(working_df) == 0:
            return safe_api_response('No salary data available', False)
        
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
        
        # Table data
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
                'total_working_graduates': len(working_df)
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in current_salary_by_field: {str(e)}")
        return safe_api_response(str(e), False)

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
        
        # Combine labels
        all_labels = sorted(list(set(current_data.index.tolist() + expected_data.index.tolist())))
        
        current_values = [int(current_data.get(label, 0)) for label in all_labels]
        expected_values = [int(expected_data.get(label, 0)) for label in all_labels]
        
        result = {
            'chart_data': {
                'labels': all_labels,
                'datasets': [
                    {
                        'label': 'Gaji Semasa',
                        'data': current_values,
                        'backgroundColor': '#10b981',
                        'borderColor': '#10b981',
                        'borderWidth': 1
                    },
                    {
                        'label': 'Jangkaan Gaji',
                        'data': expected_values,
                        'backgroundColor': '#3b82f6',
                        'borderColor': '#3b82f6',
                        'borderWidth': 1
                    }
                ]
            },
            'analysis': {
                'current_responses': len(filtered_df[current_salary_col].dropna()),
                'expected_responses': len(filtered_df[expected_salary_col].dropna())
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in salary_comparison: {str(e)}")
        return safe_api_response(str(e), False)

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
            return safe_api_response('No certifications data available', False)
        
        data = clean_data.value_counts()
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
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
            return safe_api_response('No internship data available', False)
        
        data = clean_data.value_counts()
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'analysis': {
                'internship_rate': round((data.get('Ya', 0) / len(clean_data)) * 100, 1),
                'total_responses': len(clean_data)
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in internship_impact: {str(e)}")
        return safe_api_response(str(e), False)

@app.route('/api/university-preparation')
def university_preparation():
    try:
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        filtered_df = apply_filters(df, filters)
        
        prep_col = find_column_smart(filtered_df, ['university_preparation'])
        
        if prep_col is None:
            return safe_api_response('University preparation column not found', False)
        
        clean_data = filtered_df[prep_col].dropna()
        clean_data = clean_data[clean_data != 'Tidak Dinyatakan']
        
        if len(clean_data) == 0:
            return safe_api_response('No university preparation data available', False)
        
        data = clean_data.value_counts()
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
            'analysis': {
                'satisfaction_rate': round(((data.get('Sangat setuju', 0) + data.get('Setuju', 0)) / len(clean_data)) * 100, 1),
                'total_responses': len(clean_data)
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in university_preparation: {str(e)}")
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
            return safe_api_response('No gig economy data available', False)
        
        data = clean_data.value_counts()
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
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
            return safe_api_response('No support needed data available', False)
        
        data = clean_data.value_counts()
        
        result = {
            'chart_data': {
                'labels': [str(label) for label in data.index.tolist()],
                'data': [int(val) for val in data.values.tolist()]
            },
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

# Summary Statistics API
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
                    year_range = f"{min_year}-{max_year}"
            except:
                year_range = "N/A"
        
        result = {
            'total_graduates': total_graduates,
            'employment_rate': round(employment_rate, 1),
            'fields_count': fields_count,
            'year_range': year_range,
            'data_quality': {
                'completeness': round((filtered_df.count().sum() / (len(filtered_df) * len(filtered_df.columns))) * 100, 1) if len(filtered_df) > 0 else 0,
                'response_rate': 100
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in summary_stats: {str(e)}")
        return safe_api_response(str(e), False)

if __name__ == '__main__':
    logger.info("🚀 Starting Graduate Analytics Dashboard...")
    logger.info("🔗 Dashboard URL: http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')