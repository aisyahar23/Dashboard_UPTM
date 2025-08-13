from flask import Blueprint, request, jsonify
from models.data_processor import DataProcessor, generate_sample_data

analytics_bp = Blueprint('analytics', __name__)

# Initialize data
df = generate_sample_data()
data_processor = DataProcessor(df)

@analytics_bp.route('/sosioekonomi/summary')
def sosioekonomi_summary():
    filters = {k: request.args.getlist(k) for k in request.args.keys()}
    filtered_processor = data_processor.apply_filters(filters)
    
    stats = filtered_processor.get_summary_stats()
    stats.update({
        'avg_income_category': 'RM 3000-4000',
        'scholarship_rate': 45,
        'loan_rate': 35,
        'family_funding_rate': 20
    })
    
    return jsonify(stats)

@analytics_bp.route('/sosioekonomi/income-distribution')
def sosioekonomi_income_distribution():
    filters = {k: request.args.getlist(k) for k in request.args.keys()}
    filtered_processor = data_processor.apply_filters(filters)
    
    data = filtered_processor.get_chart_data('bar', 'Pendapatan isi rumah bulanan keluarga anda?')
    return jsonify(data)

@analytics_bp.route('/sosioekonomi/financing-methods')
def sosioekonomi_financing_methods():
    filters = {k: request.args.getlist(k) for k in request.args.keys()}
    filtered_processor = data_processor.apply_filters(filters)
    
    data = filtered_processor.get_chart_data('pie', 'Bagaimana anda membiayai pendidikan anda?')
    return jsonify(data)

@analytics_bp.route('/sosioekonomi/father-occupation')
def sosioekonomi_father_occupation():
    filters = {k: request.args.getlist(k) for k in request.args.keys()}
    filtered_processor = data_processor.apply_filters(filters)
    
    data = filtered_processor.get_chart_data('stacked_bar', 'Pendapatan isi rumah bulanan keluarga anda?', 
                                           group_by='Pekerjaan bapa anda')
    return jsonify(data)

@analytics_bp.route('/sosioekonomi/table-data')
def sosioekonomi_table_data():
    filters = {k: request.args.getlist(k) for k in request.args.keys() 
               if k not in ['page', 'per_page', 'search']}
    filtered_processor = data_processor.apply_filters(filters)
    
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    search = request.args.get('search', '')
    
    data = filtered_processor.get_table_data(page, per_page, search)
    return jsonify(data)

@analytics_bp.route('/demografi/summary')
def demografi_summary():
    filters = {k: request.args.getlist(k) for k in request.args.keys()}
    filtered_processor = data_processor.apply_filters(filters)
    
    stats = filtered_processor.get_summary_stats()
    filtered_df = filtered_processor.filtered_df
    
    stats.update({
        'avg_age': float(filtered_df['Umur anda?'].mean()) if len(filtered_df) > 0 else 0,
        'graduation_years': int(filtered_df['Tahun graduasi anda?'].nunique()) if len(filtered_df) > 0 else 0,
        'institutions': int(filtered_df['Institusi pendidikan MARA yang anda hadiri?'].nunique()) if len(filtered_df) > 0 else 0
    })
    
    return jsonify(stats)

@analytics_bp.route('/demografi/gender-distribution')
def demografi_gender_distribution():
    filters = {k: request.args.getlist(k) for k in request.args.keys()}
    filtered_processor = data_processor.apply_filters(filters)
    
    data = filtered_processor.get_chart_data('pie', 'Jantina anda?')
    return jsonify(data)

@analytics_bp.route('/demografi/institution-distribution')
def demografi_institution_distribution():
    filters = {k: request.args.getlist(k) for k in request.args.keys()}
    filtered_processor = data_processor.apply_filters(filters)
    
    data = filtered_processor.get_chart_data('bar', 'Institusi pendidikan MARA yang anda hadiri?')
    return jsonify(data)

@analytics_bp.route('/demografi/age-graduation')
def demografi_age_graduation():
    filters = {k: request.args.getlist(k) for k in request.args.keys()}
    filtered_processor = data_processor.apply_filters(filters)
    
    data = filtered_processor.get_chart_data('stacked_bar', 'Tahun graduasi anda?', 
                                           group_by='Umur anda?')
    return jsonify(data)

@analytics_bp.route('/demografi/field-distribution')
def demografi_field_distribution():
    filters = {k: request.args.getlist(k) for k in request.args.keys()}
    filtered_processor = data_processor.apply_filters(filters)
    
    data = filtered_processor.get_chart_data('bar', 'Bidang pengajian utama anda?')
    return jsonify(data)

@analytics_bp.route('/demografi/table-data')
def demografi_table_data():
    filters = {k: request.args.getlist(k) for k in request.args.keys() 
               if k not in ['page', 'per_page', 'search']}
    filtered_processor = data_processor.apply_filters(filters)
    
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    search = request.args.get('search', '')
    
    data = filtered_processor.get_table_data(page, per_page, search)
    return jsonify(data)

# Global analytics endpoints
@analytics_bp.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': data_processor.get_summary_stats()['last_updated'],
        'version': '1.0.0'
    })

@analytics_bp.route('/filters/available')
def available_filters():
    """Return available filter options for all pages"""
    sample_df = data_processor.df
    
    filters = {}
    for column in sample_df.columns:
        if sample_df[column].dtype == 'object' or sample_df[column].nunique() < 20:
            filters[column] = sorted(sample_df[column].unique().tolist())
    
    return jsonify(filters)