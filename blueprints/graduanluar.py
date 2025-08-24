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
                'chartType': 'horizontal-bar'  # Specific identifier for styling
            }],
            'chartConfig': {
                'type': 'horizontal-bar',
                'responsive': True,
                'maintainAspectRatio': False,
                'indexAxis': 'y',  # This makes it horizontal
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
    
    @staticmethod
    def format_enhanced_stacked_bar_chart(crosstab_df, title="Enhanced Stacked Bar Chart", orientation='vertical'):
        """Format data for enhanced stacked bar charts with better styling"""
        datasets = []
        
        # Limit categories for better visualization
        if len(crosstab_df.columns) > 8:
            top_cols = crosstab_df.sum().nlargest(8).index
            crosstab_df = crosstab_df[top_cols]
        
        if len(crosstab_df.index) > 10:
            top_rows = crosstab_df.sum(axis=1).nlargest(10).index
            crosstab_df = crosstab_df.loc[top_rows]
        
        for i, column in enumerate(crosstab_df.columns):
            datasets.append({
                'label': str(column)[:30] + ('...' if len(str(column)) > 30 else ''),  # Truncate long labels
                'data': crosstab_df[column].tolist(),
                'chartType': 'enhanced-stacked-bar',
                'stack': 'stack1'  # All datasets in same stack
            })
        
        # For vertical charts, keep institution names shorter but readable
        label_max_length = 20 if orientation == 'vertical' else 25
        labels = [str(label)[:label_max_length] + ('...' if len(str(label)) > label_max_length else '') 
                  for label in crosstab_df.index.tolist()]
        
        chart_config = {
            'type': 'enhanced-stacked-bar',
            'responsive': True,
            'maintainAspectRatio': False,
            'orientation': orientation
        }
        
        # Only set indexAxis for horizontal orientation
        if orientation == 'horizontal':
            chart_config['indexAxis'] = 'y'
        
        return {
            'labels': labels,
            'datasets': datasets,
            'chartConfig': chart_config
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

@graduanluar_bp.route('/api/summary')
def api_summary():
    """Get enhanced summary statistics for graduan luar data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        stats = filtered_processor.get_summary_stats()
        filtered_df = filtered_processor.filtered_df
        
        total_records = len(filtered_df)
        
        # Enhanced KPI calculations
        reason_stats = {}
        job_type_stats = {}
        
        if total_records > 0:
            # Enhanced reason analysis with better categorization
            reason_column = 'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?'
            if reason_column in filtered_df.columns:
                reason_counts = filtered_df[reason_column].dropna().str.split(',').explode().str.strip().value_counts()
                total_reasons = reason_counts.sum()
                
                # More comprehensive keyword matching
                categorization = {
                    'mismatch': ['bidang', 'field', 'tidak sesuai', 'mismatch', 'tidak berkaitan', 'berbeza'],
                    'opportunity': ['peluang', 'opportunity', 'limited', 'terhad', 'kerja', 'job', 'tiada', 'kurang'],
                    'prospect': ['prospek', 'prospect', 'better', 'baik', 'masa depan', 'career', 'kerjaya', 'future'],
                    'salary': ['gaji', 'salary', 'pay', 'income', 'pendapatan', 'wang', 'money', 'bayaran'],
                    'personal': ['minat', 'interest', 'suka', 'passion', 'hobby', 'personal', 'kegemaran']
                }
                
                category_counts = {category: 0 for category in categorization.keys()}
                
                for reason, count in reason_counts.items():
                    reason_lower = str(reason).lower()
                    for category, keywords in categorization.items():
                        if any(keyword in reason_lower for keyword in keywords):
                            category_counts[category] += count
                            break
                
                reason_stats = {
                    'mismatch_rate': (category_counts['mismatch'] / total_reasons) * 100 if total_reasons > 0 else 0,
                    'opportunity_rate': (category_counts['opportunity'] / total_reasons) * 100 if total_reasons > 0 else 0,
                    'better_prospects_rate': (category_counts['prospect'] / total_reasons) * 100 if total_reasons > 0 else 0,
                    'salary_rate': (category_counts['salary'] / total_reasons) * 100 if total_reasons > 0 else 0,
                    'personal_rate': (category_counts['personal'] / total_reasons) * 100 if total_reasons > 0 else 0
                }
            
            # Enhanced job type analysis
            job_column = 'Apakah jenis pekerjaan anda sekarang'
            if job_column in filtered_df.columns:
                job_counts = filtered_df[job_column].value_counts()
                most_common_job = job_counts.index[0] if len(job_counts) > 0 else 'N/A'
                
                job_type_stats = {
                    'most_common_job': most_common_job,
                    'job_diversity': len(job_counts),
                    'top_3_jobs': job_counts.head(3).to_dict()
                }
            
            # Enhanced institution analysis
            institution_column = 'Institusi pendidikan MARA yang anda hadiri?'
            institution_stats = {}
            if institution_column in filtered_df.columns:
                institution_counts = filtered_df[institution_column].value_counts()
                most_represented_institution = institution_counts.index[0] if len(institution_counts) > 0 else 'N/A'
                institution_stats = {
                    'most_represented_institution': most_represented_institution,
                    'institution_count': len(institution_counts),
                    'top_institutions': institution_counts.head(5).to_dict()
                }
        
        # Enhanced stats response
        enhanced_stats = {
            'total_records': total_records,
            'mismatch_rate': round(reason_stats.get('mismatch_rate', 0), 1),
            'opportunity_rate': round(reason_stats.get('opportunity_rate', 0), 1),
            'better_prospects_rate': round(reason_stats.get('better_prospects_rate', 0), 1),
            'salary_consideration_rate': round(reason_stats.get('salary_rate', 0), 1),
            'personal_interest_rate': round(reason_stats.get('personal_rate', 0), 1),
            'most_common_job': job_type_stats.get('most_common_job', 'N/A'),
            'job_diversity': job_type_stats.get('job_diversity', 0),
            'top_jobs': job_type_stats.get('top_3_jobs', {}),
            'most_represented_institution': institution_stats.get('most_represented_institution', 'N/A'),
            'institution_diversity': institution_stats.get('institution_count', 0),
            'filter_applied': len([f for f in filters.values() if f]) > 0,
            **stats  # Include original stats as well
        }
        
        return jsonify(enhanced_stats)
        
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
    """Get enhanced reasons distribution data for horizontal bar chart"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        reason_column = 'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?'
        if reason_column not in filtered_processor.filtered_df.columns:
            return jsonify(formatter.format_horizontal_bar_chart(
                pd.Series([1], index=['No Data Available']),
                "Sebab Bekerja di Luar Bidang"
            ))
        
        # Enhanced reason processing
        reasons = filtered_processor.filtered_df[reason_column].dropna()
        all_reasons = []
        
        for reasons_list in reasons:
            individual_reasons = str(reasons_list).split(',')
            for reason in individual_reasons:
                clean_reason = reason.strip()
                if clean_reason and len(clean_reason) > 3:  # Filter out very short responses
                    all_reasons.append(clean_reason)
        
        reason_counts = pd.Series(all_reasons).value_counts().head(12)  # Top 12 for better visualization
        
        # Use enhanced horizontal bar formatter
        chart_data = formatter.format_horizontal_bar_chart(
            reason_counts,
            "Sebab Utama Bekerja di Luar Bidang Pengajian",
            sort_desc=True,
            max_items=12
        )
        
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
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        job_column = 'Apakah jenis pekerjaan anda sekarang'
        if job_column not in filtered_processor.filtered_df.columns:
            return jsonify(formatter.format_enhanced_pie_chart(
                pd.Series([1], index=['No Data Available']),
                "Agihan Jenis Pekerjaan"
            ))
        
        job_counts = filtered_processor.filtered_df[job_column].value_counts()
        
        # Use enhanced pie chart formatter
        chart_data = formatter.format_enhanced_pie_chart(
            job_counts,
            "Agihan Jenis Pekerjaan Semasa",
            max_items=8
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify(formatter.format_enhanced_pie_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@graduanluar_bp.route('/api/institution-reasons')
def api_institution_reasons():
    """Get enhanced institution vs reasons correlation for stacked bar chart"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        institution_column = 'Institusi pendidikan MARA yang anda hadiri?'
        reason_column = 'Apakah sebab utama jika anda tidak bekerja dalam bidang pengajian?'
        
        if institution_column not in filtered_processor.filtered_df.columns or reason_column not in filtered_processor.filtered_df.columns:
            return jsonify(formatter.format_enhanced_stacked_bar_chart(
                pd.DataFrame({'No Data': [1]}, index=['No Data Available']),
                "Institusi vs Faktor Perubahan Kerjaya"
            ))
        
        # Enhanced data processing
        df_clean = filtered_processor.filtered_df[[institution_column, reason_column]].dropna()
        
        # Process and expand the data
        expanded_data = []
        for _, row in df_clean.iterrows():
            institution = str(row[institution_column]).strip()
            reasons = str(row[reason_column]).split(',')
            
            for reason in reasons:
                clean_reason = reason.strip()
                if clean_reason and len(clean_reason) > 3:
                    # Shorten institution names for better display
                    short_institution = institution[:20] + '...' if len(institution) > 20 else institution
                    expanded_data.append({
                        'institution': short_institution,
                        'reason': clean_reason[:40] + '...' if len(clean_reason) > 40 else clean_reason
                    })
        
        if not expanded_data:
            return jsonify(formatter.format_enhanced_stacked_bar_chart(
                pd.DataFrame({'No Data': [1]}, index=['No Data']),
                "Institusi vs Faktor Perubahan Kerjaya"
            ))
        
        expanded_df = pd.DataFrame(expanded_data)
        
        # Create enhanced cross-tabulation
        crosstab = pd.crosstab(expanded_df['institution'], expanded_df['reason'])
        
        # Use enhanced stacked bar formatter
        chart_data = formatter.format_enhanced_stacked_bar_chart(
            crosstab,
            "Institusi vs Faktor Perubahan Kerjaya",
            orientation='horizontal'  # Make it horizontal for better label reading
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify(formatter.format_enhanced_stacked_bar_chart(
            pd.DataFrame({'Error': [1]}, index=['Error Loading Data']),
            "Error"
        )), 500

# Keep existing endpoints (table, export, filters) unchanged
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