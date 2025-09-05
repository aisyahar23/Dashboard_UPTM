from flask import Blueprint, render_template, request, jsonify, send_file
from models.data_processor import DataProcessor, load_excel_data
import io
import os
import pandas as pd
from collections import Counter
import numpy as np

sektor_gaji_bp = Blueprint('sektor-gaji', __name__)

# Load data from Excel file
EXCEL_FILE_PATH = 'data/Questionnaire.xlsx'
df = load_excel_data(EXCEL_FILE_PATH)
data_processor = DataProcessor(df)

@sektor_gaji_bp.route('/')
def index():
    """Main sektor gaji dashboard page"""
    return render_template('industri_gaji.html')

@sektor_gaji_bp.route('/api/summary')
def api_summary():
    """Get enhanced summary statistics for sektor gaji"""
    try:
        # Fixed filter handling - get all parameters properly
        filters = {}
        for key in request.args.keys():
            values = request.args.getlist(key)
            # Convert graduation year strings back to integers if needed
            if key == 'Tahun graduasi anda?':
                try:
                    values = [int(float(v)) for v in values if v.strip()]
                except (ValueError, TypeError):
                    print(f"Warning: Could not convert graduation years to int: {values}")
                    # Keep as strings if conversion fails
                    pass
            filters[key] = values
        
        print(f"API Summary - Received filters: {filters}")
        
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        print(f"Filtered data shape: {filtered_df.shape}")
        
        total_records = len(filtered_df)
        
        # Initialize default values
        avg_salary_range = "N/A"
        high_salary_rate = 0
        most_common_education = "N/A"
        most_common_sector = "N/A"
        private_sector_rate = 0
        most_common_field = "N/A"
        education_column = None
        field_column = None
        
        # Salary range analysis
        salary_column = 'Berapakah julat gaji bulanan anda sekarang?'
        
        if salary_column in filtered_df.columns:
            # Remove NaN values first
            salary_data = filtered_df[salary_column].dropna()
            if len(salary_data) > 0:
                salary_counts = salary_data.value_counts()
                if len(salary_counts) > 0:
                    avg_salary_range = str(salary_counts.index[0])
                    total_salary_responses = salary_counts.sum()
                    
                    # Calculate high salary rate (RM4000 and above) - check various patterns
                    high_salary_patterns = ['RM4', 'RM5', 'RM6', 'RM7', 'RM8', 'RM9', 'RM10', '4000', '5000', '6000', '7000', '8000', '9000', '10000']
                    high_salary_responses = 0
                    
                    for salary_range in salary_counts.index:
                        salary_str = str(salary_range)
                        if any(pattern in salary_str for pattern in high_salary_patterns):
                            high_salary_responses += salary_counts[salary_range]
                    
                    if total_salary_responses > 0:
                        high_salary_rate = (high_salary_responses / total_salary_responses) * 100

        # Education level analysis - try multiple possible column names including broader search
        education_columns = [
            'Tahap pendidikan tertinggi', 
            'Tahap pendidikan', 
            'Education Level', 
            'Pendidikan',
            'Institusi pendidikan MARA yang anda hadiri?',  # Try using institution as education proxy
            'Program pengajian yang anda ikuti?'  # Try using program as education proxy
        ]
        
        # Also search for any column containing education-related keywords
        education_keywords = ['pendidikan', 'education', 'level', 'tahap']
        for col in filtered_df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in education_keywords) and col not in education_columns:
                education_columns.append(col)
        
        for col in education_columns:
            if col in filtered_df.columns:
                education_column = col
                print(f"Using education column: {education_column}")
                break
        
        if education_column:
            try:
                education_data = filtered_df[education_column].dropna()
                if len(education_data) > 0:
                    education_counts = education_data.value_counts()
                    if len(education_counts) > 0:
                        most_common_education = str(education_counts.index[0])
            except Exception as e:
                print(f"Error processing education data: {str(e)}")

        # Sector analysis
        sector_column = 'Apakah sektor pekerjaan anda?'
        if sector_column in filtered_df.columns:
            try:
                sector_data = filtered_df[sector_column].dropna()
                if len(sector_data) > 0:
                    sector_counts = sector_data.value_counts()
                    if len(sector_counts) > 0:
                        most_common_sector = str(sector_counts.index[0])
                        total_sector_responses = sector_counts.sum()
                        
                        # Calculate private sector rate - check for various private sector patterns
                        private_patterns = ['Swasta', 'Private', 'swasta', 'private']
                        private_responses = 0
                        
                        for sector in sector_counts.index:
                            sector_str = str(sector)
                            if any(pattern in sector_str for pattern in private_patterns):
                                private_responses += sector_counts[sector]
                        
                        if total_sector_responses > 0:
                            private_sector_rate = (private_responses / total_sector_responses) * 100
            except Exception as e:
                print(f"Error processing sector data: {str(e)}")

        # Field matching analysis - enhanced search
        field_columns = [
            'Bidang pengajian', 
            'Field of Study', 
            'Bidang', 
            'Program pengajian yang anda ikuti?',
            'Institusi pendidikan MARA yang anda hadiri?'  # Try institution as field proxy
        ]
        
        # Also search for any column containing field-related keywords
        field_keywords = ['bidang', 'field', 'program', 'pengajian', 'study']
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
                        most_common_field = str(field_counts.index[0])
            except Exception as e:
                print(f"Error processing field data: {str(e)}")

        enhanced_stats = {
            'total_records': total_records,
            'avg_salary_range': avg_salary_range,
            'high_salary_rate': round(high_salary_rate, 1),
            'most_common_education': most_common_education,
            'most_common_sector': most_common_sector,
            'private_sector_rate': round(private_sector_rate, 1),
            'most_common_field': most_common_field,
            'filter_applied': len([f for f in filters.values() if f]) > 0,
            'debug_info': {
                'found_education_column': education_column,
                'found_field_column': field_column,
                'available_columns': list(filtered_df.columns)[:10],  # First 10 columns for debug
                'data_shape': list(filtered_df.shape)
            }
        }
        
        print(f"Returning enhanced stats: {enhanced_stats}")
        return jsonify(enhanced_stats)
        
    except Exception as e:
        print(f"Error in summary endpoint: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'total_records': 0,
            'avg_salary_range': 'N/A',
            'high_salary_rate': 0,
            'most_common_education': 'N/A',
            'most_common_sector': 'N/A',
            'private_sector_rate': 0,
            'most_common_field': 'N/A'
        }), 500

@sektor_gaji_bp.route('/api/salary-by-field')
def api_salary_by_field():
    """Get salary distribution by field of study - Stacked Bar Chart"""
    try:
        # Fixed filter handling
        filters = {}
        for key in request.args.keys():
            values = request.args.getlist(key)
            if key == 'Tahun graduasi anda?':
                try:
                    values = [int(float(v)) for v in values if v.strip()]
                except (ValueError, TypeError):
                    pass
            filters[key] = values
        
        print(f"API Salary by Field - Received filters: {filters}")
        
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        print(f"Salary by field - Filtered data shape: {filtered_df.shape}")
        
        # Try multiple possible column names for field of study
        field_columns = ['Bidang pengajian', 'Field of Study', 'Bidang', 'Program pengajian yang anda ikuti?']
        field_column = None
        for col in field_columns:
            if col in filtered_df.columns:
                field_column = col
                print(f"Found field column: {field_column}")
                break
        
        salary_column = 'Berapakah julat gaji bulanan anda sekarang?'
        
        if not field_column or salary_column not in filtered_df.columns:
            print(f"Missing columns - Field: {field_column}, Salary: {salary_column in filtered_df.columns}")
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1]
                }]
            })
        
        # Remove NaN values and group by field and salary range
        clean_df = filtered_df[[field_column, salary_column]].dropna()
        print(f"Clean dataframe shape: {clean_df.shape}")
        
        if clean_df.empty:
            return jsonify({
                'labels': ['No Data'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1]
                }]
            })
        
        # Group by field and salary range
        grouped_data = clean_df.groupby([field_column, salary_column]).size().unstack(fill_value=0)
        print(f"Grouped data shape: {grouped_data.shape}")
        
        if grouped_data.empty:
            return jsonify({
                'labels': ['No Data'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1]
                }]
            })
        
        # Prepare data for stacked bar chart
        labels = [str(field) for field in grouped_data.index.tolist()]
        datasets = []
        
        for salary_range in grouped_data.columns:
            datasets.append({
                'label': str(salary_range),
                'data': [int(val) for val in grouped_data[salary_range].tolist()]
            })
        
        chart_data = {
            'labels': labels,
            'datasets': datasets
        }
        
        print(f"Returning field chart data: {chart_data}")
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in salary by field endpoint: {str(e)}")
        print(f"Available columns: {list(filtered_df.columns) if 'filtered_df' in locals() else 'No DataFrame'}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

@sektor_gaji_bp.route('/api/salary-by-education')
def api_salary_by_education():
    """Get salary distribution by education level - Stacked Bar Chart"""
    try:
        # Fixed filter handling
        filters = {}
        for key in request.args.keys():
            values = request.args.getlist(key)
            if key == 'Tahun graduasi anda?':
                try:
                    values = [int(float(v)) for v in values if v.strip()]
                except (ValueError, TypeError):
                    pass
            filters[key] = values
        
        print(f"API Salary by Education - Received filters: {filters}")
        
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        print(f"Salary by education - Filtered data shape: {filtered_df.shape}")
        
        # Try multiple possible column names for education - ENHANCED SEARCH
        education_columns = [
            'Tahap pendidikan tertinggi', 
            'Tahap pendidikan', 
            'Education Level', 
            'Pendidikan',
            'Institusi pendidikan MARA yang anda hadiri?',  # Use institution as education proxy
            'Program pengajian yang anda ikuti?'  # Use program as education proxy
        ]
        
        # Search for any column containing education-related keywords
        education_keywords = ['pendidikan', 'education', 'level', 'tahap', 'institusi', 'institution']
        for col in filtered_df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in education_keywords) and col not in education_columns:
                education_columns.append(col)
        
        education_column = None
        for col in education_columns:
            if col in filtered_df.columns:
                education_column = col
                print(f"Found education column for chart: {education_column}")
                break
        
        salary_column = 'Berapakah julat gaji bulanan anda sekarang?'
        
        print(f"Available columns for education chart: {list(filtered_df.columns)}")
        print(f"Education column found: {education_column}")
        print(f"Salary column exists: {salary_column in filtered_df.columns}")
        
        if not education_column or salary_column not in filtered_df.columns:
            # Return debug info instead of generic error
            return jsonify({
                'labels': ['No Education Column Found'],
                'datasets': [{
                    'label': f'Missing: {education_column or "Education Column"}',
                    'data': [1]
                }],
                'debug': {
                    'education_column_found': education_column,
                    'salary_column_exists': salary_column in filtered_df.columns,
                    'available_columns': list(filtered_df.columns),
                    'searched_education_columns': education_columns
                }
            })
        
        # Remove NaN values and group by education level and salary range
        clean_df = filtered_df[[education_column, salary_column]].dropna()
        
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
        
        # Group by education level and salary range
        grouped_data = clean_df.groupby([education_column, salary_column]).size().unstack(fill_value=0)
        
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
        
        # Prepare data for stacked bar chart
        labels = [str(education) for education in grouped_data.index.tolist()]
        datasets = []
        
        for salary_range in grouped_data.columns:
            datasets.append({
                'label': str(salary_range),
                'data': [int(val) for val in grouped_data[salary_range].tolist()]
            })
        
        chart_data = {
            'labels': labels,
            'datasets': datasets
        }
        
        print(f"Final chart data: {chart_data}")
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in salary by education endpoint: {str(e)}")
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

@sektor_gaji_bp.route('/api/employment-sectors')
def api_employment_sectors():
    """Get employment sectors distribution - Pie Chart"""
    try:
        # Fixed filter handling
        filters = {}
        for key in request.args.keys():
            values = request.args.getlist(key)
            if key == 'Tahun graduasi anda?':
                try:
                    values = [int(float(v)) for v in values if v.strip()]
                except (ValueError, TypeError):
                    pass
            filters[key] = values
        
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        # Filter for working respondents only
        employment_column = 'Adakah anda kini bekerja?'
        sector_column = 'Apakah sektor pekerjaan anda?'
        
        if employment_column in filtered_df.columns:
            df_working = filtered_df[filtered_df[employment_column].isin(['Ya, bekerja sepenuh masa', 'Ya, bekerja separuh masa'])].copy()
        else:
            df_working = filtered_df.copy()
        
        if sector_column not in df_working.columns or df_working.empty:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Sektor Pekerjaan',
                    'data': [1]
                }]
            })
        
        # Get sector distribution
        sector_counts = df_working[sector_column].value_counts()
        
        chart_data = {
            'labels': [str(label) for label in sector_counts.index.tolist()],
            'datasets': [{
                'label': 'Taburan Sektor Pekerjaan',
                'data': [int(val) for val in sector_counts.values.tolist()]
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in employment sectors endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

@sektor_gaji_bp.route('/api/salary-by-industry')
def api_salary_by_industry():
    """Get salary distribution by industry - Stacked Bar Chart"""
    try:
        # Fixed filter handling
        filters = {}
        for key in request.args.keys():
            values = request.args.getlist(key)
            if key == 'Tahun graduasi anda?':
                try:
                    values = [int(float(v)) for v in values if v.strip()]
                except (ValueError, TypeError):
                    pass
            filters[key] = values
        
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        # Filter for working respondents only
        employment_column = 'Adakah anda kini bekerja?'
        if employment_column in filtered_df.columns:
            df_working = filtered_df[filtered_df[employment_column].isin(['Ya, bekerja sepenuh masa', 'Ya, bekerja separuh masa'])].copy()
        else:
            df_working = filtered_df.copy()
        
        industry_column = 'Apakah sektor pekerjaan anda?'
        salary_column = 'Berapakah julat gaji bulanan anda sekarang?'
        
        if industry_column not in df_working.columns or salary_column not in df_working.columns or df_working.empty:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1]
                }]
            })
        
        # Group by industry and salary range
        grouped_data = df_working.groupby([industry_column, salary_column]).size().unstack(fill_value=0)
        
        if grouped_data.empty:
            return jsonify({
                'labels': ['No Data'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1]
                }]
            })
        
        # Prepare data for stacked bar chart
        labels = [str(industry) for industry in grouped_data.index.tolist()]
        datasets = []
        
        for salary_range in grouped_data.columns:
            datasets.append({
                'label': str(salary_range),
                'data': [int(val) for val in grouped_data[salary_range].tolist()]
            })
        
        chart_data = {
            'labels': labels,
            'datasets': datasets
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in salary by industry endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

@sektor_gaji_bp.route('/api/expected-vs-current-salary')
def api_expected_vs_current_salary():
    """Get expected starting salary vs current salary - Stacked Bar Chart"""
    try:
        # Fixed filter handling
        filters = {}
        for key in request.args.keys():
            values = request.args.getlist(key)
            if key == 'Tahun graduasi anda?':
                try:
                    values = [int(float(v)) for v in values if v.strip()]
                except (ValueError, TypeError):
                    pass
            filters[key] = values
        
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        # Filter for working respondents only
        employment_column = 'Adakah anda kini bekerja?'
        if employment_column in filtered_df.columns:
            df_working = filtered_df[filtered_df[employment_column].isin(['Ya, bekerja sepenuh masa', 'Ya, bekerja separuh masa'])].copy()
        else:
            df_working = filtered_df.copy()
        
        expected_column = 'Apakah jangkaan gaji permulaan yang anda anggap sesuai dengan kelulusan anda?'
        current_column = 'Berapakah julat gaji bulanan anda sekarang?'
        
        if expected_column not in df_working.columns or current_column not in df_working.columns or df_working.empty:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1]
                }]
            })
        
        # Group by expected salary and current salary
        grouped_data = df_working.groupby([expected_column, current_column]).size().unstack(fill_value=0)
        
        if grouped_data.empty:
            return jsonify({
                'labels': ['No Data'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1]
                }]
            })
        
        # Prepare data for stacked bar chart
        labels = [str(expected) for expected in grouped_data.index.tolist()]
        datasets = []
        
        for current_salary in grouped_data.columns:
            datasets.append({
                'label': str(current_salary),
                'data': [int(val) for val in grouped_data[current_salary].tolist()]
            })
        
        chart_data = {
            'labels': labels,
            'datasets': datasets
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in expected vs current salary endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

@sektor_gaji_bp.route('/api/salary-commensurate')
def api_salary_commensurate():
    """Get salary commensurate with qualifications - Bar Chart"""
    try:
        # Fixed filter handling
        filters = {}
        for key in request.args.keys():
            values = request.args.getlist(key)
            if key == 'Tahun graduasi anda?':
                try:
                    values = [int(float(v)) for v in values if v.strip()]
                except (ValueError, TypeError):
                    pass
            filters[key] = values
        
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        # Filter for working respondents only
        employment_column = 'Adakah anda kini bekerja?'
        if employment_column in filtered_df.columns:
            df_working = filtered_df[filtered_df[employment_column].isin(['Ya, bekerja sepenuh masa', 'Ya, bekerja separuh masa'])].copy()
        else:
            df_working = filtered_df.copy()
        
        commensurate_column = 'Adakah gaji anda bersesuaian dengan kelulusan anda?'
        
        if commensurate_column not in df_working.columns or df_working.empty:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Kesesuaian Gaji',
                    'data': [1]
                }]
            })
        
        # Get commensurate distribution
        commensurate_counts = df_working[commensurate_column].value_counts()
        
        chart_data = {
            'labels': [str(label) for label in commensurate_counts.index.tolist()],
            'datasets': [{
                'label': 'Kesesuaian Gaji dengan Kelulusan',
                'data': [int(val) for val in commensurate_counts.values.tolist()]
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in salary commensurate endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

# Keep existing endpoints (table, export, filters) with fixed filter handling
@sektor_gaji_bp.route('/api/table-data')
def api_table_data():
    """Get paginated table data for sektor gaji"""
    try:
        # Fixed filter handling
        filters = {}
        for key in request.args.keys():
            if key not in ['page', 'per_page', 'search']:
                values = request.args.getlist(key)
                if key == 'Tahun graduasi anda?':
                    try:
                        values = [int(float(v)) for v in values if v.strip()]
                    except (ValueError, TypeError):
                        pass
                filters[key] = values
        
        filtered_processor = data_processor.apply_filters(filters)
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        
        # Define relevant columns for sektor gaji
        relevant_columns = [
            'Bidang pengajian',
            'Berapakah julat gaji bulanan anda sekarang?',
            'Tahap pendidikan tertinggi',
            'Apakah sektor pekerjaan anda?',
            'Apakah jangkaan gaji permulaan yang anda anggap sesuai dengan kelulusan anda?',
            'Adakah gaji anda bersesuaian dengan kelulusan anda?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?'
        ]
        
        available_columns = [col for col in relevant_columns if col in filtered_processor.filtered_df.columns]
        
        data = filtered_processor.get_table_data(page, per_page, search, available_columns)
        return jsonify(data)
        
    except Exception as e:
        print(f"Error in table data: {str(e)}")
        return jsonify({
            'error': str(e),
            'data': [],
            'pagination': {'page': 1, 'per_page': 50, 'total': 0, 'pages': 0},
            'columns': []
        }), 500

@sektor_gaji_bp.route('/api/export')
def api_export():
    """Export sektor gaji data in various formats"""
    try:
        # Fixed filter handling
        filters = {}
        for key in request.args.keys():
            if key != 'format':
                values = request.args.getlist(key)
                if key == 'Tahun graduasi anda?':
                    try:
                        values = [int(float(v)) for v in values if v.strip()]
                    except (ValueError, TypeError):
                        pass
                filters[key] = values
        
        filtered_processor = data_processor.apply_filters(filters)
        
        format_type = request.args.get('format', 'csv')
        
        relevant_columns = [
            'Timestamp',
            'Bidang pengajian',
            'Berapakah julat gaji bulanan anda sekarang?',
            'Tahap pendidikan tertinggi',
            'Apakah sektor pekerjaan anda?',
            'Apakah jangkaan gaji permulaan yang anda anggap sesuai dengan kelulusan anda?',
            'Adakah gaji anda bersesuaian dengan kelulusan anda?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?'
        ]
        
        available_columns = [col for col in relevant_columns if col in filtered_processor.filtered_df.columns]
        
        data = filtered_processor.export_data(format_type, available_columns)
        
        if format_type == 'csv':
            mimetype = 'text/csv'
            filename = 'sektor_gaji_data.csv'
        elif format_type == 'excel':
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = 'sektor_gaji_data.xlsx'
        else:
            mimetype = 'application/json'
            filename = 'sektor_gaji_data.json'
        
        return send_file(
            io.BytesIO(data),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sektor_gaji_bp.route('/api/filters/available')
def api_available_filters():
    """Get available filter options for sektor gaji data"""
    try:
        sample_df = data_processor.df
        filters = {}
        
        filter_columns = [
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?',
            'Bidang pengajian',
            'Tahap pendidikan tertinggi',
            'Apakah sektor pekerjaan anda?'
        ]
        
        for column in filter_columns:
            if column in sample_df.columns:
                unique_values = sample_df[column].dropna().unique().tolist()
                if isinstance(unique_values[0] if unique_values else None, (int, float)):
                    unique_values = sorted(unique_values)
                else:
                    unique_values = sorted([str(val) for val in unique_values])
                filters[column] = unique_values
                print(f"Filter options for {column}: {unique_values}")
        
        return jsonify(filters)
        
    except Exception as e:
        print(f"Error loading filters: {str(e)}")
        return jsonify({'error': str(e), 'filters': {}}), 500

@sektor_gaji_bp.route('/api/test')
def api_test():
    """Test endpoint to verify the blueprint is working + get available filters"""
    try:
        # Test info
        test_info = {
            'status': 'success',
            'message': 'Sektor Gaji API is working',
            'available_columns': list(df.columns) if not df.empty else [],
            'total_records': len(df)
        }

        # Build filter options
        sample_df = data_processor.df
        filters = {}
        filter_columns = [
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?',
            'Bidang pengajian',
            'Tahap pendidikan tertinggi',
            'Apakah sektor pekerjaan anda?'
        ]

        for column in filter_columns:
            if column in sample_df.columns:
                unique_values = sample_df[column].dropna().unique().tolist()
                if isinstance(unique_values[0] if unique_values else None, (int, float)):
                    unique_values = sorted(unique_values)
                else:
                    unique_values = sorted([str(val) for val in unique_values])
                filters[column] = unique_values

        # Return everything together
        return jsonify({
            **test_info,
            'filters': filters
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500