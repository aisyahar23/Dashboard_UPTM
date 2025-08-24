from flask import Blueprint, render_template, request, jsonify, send_file
from models.data_processor import DataProcessor, load_excel_data
import io
import os
import pandas as pd
from collections import Counter
import numpy as np

status_pekerjaan_bp = Blueprint('status-pekerjaan', __name__)

# Load data from Excel file
EXCEL_FILE_PATH = 'data/Questionnaire.xlsx'
df = load_excel_data(EXCEL_FILE_PATH)
data_processor = DataProcessor(df)

@status_pekerjaan_bp.route('/')
def index():
    """Main status pekerjaan dashboard page"""
    return render_template('statuspekerjaan.html')

@status_pekerjaan_bp.route('/api/test')
def api_test():
    """Test endpoint to verify the blueprint is working"""
    return jsonify({
        'status': 'success',
        'message': 'Status Pekerjaan API is working',
        'available_columns': list(df.columns) if not df.empty else [],
        'total_records': len(df)
    })

@status_pekerjaan_bp.route('/api/summary')
def api_summary():
    """Get enhanced summary statistics for employment status"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        total_records = len(filtered_df)
        
        # Employment status analysis
        employment_column = 'Adakah anda kini bekerja?'
        employment_rate = 0
        full_time_rate = 0
        part_time_rate = 0
        
        if employment_column in filtered_df.columns:
            employment_counts = filtered_df[employment_column].value_counts()
            total_responses = employment_counts.sum()
            
            if total_responses > 0:
                # Calculate employment rates
                working_responses = employment_counts[employment_counts.index.str.contains('Ya', na=False)].sum()
                employment_rate = (working_responses / total_responses) * 100
                
                full_time_count = employment_counts.get('Ya, bekerja sepenuh masa', 0)
                part_time_count = employment_counts.get('Ya, bekerja separuh masa', 0)
                
                full_time_rate = (full_time_count / total_responses) * 100
                part_time_rate = (part_time_count / total_responses) * 100
        
        # Job matching analysis
        job_type_column = 'Apakah jenis pekerjaan anda sekarang'
        field_match_rate = 0
        most_common_job_type = "N/A"
        
        if job_type_column in filtered_df.columns:
            job_type_counts = filtered_df[job_type_column].value_counts()
            if len(job_type_counts) > 0:
                most_common_job_type = job_type_counts.index[0]
                total_job_responses = job_type_counts.sum()
                
                # Calculate field matching rate
                field_match_responses = job_type_counts.get('Bekerja dalam bidang pengajian', 0)
                if total_job_responses > 0:
                    field_match_rate = (field_match_responses / total_job_responses) * 100
        
        # Time to first job analysis
        time_to_job_column = 'Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?'
        avg_time_to_job = "N/A"
        quick_employment_rate = 0
        
        if time_to_job_column in filtered_df.columns:
            time_responses = filtered_df[time_to_job_column].dropna()
            if len(time_responses) > 0:
                # Count quick employment (within 3 months)
                quick_responses = time_responses[time_responses.str.contains('1-3 bulan|Kurang daripada 1 bulan', na=False)].count()
                quick_employment_rate = (quick_responses / len(time_responses)) * 100
                
                # Most common time period
                time_counts = time_responses.value_counts()
                if len(time_counts) > 0:
                    avg_time_to_job = time_counts.index[0]
        
        enhanced_stats = {
            'total_records': total_records,
            'employment_rate': round(employment_rate, 1),
            'full_time_rate': round(full_time_rate, 1),
            'part_time_rate': round(part_time_rate, 1),
            'field_match_rate': round(field_match_rate, 1),
            'most_common_job_type': most_common_job_type,
            'avg_time_to_job': avg_time_to_job,
            'quick_employment_rate': round(quick_employment_rate, 1),
            'filter_applied': len([f for f in filters.values() if f]) > 0
        }
        
        return jsonify(enhanced_stats)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'total_records': 0,
            'employment_rate': 0,
            'full_time_rate': 0,
            'part_time_rate': 0,
            'field_match_rate': 0,
            'most_common_job_type': 'N/A',
            'avg_time_to_job': 'N/A',
            'quick_employment_rate': 0
        }), 500

@status_pekerjaan_bp.route('/api/employment-status')
def api_employment_status():
    """Get employment status distribution - Pie Chart"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        employment_column = 'Adakah anda kini bekerja?'
        
        if employment_column not in filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Status Pekerjaan',
                    'data': [1]
                }]
            })
        
        # Get employment status counts
        status_counts = filtered_df[employment_column].value_counts()
        
        chart_data = {
            'labels': [str(label) for label in status_counts.index.tolist()],
            'datasets': [{
                'label': 'Taburan Status Pekerjaan',
                'data': [int(val) for val in status_counts.values.tolist()]
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in employment status endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

@status_pekerjaan_bp.route('/api/current-job-status')
def api_current_job_status():
    """Get current job status for working respondents - Bar Chart"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        # Filter for working respondents only
        employment_column = 'Adakah anda kini bekerja?'
        job_status_column = 'Apakah status pekerjaan anda sekarang?'
        
        if employment_column not in filtered_df.columns or job_status_column not in filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Status Pekerjaan Semasa',
                    'data': [1]
                }]
            })
        
        # Filter for working respondents (full-time or part-time)
        df_working = filtered_df[filtered_df[employment_column].isin(['Ya, bekerja sepenuh masa', 'Ya, bekerja separuh masa'])].copy()
        
        if df_working.empty:
            return jsonify({
                'labels': ['No Working Respondents'],
                'datasets': [{
                    'label': 'Status Pekerjaan Semasa',
                    'data': [1]
                }]
            })
        
        # Get job status counts
        status_counts = df_working[job_status_column].value_counts()
        
        chart_data = {
            'labels': [str(label) for label in status_counts.index.tolist()],
            'datasets': [{
                'label': 'Jenis Pekerjaan Semasa',
                'data': [int(val) for val in status_counts.values.tolist()]
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in current job status endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

@status_pekerjaan_bp.route('/api/time-to-first-job')
def api_time_to_first_job():
    """Get time taken to get first job after graduation - Area Chart"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        time_column = 'Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?'
        
        if time_column not in filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Masa Mendapat Pekerjaan',
                    'data': [1]
                }]
            })
        
        # Get time distribution counts and sort by logical order
        tempoh_counts = filtered_df[time_column].value_counts()
        
        # Define logical order for time periods
        time_order = [
            'Kurang daripada 1 bulan',
            '1-3 bulan',
            '4-6 bulan', 
            '7-12 bulan',
            'Lebih daripada 1 tahun',
            'Belum mendapat pekerjaan'
        ]
        
        # Sort according to logical order
        ordered_data = []
        ordered_labels = []
        for time_period in time_order:
            if time_period in tempoh_counts.index:
                ordered_labels.append(time_period)
                ordered_data.append(int(tempoh_counts[time_period]))
        
        # Add any remaining categories not in our predefined order
        for period in tempoh_counts.index:
            if period not in time_order:
                ordered_labels.append(str(period))
                ordered_data.append(int(tempoh_counts[period]))
        
        chart_data = {
            'labels': ordered_labels,
            'datasets': [{
                'label': 'Bilangan Responden',
                'data': ordered_data,
                'fill': True,  # For area chart
                'backgroundColor': 'rgba(54, 162, 235, 0.3)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'tension': 0.4
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in time to first job endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

@status_pekerjaan_bp.route('/api/current-job-types')
def api_current_job_types():
    """Get current job types distribution - Bar Chart"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        job_type_column = 'Apakah jenis pekerjaan anda sekarang'
        
        if job_type_column not in filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Jenis Pekerjaan',
                    'data': [1]
                }]
            })
        
        # Get job type counts
        pekerjaan_counts = filtered_df[job_type_column].value_counts()
        
        chart_data = {
            'labels': [str(label) for label in pekerjaan_counts.index.tolist()],
            'datasets': [{
                'label': 'Jenis Pekerjaan Semasa',
                'data': [int(val) for val in pekerjaan_counts.values.tolist()]
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in current job types endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

@status_pekerjaan_bp.route('/api/job-finding-factors')
def api_job_finding_factors():
    """Get job finding factors grouped analysis - Bar Chart"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        factors_column = 'Apakah faktor utama yang membantu anda mendapat pekerjaan tersebut?'
        
        if factors_column not in filtered_df.columns:
            # Try to find similar column
            similar_columns = [col for col in filtered_df.columns if 'faktor' in col.lower() and 'pekerjaan' in col.lower()]
            if similar_columns:
                factors_column = similar_columns[0]
                print(f"Using similar column: {factors_column}")
            else:
                return jsonify({
                    'labels': ['No Factors Column Found'],
                    'datasets': [{
                        'label': 'Faktor Pekerjaan',
                        'data': [1]
                    }]
                })
        
        # EXACT COLAB REPLICATION - Job factor grouping mapping
        job_factor_grouping = {
            'Permohonan terus kepada syarikat (JobStreet, LinkedIn, laman web syarikat)': 'Saluran Rasmi',
            'Program kerajaan (contoh: MySTEP, Protege, SL1M)': 'Saluran Rasmi',
            'Melalui pameran kerjaya atau job fair': 'Saluran Rasmi',
            'Rangkaian peribadi / kenalan (pensyarah, alumni, keluarga, rakan)': 'Saluran Informal / Sosial',
            'Dihubungi oleh perekrut atau headhunter': 'Saluran Informal / Sosial',
            'Melalui latihan industri / praktikal': 'Laluan Berasaskan Institusi Pendidikan',
            'Tawaran daripada syarikat sebelum tamat pengajian': 'Laluan Berasaskan Institusi Pendidikan',
            'Memulakan perniagaan sendiri / bekerja dalam ekonomi gig': 'Laluan Kendiri / Keusahawanan'
        }
        
        # EXACT COLAB REPLICATION - Group job factors function
        def group_job_factors(cell):
            if pd.isnull(cell):
                return ''
            # Split using semicolon or newline if that's the actual delimiter
            raw_factors = [x.strip() for x in str(cell).split(';')]
            # Replace each factor using the map
            mapped = [job_factor_grouping.get(factor, factor) for factor in raw_factors]
            # Remove duplicates while preserving order
            return '; '.join(dict.fromkeys(mapped))
        
        # Apply grouping to the column
        filtered_df_copy = filtered_df.copy()
        filtered_df_copy['Faktor_Pekerjaan_Grouped'] = filtered_df_copy[factors_column].apply(group_job_factors)
        
        print(f"Job factors grouping results:")
        print(filtered_df_copy['Faktor_Pekerjaan_Grouped'].value_counts())
        
        # EXACT COLAB REPLICATION - Step 1: Drop NA and split each row by ';', stripping whitespace
        split_factors = filtered_df_copy['Faktor_Pekerjaan_Grouped'].dropna().apply(lambda x: [i.strip() for i in x.split(';')])
        
        # EXACT COLAB REPLICATION - Step 2: Flatten the list into a single list
        all_factors = [item for sublist in split_factors for item in sublist]
        
        print(f"All factors extracted: {all_factors}")
        
        if not all_factors:
            return jsonify({
                'labels': ['No Factors Found'],
                'datasets': [{
                    'label': 'Faktor Pekerjaan',
                    'data': [1]
                }]
            })
        
        # EXACT COLAB REPLICATION - Step 3: Count using Counter
        factor_counts = pd.Series(Counter(all_factors)).sort_values(ascending=False)
        
        print(f"Factor counts: {dict(factor_counts)}")
        
        chart_data = {
            'labels': [str(factor) for factor in factor_counts.index.tolist()],
            'datasets': [{
                'label': 'Kekerapan Faktor',
                'data': [int(count) for count in factor_counts.values.tolist()]
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in job finding factors endpoint: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'labels': ['Error Loading Factors Data'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

# Keep existing endpoints (table, export, filters)
@status_pekerjaan_bp.route('/api/table-data')
def api_table_data():
    """Get paginated table data for status pekerjaan"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() 
                   if k not in ['page', 'per_page', 'search']}
        filtered_processor = data_processor.apply_filters(filters)
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        
        # Define relevant columns for status pekerjaan
        relevant_columns = [
            'Adakah anda kini bekerja?',
            'Apakah status pekerjaan anda sekarang?',
            'Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?',
            'Apakah jenis pekerjaan anda sekarang',
            'Apakah faktor utama yang membantu anda mendapat pekerjaan tersebut?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?'
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

@status_pekerjaan_bp.route('/api/export')
def api_export():
    """Export status pekerjaan data in various formats"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() if k != 'format'}
        filtered_processor = data_processor.apply_filters(filters)
        
        format_type = request.args.get('format', 'csv')
        
        relevant_columns = [
            'Timestamp',
            'Adakah anda kini bekerja?',
            'Apakah status pekerjaan anda sekarang?',
            'Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?',
            'Apakah jenis pekerjaan anda sekarang',
            'Apakah faktor utama yang membantu anda mendapat pekerjaan tersebut?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?'
        ]
        
        available_columns = [col for col in relevant_columns if col in filtered_processor.filtered_df.columns]
        
        data = filtered_processor.export_data(format_type, available_columns)
        
        if format_type == 'csv':
            mimetype = 'text/csv'
            filename = 'status_pekerjaan_data.csv'
        elif format_type == 'excel':
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = 'status_pekerjaan_data.xlsx'
        else:
            mimetype = 'application/json'
            filename = 'status_pekerjaan_data.json'
        
        return send_file(
            io.BytesIO(data),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@status_pekerjaan_bp.route('/api/filters/available')
def api_available_filters():
    """Get available filter options for status pekerjaan data"""
    try:
        sample_df = data_processor.df
        filters = {}
        
        filter_columns = [
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?',
            'Adakah anda kini bekerja?',
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