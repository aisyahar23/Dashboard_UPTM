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

# Create comprehensive sample data with proper Malay column names
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
        'Bidang pengajian utama anda?': np.random.choice([
            'Teknologi Maklumat', 'Perniagaan', 'Kejuruteraan', 
            'Perakaunan', 'Pemasaran', 'Sains Komputer',
            'Pengurusan', 'Kewangan'
        ], sample_size),
        
        # Graduation Years
        'Tahun graduasi anda?': np.random.choice([2020, 2021, 2022, 2023, 2024], sample_size),
        
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
        
        # Job Challenges - Updated with 12 options in Malay (CHECKBOX DATA)
        'Apakah cabaran utama yang anda hadapi dalam mendapatkan pekerjaan?': [
            generate_checkbox_response([
                'Tiada pengalaman kerja yang mencukupi',
                'Terlalu banyak persaingan dalam bidang saya',
                'Kekurangan kemahiran yang dicari majikan',
                'Gaji yang ditawarkan terlalu rendah',
                'Saya tidak tahu bagaimana mencari pekerjaan yang sesuai',
                'Tiada rangkaian atau hubungan yang boleh membantu saya mendapatkan pekerjaan',
                'Kriteria pekerjaan tidak sesuai dengan kelayakan akademik saya',
                'Kebanyakan syarikat lebih memilih pekerja yang sudah berpengalaman',
                'Tiada peluang pekerjaan dalam bidang saya di kawasan tempat tinggal saya',
                'Saya perlu menjaga keluarga dan sukar untuk bekerja di luar kawasan',
                'Proses permohonan kerja terlalu kompleks atau mengambil masa yang lama',
                'Keadaan ekonomi semasa menyukarkan peluang pekerjaan'
            ]) for _ in range(sample_size)
        ],
        
        # Success Factors (CHECKBOX DATA)
        'Apakah faktor utama yang membantu anda mendapat pekerjaan tersebut?': [
            generate_checkbox_response([
                'Melalui latihan industri / praktikal',
                'Permohonan terus kepada syarikat (JobStreet, LinkedIn, laman web syarikat)',
                'Program kerajaan (contoh: MySTEP, Protege, SL1M)',
                'Rangkaian peribadi / kenalan (pensyarah, alumni, keluarga, rakan)',
                'Melalui pameran kerjaya atau job fair',
                'Tawaran daripada syarikat sebelum tamat pengajian',
                'Dihubungi oleh perekrut atau headhunter',
                'Memulakan perniagaan sendiri / bekerja dalam ekonomi gig'
            ]) for _ in range(sample_size)
        ],
        
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
        
        # Support Needed (CHECKBOX DATA) - Fixed the categories as mentioned in the paste
        'Apakah bantuan atau sokongan yang anda rasa perlu untuk berjaya dalam keusahawanan dan ekonomi gig?': [
            generate_checkbox_response([
                'Latihan teknikal dalam bidang spesifik (design, coding, pemasaran digital)',
                'Bimbingan dalam pengurusan kewangan dan cukai untuk pekerja gig',
                'Platform khas untuk graduan MARA dalam ekonomi gig',
                'Pinjaman atau geran untuk membangunkan perniagaan gig',
                'Perlindungan sosial (KWSP, PERKESO, insurans)'
            ]) for _ in range(sample_size)
        ],
        
        # Gender
        'Jantina anda?': np.random.choice(['Lelaki', 'Perempuan'], sample_size),
        
        # Age
        'Umur anda?': np.random.randint(22, 35, sample_size),
        
        # Institution
        'Institusi pendidikan MARA yang anda hadiri?': np.random.choice([
            'MARA Professional College',
            'MARA University of Technology',
            'MARA Skills Institute'
        ], sample_size)
    })

def generate_checkbox_response(options, min_choices=1, max_choices=3):
    """Generate realistic checkbox responses"""
    num_choices = np.random.randint(min_choices, min(max_choices + 1, len(options)))
    selected = np.random.choice(options, size=num_choices, replace=False)
    return ', '.join(selected)

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

# Enhanced column mapping with multiple possible column names
COLUMN_MAPPING = {
    'employment_status': ['Adakah anda kini bekerja?'],
    'job_type': ['Apakah jenis pekerjaan anda sekarang'],
    'time_to_employment': ['Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?'],
    'field_of_study': ['Bidang pengajian utama anda?'],
    'graduation_year': ['Tahun graduasi anda?'],
    'current_salary': ['Berapakah julat gaji bulanan anda sekarang?'],
    'expected_salary': ['Apakah jangkaan gaji permulaan yang anda anggap sesuai dengan kelulusan anda?'],
    'out_of_field_reason': ['Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?'],
    'academic_skills_needed': ['Jika anda bekerja di luar bidang pengajian, adakah pekerjaan tersebut masih memerlukan kemahiran akademik anda?'],
    'job_challenges': ['Apakah cabaran utama yang anda hadapi dalam mendapatkan pekerjaan?'],
    'success_factors': ['Apakah faktor utama yang membantu anda mendapat pekerjaan tersebut?'],
    'employment_sectors': ['Apakah sektor pekerjaan anda?'],
    'professional_cert': ['Adakah anda memiliki sijil profesional tambahan selain ijazah/diploma?'],
    'internship': ['Adakah anda menjalani internship/praktikal sebelum tamat pengajian?'],
    'university_preparation': ['Sejauh mana anda bersetuju bahawa universiti telah menyediakan anda untuk pasaran kerja?'],
    'gig_economy': ['Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?'],
    'support_needed': ['Apakah bantuan atau sokongan yang anda rasa perlu untuk berjaya dalam keusahawanan dan ekonomi gig?'],
    'gender': ['Jantina anda?'],
    'age': ['Umur anda?'],
    'institution': ['Institusi pendidikan MARA yang anda hadiri?']
}

def get_column(key):
    """Get column name from mapping"""
    possible_names = COLUMN_MAPPING.get(key, [])
    return possible_names[0] if possible_names else None

def find_column_smart(df, possible_keys):
    """Smart column finder that uses both mapping and fuzzy matching"""
    # First try exact matches from mapping
    for key in possible_keys:
        possible_names = COLUMN_MAPPING.get(key, [])
        for col_name in possible_names:
            if col_name in df.columns:
                return col_name
    
    # Then try fuzzy matching
    all_possible_names = []
    for key in possible_keys:
        if key in COLUMN_MAPPING:
            all_possible_names.extend(COLUMN_MAPPING[key])
        all_possible_names.append(key.replace('_', ' ').title())
        all_possible_names.append(key)
    
    return find_column_fuzzy(df, all_possible_names)

def apply_filters(data_df, filters):
    """Enhanced filter application with array support and proper column mapping"""
    filtered_df = data_df.copy()
    initial_count = len(filtered_df)
    
    try:
        logger.info(f"Starting filter application with {initial_count} rows")
        logger.info(f"Filters received: {filters}")
        logger.info(f"Available columns: {list(filtered_df.columns)}")
        
        # Handle year filter (array) - check both short and full column names
        year_filters = filters.get('year', []) + filters.get('Tahun graduasi anda?', [])
        if year_filters and len(year_filters) > 0:
            year_col = find_column_smart(filtered_df, ['graduation_year'])
            logger.info(f"Year filter - Column found: {year_col}")
            if year_col and year_col in filtered_df.columns:
                unique_years = filtered_df[year_col].unique()
                logger.info(f"Available years: {sorted(unique_years)}")
                logger.info(f"Filtering for years: {year_filters}")
                
                # Create mask for multiple years
                year_mask = pd.Series([False] * len(filtered_df))
                for year_filter in year_filters:
                    mask = (filtered_df[year_col].astype(str) == str(year_filter))
                    try:
                        numeric_year = int(year_filter)
                        mask |= (pd.to_numeric(filtered_df[year_col], errors='coerce') == numeric_year)
                    except (ValueError, TypeError):
                        pass
                    year_mask |= mask
                
                filtered_df = filtered_df[year_mask]
                logger.info(f"Year filter applied: {len(filtered_df)} rows remaining")
        
        # Handle field filter (array) - check both short and full column names
        field_filters = filters.get('field', []) + filters.get('Bidang pengajian utama anda?', [])
        if field_filters and len(field_filters) > 0:
            field_col = find_column_smart(filtered_df, ['field_of_study'])
            logger.info(f"Field filter - Column found: {field_col}")
            if field_col and field_col in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[field_col].isin(field_filters)]
                logger.info(f"Field filter applied: {len(filtered_df)} rows remaining")
        
        # Handle employment filter (array) - check both short and full column names
        emp_filters = filters.get('employment', []) + filters.get('Adakah anda kini bekerja?', [])
        if emp_filters and len(emp_filters) > 0:
            emp_col = find_column_smart(filtered_df, ['employment_status'])
            logger.info(f"Employment filter - Column found: {emp_col}")
            if emp_col and emp_col in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[emp_col].isin(emp_filters)]
                logger.info(f"Employment filter applied: {len(filtered_df)} rows remaining")
        
        # Handle gender filter (array) - check both short and full column names
        gender_filters = filters.get('gender', []) + filters.get('Jantina anda?', [])
        if gender_filters and len(gender_filters) > 0:
            gender_col = find_column_smart(filtered_df, ['gender'])
            logger.info(f"Gender filter - Column found: {gender_col}")
            if gender_col and gender_col in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[gender_col].isin(gender_filters)]
                logger.info(f"Gender filter applied: {len(filtered_df)} rows remaining")
        
        # Handle institution filter (array) - check both short and full column names
        inst_filters = filters.get('institution', []) + filters.get('Institusi pendidikan MARA yang anda hadiri?', [])
        if inst_filters and len(inst_filters) > 0:
            inst_col = find_column_smart(filtered_df, ['institution'])
            logger.info(f"Institution filter - Column found: {inst_col}")
            if inst_col and inst_col in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[inst_col].isin(inst_filters)]
                logger.info(f"Institution filter applied: {len(filtered_df)} rows remaining")
        
        logger.info(f"Total filtering: {initial_count} -> {len(filtered_df)} rows")
        return filtered_df
        
    except Exception as e:
        logger.error(f"Error applying filters: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
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
    """Process checkbox-style responses where multiple options can be selected - FIXED VERSION"""
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
        # FIXED: Proper null checking for pandas compatibility
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

def createApp():
    """Factory function that returns the existing app instance"""
    return app

@app.route('/')
def index():
    return render_template('login.html')  # This page

@app.route('/dashboard') 
def dashboard():
    return render_template('dashboard.html')  # Your dashboard page

@app.route('/data-table')
def data_table_page():
    return render_template('data_table.html', 
                         page_title='Graduate Data Table',
                         api_endpoint='/api/table-data') 

# 1. Enhanced Employment Status API with proper response count
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
                'total_responses': total,  # FIXED: Added this field
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

# 2. Enhanced Job Types API with proper response count
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
                'total_responses': len(clean_data),  # FIXED: Added this field
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
                'total_employed_surveyed': len(employed_df),  # FIXED: Added this field
                'total_responses': len(employed_df),  # FIXED: Added this field
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
                'total_graduates': total_graduates,  # FIXED: Added this field
                'total_responses': total_graduates,  # FIXED: Added this field
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
                'total_working_graduates': len(working_df),  # FIXED: Added this field
                'total_responses': len(working_df),  # FIXED: Added this field
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
                'total_responses': max(current_responses, expected_responses)  # FIXED: Added this field
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
                'total_graduates': len(filtered_df),
                'total_responses': len(filtered_df)  # FIXED: Added this field
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

# 8. FIXED Job Challenges API with proper checkbox data processing
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
        
        # Get the predefined challenge categories (12 as mentioned)
        predefined_challenges = [
            'Tiada pengalaman kerja yang mencukupi',
            'Terlalu banyak persaingan dalam bidang saya',
            'Kekurangan kemahiran yang dicari majikan',
            'Gaji yang ditawarkan terlalu rendah',
            'Saya tidak tahu bagaimana mencari pekerjaan yang sesuai',
            'Tiada rangkaian atau hubungan yang boleh membantu saya mendapatkan pekerjaan',
            'Kriteria pekerjaan tidak sesuai dengan kelayakan akademik saya',
            'Kebanyakan syarikat lebih memilih pekerja yang sudah berpengalaman',
            'Tiada peluang pekerjaan dalam bidang saya di kawasan tempat tinggal saya',
            'Saya perlu menjaga keluarga dan sukar untuk bekerja di luar kawasan',
            'Proses permohonan kerja terlalu kompleks atau mengambil masa yang lama',
            'Keadaan ekonomi semasa menyukarkan peluang pekerjaan'
        ]
        
        # Process checkbox data
        labels, data, total_responses = process_checkbox_data(clean_data, predefined_challenges)
        
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
                'total_survey_responses': total_responses,  # FIXED: Added this field
                'total_responses': total_responses,  # FIXED: Added this field
                'total_individual_challenges': total_individual_challenges,
                'average_challenges_per_person': round(total_individual_challenges / total_responses, 1) if total_responses > 0 else 0,
                'diversity_of_challenges': len(labels)
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in job_challenges: {str(e)}")
        return safe_api_response(str(e), False)

#  Success Factors API with proper Series handling
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
        success_col = find_column_smart(filtered_df, ['success_factors'])
        
        if success_col is None:
            return safe_api_response('Success factors column not found', False)
        
        # FIXED: Proper Series handling
        clean_data = filtered_df[success_col].dropna()
        
        # Convert to list to avoid Series boolean evaluation issues
        clean_data_list = []
        for item in clean_data:
            if item != 'Tidak Dinyatakan' and str(item).strip() != '':
                clean_data_list.append(item)
        
        if len(clean_data_list) == 0:
            return safe_api_response('No success factors data available after filtering', False)
        
        # Predefined success factor categories as mentioned in paste.txt
        predefined_factors = [
            'Melalui latihan industri / praktikal',
            'Permohonan terus kepada syarikat (JobStreet, LinkedIn, laman web syarikat)',
            'Program kerajaan (contoh: MySTEP, Protege, SL1M)',
            'Rangkaian peribadi / kenalan (pensyarah, alumni, keluarga, rakan)',
            'Melalui pameran kerjaya atau job fair',
            'Tawaran daripada syarikat sebelum tamat pengajian',
            'Dihubungi oleh perekrut atau headhunter',
            'Memulakan perniagaan sendiri / bekerja dalam ekonomi gig'
        ]
        
        # Process checkbox data
        labels, data, total_responses = process_checkbox_data(clean_data_list, predefined_factors)
        
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
                'total_individual_factors': sum(data) if data else 0
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in success_factors: {str(e)}")
        return safe_api_response(str(e), False)
# Employment Sectors API
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
                'total_responses': len(clean_data),  # FIXED: Added this field
                'dominant_sector': str(data.idxmax()) if len(data) > 0 else 'N/A'
            }
        }
        
        return safe_api_response(result)
    except Exception as e:
        logger.error(f"❌ Error in employment_sectors: {str(e)}")
        return safe_api_response(str(e), False)


# BACKEND - Fixed support_needed function
@app.route('/api/support-needed')
def support_needed():
    try:
        print('🔄 Starting support_needed API...')
        
        filters = {
            'year': request.args.get('year'),
            'field': request.args.get('field'),
            'employment': request.args.get('employment'),
            'gender': request.args.get('gender'),
            'institution': request.args.get('institution')
        }
        
        print(f'📝 Applied filters: {filters}')
        
        filtered_df = apply_filters(df, filters)
        print(f'📊 Filtered dataframe shape: {filtered_df.shape}')
        
        support_col = find_column_smart(filtered_df, ['support_needed'])
        
        if support_col is None:
            print('❌ Support needed column not found')
            available_cols = list(filtered_df.columns)
            print(f'Available columns: {available_cols}')
            return safe_api_response('Support needed column not found', False)
        
        print(f'✅ Found support column: {support_col}')
        
        # FIXED: Proper Series handling
        clean_data = filtered_df[support_col].dropna()
        print(f'📊 Raw data count: {len(clean_data)}')
        
        # Convert to list to avoid Series boolean evaluation issues
        clean_data_list = []
        for item in clean_data:
            if item != 'Tidak Dinyatakan' and str(item).strip() != '':
                clean_data_list.append(item)
        
        print(f'📊 Clean data count: {len(clean_data_list)}')
        
        if len(clean_data_list) == 0:
            print('❌ No support needed data available after filtering')
            return safe_api_response('No support needed data available after filtering', False)
        
        # Get the predefined support categories
        predefined_support = [
            'Latihan teknikal dalam bidang spesifik (design, coding, pemasaran digital)',
            'Bimbingan dalam pengurusan kewangan dan cukai untuk pekerja gig',
            'Platform khas untuk graduan MARA dalam ekonomi gig',
            'Pinjaman atau geran untuk membangunkan perniagaan gig',
            'Perlindungan sosial (KWSP, PERKESO, insurans)'
        ]
        
        # DEBUGGING: Check what the actual data looks like
        print(f'📋 Sample data entries:')
        for i, item in enumerate(clean_data_list[:3]):  # Show first 3 entries
            print(f'  [{i}]: {repr(item)} (type: {type(item)})')
        
        # Process checkbox data
        labels, data, total_responses = process_checkbox_data(clean_data_list, predefined_support)
        
        print(f'📊 Processed data - Labels: {len(labels)}, Data: {len(data)}, Total: {total_responses}')
        
        # DEBUGGING: If no data, let's try manual processing
        if not labels or not data or len(labels) == 0 or len(data) == 0:
            print('⚠️ process_checkbox_data returned empty, trying manual processing...')
            
            # Manual checkbox processing as fallback
            support_counts = {}
            for response in clean_data_list:
                response_str = str(response)
                print(f'Processing response: {repr(response_str)}')
                
                # Check if response contains multiple selections (common checkbox formats)
                if ';' in response_str:
                    selections = [s.strip() for s in response_str.split(';')]
                elif ',' in response_str:
                    selections = [s.strip() for s in response_str.split(',')]
                elif '|' in response_str:
                    selections = [s.strip() for s in response_str.split('|')]
                else:
                    selections = [response_str.strip()]
                
                for selection in selections:
                    if selection and selection != 'Tidak Dinyatakan':
                        # Try to match with predefined categories
                        matched = False
                        for predefined in predefined_support:
                            if selection.lower() in predefined.lower() or predefined.lower() in selection.lower():
                                support_counts[predefined] = support_counts.get(predefined, 0) + 1
                                matched = True
                                break
                        
                        # If no match found, add as-is
                        if not matched:
                            support_counts[selection] = support_counts.get(selection, 0) + 1
            
            print(f'📊 Manual processing results: {support_counts}')
            
            if support_counts:
                labels = list(support_counts.keys())
                data = list(support_counts.values())
                total_responses = len(clean_data_list)
                print(f'✅ Manual processing successful: {len(labels)} categories')
            else:
                print('❌ Even manual processing returned no data')
                return safe_api_response('No valid chart data available after manual processing', False)
        
        # Sort by count (highest first)
        if labels and data:
            sorted_data = sorted(zip(labels, data), key=lambda x: x[1], reverse=True)
            labels, data = zip(*sorted_data)
            labels, data = list(labels), list(data)
        
        total_individual_support = sum(data) if data else 0
        
        table_data = create_table_data(labels, data, 'support_type', 'count')
        
        result = {
            'chart_data': {
                'labels': labels,
                'data': data
            },
            'table_data': table_data,
            'analysis': {
                'top_need': labels[0] if labels else 'N/A',
                'top_need_count': data[0] if data else 0,
                'total_survey_responses': total_responses,
                'total_responses': total_responses,
                'total_individual_support': total_individual_support,
                'average_support_per_person': round(total_individual_support / total_responses, 1) if total_responses > 0 else 0,
                'diversity_of_support': len(labels)
            }
        }
        
        print(f'✅ Returning result: {len(labels)} categories, {total_responses} total responses')
        return safe_api_response(result)
        
    except Exception as e:
        print(f"❌ Error in support_needed: {str(e)}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        return safe_api_response(str(e), False)
   
# Enhanced Summary Statistics API
@app.route('/api/summary-stats')
def summary_stats():
    try:
        # Get filter parameters with both short and full column names
        filters = {
            'year': request.args.getlist('year'),
            'field': request.args.getlist('field'),
            'employment': request.args.getlist('employment'),
            'gender': request.args.getlist('gender'),
            'institution': request.args.getlist('institution'),
            'Tahun graduasi anda?': request.args.getlist('Tahun graduasi anda?'),
            'Bidang pengajian utama anda?': request.args.getlist('Bidang pengajian utama anda?'),
            'Adakah anda kini bekerja?': request.args.getlist('Adakah anda kini bekerja?'),
            'Jantina anda?': request.args.getlist('Jantina anda?'),
            'Institusi pendidikan MARA yang anda hadiri?': request.args.getlist('Institusi pendidikan MARA yang anda hadiri?')
        }
        
        logger.info(f"Summary stats filters: {filters}")
        
        filtered_df = apply_filters(df, filters)
        total_graduates = len(filtered_df)
        
        logger.info(f"Summary stats - Total graduates after filtering: {total_graduates}")
        
        # Employment rate calculation
        employment_col = find_column_smart(filtered_df, ['employment_status'])
        logger.info(f"Employment column found: {employment_col}")
        
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
        year_range = "N/A"
        if year_col:
            try:
                years = pd.to_numeric(filtered_df[year_col], errors='coerce').dropna()
                if len(years) > 0:
                    min_year = int(years.min())
                    max_year = int(years.max())
                    year_range = f"{min_year}-{max_year}" if min_year != max_year else str(min_year)
            except:
                year_range = "N/A"
        
        result = {
            'total_records': total_graduates,
            'employment_rate': round(employment_rate, 1),
            'fields_of_study_count': fields_count,
            'year_range': year_range,
            'total_institutions': len(filtered_df[find_column_smart(filtered_df, ['institution'])].unique()) if find_column_smart(filtered_df, ['institution']) else 0,
            'gender_distribution': dict(filtered_df[find_column_smart(filtered_df, ['gender'])].value_counts()) if find_column_smart(filtered_df, ['gender']) else {},
            'filter_applied': any(v for v in filters.values() if v)
        }
        
        logger.info(f"Summary stats result: {result}")
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

# Table Data API for data_table.html template
@app.route('/api/table-data')
def table_data():
    """Generic table data endpoint with search, filtering, and pagination"""
    try:
        # Get request parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search_query = request.args.get('search', '').strip()
        sort_by = request.args.get('sort_by', '')
        sort_direction = request.args.get('sort_direction', 'asc')
        
        # Get filter parameters (handle multiple values with exact column names)
        filters = {
            'year': request.args.getlist('year'),
            'field': request.args.getlist('field'),
            'employment': request.args.getlist('employment'),
            'gender': request.args.getlist('gender'),
            'institution': request.args.getlist('institution'),
            'Tahun graduasi anda?': request.args.getlist('Tahun graduasi anda?'),
            'Bidang pengajian utama anda?': request.args.getlist('Bidang pengajian utama anda?'),
            'Adakah anda kini bekerja?': request.args.getlist('Adakah anda kini bekerja?'),
            'Jantina anda?': request.args.getlist('Jantina anda?'),
            'Institusi pendidikan MARA yang anda hadiri?': request.args.getlist('Institusi pendidikan MARA yang anda hadiri?')
        }
        
        logger.info(f"🔍 Raw request args: {dict(request.args)}")
        logger.info(f"📋 Processed filters: {filters}")
        
        logger.info(f"📊 Table data request - Page: {page}, Per page: {per_page}, Search: '{search_query}'")
        logger.info(f"🎯 Active filters: {filters}")
        
        # Apply filters
        filtered_df = apply_filters(df, filters)
        
        # Apply search if provided
        if search_query:
            # Search across all text columns
            text_columns = filtered_df.select_dtypes(include=['object']).columns
            search_mask = pd.Series([False] * len(filtered_df))
            
            for col in text_columns:
                search_mask |= filtered_df[col].astype(str).str.contains(search_query, case=False, na=False)
            
            filtered_df = filtered_df[search_mask]
            logger.info(f"Search applied: {len(filtered_df)} rows remaining")
        
        # Apply sorting if specified
        if sort_by and sort_by in filtered_df.columns:
            ascending = sort_direction.lower() == 'asc'
            filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)
            logger.info(f"Sorting applied: {sort_by} {sort_direction}")
        
        # Calculate pagination
        total_records = len(filtered_df)
        total_pages = max(1, (total_records + per_page - 1) // per_page)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        # Get page data
        page_data = filtered_df.iloc[start_idx:end_idx]
        
        # Convert to records format
        records = page_data.to_dict('records')
        columns = list(filtered_df.columns)
        
        # Clean up the data for JSON serialization
        for record in records:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = ''
                elif isinstance(value, (np.integer, np.floating)):
                    record[key] = int(value) if isinstance(value, np.integer) else float(value)
                else:
                    record[key] = str(value)
        
        result = {
            'records': records,
            'columns': columns,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total': total_records,
                'pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            },
            'search': {
                'query': search_query,
                'results_count': len(records)
            },
            'filters_applied': {k: v for k, v in filters.items() if v},
            'sort': {
                'column': sort_by,
                'direction': sort_direction
            }
        }
        
        logger.info(f"Returning {len(records)} records (page {page}/{total_pages})")
        return safe_api_response(result)
        
    except Exception as e:
        logger.error(f"❌ Error in table_data: {str(e)}")
        return safe_api_response(str(e), False)

# Export Data API for data_table.html template
@app.route('/api/export')
def export_data():
    """Export filtered data in various formats"""
    try:
        format_type = request.args.get('format', 'csv').lower()
        
        # Get filter parameters (same as table_data) - handle arrays with exact column names
        filters = {
            'year': request.args.getlist('year'),
            'field': request.args.getlist('field'),
            'employment': request.args.getlist('employment'),
            'gender': request.args.getlist('gender'),
            'institution': request.args.getlist('institution'),
            'Tahun graduasi anda?': request.args.getlist('Tahun graduasi anda?'),
            'Bidang pengajian utama anda?': request.args.getlist('Bidang pengajian utama anda?'),
            'Adakah anda kini bekerja?': request.args.getlist('Adakah anda kini bekerja?'),
            'Jantina anda?': request.args.getlist('Jantina anda?'),
            'Institusi pendidikan MARA yang anda hadiri?': request.args.getlist('Institusi pendidikan MARA yang anda hadiri?')
        }
        
        search_query = request.args.get('search', '').strip()
        
        # Apply filters and search (same logic as table_data)
        filtered_df = apply_filters(df, filters)
        
        if search_query:
            text_columns = filtered_df.select_dtypes(include=['object']).columns
            search_mask = pd.Series([False] * len(filtered_df))
            
            for col in text_columns:
                search_mask |= filtered_df[col].astype(str).str.contains(search_query, case=False, na=False)
            
            filtered_df = filtered_df[search_mask]
        
        # Generate filename
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        filename = f"graduate_data_{timestamp}"
        
        if format_type == 'csv':
            from flask import Response
            import io
            
            output = io.StringIO()
            filtered_df.to_csv(output, index=False)
            output.seek(0)
            
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={"Content-disposition": f"attachment; filename={filename}.csv"}
            )
            
        elif format_type == 'excel':
            from flask import Response
            import io
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, sheet_name='Graduate Data', index=False)
            output.seek(0)
            
            return Response(
                output.getvalue(),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={"Content-disposition": f"attachment; filename={filename}.xlsx"}
            )
            
        elif format_type == 'json':
            from flask import Response
            import json
            
            # Convert to JSON-serializable format
            records = filtered_df.to_dict('records')
            for record in records:
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
                    elif isinstance(value, (np.integer, np.floating)):
                        record[key] = int(value) if isinstance(value, np.integer) else float(value)
            
            json_data = json.dumps(records, indent=2, ensure_ascii=False)
            
            return Response(
                json_data,
                mimetype='application/json',
                headers={"Content-disposition": f"attachment; filename={filename}.json"}
            )
        
        else:
            return safe_api_response(f'Unsupported format: {format_type}', False)
            
    except Exception as e:
        logger.error(f"❌ Error in export_data: {str(e)}")
        return safe_api_response(str(e), False)

if __name__ == '__main__':
    logger.info("🚀 Starting COMPLETELY FIXED Graduate Analytics Dashboard...")
    logger.info("🔗 Dashboard URL: http://localhost:5000")
    logger.info("📊 All 8 required graphs supported with FIXED filtering:")
    logger.info("   1. ✅ Kadar Kebolehpasaran Graduan (Status Pekerjaan) - Pie Chart [RESPONSE COUNT FIXED]")
    logger.info("   2. ✅ Kadar Kebolehpasaran Graduan (Jenis Pekerjaan) - Bar Chart [RESPONSE COUNT FIXED]")
    logger.info("   3. ✅ Tempoh Mendapat Kerja - Area Chart [RESPONSE COUNT FIXED]")
    logger.info("   4. ✅ Graduan Mengikut Bidang & Tahun - Stacked Bar [RESPONSE COUNT FIXED]")
    logger.info("   5. ✅ Julat Gaji Graduan Mengikut Bidang - Stacked Bar [RESPONSE COUNT FIXED]")
    logger.info("   6. ✅ Julat Gaji Graduan Mengikut Bidang - Stacked Bar [RESPONSE COUNT FIXED]")
    logger.info("   7. ✅ Graduan Bekerja di Luar Bidang - Multiple Charts [RESPONSE COUNT FIXED]")
    logger.info("   8. ✅ Cabaran Utama Mendapat Kerja - Bar Chart [CHECKBOX DATA FIXED]")
    logger.info("   9. ✅ Table Data API - Search, Filter, Sort, Export [NEW]")
    
    app.run(debug=True, port=5000, host='0.0.0.0')