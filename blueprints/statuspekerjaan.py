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

def process_filter_values(key, values):
    """Process filter values based on the filter type"""
    # Handle graduation year with better conversion
    if 'Tahun graduasi' in key:
        processed_values = []
        for val in values:
            if val and str(val).strip():
                # Clean the value
                clean_val = str(val).strip()
                processed_values.append(clean_val)
                
                # Also try to add as float/int for broader matching
                try:
                    numeric_val = float(clean_val)
                    if numeric_val.is_integer():
                        int_val = int(numeric_val)
                        if str(int_val) not in processed_values:
                            processed_values.append(str(int_val))
                        if int_val not in processed_values:
                            processed_values.append(int_val)
                except (ValueError, AttributeError):
                    pass
        
        print(f"  Graduation year processed: {processed_values}")
        return processed_values
    else:
        # For other filters, ensure we have clean string values
        clean_values = []
        for val in values:
            if val and str(val).strip():
                clean_values.append(str(val).strip())
        print(f"  Other filter processed: {clean_values}")
        return clean_values

def process_filters_with_conversion_v2(request_args, exclude_keys=None):
    """Improved filter processing that can handle both request.args and dict objects"""
    filters = {}
    exclude_keys = exclude_keys or ['page', 'per_page', 'search']
    
    print(f"=== PROCESSING FILTERS (V2) ===")
    print(f"Raw request args type: {type(request_args)}")
    
    # Handle both Flask request.args and regular dict
    if hasattr(request_args, 'getlist'):
        # It's a Flask request.args object
        keys_to_process = [k for k in request_args.keys() if k not in exclude_keys]
        for key in keys_to_process:
            values = request_args.getlist(key)
            print(f"Processing filter key: '{key}' with values: {values}")
            
            if not values or (len(values) == 1 and values[0] == ''):
                continue
                
            filters[key] = process_filter_values(key, values)
    else:
        # It's a regular dict where values are already lists
        for key, values in request_args.items():
            if key in exclude_keys:
                continue
                
            print(f"Processing filter key: '{key}' with values: {values}")
            
            if not values or (len(values) == 1 and values[0] == ''):
                continue
                
            filters[key] = process_filter_values(key, values)
    
    print(f"Final processed filters: {filters}")
    return filters

def apply_improved_filters(df, filters):
    """Apply filters with improved matching logic"""
    if not filters:
        return df
    
    filtered_df = df.copy()
    
    print(f"=== APPLYING IMPROVED FILTERS ===")
    print(f"Original dataframe shape: {filtered_df.shape}")
    
    for filter_key, filter_values in filters.items():
        if not filter_values:
            continue
            
        print(f"Applying filter: {filter_key} = {filter_values}")
        
        if filter_key not in filtered_df.columns:
            print(f"  Warning: Column '{filter_key}' not found in dataframe")
            continue
        
        # Get the column data and handle different data types
        column_data = filtered_df[filter_key]
        
        # Create mask for matching values
        mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
        
        # Special handling for graduation year
        if 'Tahun graduasi' in filter_key:
            for filter_val in filter_values:
                # Try multiple matching strategies
                try:
                    # Direct string match
                    string_match = column_data.astype(str).str.strip() == str(filter_val).strip()
                    mask |= string_match
                    
                    # Numeric match if possible
                    if pd.api.types.is_numeric_dtype(column_data):
                        try:
                            numeric_filter = float(filter_val)
                            numeric_match = column_data == numeric_filter
                            mask |= numeric_match
                        except (ValueError, TypeError):
                            pass
                    
                    # Try converting column to numeric and compare
                    try:
                        numeric_column = pd.to_numeric(column_data, errors='coerce')
                        numeric_filter = float(filter_val)
                        numeric_match = numeric_column == numeric_filter
                        mask |= numeric_match.fillna(False)
                    except (ValueError, TypeError):
                        pass
                        
                except Exception as e:
                    print(f"    Error processing graduation year filter {filter_val}: {e}")
                    
        else:
            # Standard string matching for other filters
            for filter_val in filter_values:
                try:
                    string_match = column_data.astype(str).str.strip() == str(filter_val).strip()
                    mask |= string_match
                except Exception as e:
                    print(f"    Error processing filter {filter_val}: {e}")
        
        # Apply the mask
        before_count = len(filtered_df)
        filtered_df = filtered_df[mask]
        after_count = len(filtered_df)
        
        print(f"  Filter '{filter_key}' reduced data from {before_count} to {after_count} rows")
        
        if after_count == 0:
            print(f"  Warning: Filter '{filter_key}' resulted in empty dataset")
            break
    
    print(f"Final filtered dataframe shape: {filtered_df.shape}")
    return filtered_df

@status_pekerjaan_bp.route('/')
def index():
    """Main status pekerjaan dashboard page"""
    return render_template('statuspekerjaan.html')

@status_pekerjaan_bp.route('/table')
def table_view():
    """Table view for status pekerjaan data"""
    return render_template('data_table.html', 
                         page_title='Status Pekerjaan Data Table',
                         api_endpoint='/status-pekerjaan/api/table-data')

@status_pekerjaan_bp.route('/api/test')
def api_test():
    """Test endpoint to verify the blueprint is working"""
    return jsonify({
        'status': 'success',
        'message': 'Status Pekerjaan API is working',
        'available_columns': list(df.columns) if not df.empty else [],
        'total_records': len(df)
    })

@status_pekerjaan_bp.route('/api/debug-columns')
def api_debug_columns():
    """Debug endpoint to check column names and graduation year data"""
    try:
        sample_df = df.copy()
        
        # Find columns that might contain graduation year
        grad_columns = [col for col in sample_df.columns if 'tahun' in col.lower() or 'graduasi' in col.lower() or 'grad' in col.lower()]
        
        result = {
            'total_columns': len(sample_df.columns),
            'all_columns': list(sample_df.columns),
            'graduation_columns': grad_columns,
            'sample_data': {}
        }
        
        # Get sample data for graduation columns
        for col in grad_columns:
            sample_values = sample_df[col].dropna().head(10).tolist()
            unique_count = sample_df[col].nunique()
            result['sample_data'][col] = {
                'sample_values': sample_values,
                'unique_count': unique_count,
                'total_non_null': sample_df[col].count()
            }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@status_pekerjaan_bp.route('/api/summary')
def api_summary():
    """Get enhanced summary statistics for employment status"""
    try:
        # Use improved filter processing
        filters = process_filters_with_conversion_v2(request.args)
        
        print(f"=== API SUMMARY DEBUG ===")
        print(f"Processed filters: {filters}")
        
        # Apply improved filtering
        filtered_df = apply_improved_filters(df, filters)
        
        print(f"Filtered DF shape: {filtered_df.shape}")
        print(f"Original DF shape: {df.shape}")
        
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
        
        print(f"Summary stats: {enhanced_stats}")
        return jsonify(enhanced_stats)
        
    except Exception as e:
        print(f"Error in API summary: {str(e)}")
        import traceback
        print(traceback.format_exc())
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
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
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

@status_pekerjaan_bp.route('/api/employment-status-table')
def api_employment_status_table():
    """Get table data for employment status chart"""
    try:
        filters = process_filters_with_conversion_v2(
            request.args, 
            exclude_keys=['page', 'per_page', 'search']
        )
        filtered_df = apply_improved_filters(df, filters)
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        
        # Define relevant columns for employment status
        relevant_columns = [
            'Adakah anda kini bekerja?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?'
        ]
        
        available_columns = [col for col in relevant_columns if col in filtered_df.columns]
        
        # Create filtered processor and get data
        class FilteredProcessor:
            def __init__(self, df):
                self.filtered_df = df
                
            def get_table_data(self, page, per_page, search, columns):
                df_subset = self.filtered_df[columns] if columns else self.filtered_df
                
                # Apply search if provided
                if search:
                    search_mask = df_subset.astype(str).apply(
                        lambda x: x.str.contains(search, case=False, na=False)
                    ).any(axis=1)
                    df_subset = df_subset[search_mask]
                
                # Calculate pagination
                total = len(df_subset)
                pages = (total + per_page - 1) // per_page
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                
                # Get page data
                page_data = df_subset.iloc[start_idx:end_idx].fillna('').to_dict('records')
                
                return {
                    'data': page_data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total,
                        'pages': pages
                    },
                    'columns': list(df_subset.columns)
                }
        
        processor = FilteredProcessor(filtered_df)
        data = processor.get_table_data(page, per_page, search, available_columns)
        return jsonify(data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'data': [],
            'pagination': {'page': 1, 'per_page': 50, 'total': 0, 'pages': 0},
            'columns': []
        }), 500

@status_pekerjaan_bp.route('/api/current-job-status')
def api_current_job_status():
    """Get current job status for working respondents - Bar Chart"""
    try:
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
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

@status_pekerjaan_bp.route('/api/job-status-table')
def api_job_status_table():
    """Get table data for job status chart"""
    try:
        filters = process_filters_with_conversion_v2(
            request.args, 
            exclude_keys=['page', 'per_page', 'search']
        )
        filtered_df = apply_improved_filters(df, filters)
        
        # Filter for working respondents only
        employment_column = 'Adakah anda kini bekerja?'
        df_working = filtered_df[
            filtered_df[employment_column].isin(['Ya, bekerja sepenuh masa', 'Ya, bekerja separuh masa'])
        ].copy()
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        
        relevant_columns = [
            'Adakah anda kini bekerja?',
            'Apakah status pekerjaan anda sekarang?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?'
        ]
        
        available_columns = [col for col in relevant_columns if col in df_working.columns]
        
        class FilteredProcessor:
            def __init__(self, df):
                self.filtered_df = df
                
            def get_table_data(self, page, per_page, search, columns):
                df_subset = self.filtered_df[columns] if columns else self.filtered_df
                
                if search:
                    search_mask = df_subset.astype(str).apply(
                        lambda x: x.str.contains(search, case=False, na=False)
                    ).any(axis=1)
                    df_subset = df_subset[search_mask]
                
                total = len(df_subset)
                pages = (total + per_page - 1) // per_page
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                
                page_data = df_subset.iloc[start_idx:end_idx].fillna('').to_dict('records')
                
                return {
                    'data': page_data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total,
                        'pages': pages
                    },
                    'columns': list(df_subset.columns)
                }
        
        processor = FilteredProcessor(df_working)
        data = processor.get_table_data(page, per_page, search, available_columns)
        return jsonify(data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'data': [],
            'pagination': {'page': 1, 'per_page': 50, 'total': 0, 'pages': 0},
            'columns': []
        }), 500

@status_pekerjaan_bp.route('/api/time-to-first-job')
def api_time_to_first_job():
    """Get time taken to get first job after graduation - Area Chart"""
    try:
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
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

@status_pekerjaan_bp.route('/api/time-to-job-table')
def api_time_to_job_table():
    """Get table data for time to first job chart"""
    try:
        filters = process_filters_with_conversion_v2(
            request.args, 
            exclude_keys=['page', 'per_page', 'search']
        )
        filtered_df = apply_improved_filters(df, filters)
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        
        relevant_columns = [
            'Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?',
            'Adakah anda kini bekerja?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?'
        ]
        
        available_columns = [col for col in relevant_columns if col in filtered_df.columns]
        
        class FilteredProcessor:
            def __init__(self, df):
                self.filtered_df = df
                
            def get_table_data(self, page, per_page, search, columns):
                df_subset = self.filtered_df[columns] if columns else self.filtered_df
                
                if search:
                    search_mask = df_subset.astype(str).apply(
                        lambda x: x.str.contains(search, case=False, na=False)
                    ).any(axis=1)
                    df_subset = df_subset[search_mask]
                
                total = len(df_subset)
                pages = (total + per_page - 1) // per_page
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                
                page_data = df_subset.iloc[start_idx:end_idx].fillna('').to_dict('records')
                
                return {
                    'data': page_data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total,
                        'pages': pages
                    },
                    'columns': list(df_subset.columns)
                }
        
        processor = FilteredProcessor(filtered_df)
        data = processor.get_table_data(page, per_page, search, available_columns)
        return jsonify(data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'data': [],
            'pagination': {'page': 1, 'per_page': 50, 'total': 0, 'pages': 0},
            'columns': []
        }), 500

@status_pekerjaan_bp.route('/api/current-job-types')
def api_current_job_types():
    """Get current job types distribution - Bar Chart"""
    try:
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
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

@status_pekerjaan_bp.route('/api/job-types-table')
def api_job_types_table():
    """Get table data for job types chart"""
    try:
        filters = process_filters_with_conversion_v2(
            request.args, 
            exclude_keys=['page', 'per_page', 'search']
        )
        filtered_df = apply_improved_filters(df, filters)
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        
        relevant_columns = [
            'Apakah jenis pekerjaan anda sekarang',
            'Adakah anda kini bekerja?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?'
        ]
        
        available_columns = [col for col in relevant_columns if col in filtered_df.columns]
        
        class FilteredProcessor:
            def __init__(self, df):
                self.filtered_df = df
                
            def get_table_data(self, page, per_page, search, columns):
                df_subset = self.filtered_df[columns] if columns else self.filtered_df
                
                if search:
                    search_mask = df_subset.astype(str).apply(
                        lambda x: x.str.contains(search, case=False, na=False)
                    ).any(axis=1)
                    df_subset = df_subset[search_mask]
                
                total = len(df_subset)
                pages = (total + per_page - 1) // per_page
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                
                page_data = df_subset.iloc[start_idx:end_idx].fillna('').to_dict('records')
                
                return {
                    'data': page_data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total,
                        'pages': pages
                    },
                    'columns': list(df_subset.columns)
                }
        
        processor = FilteredProcessor(filtered_df)
        data = processor.get_table_data(page, per_page, search, available_columns)
        return jsonify(data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'data': [],
            'pagination': {'page': 1, 'per_page': 50, 'total': 0, 'pages': 0},
            'columns': []
        }), 500

@status_pekerjaan_bp.route('/api/job-finding-factors')
def api_job_finding_factors():
    """Get job finding factors grouped analysis - Bar Chart"""
    try:
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
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

@status_pekerjaan_bp.route('/api/job-factors-table')
def api_job_factors_table():
    """Get table data for job finding factors chart"""
    try:
        filters = process_filters_with_conversion_v2(
            request.args, 
            exclude_keys=['page', 'per_page', 'search']
        )
        filtered_df = apply_improved_filters(df, filters)
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        
        relevant_columns = [
            'Apakah faktor utama yang membantu anda mendapat pekerjaan tersebut?',
            'Adakah anda kini bekerja?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?'
        ]
        
        available_columns = [col for col in relevant_columns if col in filtered_df.columns]
        
        class FilteredProcessor:
            def __init__(self, df):
                self.filtered_df = df
                
            def get_table_data(self, page, per_page, search, columns):
                df_subset = self.filtered_df[columns] if columns else self.filtered_df
                
                if search:
                    search_mask = df_subset.astype(str).apply(
                        lambda x: x.str.contains(search, case=False, na=False)
                    ).any(axis=1)
                    df_subset = df_subset[search_mask]
                
                total = len(df_subset)
                pages = (total + per_page - 1) // per_page
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                
                page_data = df_subset.iloc[start_idx:end_idx].fillna('').to_dict('records')
                
                return {
                    'data': page_data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total,
                        'pages': pages
                    },
                    'columns': list(df_subset.columns)
                }
        
        processor = FilteredProcessor(filtered_df)
        data = processor.get_table_data(page, per_page, search, available_columns)
        return jsonify(data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'data': [],
            'pagination': {'page': 1, 'per_page': 50, 'total': 0, 'pages': 0},
            'columns': []
        }), 500

@status_pekerjaan_bp.route('/api/table-data')
def api_table_data():
    """Get paginated table data for status pekerjaan"""
    try:
        filters = process_filters_with_conversion_v2(
            request.args, 
            exclude_keys=['page', 'per_page', 'search']
        )
        filtered_df = apply_improved_filters(df, filters)
        
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
        
        available_columns = [col for col in relevant_columns if col in filtered_df.columns]
        
        class FilteredProcessor:
            def __init__(self, df):
                self.filtered_df = df
                
            def get_table_data(self, page, per_page, search, columns):
                df_subset = self.filtered_df[columns] if columns else self.filtered_df
                
                if search:
                    search_mask = df_subset.astype(str).apply(
                        lambda x: x.str.contains(search, case=False, na=False)
                    ).any(axis=1)
                    df_subset = df_subset[search_mask]
                
                total = len(df_subset)
                pages = (total + per_page - 1) // per_page
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                
                page_data = df_subset.iloc[start_idx:end_idx].fillna('').to_dict('records')
                
                return {
                    'data': page_data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total,
                        'pages': pages
                    },
                    'columns': list(df_subset.columns)
                }
        
        processor = FilteredProcessor(filtered_df)
        data = processor.get_table_data(page, per_page, search, available_columns)
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
        filters = process_filters_with_conversion_v2(
            request.args, 
            exclude_keys=['format']
        )
        filtered_df = apply_improved_filters(df, filters)
        
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
        
        available_columns = [col for col in relevant_columns if col in filtered_df.columns]
        export_df = filtered_df[available_columns]
        
        if format_type == 'csv':
            output = io.StringIO()
            export_df.to_csv(output, index=False)
            data = output.getvalue().encode('utf-8')
            mimetype = 'text/csv'
            filename = 'status_pekerjaan_data.csv'
        elif format_type == 'excel':
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Status Pekerjaan Data')
            data = output.getvalue()
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = 'status_pekerjaan_data.xlsx'
        else:
            data = export_df.to_json(orient='records', indent=2).encode('utf-8')
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
        sample_df = df.copy()
        filters = {}
        
        filter_columns = [
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?',
            'Adakah anda kini bekerja?',
            'Apakah jenis pekerjaan anda sekarang'
        ]
        
        # Debug: Print all column names to see exact format
        print("Available columns in dataset:")
        for i, col in enumerate(sample_df.columns):
            print(f"  {i}: '{col}'")
        
        for column in filter_columns:
            if column in sample_df.columns:
                # Get unique values and handle different data types
                unique_values = sample_df[column].dropna().unique()
                print(f"Column '{column}' has {len(unique_values)} unique values: {list(unique_values)[:5]}...")
                
                # Special handling for graduation years - ensure consistent string format
                if 'Tahun graduasi' in column:
                    processed_values = []
                    for val in unique_values:
                        # Convert to string and clean
                        str_val = str(val).strip()
                        if str_val and str_val != 'nan':
                            processed_values.append(str_val)
                    
                    # Sort numerically if possible, otherwise alphabetically
                    try:
                        processed_values = sorted(processed_values, key=lambda x: float(x), reverse=True)
                    except (ValueError, TypeError):
                        processed_values = sorted(processed_values)
                    
                    filters[column] = processed_values
                    print(f"  Graduation years after processing: {processed_values}")
                else:
                    # Convert all values to string for consistency and clean
                    processed_values = []
                    for val in unique_values:
                        str_val = str(val).strip()
                        if str_val and str_val != 'nan':
                            processed_values.append(str_val)
                    
                    filters[column] = sorted(processed_values)
                    print(f"  Other filter processed: {len(processed_values)} values")
            else:
                print(f"Column '{column}' not found in dataset")
                filters[column] = []
        
        return jsonify(filters)
        
    except Exception as e:
        print(f"Error in api_available_filters: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e), 'filters': {}}), 500