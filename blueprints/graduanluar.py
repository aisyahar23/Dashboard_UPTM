from flask import Blueprint, render_template, request, jsonify, send_file
from models.data_processor import DataProcessor, load_excel_data
import io
import os
import pandas as pd

graduanluar_bp = Blueprint('graduanluar', __name__)

# Load data from Excel file
EXCEL_FILE_PATH = 'data/Questionnaire.xlsx'
df = load_excel_data(EXCEL_FILE_PATH)

# Filter out rows where 'Apakah jenis pekerjaan anda sekarang' is 'Bekerja dalam bidang pengajian' or 'Tidak bekerja'
df_filtered = df[~df['Apakah jenis pekerjaan anda sekarang'].isin(['Bekerja dalam bidang pengajian', 'Tidak bekerja'])]
data_processor = DataProcessor(df_filtered)

@graduanluar_bp.route('/')
def index():
    """Main graduan luar dashboard page"""
    return render_template('graduanluar.html')

@graduanluar_bp.route('/table')
def table_view():
    """Table view for graduan luar data"""
    return render_template('data_table.html', 
                         page_title='Graduan Bekerja di Luar Bidang Data Table',
                         api_endpoint='/graduan-luar/api/table-data')

@graduanluar_bp.route('/api/summary')
def api_summary():
    """Get summary statistics for graduan luar data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        stats = filtered_processor.get_summary_stats()
        filtered_df = filtered_processor.filtered_df
        
        total_records = len(filtered_df)
        
        # Calculate real KPIs from actual data
        reason_stats = {}
        job_type_stats = {}
        
        if total_records > 0:
            # Analyze reasons for not working in field of study
            reason_column = 'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?'
            if reason_column in filtered_df.columns:
                reason_counts = filtered_df[reason_column].dropna().str.split(',').explode().str.strip().value_counts()
                total_reasons = reason_counts.sum()
                
                # Categorize reasons
                mismatch_keywords = ['bidang', 'field', 'tidak sesuai', 'mismatch']
                opportunity_keywords = ['peluang', 'opportunity', 'limited', 'terhad', 'kerja']
                prospect_keywords = ['prospek', 'prospect', 'better', 'baik', 'masa depan', 'career']
                salary_keywords = ['gaji', 'salary', 'pay', 'income', 'pendapatan']
                
                mismatch_count = 0
                opportunity_count = 0
                prospect_count = 0
                salary_count = 0
                
                for reason, count in reason_counts.items():
                    reason_lower = str(reason).lower()
                    if any(keyword in reason_lower for keyword in mismatch_keywords):
                        mismatch_count += count
                    elif any(keyword in reason_lower for keyword in opportunity_keywords):
                        opportunity_count += count
                    elif any(keyword in reason_lower for keyword in prospect_keywords):
                        prospect_count += count
                    elif any(keyword in reason_lower for keyword in salary_keywords):
                        salary_count += count
                
                reason_stats = {
                    'mismatch_rate': (mismatch_count / total_reasons) * 100 if total_reasons > 0 else 0,
                    'opportunity_rate': (opportunity_count / total_reasons) * 100 if total_reasons > 0 else 0,
                    'better_prospects_rate': (prospect_count / total_reasons) * 100 if total_reasons > 0 else 0,
                    'salary_rate': (salary_count / total_reasons) * 100 if total_reasons > 0 else 0
                }
            
            # Analyze current job types
            job_column = 'Apakah jenis pekerjaan anda sekarang'
            if job_column in filtered_df.columns:
                job_counts = filtered_df[job_column].value_counts()
                most_common_job = job_counts.index[0] if len(job_counts) > 0 else 'N/A'
                
                job_type_stats = {
                    'most_common_job': most_common_job,
                    'job_diversity': len(job_counts)
                }
            
            # Institution analysis
            institution_column = 'Institusi pendidikan MARA yang anda hadiri?'
            institution_stats = {}
            if institution_column in filtered_df.columns:
                institution_counts = filtered_df[institution_column].value_counts()
                most_represented_institution = institution_counts.index[0] if len(institution_counts) > 0 else 'N/A'
                institution_stats = {
                    'most_represented_institution': most_represented_institution,
                    'institution_count': len(institution_counts)
                }
        
        # Update stats with real calculations
        stats.update({
            'total_records': total_records,
            'mismatch_rate': round(reason_stats.get('mismatch_rate', 0), 1),
            'opportunity_rate': round(reason_stats.get('opportunity_rate', 0), 1),
            'better_prospects_rate': round(reason_stats.get('better_prospects_rate', 0), 1),
            'salary_consideration_rate': round(reason_stats.get('salary_rate', 0), 1),
            'most_common_job': job_type_stats.get('most_common_job', 'N/A'),
            'job_diversity': job_type_stats.get('job_diversity', 0),
            'most_represented_institution': institution_stats.get('most_represented_institution', 'N/A'),
            'institution_diversity': institution_stats.get('institution_count', 0)
        })
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'total_records': 0,
            'mismatch_rate': 0,
            'opportunity_rate': 0,
            'better_prospects_rate': 0,
            'salary_consideration_rate': 0
        }), 500

@graduanluar_bp.route('/api/reasons-distribution')
def api_reasons_distribution():
    """Get reasons distribution data (split by comma and count individual reasons)"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        reason_column = 'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?'
        if reason_column not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 2,
                    'borderRadius': 8
                }]
            })
        
        # Split by comma and count individual reasons
        reasons = filtered_processor.filtered_df[reason_column].dropna()
        all_reasons = [reason.strip() for reasons_list in reasons for reason in str(reasons_list).split(',')]
        reason_counts = pd.Series(all_reasons).value_counts()
        
        # Prepare chart data
        colors = [
            '#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', 
            '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#f59e0b'
        ]
        
        chart_data = {
            'labels': reason_counts.index.tolist()[:10],  # Top 10 reasons
            'datasets': [{
                'data': reason_counts.values.tolist()[:10],
                'backgroundColor': colors[:len(reason_counts.index.tolist()[:10])],
                'borderColor': '#ffffff',
                'borderWidth': 2,
                'borderRadius': 8
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'labels': ['Error Loading Data'],
            'datasets': [{
                'data': [1],
                'backgroundColor': ['#ef4444'],
                'borderColor': '#dc2626',
                'borderWidth': 2,
                'borderRadius': 8
            }]
        }), 500

@graduanluar_bp.route('/api/job-types')
def api_job_types():
    """Get current job types distribution"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        job_column = 'Apakah jenis pekerjaan anda sekarang'
        if job_column not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderWidth': 3,
                    'borderColor': '#ffffff'
                }]
            })
        
        data = filtered_processor.get_chart_data('pie', job_column)
        return jsonify(data)
        
    except Exception as e:
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

@graduanluar_bp.route('/api/institution-reasons')
def api_institution_reasons():
    """Get institution vs reasons correlation"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        institution_column = 'Institusi pendidikan MARA yang anda hadiri?'
        reason_column = 'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?'
        
        if institution_column not in filtered_processor.filtered_df.columns or reason_column not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1],
                    'backgroundColor': '#6b7280',
                    'borderWidth': 0
                }]
            })
        
        # Create cross-tabulation
        df_clean = filtered_processor.filtered_df[[institution_column, reason_column]].dropna()
        
        # For stacked bar chart, we need to process the reasons (split by comma)
        expanded_data = []
        for _, row in df_clean.iterrows():
            institution = row[institution_column]
            reasons = str(row[reason_column]).split(',')
            for reason in reasons:
                expanded_data.append({
                    'institution': institution.strip(),
                    'reason': reason.strip()
                })
        
        expanded_df = pd.DataFrame(expanded_data)
        
        if expanded_df.empty:
            return jsonify({
                'labels': ['No Data'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1],
                    'backgroundColor': '#6b7280'
                }]
            })
        
        # Create cross-tabulation
        crosstab = pd.crosstab(expanded_df['institution'], expanded_df['reason'])
        
        # Limit to top institutions and reasons for readability
        top_institutions = crosstab.sum(axis=1).nlargest(8).index
        top_reasons = crosstab.sum(axis=0).nlargest(6).index
        
        crosstab_limited = crosstab.loc[top_institutions, top_reasons]
        
        # Prepare data for stacked bar chart
        colors = [
            '#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6'
        ]
        
        datasets = []
        for i, reason in enumerate(crosstab_limited.columns):
            datasets.append({
                'label': reason,
                'data': crosstab_limited[reason].tolist(),
                'backgroundColor': colors[i % len(colors)],
                'borderWidth': 0
            })
        
        chart_data = {
            'labels': crosstab_limited.index.tolist(),
            'datasets': datasets
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
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

@graduanluar_bp.route('/api/table-data')
def api_table_data():
    """Get paginated table data for graduan luar"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() 
                   if k not in ['page', 'per_page', 'search']}
        filtered_processor = data_processor.apply_filters(filters)
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        
        # Define relevant columns for graduan luar
        relevant_columns = [
            'Apakah jenis pekerjaan anda sekarang',
            'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Program pengajian yang anda ikuti?',
            'Bidang pekerjaan yang anda ceburi sekarang?'
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

@graduanluar_bp.route('/api/export')
def api_export():
    """Export graduan luar data in various formats"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() if k != 'format'}
        filtered_processor = data_processor.apply_filters(filters)
        
        format_type = request.args.get('format', 'csv')
        
        relevant_columns = [
            'Timestamp',
            'Apakah jenis pekerjaan anda sekarang',
            'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?',
            'Bidang pekerjaan yang anda ceburi sekarang?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Umur anda?'
        ]
        
        available_columns = [col for col in relevant_columns if col in filtered_processor.filtered_df.columns]
        
        data = filtered_processor.export_data(format_type, available_columns)
        
        if format_type == 'csv':
            mimetype = 'text/csv'
            filename = 'graduan_luar_bidang_data.csv'
        elif format_type == 'excel':
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = 'graduan_luar_bidang_data.xlsx'
        else:
            mimetype = 'application/json'
            filename = 'graduan_luar_bidang_data.json'
        
        return send_file(
            io.BytesIO(data),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@graduanluar_bp.route('/api/filters/available')
def api_available_filters():
    """Get available filter options for graduan luar data"""
    try:
        sample_df = data_processor.df
        filters = {}
        
        filter_columns = [
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?',
            'Apakah jenis pekerjaan anda sekarang'
        ]
        
        for column in filter_columns:
            if column in sample_df.columns:
                unique_values = sample_df[column].dropna().unique().tolist()
                if isinstance(unique_values[0] if unique_values else None, (int, float)):
                    unique_values = sorted(unique_values)
                else:
                    unique_values = sorted([str(val) for val in unique_values])
                filters[column] = unique_values
        
        return jsonify(filters)
        
    except Exception as e:
        return jsonify({'error': str(e), 'filters': {}}), 500