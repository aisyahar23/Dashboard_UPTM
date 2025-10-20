from flask import Blueprint, render_template, request, jsonify, send_file
from models.data_processor import DataProcessor, load_excel_data
import io
import os
import pandas as pd
import numpy as np
import re

graduanluar_bp = Blueprint('graduanluar', __name__)

# Load data from Excel file
EXCEL_FILE_PATH = 'data/Questionnaire.xlsx'
df = load_excel_data(EXCEL_FILE_PATH)

# Remove the global pre-filtering — keep full dataset and let endpoints apply filters explicitly
# (previous code removed rows early which caused missing/incorrect reason aggregation)
data_processor = DataProcessor(df)

# Enhanced Chart Data Formatter for better integration with ChartConfig
class EnhancedChartDataFormatter:
    """Enhanced formatter that works seamlessly with the centralized chart configuration system"""
    
    @staticmethod
    def format_horizontal_bar_chart(data_series, title="Horizontal Bar Chart", sort_desc=True, max_items=10):
        """Format data specifically for horizontal bar charts with enhanced styling"""
        if sort_desc:
            data_series = data_series.sort_values(ascending=True)  # Ascending for horizontal bars (largest at top)
        
        # Limit items for better visualization
        if len(data_series) > max_items:
            data_series = data_series.tail(max_items)
        
        # Prepare labels with truncation for long text
        labels = [label[:50] + '...' if len(str(label)) > 50 else str(label) 
                 for label in data_series.index.tolist()]
        
        return {
            'labels': labels,
            'datasets': [{
                'label': title,
                'data': data_series.values.tolist(),
                'chartType': 'horizontal-bar'
            }],
            'chartConfig': {
                'type': 'horizontal-bar',
                'responsive': True,
                'maintainAspectRatio': False,
                'indexAxis': 'y',
                'maxItems': max_items
            }
        }
    
    @staticmethod  
    def format_vertical_bar_chart(data_series, title="Vertical Bar Chart", sort_desc=True, max_items=12):
        """Format data for vertical bar charts with enhanced styling"""
        if sort_desc:
            data_series = data_series.sort_values(ascending=False)
        
        if len(data_series) > max_items:
            data_series = data_series.head(max_items)
        
        return {
            'labels': data_series.index.tolist(),
            'datasets': [{
                'label': title,
                'data': data_series.values.tolist(),
                'chartType': 'vertical-bar'
            }],
            'chartConfig': {
                'type': 'vertical-bar',
                'responsive': True,
                'maintainAspectRatio': False,
                'maxItems': max_items
            }
        }
    
    @staticmethod
    def format_enhanced_pie_chart(data_series, title="Enhanced Pie Chart", max_items=8):
        """Format data for pie charts with enhanced styling and better legends"""
        # Limit items and group others
        if len(data_series) > max_items:
            top_items = data_series.head(max_items - 1)
            others_sum = data_series.tail(len(data_series) - (max_items - 1)).sum()
            if others_sum > 0:
                top_items['Others'] = others_sum
            data_series = top_items
        
        return {
            'labels': data_series.index.tolist(),
            'datasets': [{
                'label': title,
                'data': data_series.values.tolist(),
                'chartType': 'enhanced-pie'
            }],
            'chartConfig': {
                'type': 'enhanced-pie',
                'responsive': True,
                'maintainAspectRatio': False,
                'maxItems': max_items
            }
        }

formatter = EnhancedChartDataFormatter()

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

# NEW: Improved normalization and canonical mapping for reasons
CANONICAL_REASONS = [
    'Tiada peluang pekerjaan yang sesuai',
    'Gaji terlalu rendah dalam bidang asal',
    'Lebih banyak peluang dalam bidang lain',
    'Tidak berminat dengan bidang asal',
    'Tidak berkaitan kerana bekerja dalam bidang pengajian'
]

# mapping of keywords/variants -> canonical (all lowercased keys)
_REASON_VARIANTS = {
    'tiada peluang': CANONICAL_REASONS[0],
    'tiada peluang pekerjaan': CANONICAL_REASONS[0],
    'tiada peluang pekerjaan yang sesuai': CANONICAL_REASONS[0],
    'gaji rendah': CANONICAL_REASONS[1],
    'gaji terlalu rendah': CANONICAL_REASONS[1],
    'gaji terlalu rendah dalam bidang asal': CANONICAL_REASONS[1],
    'lebih banyak peluang': CANONICAL_REASONS[2],
    'lebih banyak peluang dalam bidang lain': CANONICAL_REASONS[2],
    'lebih banyak peluang dalam bidang lain': CANONICAL_REASONS[2],
    'tidak berminat': CANONICAL_REASONS[3],
    'tidak berminat dengan bidang asal': CANONICAL_REASONS[3],
    'tidak berkaitan kerana bekerja dalam bidang pengajian': CANONICAL_REASONS[4],
    'tidak berkaitan kerana saya bekerja dalam bidang pengajian': CANONICAL_REASONS[4],
    'bekerja dalam bidang pengajian': CANONICAL_REASONS[4]
}

IGNORED_REASON_MARKERS = ['tidak dinyatakan', 'tidak relevan']

def normalize_text(val):
    if pd.isna(val):
        return ''
    return str(val).strip()

def split_reasons_cell(text):
    """Split multi-answer cells by common separators"""
    if not text or pd.isna(text):
        return []
    
    text = str(text).strip()
    if not text:
        return []
    
    # Split by common separators
    separators = [',', ';', '|', '\n']
    parts = [text]
    
    for sep in separators:
        new_parts = []
        for part in parts:
            new_parts.extend([p.strip() for p in part.split(sep) if p.strip()])
        parts = new_parts
    
    return [p for p in parts if p and len(p) > 2]  # Filter out very short fragments

def map_reason_to_canonical(text):
    """Map raw reason text (or a fragment) to one of the CANONICAL_REASONS.
       Returns canonical string or None if should be ignored/unknown.
    """
    if not text:
        return None
    s = normalize_text(text).lower()
    # exact match first
    for c in CANONICAL_REASONS:
        if s == c.lower():
            return c
    # check variants (substring)
    for variant, canonical in _REASON_VARIANTS.items():
        if variant in s:
            return canonical
    # ignore markers
    if any(marker in s for marker in IGNORED_REASON_MARKERS):
        return None
    # fallback: return title-cased original as 'Lain-lain' entry if not empty
    return s.capitalize()

@graduanluar_bp.route('/api/summary')
def api_summary():
    """Get enhanced summary statistics for graduan luar data"""
    try:
        # Get filters properly like demografi
        filters = {}
        for key in request.args.keys():
            values = request.args.getlist(key)
            if values:  # Only include non-empty filters
                filters[key] = values
        
        # Apply filters directly to dataframe like demografi
        filtered_df = data_processor.df.copy()
        
        for column, values in filters.items():
            if not values or len(values) == 0:
                continue
            
            if column in filtered_df.columns:
                # Convert filter values to match column data type
                if filtered_df[column].dtype in ['int64', 'float64']:
                    try:
                        converted_values = []
                        for v in values:
                            if isinstance(v, (int, float)):
                                converted_values.append(v)
                            else:
                                converted_values.append(int(float(v)))
                        filtered_df = filtered_df[filtered_df[column].isin(converted_values)]
                    except Exception:
                        filtered_df = filtered_df[filtered_df[column].astype(str).isin([str(v) for v in values])]
                else:
                    filtered_df = filtered_df[filtered_df[column].isin(values)]
        
        total_records = len(filtered_df)
        
        # Enhanced KPI calculations
        reason_stats = {}
        private_sector_rate = 0
        
        if total_records > 0:
            # Count graduates by canonical reason categories
            reason_col = 'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?'
            if reason_col in filtered_df.columns:
                # Get raw reasons and process them
                raw_reasons = filtered_df[reason_col].dropna().astype(str)
                
                # Count occurrences of each canonical reason
                counts = {canonical: 0 for canonical in CANONICAL_REASONS}
                
                for reason_text in raw_reasons:
                    # Check each canonical reason against the text
                    for canonical in CANONICAL_REASONS:
                        if canonical.lower() in reason_text.lower():
                            counts[canonical] += 1
                            break  # Only count once per response
                
                reason_stats = {
                    'Tiada peluang pekerjaan yang sesuai': counts[CANONICAL_REASONS[0]],
                    'Gaji terlalu rendah dalam bidang asal': counts[CANONICAL_REASONS[1]],
                    'Lebih banyak peluang dalam bidang lain': counts[CANONICAL_REASONS[2]],
                    'Tidak berminat dengan bidang asal': counts[CANONICAL_REASONS[3]],
                    'Tidak berkaitan kerana bekerja dalam bidang pengajian': counts[CANONICAL_REASONS[4]]
                }
            
            # Private sector rate unchanged (existing logic)
            job_column = 'Apakah jenis pekerjaan anda sekarang'
            if job_column in filtered_df.columns:
                job_counts = filtered_df[job_column].value_counts()
                private_keywords = ['swasta', 'private', 'syarikat', 'company', 'korporat']
                private_count = 0
                for job_type, count in job_counts.items():
                    jt = str(job_type).lower()
                    if any(k in jt for k in private_keywords):
                        private_count += count
                private_sector_rate = (private_count / total_records) * 100 if total_records > 0 else 0
        
        # Build response - include reason selection counts as well as rates (percent of selections)
        enhanced_stats = {
            'total_records': total_records,
            'private_sector_rate': round(private_sector_rate, 1),
            'reason_counts': reason_stats,
            'filter_applied': len([f for f in filters.values() if f]) > 0
        }
        return jsonify(enhanced_stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@graduanluar_bp.route('/api/reasons-distribution')
def api_reasons_distribution():
    """Get enhanced reasons distribution data for horizontal bar chart"""
    try:
        # Get filters properly like demografi
        filters = {}
        for key in request.args.keys():
            values = request.args.getlist(key)
            if values:
                filters[key] = values
        
        # Apply filters directly to dataframe
        filtered_df = data_processor.df.copy()
        for column, values in filters.items():
            if not values or len(values) == 0:
                continue
            if column in filtered_df.columns:
                if filtered_df[column].dtype in ['int64', 'float64']:
                    try:
                        converted_values = [int(float(v)) if isinstance(v, str) else v for v in values]
                        filtered_df = filtered_df[filtered_df[column].isin(converted_values)]
                    except:
                        filtered_df = filtered_df[filtered_df[column].astype(str).isin([str(v) for v in values])]
                else:
                    filtered_df = filtered_df[filtered_df[column].isin(values)]
        
        reason_column = 'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?'
        if reason_column not in filtered_df.columns:
            return jsonify(formatter.format_horizontal_bar_chart(
                pd.Series([1], index=['No Data Available']),
                "Sebab Bekerja di Luar Bidang"
            ))
        
        # Get raw reasons and process them
        raw_reasons = filtered_df[reason_column].dropna().astype(str)
        print(f"DEBUG REASONS: Found {len(raw_reasons)} non-null reasons")
        
        if len(raw_reasons) > 0:
            print(f"DEBUG REASONS: Sample reasons: {raw_reasons.head(3).tolist()}")
        
        # Count occurrences of each canonical reason
        reason_counts = pd.Series(0, index=CANONICAL_REASONS)
        
        for reason_text in raw_reasons:
            # Check each canonical reason against the text
            for canonical in CANONICAL_REASONS:
                if canonical.lower() in reason_text.lower():
                    reason_counts[canonical] += 1
                    print(f"DEBUG REASONS: Matched '{canonical}' in '{reason_text[:50]}...'")
                    break  # Only count once per response
        
        print(f"DEBUG REASONS: Final counts: {reason_counts.to_dict()}")
        
        if reason_counts.sum() == 0:
            print("DEBUG REASONS: No matches found, returning default data")
            return jsonify({
                'labels': CANONICAL_REASONS,
                'datasets': [{
                    'label': 'Sebab Utama Bekerja di Luar Bidang',
                    'data': [1, 1, 1, 1, 1],
                    'backgroundColor': ['#EF4444', '#DC2626', '#B91C1C', '#991B1B', '#7F1D1D']
                }]
            })
        # Return simple chart data format
        chart_data = {
            'labels': CANONICAL_REASONS,
            'datasets': [{
                'label': 'Sebab Utama Bekerja di Luar Bidang',
                'data': reason_counts.tolist(),
                'backgroundColor': ['#EF4444', '#DC2626', '#B91C1C', '#991B1B', '#7F1D1D']
            }]
        }
        print(f"DEBUG REASONS: Returning chart data: {chart_data}")
        return jsonify(chart_data)
    except Exception as e:
        return jsonify(formatter.format_horizontal_bar_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@graduanluar_bp.route('/api/job-types')
def api_job_types():
    """Get enhanced job types distribution for pie chart"""
    try:
        # Get filters properly like demografi
        filters = {}
        for key in request.args.keys():
            values = request.args.getlist(key)
            if values:
                filters[key] = values
        
        # Apply filters directly to dataframe
        filtered_df = data_processor.df.copy()
        
        for column, values in filters.items():
            if not values or len(values) == 0:
                continue
            if column in filtered_df.columns:
                if filtered_df[column].dtype in ['int64', 'float64']:
                    try:
                        converted_values = [int(float(v)) if isinstance(v, str) else v for v in values]
                        filtered_df = filtered_df[filtered_df[column].isin(converted_values)]
                    except:
                        filtered_df = filtered_df[filtered_df[column].astype(str).isin([str(v) for v in values])]
                else:
                    filtered_df = filtered_df[filtered_df[column].isin(values)]
        
        job_column = 'Apakah jenis pekerjaan anda sekarang'
        if job_column not in filtered_df.columns:
            return jsonify(formatter.format_enhanced_pie_chart(
                pd.Series([1], index=['No Data Available']),
                "Agihan Bidang Pekerjaan"
            ))
        
        job_counts = filtered_df[job_column].value_counts()
        print(f"DEBUG JOB TYPES: Found {len(job_counts)} job types")
        print(f"DEBUG JOB TYPES: Job counts: {job_counts.head().to_dict()}")
        
        if job_counts.empty:
            chart_data = {
                'labels': ['Tiada Data'],
                'datasets': [{
                    'label': 'Jenis Pekerjaan',
                    'data': [1],
                    'backgroundColor': ['#EF4444']
                }]
            }
        else:
            # Limit to top 8 for better visualization
            top_jobs = job_counts.head(8)
            chart_data = {
                'labels': [str(label) for label in top_jobs.index.tolist()],
                'datasets': [{
                    'label': 'Jenis Pekerjaan',
                    'data': [int(val) for val in top_jobs.values.tolist()],
                    'backgroundColor': [
                        '#EF4444', '#DC2626', '#B91C1C', '#991B1B',
                        '#7F1D1D', '#F87171', '#FCA5A5', '#FECACA'
                    ][:len(top_jobs)]
                }]
            }
        
        print(f"DEBUG JOB TYPES: Returning chart data: {chart_data}")
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify(formatter.format_enhanced_pie_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@graduanluar_bp.route('/api/reasons-simple')
def api_reasons_simple():
    """Get simplified reasons distribution for vertical bar chart (NEW ENDPOINT)"""
    try:
        # Get filters properly like demografi
        filters = {}
        for key in request.args.keys():
            values = request.args.getlist(key)
            if values:
                filters[key] = values
        
        # Apply filters directly to dataframe
        filtered_df = data_processor.df.copy()
        for column, values in filters.items():
            if not values or len(values) == 0:
                continue
            if column in filtered_df.columns:
                if filtered_df[column].dtype in ['int64', 'float64']:
                    try:
                        converted_values = [int(float(v)) if isinstance(v, str) else v for v in values]
                        filtered_df = filtered_df[filtered_df[column].isin(converted_values)]
                    except:
                        filtered_df = filtered_df[filtered_df[column].astype(str).isin([str(v) for v in values])]
                else:
                    filtered_df = filtered_df[filtered_df[column].isin(values)]
        
        reason_column = 'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?'
        if reason_column not in filtered_df.columns:
            return jsonify(formatter.format_vertical_bar_chart(
                pd.Series([1], index=['No Data Available']),
                "Sebab Tidak Bekerja dalam Bidang"
            ))
        
        # Get raw reasons and process them
        raw_reasons = filtered_df[reason_column].dropna().astype(str)
        
        # Count occurrences of each canonical reason
        reason_counts = pd.Series(0, index=CANONICAL_REASONS)
        
        for reason_text in raw_reasons:
            # Check each canonical reason against the text
            for canonical in CANONICAL_REASONS:
                if canonical.lower() in reason_text.lower():
                    reason_counts[canonical] += 1
                    break  # Only count once per response
        
        if reason_counts.sum() == 0:
            return jsonify(formatter.format_vertical_bar_chart(
                pd.Series([1], index=['Tiada Data']),
                "Sebab Tidak Bekerja dalam Bidang"
            ))
        # Return simple chart data format
        chart_data = {
            'labels': CANONICAL_REASONS,
            'datasets': [{
                'label': 'Sebab Tidak Bekerja dalam Bidang',
                'data': reason_counts.tolist(),
                'backgroundColor': ['#3B82F6', '#1D4ED8', '#1E40AF', '#1E3A8A', '#172554']
            }]
        }
        print(f"DEBUG REASONS SIMPLE: Returning chart data: {chart_data}")
        return jsonify(chart_data)
    except Exception as e:
        return jsonify(formatter.format_vertical_bar_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@graduanluar_bp.route('/api/chart-table-data/<chart_type>')
def api_chart_table_data(chart_type):
    """Get table data for specific chart modals"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        # Define relevant columns for each chart type
        chart_columns = {
            'reasons': [
                'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?',
                'Tahun graduasi anda?',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?',
                'Program pengajian yang anda ikuti?',
                'Apakah jenis pekerjaan anda sekarang'
            ],
            'jobtypes': [
                'Apakah jenis pekerjaan anda sekarang',
                'Bidang pekerjaan yang anda ceburi sekarang?',
                'Tahun graduasi anda?',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?',
                'Program pengajian yang anda ikuti?'
            ],
            'reasons-simple': [
                'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?',
                'Tahun graduasi anda?',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?',
                'Program pengajian yang anda ikuti?'
            ]
        }
        
        relevant_columns = chart_columns.get(chart_type, [
            'Apakah jenis pekerjaan anda sekarang',
            'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Tahun graduasi anda?',
            'Jantina anda?'
        ])
        
        available_columns = [col for col in relevant_columns if col in filtered_processor.filtered_df.columns]
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 100))
        search = request.args.get('search', '')
        
        data = filtered_processor.get_table_data(page, per_page, search, available_columns)
        return jsonify(data)
        
    except Exception as e:
        print(f"GRADUAN LUAR CHART TABLE ERROR: {str(e)}")
        return jsonify({
            'error': str(e),
            'data': [],
            'pagination': {'page': 1, 'per_page': 100, 'total': 0, 'pages': 0},
            'columns': []
        }), 500

@graduanluar_bp.route('/api/table-data')
def api_table_data():
    """Get paginated table data for graduan luar"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() 
                   if k not in ['page', 'per_page', 'search']}
        
        print(f"GRADUAN LUAR TABLE: Received filters: {filters}")
        filtered_processor = data_processor.apply_filters(filters)
        print(f"GRADUAN LUAR TABLE: Filtered to {len(filtered_processor.filtered_df)} records")
        
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
        print(f"GRADUAN LUAR TABLE: Available columns: {available_columns}")
        
        data = filtered_processor.get_table_data(page, per_page, search, available_columns)
        return jsonify(data)
        
    except Exception as e:
        print(f"GRADUAN LUAR TABLE ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'data': [],
            'pagination': {'page': 1, 'per_page': 50, 'total': 0, 'pages': 0},
            'columns': []
        }), 500

@graduanluar_bp.route('/api/outside-field-programs')
def api_outside_field_programs():
    """Get programs breakdown for graduates working outside their field - requested for Graduan Luar module"""
    try:
        # Get filters properly like demografi
        filters = {}
        for key in request.args.keys():
            values = request.args.getlist(key)
            if values:
                filters[key] = values
        
        # Apply filters directly to dataframe
        filtered_df = data_processor.df.copy()
        
        for column, values in filters.items():
            if not values or len(values) == 0:
                continue
            if column in filtered_df.columns:
                if filtered_df[column].dtype in ['int64', 'float64']:
                    try:
                        converted_values = [int(float(v)) if isinstance(v, str) else v for v in values]
                        filtered_df = filtered_df[filtered_df[column].isin(converted_values)]
                    except:
                        filtered_df = filtered_df[filtered_df[column].astype(str).isin([str(v) for v in values])]
                else:
                    filtered_df = filtered_df[filtered_df[column].isin(values)]

        # Use the correct program column from the actual data structure
        program_column = 'Bidang pengajian utama anda?'
        not_in_field_column = 'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?'

        if program_column not in filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Program Luar Bidang',
                    'data': [1],
                    'backgroundColor': ['#DC2626']
                }]
            })

        # Filter for graduates who ARE working outside their field
        # These are people who have actual reasons (not "Tidak berkaitan kerana saya bekerja dalam bidang pengajian")
        outside_field_df = filtered_df[
            filtered_df[not_in_field_column].notna() &
            (filtered_df[not_in_field_column] != '') &
            (~filtered_df[not_in_field_column].str.contains('Tidak berkaitan kerana saya bekerja dalam bidang pengajian', na=False))
        ].copy()

        # Debug: Check what data we have
        print(f"DEBUG GRADUAN LUAR: Total filtered rows: {len(filtered_df)}")
        print(f"DEBUG GRADUAN LUAR: Outside field rows: {len(outside_field_df)}")
        print(f"DEBUG GRADUAN LUAR: Program column exists: {program_column in filtered_df.columns}")

        if len(outside_field_df) > 0:
            print(f"DEBUG GRADUAN LUAR: Sample programs: {outside_field_df[program_column].dropna().head().tolist()}")
            print(f"DEBUG GRADUAN LUAR: Program value counts: {outside_field_df[program_column].value_counts().head()}")

        # Get program distribution for those working outside their field
        program_counts = outside_field_df[program_column].value_counts(dropna=False)
        
        # Count records with missing program data
        missing_program_count = program_counts.get(np.nan, 0) if np.nan in program_counts else 0
        
        # Remove NaN from counts for display
        program_counts = program_counts[program_counts.index.notna()]
        
        print(f"DEBUG GRADUAN LUAR: Program counts (excluding NaN): {program_counts.to_dict()}")
        print(f"DEBUG GRADUAN LUAR: Missing program data: {missing_program_count}")
        print(f"DEBUG GRADUAN LUAR: Total should be: {program_counts.sum() + missing_program_count}")

        if program_counts.empty:
            return jsonify({
                'labels': ['Tiada Data Program'],
                'datasets': [{
                    'label': 'Program Luar Bidang',
                    'data': [1],
                    'backgroundColor': ['#EF4444']
                }]
            })

        chart_data = {
            'labels': [str(label) for label in program_counts.index.tolist()],
            'datasets': [{
                'label': 'Bilangan Graduan Bekerja Luar Bidang',
                'data': [int(val) for val in program_counts.values.tolist()],
                'backgroundColor': [
                    '#EF4444', '#DC2626', '#B91C1C', '#991B1B',
                    '#7F1D1D', '#F87171', '#FCA5A5', '#FECACA',
                    '#FEE2E2', '#FEF2F2'
                ][:len(program_counts)]
            }]
        }
        
        # Add note about total count including missing data
        chart_data['total_count'] = int(program_counts.sum() + missing_program_count)
        chart_data['missing_program_count'] = int(missing_program_count)

        return jsonify(chart_data)

    except Exception as e:
        print(f"Error in outside field programs endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

@graduanluar_bp.route('/api/outside-field-table')
def api_outside_field_table():
    """Get table data for outside field programs chart"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()
                  if k not in ['page', 'per_page', 'search']}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df

        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')

        relevant_columns = [
            'Bidang pengajian utama anda?',
            'Apakah jenis pekerjaan anda sekarang',
            'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?',
            'Adakah anda kini bekerja?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?'
        ]

        available_columns = [col for col in relevant_columns if col in filtered_df.columns]

        # Filter for graduates working outside their field (same logic as chart)
        not_in_field_column = 'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?'
        outside_field_df = filtered_df[
            filtered_df[not_in_field_column].notna() &
            (filtered_df[not_in_field_column] != '') &
            (~filtered_df[not_in_field_column].str.contains('Tidak berkaitan kerana saya bekerja dalam bidang pengajian', na=False))
        ].copy()

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

        processor = FilteredProcessor(outside_field_df)
        data = processor.get_table_data(page, per_page, search, available_columns)
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
        filters = {k: request.args.getlist(k) for k in request.args.keys() 
                  if k not in ['format', 'chart_type']}
        filtered_processor = data_processor.apply_filters(filters)
        
        format_type = request.args.get('format', 'csv')
        chart_type = request.args.get('chart_type', None)
        
        # If exporting from a specific chart, use relevant columns for that chart
        if chart_type:
            chart_columns = {
                'reasons': [
                    'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?',
                    'Tahun graduasi anda?',
                    'Jantina anda?',
                    'Institusi pendidikan MARA yang anda hadiri?',
                    'Program pengajian yang anda ikuti?'
                ],
                'jobtypes': [
                    'Apakah jenis pekerjaan anda sekarang',
                    'Bidang pekerjaan yang anda ceburi sekarang?',
                    'Tahun graduasi anda?',
                    'Jantina anda?',
                    'Institusi pendidikan MARA yang anda hadiri?'
                ],
                'reasons-simple': [
                    'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?',
                    'Tahun graduasi anda?',
                    'Jantina anda?',
                    'Institusi pendidikan MARA yang anda hadiri?',
                    'Program pengajian yang anda ikuti?'
                ]
            }
            relevant_columns = chart_columns.get(chart_type, [])
        else:
            # Default columns for general export
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
            filename = f'graduan_luar_bidang_{chart_type or "data"}.csv'
        elif format_type == 'excel':
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f'graduan_luar_bidang_{chart_type or "data"}.xlsx'
        else:
            mimetype = 'application/json'
            filename = f'graduan_luar_bidang_{chart_type or "data"}.json'
        
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
        
        print("GRADUAN LUAR FILTERS DEBUG START:")
        print(f"DataFrame shape: {sample_df.shape}")
        
        for column in filter_columns:
            print(f"\n--- Processing: {column} ---")
            if column in sample_df.columns:
                # Get non-null values
                non_null_series = sample_df[column].dropna()
                print(f"Non-null values: {len(non_null_series)}/{len(sample_df)}")
                
                if len(non_null_series) > 0:
                    unique_values = non_null_series.unique().tolist()
                    print(f"Unique values: {len(unique_values)}")
                    print(f"Sample values: {unique_values[:5] if len(unique_values) > 5 else unique_values}")
                    
                    # Handle different data types properly
                    if column == 'Tahun graduasi anda?' and len(unique_values) > 0:
                        # Special handling for graduation year
                        print("GRADUATION YEAR PROCESSING:")
                        try:
                            # Convert to integers if they're numeric
                            processed_values = []
                            for val in unique_values:
                                try:
                                    if pd.isna(val):
                                        continue
                                    # Convert to int if possible
                                    int_val = int(float(val)) if isinstance(val, (int, float, str)) else val
                                    processed_values.append(int_val)
                                    print(f"  '{val}' -> {int_val}")
                                except (ValueError, TypeError):
                                    print(f"  '{val}' -> kept as string")
                                    processed_values.append(str(val))
                            
                            processed_values = sorted(list(set(processed_values)))
                            print(f"FINAL YEARS: {processed_values}")
                            filters[column] = processed_values
                        except Exception as e:
                            print(f"Error processing graduation years: {e}")
                            filters[column] = [str(val) for val in sorted(unique_values)]
                    else:
                        # Handle other columns
                        if isinstance(unique_values[0] if unique_values else None, (int, float)):
                            processed_values = sorted(unique_values)
                        else:
                            processed_values = sorted([str(val) for val in unique_values])
                        filters[column] = processed_values
                    
                    print(f"Final filter values: {len(filters[column])} items")
                else:
                    print(f"No non-null values found")
                    filters[column] = []
            else:
                print(f"COLUMN NOT FOUND: {column}")
                filters[column] = []
        
        print(f"\nFILTER SUMMARY:")
        for col, vals in filters.items():
            print(f"  {col}: {len(vals)} values")
            if col == 'Tahun graduasi anda?':
                print(f"    Graduation years: {vals}")
        
        print(f"\nFinal filters response: {filters}")
        return jsonify(filters)
        
    except Exception as e:
        print(f"GRADUAN LUAR FILTERS ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'filters': {}}), 500