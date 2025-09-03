from flask import Blueprint, render_template, request, jsonify, send_file
from models.data_processor import DataProcessor, load_excel_data
import io
import os
import pandas as pd
import numpy as np
import json

alldata_bp = Blueprint('alldata', __name__)

# Load data from Excel file
EXCEL_FILE_PATH = 'data/Questionnaire.xlsx'
df = load_excel_data(EXCEL_FILE_PATH)
data_processor = DataProcessor(df)

def clean_nan_values(obj):
    """Recursively clean NaN values from nested dictionaries and lists for JSON serialization"""
    if isinstance(obj, dict):
        return {key: clean_nan_values(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan_values(item) for item in obj]
    elif pd.isna(obj) or (isinstance(obj, float) and np.isnan(obj)):
        return None
    else:
        return obj

@alldata_bp.route('/')
def index():
    """Main all data page"""
    return render_template('alldata.html')

@alldata_bp.route('/api/test')
def api_test():
    """Test endpoint to verify the blueprint is working"""
    return jsonify({
        'status': 'success',
        'message': 'All Data API is working',
        'available_columns': list(df.columns) if not df.empty else [],
        'total_records': len(df)
    })

@alldata_bp.route('/api/summary')
def api_summary():
    """Get comprehensive summary statistics for all data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        total_records = len(filtered_df)
        
        # Basic demographics
        gender_dist = filtered_df['Jantina anda?'].value_counts().to_dict() if 'Jantina anda?' in filtered_df.columns else {}
        
        # Graduation years
        years = filtered_df['Tahun graduasi anda?'].dropna().unique() if 'Tahun graduasi anda?' in filtered_df.columns else []
        year_range = f"{min(years)} - {max(years)}" if len(years) > 0 else "N/A"
        
        # Institutions
        institutions = filtered_df['Institusi pendidikan MARA yang anda hadiri?'].nunique() if 'Institusi pendidikan MARA yang anda hadiri?' in filtered_df.columns else 0
        
        # Employment status
        employment_rate = 0
        if 'Adakah anda kini bekerja?' in filtered_df.columns:
            employment_counts = filtered_df['Adakah anda kini bekerja?'].value_counts()
            total_responses = employment_counts.sum()
            if total_responses > 0:
                working_responses = employment_counts[employment_counts.index.str.contains('Ya', na=False)].sum()
                employment_rate = (working_responses / total_responses) * 100
        
        # Fields of study
        fields_count = filtered_df['Bidang pengajian utama anda?'].nunique() if 'Bidang pengajian utama anda?' in filtered_df.columns else 0
        
        summary_stats = {
            'total_records': total_records,
            'gender_distribution': gender_dist,
            'year_range': year_range,
            'total_institutions': institutions,
            'employment_rate': round(employment_rate, 1),
            'fields_of_study_count': fields_count,
            'filter_applied': len([f for f in filters.values() if f]) > 0
        }
        
        # Clean NaN values before returning
        summary_stats = clean_nan_values(summary_stats)
        return jsonify(summary_stats)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'total_records': 0,
            'gender_distribution': {},
            'year_range': 'N/A',
            'total_institutions': 0,
            'employment_rate': 0,
            'fields_of_study_count': 0
        }), 500

@alldata_bp.route('/api/sections')
def api_sections():
    """Get data sections with relevant columns"""
    try:
        sections = {
            'demografi': {
                'name': 'Demografi & Latar Belakang Akademik',
                'columns': [
                    'Tahun graduasi anda?',
                    'Umur anda?',
                    'Jantina anda?',
                    'Institusi pendidikan MARA yang anda hadiri?',
                    'Bidang pengajian utama anda?',
                    'Tahap pendidikan tertinggi'
                ],
                'description': 'Maklumat demografi dan latar belakang akademik responden'
            },
            'sosioekonomi': {
                'name': 'Sosioekonomi Graduan',
                'columns': [
                    'Pendapatan isi rumah bulanan keluarga anda?',
                    'Pekerjaan bapa anda',
                    'Pekerjaan ibu anda?',
                    'Bagaimana anda membiayai pendidikan anda?',
                    'Adakah jenis pembiayaan ini memberi kelebihan dalam mencari kerja?',
                    'Jika anda mempunyai pinjaman pendidikan, adakah beban hutang mempengaruhi pilihan kerjaya anda?'
                ],
                'description': 'Status sosioekonomi dan pembiayaan pendidikan'
            },
            'status_pekerjaan': {
                'name': 'Status Pekerjaan & Kesesuaian dengan Bidang Pengajian',
                'columns': [
                    'Adakah anda kini bekerja?',
                    'Apakah status pekerjaan anda sekarang?',
                    'Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?',
                    'Apakah jenis pekerjaan anda sekarang',
                    'Apakah faktor utama yang membantu anda mendapat pekerjaan tersebut?',
                    'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?'
                ],
                'description': 'Status pekerjaan semasa dan kesesuaian dengan bidang pengajian'
            },
            'sektor_industri': {
                'name': 'Sektor, Industri & Gaji Graduan',
                'columns': [
                    'Berapakah julat gaji bulanan anda sekarang?',
                    'Apakah sektor pekerjaan anda?',
                    'Apakah jangkaan gaji permulaan yang anda anggap sesuai dengan kelulusan anda?',
                    'Adakah gaji anda bersesuaian dengan kelulusan anda?'
                ],
                'description': 'Maklumat sektor pekerjaan, industri dan gaji'
            },
            'kebolehpasaran': {
                'name': 'Faktor Mempengaruhi Kebolehpasaran Graduan',
                'columns': [
                    'Sejauh mana latihan industri/praktikal mempengaruhi kebolehpasaran anda?',
                    'Sejauh mana kemahiran komunikasi  mempengaruhi kebolehpasaran anda?',
                    'Sejauh mana kemahiran teknikal mempengaruhi kebolehpasaran anda?',
                    'Sejauh mana rangkaian peribadi (networking) mempengaruhi kebolehpasaran anda?',
                    'Sejauh mana kelayakan akademik mempengaruhi kebolehpasaran anda?',
                    'Adakah anda memiliki sijil profesional tambahan selain ijazah/diploma?',
                    'Adakah sijil profesional ini membantu anda dalam mendapatkan pekerjaan?',
                    'Adakah majikan anda meminta kelayakan tambahan selain daripada ijazah anda?',
                    'Kemahiran tambahan manakah yang paling banyak diminta oleh majikan semasa temu duga? ',
                    'Sejauh mana anda bersetuju bahawa universiti telah menyediakan anda untuk pasaran kerja?'
                ],
                'description': 'Faktor-faktor yang mempengaruhi kebolehpasaran graduan'
            },
            'graduan_bidang': {
                'name': 'Graduan Mengikut Bidang dan Tahun Graduasi',
                'columns': [
                    'Tahun graduasi anda?',
                    'Bidang pengajian utama anda?',
                    'Institusi pendidikan MARA yang anda hadiri?'
                ],
                'description': 'Taburan graduan mengikut bidang dan tahun graduasi'
            },
            'luar_bidang': {
                'name': 'Graduan Bekerja di Luar Bidang',
                'columns': [
                    'Apakah jenis pekerjaan anda sekarang',
                    'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?',
                    'Bidang pengajian utama anda?'
                ],
                'description': 'Analisis graduan yang bekerja di luar bidang pengajian'
            },
            'internship': {
                'name': 'Internship dan Cabaran Mendapat Kerja',
                'columns': [
                    'Adakah anda menjalani internship/praktikal sebelum tamat pengajian?',
                    'Bagaimana internship membantu anda dalam mendapatkan pekerjaan?',
                    'Jika tidak menjalani internship, apakah sebab utama?',
                    'Apakah cabaran utama yang anda hadapi dalam mendapatkan pekerjaan?'
                ],
                'description': 'Maklumat mengenai internship dan cabaran mencari kerja'
            },
            'ekonomi_gig': {
                'name': 'Trend Ekonomi Gig/Keusahawanan',
                'columns': [
                    'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?',
                    'Adakah universiti anda menawarkan kursus atau latihan berkaitan keusahawanan?',
                    'Adakah universiti anda pernah menganjurkan program berkaitan perniagaan atau ekonomi gig seperti hackathon, bootcamp, atau geran permulaan perniagaan?',
                    'Apakah sebab utama anda memilih untuk bekerja dalam ekonomi gig? ',
                    'Bagaimanakah anda memperoleh kemahiran untuk bekerja dalam ekonomi gig?',
                    'Apakah cabaran utama yang anda hadapi dalam keusahawanan atau ekonomi gig?',
                    'Apakah bantuan atau sokongan yang anda rasa perlu untuk berjaya dalam keusahawanan dan ekonomi gig?',
                    'Berapakah purata pendapatan bulan anda daripada ekonomi gig?',
                    'Jika diberikan peluang pekerjaan tetap dengan gaji setanding ekonomi gig, adakah anda akan menerimanya?'
                ],
                'description': 'Trend keusahawanan dan ekonomi gig di kalangan graduan'
            }
        }
        
        return jsonify(sections)
        
    except Exception as e:
        return jsonify({'error': str(e), 'sections': {}}), 500

@alldata_bp.route('/api/table-data')
def api_table_data():
    """Get paginated table data with section filtering"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() 
                   if k not in ['page', 'per_page', 'search', 'section']}
        filtered_processor = data_processor.apply_filters(filters)
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        section = request.args.get('section', '')
        
        # Get columns based on section
        if section:
            sections_response = api_sections()
            sections_data = sections_response.get_json() if hasattr(sections_response, 'get_json') else {}
            
            if section in sections_data:
                base_columns = ['Timestamp'] + sections_data[section]['columns']
                # Handle column name variations (with/without trailing spaces)
                relevant_columns = []
                for col in base_columns:
                    if col in filtered_processor.filtered_df.columns:
                        relevant_columns.append(col)
                    elif col + ' ' in filtered_processor.filtered_df.columns:  # Try with trailing space
                        relevant_columns.append(col + ' ')
                    elif col.rstrip() in filtered_processor.filtered_df.columns:  # Try without trailing space
                        relevant_columns.append(col.rstrip())
            else:
                relevant_columns = list(filtered_processor.filtered_df.columns)
        else:
            # Show all columns by default
            relevant_columns = list(filtered_processor.filtered_df.columns)
        
        # Filter to only available columns
        available_columns = [col for col in relevant_columns if col in filtered_processor.filtered_df.columns]
        
        data = filtered_processor.get_table_data(page, per_page, search, available_columns)
        
        # Clean NaN values from data before JSON serialization
        data = clean_nan_values(data)
        
        # Add section information to response
        data['current_section'] = section
        data['section_columns'] = available_columns
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'data': [],
            'pagination': {'page': 1, 'per_page': 50, 'total': 0, 'pages': 0},
            'columns': [],
            'current_section': '',
            'section_columns': []
        }), 500

@alldata_bp.route('/api/export')
def api_export():
    """Export all data or section data in various formats"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() 
                   if k not in ['format', 'section']}
        filtered_processor = data_processor.apply_filters(filters)
        
        format_type = request.args.get('format', 'csv')
        section = request.args.get('section', '')
        
        # Get columns based on section
        if section:
            sections_response = api_sections()
            sections_data = sections_response.get_json() if hasattr(sections_response, 'get_json') else {}
            
            if section in sections_data:
                relevant_columns = ['Timestamp'] + sections_data[section]['columns']
            else:
                relevant_columns = list(filtered_processor.filtered_df.columns)
        else:
            # Export all columns
            relevant_columns = list(filtered_processor.filtered_df.columns)
        
        # Filter to only available columns
        available_columns = [col for col in relevant_columns if col in filtered_processor.filtered_df.columns]
        
        data = filtered_processor.export_data(format_type, available_columns)
        
        # Set filename based on section
        section_name = section if section else 'all_data'
        
        if format_type == 'csv':
            mimetype = 'text/csv'
            filename = f'{section_name}_data.csv'
        elif format_type == 'excel':
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f'{section_name}_data.xlsx'
        else:
            mimetype = 'application/json'
            filename = f'{section_name}_data.json'
        
        return send_file(
            io.BytesIO(data),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alldata_bp.route('/api/filters/available')
def api_available_filters():
    """Get available filter options for all data"""
    try:
        sample_df = data_processor.df
        filters = {}
        
        # Core demographic filters - handle column name variations
        filter_columns = [
            'Tahun graduasi anda?',
            'Tahun graduasi anda? ',  # With trailing space
            'Jantina anda?',
            'Jantina anda? ',  # With trailing space
            'Institusi pendidikan MARA yang anda hadiri?',
            'Bidang pengajian utama anda?',
            'Bidang pengajian utama anda? ',  # With trailing space
            'Tahap pendidikan tertinggi',
            'Umur anda?',
            'Umur anda? ',  # With trailing space
            'Adakah anda kini bekerja?',
            'Apakah status pekerjaan anda sekarang?',
            'Apakah sektor pekerjaan anda?',
            'Pendapatan isi rumah bulanan keluarga anda?',
            'Bagaimana anda membiayai pendidikan anda?'
        ]
        
        for column in filter_columns:
            if column in sample_df.columns:
                unique_values = sample_df[column].dropna().unique().tolist()
                # Clean NaN values and convert to appropriate types
                cleaned_values = []
                for val in unique_values:
                    if not pd.isna(val) and val is not np.nan:
                        if isinstance(val, (int, float)) and not np.isnan(val):
                            cleaned_values.append(val)
                        elif isinstance(val, str):
                            cleaned_values.append(val)
                
                if len(cleaned_values) > 0:
                    if isinstance(cleaned_values[0], (int, float)):
                        cleaned_values = sorted(cleaned_values)
                    else:
                        cleaned_values = sorted([str(val) for val in cleaned_values])
                    filters[column] = cleaned_values
        
        return jsonify(clean_nan_values(filters))
        
    except Exception as e:
        return jsonify({'error': str(e), 'filters': {}}), 500

@alldata_bp.route('/api/section-summary/<section>')
def api_section_summary(section):
    """Get summary for specific section"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        sections_response = api_sections()
        sections_data = sections_response.get_json() if hasattr(sections_response, 'get_json') else {}
        
        if section not in sections_data:
            return jsonify({'error': 'Section not found'}), 404
        
        section_info = sections_data[section]
        section_columns = section_info['columns']
        
        # Calculate section-specific statistics
        summary = {
            'section_name': section_info['name'],
            'description': section_info['description'],
            'total_records': len(filtered_df),
            'columns_available': [],
            'sample_data': {}
        }
        
        # Check which columns are available and get sample data
        for col in section_columns:
            if col in filtered_df.columns:
                summary['columns_available'].append(col)
                # Get top 5 values for categorical data
                if filtered_df[col].dtype == 'object':
                    top_values = filtered_df[col].value_counts().head(5).to_dict()
                    summary['sample_data'][col] = top_values
                else:
                    # For numeric data, get basic stats
                    summary['sample_data'][col] = {
                        'mean': round(filtered_df[col].mean(), 2) if not filtered_df[col].empty else 0,
                        'count': filtered_df[col].count()
                    }
        
        return jsonify(summary)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500