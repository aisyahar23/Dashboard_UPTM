from flask import Blueprint, render_template, request, jsonify, send_file
from models.data_processor import DataProcessor, load_excel_data
import io
import os
import pandas as pd
from collections import Counter
import numpy as np

sosioekonomi_bp = Blueprint('sosioekonomi', __name__)

# Load data from Excel file
EXCEL_FILE_PATH = 'data/Questionnaire.xlsx'
df = load_excel_data(EXCEL_FILE_PATH)
data_processor = DataProcessor(df)

# Centralized Chart Data Formatter for consistent data structure
class ChartDataFormatter:
    """Format chart data consistently for the centralized chart configuration system"""
    
    @staticmethod
    def format_pie_chart(data_series, title="Distribution"):
        """Format data for pie charts - compatible with centralized config"""
        return {
            'labels': data_series.index.tolist(),
            'datasets': [{
                'label': title,
                'data': data_series.values.tolist()
                # Colors and styling will be applied by EnhancedChartFactory
            }]
        }
    
    @staticmethod  
    def format_bar_chart(data_series, title="Chart", sort_desc=True):
        """Format data for bar charts - compatible with centralized config"""
        if sort_desc:
            data_series = data_series.sort_values(ascending=False)
        
        return {
            'labels': data_series.index.tolist(),
            'datasets': [{
                'label': title,
                'data': data_series.values.tolist()
                # Colors and styling will be applied by EnhancedChartFactory
            }]
        }
    
    @staticmethod
    def format_stacked_bar_chart(grouped_data, title="Stacked Chart"):
        """Format data for stacked bar charts"""
        if grouped_data.empty:
            return {
                'labels': ['No Data'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1]
                }]
            }
        
        datasets = []
        for column in grouped_data.columns:
            datasets.append({
                'label': str(column),
                'data': [int(val) for val in grouped_data[column].values.tolist()]
            })
        
        return {
            'labels': [str(label) for label in grouped_data.index.tolist()],
            'datasets': datasets
        }

formatter = ChartDataFormatter()

@sosioekonomi_bp.route('/')
def index():
    """Main sosioekonomi dashboard page"""
    return render_template('sosioekonomi.html')

@sosioekonomi_bp.route('/table')
def table_view():
    """Table view for sosioekonomi data"""
    return render_template('data_table.html', 
                         page_title='Socioeconomic Status Data Table',
                         api_endpoint='/sosioekonomi/api/table-data')

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

@sosioekonomi_bp.route('/api/test')
def api_test():
    """Test endpoint to verify the blueprint is working"""
    return jsonify({
        'status': 'success',
        'message': 'Sosioekonomi API is working',
        'available_columns': list(df.columns) if not df.empty else [],
        'total_records': len(df)
    })

@sosioekonomi_bp.route('/api/debug-data')
def api_debug_data():
    """Debug endpoint to check data structure"""
    try:
        grad_col = 'Tahun graduasi anda?'
        sample_data = {}
        
        if grad_col in df.columns:
            grad_data = df[grad_col].dropna()
            sample_data['graduation_years'] = {
                'unique_values': sorted(grad_data.unique().tolist()),
                'value_counts': grad_data.value_counts().to_dict(),
                'data_types': [str(type(x)) for x in grad_data.unique()[:5]]
            }
        
        return jsonify({
            'total_records': len(df),
            'columns': list(df.columns),
            'sample_data': sample_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sosioekonomi_bp.route('/api/summary')
def api_summary():
    """Get enhanced summary statistics for socioeconomic status"""
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
        
        # Income analysis
        income_column = 'Pendapatan isi rumah bulanan keluarga anda?'
        avg_income_range = "N/A"
        high_income_rate = 0
        
        if income_column in filtered_df.columns:
            income_counts = filtered_df[income_column].value_counts()
            if len(income_counts) > 0:
                avg_income_range = income_counts.index[0]
                
                # Calculate high income rate (above RM5000)
                high_income_mask = income_counts.index.str.contains(
                    'RM5|RM6|RM7|RM8|RM9|RM10|lebih', 
                    case=False, 
                    na=False, 
                    regex=True
                )
                high_income_responses = income_counts[high_income_mask].sum()
                
                total_income_responses = income_counts.sum()
                if total_income_responses > 0:
                    high_income_rate = (high_income_responses / total_income_responses) * 100
        
        # Education financing analysis
        financing_column = 'Bagaimana anda membiayai pendidikan anda?'
        loan_financing_rate = 0
        most_common_financing = "N/A"
        
        if financing_column in filtered_df.columns:
            financing_counts = filtered_df[financing_column].value_counts()
            if len(financing_counts) > 0:
                most_common_financing = financing_counts.index[0]
                
                # Calculate loan financing rate
                loan_mask = financing_counts.index.str.contains('Pinjaman', case=False, na=False)
                loan_responses = financing_counts[loan_mask].sum()
                
                total_financing_responses = financing_counts.sum()
                if total_financing_responses > 0:
                    loan_financing_rate = (loan_responses / total_financing_responses) * 100
        
        # Employment advantage analysis
        advantage_column = 'Adakah jenis pembiayaan ini memberi kelebihan dalam mencari kerja?'
        advantage_rate = 0
        
        if advantage_column in filtered_df.columns:
            advantage_counts = filtered_df[advantage_column].value_counts()
            if len(advantage_counts) > 0:
                yes_responses = advantage_counts.get('Ya', 0)
                total_advantage_responses = advantage_counts.sum()
                if total_advantage_responses > 0:
                    advantage_rate = (yes_responses / total_advantage_responses) * 100
        
        enhanced_stats = {
            'total_records': total_records,
            'avg_income_range': avg_income_range,
            'high_income_rate': round(high_income_rate, 1),
            'loan_financing_rate': round(loan_financing_rate, 1),
            'most_common_financing': most_common_financing,
            'advantage_rate': round(advantage_rate, 1),
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
            'avg_income_range': 'N/A',
            'high_income_rate': 0,
            'loan_financing_rate': 0,
            'most_common_financing': 'N/A',
            'advantage_rate': 0
        }), 500

@sosioekonomi_bp.route('/api/household-income')
def api_household_income():
    """Get household income distribution - Uses 'household-income' color scheme"""
    try:
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
        income_column = 'Pendapatan isi rumah bulanan keluarga anda?'
        
        if income_column not in filtered_df.columns:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Data Available']),
                "Pendapatan Isi Rumah"
            ))
        
        # Get income distribution counts
        income_counts = filtered_df[income_column].value_counts()
        
        # Define logical order for income ranges
        income_order = [
            'Kurang daripada RM1,000',
            'RM1,000 - RM2,999',
            'RM3,000 - RM4,999', 
            'RM5,000 - RM6,999',
            'RM7,000 - RM9,999',
            'RM10,000 dan lebih'
        ]
        
        # Sort according to logical order
        ordered_data = []
        ordered_labels = []
        for income_range in income_order:
            if income_range in income_counts.index:
                ordered_labels.append(income_range)
                ordered_data.append(int(income_counts[income_range]))
        
        # Add any remaining categories not in our predefined order
        for income_range in income_counts.index:
            if income_range not in income_order:
                ordered_labels.append(str(income_range))
                ordered_data.append(int(income_counts[income_range]))
        
        chart_data = {
            'labels': ordered_labels,
            'datasets': [{
                'label': 'Bilangan Responden',
                'data': ordered_data
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in household income endpoint: {str(e)}")
        return jsonify(formatter.format_bar_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@sosioekonomi_bp.route('/api/education-financing')
def api_education_financing():
    """Get education financing methods - Uses 'education-financing' color scheme"""
    try:
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
        financing_column = 'Bagaimana anda membiayai pendidikan anda?'
        
        if financing_column not in filtered_df.columns:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Data Available']),
                "Jenis Pembiayaan"
            ))
        
        # Get financing methods counts
        financing_counts = filtered_df[financing_column].value_counts()
        
        chart_data = formatter.format_bar_chart(
            financing_counts,
            "Kaedah Pembiayaan Pendidikan",
            sort_desc=True
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in education financing endpoint: {str(e)}")
        return jsonify(formatter.format_bar_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@sosioekonomi_bp.route('/api/father-occupation-by-income')
def api_father_occupation_by_income():
    """Get father occupation by income distribution - Uses 'father-occupation' color scheme"""
    try:
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
        income_column = 'Pendapatan isi rumah bulanan keluarga anda?'
        occupation_column = 'Pekerjaan bapa anda'
        
        if income_column not in filtered_df.columns or occupation_column not in filtered_df.columns:
            return jsonify(formatter.format_stacked_bar_chart(
                pd.DataFrame(), 
                "Pekerjaan Bapa vs Pendapatan"
            ))
        
        # Group by income and father occupation
        grouped_data = filtered_df.groupby([income_column, occupation_column]).size().unstack(fill_value=0)
        
        chart_data = formatter.format_stacked_bar_chart(
            grouped_data,
            "Pekerjaan Bapa Mengikut Pendapatan"
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in father occupation by income endpoint: {str(e)}")
        return jsonify(formatter.format_stacked_bar_chart(
            pd.DataFrame(),
            "Error"
        )), 500

@sosioekonomi_bp.route('/api/mother-occupation-by-income')
def api_mother_occupation_by_income():
    """Get mother occupation by income distribution - Uses 'mother-occupation' color scheme"""
    try:
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
        income_column = 'Pendapatan isi rumah bulanan keluarga anda?'
        occupation_column = 'Pekerjaan ibu anda?'
        
        if income_column not in filtered_df.columns or occupation_column not in filtered_df.columns:
            return jsonify(formatter.format_stacked_bar_chart(
                pd.DataFrame(),
                "Pekerjaan Ibu vs Pendapatan"
            ))
        
        # Group by income and mother occupation
        grouped_data = filtered_df.groupby([income_column, occupation_column]).size().unstack(fill_value=0)
        
        chart_data = formatter.format_stacked_bar_chart(
            grouped_data,
            "Pekerjaan Ibu Mengikut Pendapatan"
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in mother occupation by income endpoint: {str(e)}")
        return jsonify(formatter.format_stacked_bar_chart(
            pd.DataFrame(),
            "Error"
        )), 500

@sosioekonomi_bp.route('/api/financing-job-advantage')
def api_financing_job_advantage():
    """Get financing method vs job advantage - Uses 'financing-advantage' color scheme"""
    try:
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
        financing_column = 'Bagaimana anda membiayai pendidikan anda?'
        advantage_column = 'Adakah jenis pembiayaan ini memberi kelebihan dalam mencari kerja?'
        
        if financing_column not in filtered_df.columns or advantage_column not in filtered_df.columns:
            return jsonify(formatter.format_stacked_bar_chart(
                pd.DataFrame(),
                "Pembiayaan vs Kelebihan Kerja"
            ))
        
        # Group by financing method and job advantage
        grouped_data = filtered_df.groupby([financing_column, advantage_column]).size().unstack(fill_value=0)
        
        chart_data = formatter.format_stacked_bar_chart(
            grouped_data,
            "Pembiayaan vs Kelebihan Mencari Kerja"
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in financing job advantage endpoint: {str(e)}")
        return jsonify(formatter.format_stacked_bar_chart(
            pd.DataFrame(),
            "Error"
        )), 500

@sosioekonomi_bp.route('/api/debt-impact-career')
def api_debt_impact_career():
    """Get debt impact on career choices for loan-financed students - Uses 'debt-impact' color scheme"""
    try:
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
        financing_column = 'Bagaimana anda membiayai pendidikan anda?'
        debt_impact_column = 'Jika anda mempunyai pinjaman pendidikan, adakah beban hutang mempengaruhi pilihan kerjaya anda?'
        
        if financing_column not in filtered_df.columns or debt_impact_column not in filtered_df.columns:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Data Available']),
                "Kesan Hutang"
            ))
        
        # Filter for loan-financed students only
        df_loan_financed = filtered_df[
            filtered_df[financing_column].str.contains('Pinjaman pendidikan', na=False)
        ].copy()
        
        if df_loan_financed.empty:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['Tiada responden dengan pinjaman pendidikan']),
                "Kesan Hutang"
            ))
        
        # Get debt impact counts
        debt_impact_counts = df_loan_financed[debt_impact_column].value_counts()
        
        chart_data = formatter.format_bar_chart(
            debt_impact_counts,
            "Kesan Hutang terhadap Kerjaya",
            sort_desc=True
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in debt impact career endpoint: {str(e)}")
        return jsonify(formatter.format_bar_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@sosioekonomi_bp.route('/api/table-data')
def api_table_data():
    """Get paginated table data for sosioekonomi - FIXED VERSION"""
    try:
        # FIXED: Pass request.args directly and let the function handle exclusions
        filters = process_filters_with_conversion_v2(
            request.args, 
            exclude_keys=['page', 'per_page', 'search']
        )
        
        # Use improved filtering
        filtered_df = apply_improved_filters(df, filters)
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        
        # Define relevant columns for sosioekonomi
        relevant_columns = [
            'Pendapatan isi rumah bulanan keluarga anda?',
            'Pekerjaan bapa anda',
            'Pekerjaan ibu anda?',
            'Bagaimana anda membiayai pendidikan anda?',
            'Adakah jenis pembiayaan ini memberi kelebihan dalam mencari kerja?',
            'Jika anda mempunyai pinjaman pendidikan, adakah beban hutang mempengaruhi pilihan kerjaya anda?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?'
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

@sosioekonomi_bp.route('/api/chart-table-data/<chart_type>')
def api_chart_table_data(chart_type):
    """Get table data specific to each chart type - FIXED VERSION"""
    try:
        # FIXED: Pass request.args directly and let the function handle exclusions
        filters = process_filters_with_conversion_v2(
            request.args,
            exclude_keys=['page', 'per_page', 'search']
        )
        
        print(f"=== CHART TABLE DATA for {chart_type} ===")
        print("Processed filters:", filters)
        
        # Use improved filtering
        filtered_df = apply_improved_filters(df, filters)
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        
        # Define columns based on chart type
        if chart_type == 'household-income':
            columns = ['Pendapatan isi rumah bulanan keluarga anda?', 'Jantina anda?', 'Tahun graduasi anda?']
        elif chart_type == 'education-financing':
            columns = ['Bagaimana anda membiayai pendidikan anda?', 'Jantina anda?', 'Tahun graduasi anda?']
        elif chart_type == 'father-occupation':
            columns = ['Pekerjaan bapa anda', 'Pendapatan isi rumah bulanan keluarga anda?', 'Jantina anda?']
        elif chart_type == 'mother-occupation':
            columns = ['Pekerjaan ibu anda?', 'Pendapatan isi rumah bulanan keluarga anda?', 'Jantina anda?']
        elif chart_type == 'financing-advantage':
            columns = ['Bagaimana anda membiayai pendidikan anda?', 'Adakah jenis pembiayaan ini memberi kelebihan dalam mencari kerja?', 'Jantina anda?']
        elif chart_type == 'debt-impact':
            columns = ['Bagaimana anda membiayai pendidikan anda?', 'Jika anda mempunyai pinjaman pendidikan, adakah beban hutang mempengaruhi pilihan kerjaya anda?', 'Jantina anda?']
        else:
            columns = ['Tahun graduasi anda?', 'Jantina anda?', 'Institusi pendidikan MARA yang anda hadiri?']
        
        # Add common columns
        columns.extend(['Institusi pendidikan MARA yang anda hadiri?', 'Program pengajian yang anda ikuti?', 'Timestamp'])
        
        # Remove duplicates and filter available columns
        available_columns = list(dict.fromkeys([col for col in columns if col in filtered_df.columns]))
        
        print(f"Available columns for {chart_type}: {available_columns}")
        print(f"Filtered data shape: {filtered_df.shape}")
        
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
        print(f"Error in chart table data: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'data': [],
            'pagination': {'page': 1, 'per_page': 50, 'total': 0, 'pages': 0},
            'columns': []
        }), 500

@sosioekonomi_bp.route('/api/export')
def api_export():
    """Export sosioekonomi data in various formats - FIXED VERSION"""
    try:
        # FIXED: Pass request.args directly and let the function handle exclusions
        filters = process_filters_with_conversion_v2(
            request.args,
            exclude_keys=['format']
        )
        
        # Use improved filtering
        filtered_df = apply_improved_filters(df, filters)
        
        format_type = request.args.get('format', 'csv')
        
        relevant_columns = [
            'Timestamp',
            'Pendapatan isi rumah bulanan keluarga anda?',
            'Pekerjaan bapa anda',
            'Pekerjaan ibu anda?',
            'Bagaimana anda membiayai pendidikan anda?',
            'Adakah jenis pembiayaan ini memberi kelebihan dalam mencari kerja?',
            'Jika anda mempunyai pinjaman pendidikan, adakah beban hutang mempengaruhi pilihan kerjaya anda?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?'
        ]
        
        available_columns = [col for col in relevant_columns if col in filtered_df.columns]
        export_df = filtered_df[available_columns]
        
        # Create export data
        if format_type == 'csv':
            output = io.StringIO()
            export_df.to_csv(output, index=False)
            data = output.getvalue().encode('utf-8')
            mimetype = 'text/csv'
            filename = 'sosioekonomi_data.csv'
        elif format_type == 'excel':
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Sosioekonomi Data')
            data = output.getvalue()
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = 'sosioekonomi_data.xlsx'
        else:
            data = export_df.to_json(orient='records', indent=2).encode('utf-8')
            mimetype = 'application/json'
            filename = 'sosioekonomi_data.json'
        
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

@sosioekonomi_bp.route('/api/filters/available')
def api_available_filters():
    """Get available filter options for sosioekonomi data"""
    try:
        sample_df = df.copy()
        filters = {}
        
        filter_columns = [
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?',
            'Pendapatan isi rumah bulanan keluarga anda?',
            'Bagaimana anda membiayai pendidikan anda?'
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
        print(f"Error in api_available_filters: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e), 'filters': {}}), 500