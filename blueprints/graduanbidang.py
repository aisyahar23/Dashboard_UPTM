from flask import Blueprint, render_template, request, jsonify, send_file
from models.data_processor import DataProcessor, load_excel_data
import io
import os
import pandas as pd
from collections import Counter
import numpy as np

graduan_bidang_bp = Blueprint('graduan-bidang', __name__)

# Load data from Excel file
EXCEL_FILE_PATH = 'data/Questionnaire.xlsx'
df = load_excel_data(EXCEL_FILE_PATH)
data_processor = DataProcessor(df)

def process_filter_values(key, values):
    """Process filter values based on the filter type - FIXED VERSION"""
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

@graduan_bidang_bp.route('/')
def index():
    """Main graduan bidang dashboard page"""
    return render_template('graduanbidang.html')

@graduan_bidang_bp.route('/api/test')
def api_test():
    """Test endpoint to verify the blueprint is working"""
    # Get available columns for debugging
    available_columns = list(df.columns) if not df.empty else []
    
    # Check for specific columns we need
    year_columns = ['Tahun graduasi ', 'Tahun graduasi', 'Tahun graduasi anda?', 'Graduation Year']
    field_columns = ['Bidang pengajian utama ', 'Bidang pengajian utama', 'Bidang pengajian', 'Field of Study', 'Program pengajian yang anda ikuti?']
    
    # Find which columns exist
    found_year = [col for col in year_columns if col in available_columns]
    found_field = [col for col in field_columns if col in available_columns]
    
    # Search for columns containing relevant keywords
    year_keywords = ['tahun', 'year', 'graduasi', 'graduation']
    field_keywords = ['bidang', 'field', 'pengajian', 'program', 'study', 'utama']
    
    possible_year_columns = []
    possible_field_columns = []
    
    for col in available_columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in year_keywords):
            possible_year_columns.append(col)
        if any(keyword in col_lower for keyword in field_keywords):
            possible_field_columns.append(col)
    
    # Sample data
    year_sample = []
    field_sample = []
    
    if found_year and found_year[0] in df.columns:
        year_sample = df[found_year[0]].dropna().unique()[:10].tolist()
    elif possible_year_columns and possible_year_columns[0] in df.columns:
        year_sample = df[possible_year_columns[0]].dropna().unique()[:10].tolist()
        
    if found_field and found_field[0] in df.columns:
        field_sample = df[found_field[0]].dropna().unique()[:5].tolist()
    elif possible_field_columns and possible_field_columns[0] in df.columns:
        field_sample = df[possible_field_columns[0]].dropna().unique()[:5].tolist()
    
    return jsonify({
        'status': 'success',
        'message': 'Graduan Bidang API is working',
        'total_records': len(df),
        'available_columns': available_columns,
        'found_year_columns': found_year,
        'found_field_columns': found_field,
        'possible_year_columns': possible_year_columns,
        'possible_field_columns': possible_field_columns,
        'year_sample_data': [str(x) for x in year_sample],
        'field_sample_data': [str(x) for x in field_sample],
        'all_columns_with_year': [col for col in available_columns if 'tahun' in col.lower() or 'year' in col.lower()],
        'all_columns_with_field': [col for col in available_columns if 'bidang' in col.lower() or 'field' in col.lower() or 'pengajian' in col.lower()]
    })

@graduan_bidang_bp.route('/api/summary')
def api_summary():
    """Get enhanced summary statistics for graduan bidang - FIXED VERSION"""
    try:
        # Process filters with improved conversion
        filters = process_filters_with_conversion_v2(request.args)
        
        print(f"=== API SUMMARY DEBUG ===")
        print(f"Processed filters: {filters}")
        
        # Apply improved filtering
        filtered_df = apply_improved_filters(df, filters)
        
        print(f"Filtered DF shape: {filtered_df.shape}")
        print(f"Original DF shape: {df.shape}")
        
        total_records = len(filtered_df)
        
        # Initialize default values
        total_years = 0
        total_fields = 0
        most_recent_year = "N/A"
        most_common_field = "N/A"
        year_column = None
        field_column = None
        
        # Find year column - prioritize exact matches first
        year_columns = [
            'Tahun graduasi anda?',  # Most likely column name
            'Tahun graduasi ',
            'Tahun graduasi', 
            'Graduation Year', 
            'Year'
        ]
        
        # Search for year column with keywords
        year_keywords = ['tahun', 'year', 'graduasi', 'graduation']
        for col in filtered_df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in year_keywords) and col not in year_columns:
                year_columns.append(col)
        
        for col in year_columns:
            if col in filtered_df.columns:
                year_column = col
                print(f"Using year column: {year_column}")
                break
        
        if year_column:
            try:
                year_data = filtered_df[year_column].dropna()
                if len(year_data) > 0:
                    year_counts = year_data.value_counts()
                    if len(year_counts) > 0:
                        total_years = len(year_counts)
                        # Get most recent year (assuming numeric years)
                        try:
                            numeric_years = [int(float(str(year))) for year in year_counts.index if str(year).replace('.', '').isdigit()]
                            if numeric_years:
                                most_recent_year = str(max(numeric_years))
                            else:
                                most_recent_year = str(year_counts.index[0])
                        except:
                            most_recent_year = str(year_counts.index[0])
            except Exception as e:
                print(f"Error processing year data: {str(e)}")
        
        # Find field column - prioritize exact matches first
        field_columns = [
            'Program pengajian yang anda ikuti?',  # Most likely column name
            'Bidang pengajian utama ',
            'Bidang pengajian utama', 
            'Bidang pengajian', 
            'Field of Study'
        ]
        
        # Search for field column with keywords
        field_keywords = ['bidang', 'field', 'pengajian', 'program', 'study']
        for col in filtered_df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in field_keywords) and col not in field_columns:
                field_columns.append(col)
        
        for col in field_columns:
            if col in filtered_df.columns:
                field_column = col
                print(f"Using field column: {field_column}")
                break
        
        if field_column:
            try:
                field_data = filtered_df[field_column].dropna()
                if len(field_data) > 0:
                    field_counts = field_data.value_counts()
                    if len(field_counts) > 0:
                        total_fields = len(field_counts)
                        most_common_field = str(field_counts.index[0])
            except Exception as e:
                print(f"Error processing field data: {str(e)}")
        
        enhanced_stats = {
            'total_records': total_records,
            'total_years': total_years,
            'total_fields': total_fields,
            'most_recent_year': most_recent_year,
            'most_common_field': most_common_field,
            'filter_applied': len([f for f in filters.values() if f]) > 0,
            'debug_info': {
                'found_year_column': year_column,
                'found_field_column': field_column,
                'available_columns': list(filtered_df.columns)[:10],
                'data_shape': list(filtered_df.shape)
            }
        }
        
        return jsonify(enhanced_stats)
        
    except Exception as e:
        print(f"Error in summary endpoint: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'total_records': 0,
            'total_years': 0,
            'total_fields': 0,
            'most_recent_year': 'N/A',
            'most_common_field': 'N/A'
        }), 500

@graduan_bidang_bp.route('/api/field-by-year')
def api_field_by_year():
    """Get field distribution by graduation year - Stacked Bar Chart - FIXED VERSION"""
    try:
        # Process filters with improved conversion
        filters = process_filters_with_conversion_v2(request.args)
        
        # Apply improved filtering
        filtered_df = apply_improved_filters(df, filters)
        
        # Find year column - prioritize exact matches first
        year_columns = [
            'Tahun graduasi anda?',  # Most likely column name
            'Tahun graduasi ',
            'Tahun graduasi', 
            'Graduation Year', 
            'Year'
        ]
        
        # Search for year column with keywords
        year_keywords = ['tahun', 'year', 'graduasi', 'graduation']
        for col in filtered_df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in year_keywords) and col not in year_columns:
                year_columns.append(col)
        
        year_column = None
        for col in year_columns:
            if col in filtered_df.columns:
                year_column = col
                break
        
        # Find field column - prioritize exact matches first
        field_columns = [
            'Program pengajian yang anda ikuti?',  # Most likely column name
            'Bidang pengajian utama ',
            'Bidang pengajian utama', 
            'Bidang pengajian', 
            'Field of Study'
        ]
        
        # Search for field column with keywords
        field_keywords = ['bidang', 'field', 'pengajian', 'program', 'study']
        for col in filtered_df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in field_keywords) and col not in field_columns:
                field_columns.append(col)
        
        field_column = None
        for col in field_columns:
            if col in filtered_df.columns:
                field_column = col
                break
        
        print(f"Available columns for field by year chart: {list(filtered_df.columns)}")
        print(f"Year column found: {year_column}")
        print(f"Field column found: {field_column}")
        
        if not year_column or not field_column:
            return jsonify({
                'labels': ['Column Not Found'],
                'datasets': [{
                    'label': f'Missing: {year_column or "Year Column"} / {field_column or "Field Column"}',
                    'data': [1]
                }],
                'debug': {
                    'year_column_found': year_column,
                    'field_column_found': field_column,
                    'available_columns': list(filtered_df.columns),
                    'searched_year_columns': year_columns,
                    'searched_field_columns': field_columns
                }
            })
        
        # Remove NaN values and group by year and field
        clean_df = filtered_df[[year_column, field_column]].dropna()
        
        print(f"Clean dataframe shape: {clean_df.shape}")
        print(f"Sample clean data:\n{clean_df.head()}")
        
        if clean_df.empty:
            return jsonify({
                'labels': ['No Clean Data'],
                'datasets': [{
                    'label': 'Empty after cleaning',
                    'data': [1]
                }]
            })
        
        # Group by year and field - REPLICATING COLAB CODE EXACTLY
        # field_by_year = df.groupby(['Tahun graduasi ', 'Bidang pengajian utama ']).size().unstack(fill_value=0)
        grouped_data = clean_df.groupby([year_column, field_column]).size().unstack(fill_value=0)
        
        print(f"Grouped data shape: {grouped_data.shape}")
        print(f"Grouped data:\n{grouped_data}")
        
        if grouped_data.empty:
            return jsonify({
                'labels': ['Empty Grouped Data'],
                'datasets': [{
                    'label': 'No grouped data',
                    'data': [1]
                }]
            })
        
        # Sort years if they are numeric
        try:
            # Try to sort years numerically
            sorted_index = sorted(grouped_data.index, key=lambda x: int(float(str(x))))
            grouped_data = grouped_data.reindex(sorted_index)
        except:
            # If sorting fails, keep original order
            pass
        
        # Prepare data for stacked bar chart
        labels = [str(year) for year in grouped_data.index.tolist()]
        datasets = []
        
        # Each field becomes a dataset (series in the stacked bar)
        for field in grouped_data.columns:
            datasets.append({
                'label': str(field),
                'data': [int(val) for val in grouped_data[field].tolist()]
            })
        
        chart_data = {
            'labels': labels,
            'datasets': datasets
        }
        
        print(f"Final chart data: {chart_data}")
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in field by year endpoint: {str(e)}")
        print(f"Available columns: {list(filtered_df.columns) if 'filtered_df' in locals() else 'No DataFrame'}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }],
            'debug': {
                'error_details': str(e),
                'available_columns': list(filtered_df.columns) if 'filtered_df' in locals() else []
            }
        }), 500

@graduan_bidang_bp.route('/api/chart-table-data/field-by-year')
def api_chart_table_data():
    """Get table data for field-by-year chart - FIXED VERSION"""
    try:
        # Process filters with improved conversion
        filters = process_filters_with_conversion_v2(
            request.args,
            exclude_keys=['page', 'per_page', 'search']
        )
        
        # Apply improved filtering
        filtered_df = apply_improved_filters(df, filters)
        
        # Define relevant columns for field-by-year chart
        relevant_columns = [
            'Tahun graduasi anda?',
            'Tahun graduasi ',
            'Program pengajian yang anda ikuti?',
            'Bidang pengajian utama ',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?'
        ]
        
        # Filter to only include columns that exist in the dataframe
        available_columns = [col for col in relevant_columns if col in filtered_df.columns]
        
        # If no specific columns found, include first few columns
        if not available_columns:
            available_columns = list(filtered_df.columns)[:6]
        
        # Prepare data for the modal
        filtered_data = filtered_df[available_columns].fillna('')
        
        # Convert to list of dictionaries for JSON serialization
        data_records = filtered_data.to_dict('records')
        
        return jsonify({
            'data': data_records,
            'columns': available_columns,
            'total_records': len(data_records)
        })
        
    except Exception as e:
        print(f"Error in chart table data endpoint: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
        return jsonify({
            'error': str(e),
            'data': [],
            'columns': [],
            'total_records': 0
        }), 500

@graduan_bidang_bp.route('/api/columns')
def api_columns():
    """Get all available columns and sample data for debugging"""
    try:
        available_columns = list(df.columns) if not df.empty else []
        
        # Get sample data for each column
        column_samples = {}
        for col in available_columns[:20]:  # Limit to first 20 columns
            try:
                sample_data = df[col].dropna().unique()[:5].tolist()
                column_samples[col] = [str(x) for x in sample_data]
            except Exception as e:
                column_samples[col] = [f"Error: {str(e)}"]
        
        # Search for year and field related columns
        year_related = [col for col in available_columns if any(keyword in col.lower() for keyword in ['tahun', 'year', 'graduasi', 'graduation'])]
        field_related = [col for col in available_columns if any(keyword in col.lower() for keyword in ['bidang', 'field', 'pengajian', 'program', 'study'])]
        
        return jsonify({
            'total_columns': len(available_columns),
            'all_columns': available_columns,
            'column_samples': column_samples,
            'year_related_columns': year_related,
            'field_related_columns': field_related,
            'data_shape': df.shape if not df.empty else [0, 0]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@graduan_bidang_bp.route('/api/table-data')
def api_table_data():
    """Get paginated table data for graduan bidang - FIXED VERSION"""
    try:
        # Process filters with improved conversion
        filters = process_filters_with_conversion_v2(
            request.args, 
            exclude_keys=['page', 'per_page', 'search']
        )
        
        # Apply improved filtering
        filtered_df = apply_improved_filters(df, filters)
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        
        # Define relevant columns for graduan bidang
        relevant_columns = [
            'Tahun graduasi anda?',
            'Tahun graduasi ',
            'Bidang pengajian utama ',
            'Bidang pengajian',
            'Program pengajian yang anda ikuti?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?'
        ]
        
        available_columns = [col for col in relevant_columns if col in filtered_df.columns]
        
        # Create a mock data processor with the filtered data
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
        print(f"Error in table data: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'data': [],
            'pagination': {'page': 1, 'per_page': 50, 'total': 0, 'pages': 0},
            'columns': []
        }), 500

@graduan_bidang_bp.route('/api/export')
def api_export():
    """Export graduan bidang data in various formats - FIXED VERSION"""
    try:
        # Get chart_type if provided (for chart-specific exports)
        chart_type = request.args.get('chart_type', '')
        
        # Process filters with improved conversion
        filters = process_filters_with_conversion_v2(
            request.args, 
            exclude_keys=['format', 'chart_type']
        )
        
        # Apply improved filtering
        filtered_df = apply_improved_filters(df, filters)
        
        format_type = request.args.get('format', 'csv')
        
        # Define columns based on chart type or use default
        if chart_type == 'field-by-year':
            relevant_columns = [
                'Timestamp',
                'Tahun graduasi anda?',
                'Tahun graduasi ',
                'Program pengajian yang anda ikuti?',
                'Bidang pengajian utama ',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?'
            ]
        else:
            relevant_columns = [
                'Timestamp',
                'Tahun graduasi anda?',
                'Tahun graduasi ',
                'Bidang pengajian utama ',
                'Bidang pengajian',
                'Program pengajian yang anda ikuti?',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?'
            ]
        
        available_columns = [col for col in relevant_columns if col in filtered_df.columns]
        export_df = filtered_df[available_columns]
        
        # Create export data
        if format_type == 'csv':
            output = io.StringIO()
            export_df.to_csv(output, index=False)
            data = output.getvalue().encode('utf-8')
            mimetype = 'text/csv'
            filename = 'graduan_bidang_data.csv'
        elif format_type == 'excel':
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Graduan Bidang Data')
            data = output.getvalue()
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = 'graduan_bidang_data.xlsx'
        else:
            data = export_df.to_json(orient='records', indent=2).encode('utf-8')
            mimetype = 'application/json'
            filename = 'graduan_bidang_data.json'
        
        return send_file(
            io.BytesIO(data),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Export error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@graduan_bidang_bp.route('/api/filters/available')
def api_available_filters():
    """Get available filter options for graduan bidang data - FIXED VERSION"""
    try:
        sample_df = df.copy()
        filters = {}
        
        filter_columns = [
            'Tahun graduasi anda?',  # Primary graduation year column
            'Tahun graduasi ',
            'Tahun graduasi',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?',
            'Bidang pengajian utama ',
            'Bidang pengajian'
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
                        processed_values = sorted(processed_values, key=lambda x: float(x))
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
        print(f"Error in available filters endpoint: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e), 'filters': {}}), 500