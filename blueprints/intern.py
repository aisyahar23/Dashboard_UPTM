from flask import Blueprint, render_template, request, jsonify, send_file
from models.data_processor import DataProcessor, load_excel_data
import io
import os
import pandas as pd
import numpy as np

intern_bp = Blueprint('intern', __name__)

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

formatter = ChartDataFormatter()

@intern_bp.route('/')
def index():
    """Main intern dashboard page"""
    return render_template('intern.html')

@intern_bp.route('/table')
def table_view():
    """Table view for intern data"""
    return render_template('data_table.html', 
                         page_title='Internship & Employment Challenges Data Table',
                         api_endpoint='/intern/api/table-data')

@intern_bp.route('/api/internship-participation')
def api_internship_participation():
    """Get internship participation data - Uses 'internship-participation' color scheme"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        internship_column = 'Adakah anda menjalani internship/praktikal sebelum tamat pengajian?'
        if internship_column not in filtered_processor.filtered_df.columns:
            return jsonify(formatter.format_pie_chart(
                pd.Series([1], index=['No Data Available']),
                "Internship Participation"
            ))
        
        participation_counts = filtered_processor.filtered_df[internship_column].value_counts()
        
        # Use centralized formatter - frontend will apply colors based on endpoint name
        chart_data = formatter.format_pie_chart(
            participation_counts,
            "Internship Participation"
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify(formatter.format_pie_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@intern_bp.route('/api/internship-benefits')
def api_internship_benefits():
    """Get internship benefits data - Uses 'internship-benefits' color scheme"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        # Filter to only those who completed internship
        df_filtered = filtered_processor.filtered_df
        df_internship = df_filtered[
            df_filtered['Adakah anda menjalani internship/praktikal sebelum tamat pengajian?'] != 'Tidak menjalani internship'
        ].copy()
        
        benefits_column = 'Bagaimana internship membantu anda dalam mendapatkan pekerjaan?'
        
        if benefits_column not in df_internship.columns or df_internship.empty:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Data Available']),
                "Internship Benefits"
            ))
        
        # Process comma-separated benefits
        all_benefits = []
        for benefits_cell in df_internship[benefits_column].dropna():
            if pd.notna(benefits_cell):
                benefits = [b.strip() for b in str(benefits_cell).split(',')]
                all_benefits.extend([b for b in benefits if b])
        
        if not all_benefits:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Benefits Data']),
                "Internship Benefits"
            ))
        
        benefits_counts = pd.Series(all_benefits).value_counts()
        
        # Use centralized formatter - colors will be applied by frontend
        chart_data = formatter.format_bar_chart(
            benefits_counts,
            "Internship Benefits",
            sort_desc=True
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify(formatter.format_bar_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@intern_bp.route('/api/no-internship-reasons')
def api_no_internship_reasons():
    """Get reasons for not doing internship - Uses 'no-internship-reasons' color scheme"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        # Filter to only those who didn't do internship
        df_filtered = filtered_processor.filtered_df
        df_no_internship = df_filtered[
            df_filtered['Adakah anda menjalani internship/praktikal sebelum tamat pengajian?'] == 'Tidak menjalani internship'
        ].copy()
        
        reasons_column = 'Jika tidak menjalani internship, apakah sebab utama?'
        
        if reasons_column not in df_no_internship.columns or df_no_internship.empty:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Data Available']),
                "Reasons for No Internship"
            ))
        
        # Process comma-separated reasons
        all_reasons = []
        for reasons_cell in df_no_internship[reasons_column].dropna():
            if pd.notna(reasons_cell):
                reasons = [r.strip() for r in str(reasons_cell).split(',')]
                all_reasons.extend([r for r in reasons if r])
        
        if not all_reasons:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Reasons Data']),
                "Reasons for No Internship"
            ))
        
        reasons_counts = pd.Series(all_reasons).value_counts()
        
        # Use centralized formatter
        chart_data = formatter.format_bar_chart(
            reasons_counts,
            "Reasons for No Internship",
            sort_desc=True
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify(formatter.format_bar_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@intern_bp.route('/api/employment-challenges')
def api_employment_challenges():
    """Get employment challenges - Uses 'employment-challenges' color scheme"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        challenge_column = 'Apakah cabaran utama yang anda hadapi dalam mendapatkan pekerjaan?'
        
        if challenge_column not in filtered_processor.filtered_df.columns:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Data Available']),
                "Employment Challenges"
            ))
        
        # Apply standardized challenge mapping
        challenge_mapping = {
            'Tiada pengalaman kerja yang mencukupi': 'Tiada Pengalaman',
            'Terlalu banyak persaingan dalam bidang saya': 'Persaingan',
            'Kekurangan kemahiran yang dicari majikan': 'Kurang Kemahiran',
            'Gaji yang ditawarkan terlalu rendah': 'Gaji Rendah',
            'Saya tidak tahu bagaimana mencari pekerjaan yang sesuai': 'Tiada Pengetahuan',
            'Tiada rangkaian atau hubungan yang boleh membantu saya mendapatkan pekerjaan': 'Tiada Rangkaian',
            'Kriteria pekerjaan tidak sesuai dengan kelayakan akademik saya': 'Kelayakan Tidak Sepadan',
            'Kebanyakan syarikat lebih memilih pekerja yang sudah berpengalaman': 'Tiada Pengalaman 2',
            'Tiada peluang pekerjaan dalam bidang saya di kawasan tempat tinggal saya': 'Lokasi Pekerjaan',
            'Saya perlu menjaga keluarga dan sukar untuk bekerja di luar kawasan': 'Isu Keluarga',
            'Proses permohonan kerja terlalu kompleks atau mengambil masa yang lama': 'Proses Permohonan',
            'Keadaan ekonomi semasa menyukarkan peluang pekerjaan': 'Ekonomi'
        }
        
        # Process challenges with mapping
        all_challenges = []
        for challenges_cell in filtered_processor.filtered_df[challenge_column].dropna():
            if pd.notna(challenges_cell):
                raw_challenges = [c.strip() for c in str(challenges_cell).split(',')]
                mapped_challenges = [challenge_mapping.get(c, c) for c in raw_challenges]
                all_challenges.extend(mapped_challenges)
        
        if not all_challenges:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Challenges Data']),
                "Employment Challenges"
            ))
        
        challenge_counts = pd.Series(all_challenges).value_counts()
        
        # Use centralized formatter
        chart_data = formatter.format_bar_chart(
            challenge_counts,
            "Employment Challenges",
            sort_desc=True
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify(formatter.format_bar_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@intern_bp.route('/api/grouped-challenges')
def api_grouped_challenges():
    """Get grouped challenges - Uses 'grouped-challenges' color scheme"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        challenge_column = 'Apakah cabaran utama yang anda hadapi dalam mendapatkan pekerjaan?'
        
        if challenge_column not in filtered_processor.filtered_df.columns:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Data Available']),
                "Grouped Challenges"
            ))
        
        # Apply both mapping and grouping
        challenge_mapping = {
            'Tiada pengalaman kerja yang mencukupi': 'Tiada Pengalaman',
            'Terlalu banyak persaingan dalam bidang saya': 'Persaingan',
            'Kekurangan kemahiran yang dicari majikan': 'Kurang Kemahiran',
            'Gaji yang ditawarkan terlalu rendah': 'Gaji Rendah',
            'Saya tidak tahu bagaimana mencari pekerjaan yang sesuai': 'Tiada Pengetahuan',
            'Tiada rangkaian atau hubungan yang boleh membantu saya mendapatkan pekerjaan': 'Tiada Rangkaian',
            'Kriteria pekerjaan tidak sesuai dengan kelayakan akademik saya': 'Kelayakan Tidak Sepadan',
            'Kebanyakan syarikat lebih memilih pekerja yang sudah berpengalaman': 'Tiada Pengalaman 2',
            'Tiada peluang pekerjaan dalam bidang saya di kawasan tempat tinggal saya': 'Lokasi Pekerjaan',
            'Saya perlu menjaga keluarga dan sukar untuk bekerja di luar kawasan': 'Isu Keluarga',
            'Proses permohonan kerja terlalu kompleks atau mengambil masa yang lama': 'Proses Permohonan',
            'Keadaan ekonomi semasa menyukarkan peluang pekerjaan': 'Ekonomi'
        }
        
        grouping_mapping = {
            'Tiada Pengalaman': 'Tiada Pengalaman',
            'Tiada Pengalaman 2': 'Tiada Pengalaman',
            'Persaingan': 'Pasaran Pekerjaan',
            'Kurang Kemahiran': 'Ketidakpadanan Kemahiran',
            'Gaji Rendah': 'Pasaran Pekerjaan',
            'Tiada Pengetahuan': 'Tiada Pengetahuan',
            'Tiada Rangkaian': 'Tiada Rangkaian',
            'Kelayakan Tidak Sepadan': 'Ketidakpadanan Kemahiran',
            'Lokasi Pekerjaan': 'Kekangan Struktur',
            'Isu Keluarga': 'Kekangan Personal',
            'Proses Permohonan': 'Kekangan Struktur',
            'Ekonomi': 'Pasaran Pekerjaan'
        }
        
        # Process and group challenges
        all_grouped_challenges = []
        for challenges_cell in filtered_processor.filtered_df[challenge_column].dropna():
            if pd.notna(challenges_cell):
                raw_challenges = [c.strip() for c in str(challenges_cell).split(',')]
                mapped_challenges = [challenge_mapping.get(c, c) for c in raw_challenges]
                grouped_challenges = [grouping_mapping.get(c, c) for c in mapped_challenges]
                all_grouped_challenges.extend(grouped_challenges)
        
        if not all_grouped_challenges:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Challenges Data']),
                "Grouped Challenges"
            ))
        
        grouped_challenge_counts = pd.Series(all_grouped_challenges).value_counts()
        
        # Use centralized formatter
        chart_data = formatter.format_bar_chart(
            grouped_challenge_counts,
            "Grouped Employment Challenges",
            sort_desc=True
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify(formatter.format_bar_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

# Keep the existing table, export, and filters endpoints as they are
@intern_bp.route('/api/table-data')
def api_table_data():
    """Get paginated table data for intern"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() 
                   if k not in ['page', 'per_page', 'search']}
        filtered_processor = data_processor.apply_filters(filters)
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        
        # Define relevant columns for intern analysis
        relevant_columns = [
            'Adakah anda menjalani internship/praktikal sebelum tamat pengajian?',
            'Bagaimana internship membantu anda dalam mendapatkan pekerjaan?',
            'Jika tidak menjalani internship, apakah sebab utama?',
            'Apakah cabaran utama yang anda hadapi dalam mendapatkan pekerjaan?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?'
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

@intern_bp.route('/api/export')
def api_export():
    """Export intern data in various formats"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() if k != 'format'}
        filtered_processor = data_processor.apply_filters(filters)
        
        format_type = request.args.get('format', 'csv')
        
        relevant_columns = [
            'Timestamp',
            'Adakah anda menjalani internship/praktikal sebelum tamat pengajian?',
            'Bagaimana internship membantu anda dalam mendapatkan pekerjaan?',
            'Jika tidak menjalani internship, apakah sebab utama?',
            'Apakah cabaran utama yang anda hadapi dalam mendapatkan pekerjaan?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?'
        ]
        
        available_columns = [col for col in relevant_columns if col in filtered_processor.filtered_df.columns]
        
        data = filtered_processor.export_data(format_type, available_columns)
        
        if format_type == 'csv':
            mimetype = 'text/csv'
            filename = 'internship_employment_challenges.csv'
        elif format_type == 'excel':
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = 'internship_employment_challenges.xlsx'
        else:
            mimetype = 'application/json'
            filename = 'internship_employment_challenges.json'
        
        return send_file(
            io.BytesIO(data),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@intern_bp.route('/api/filters/available')
def api_available_filters():
    """Get available filter options for intern data"""
    try:
        sample_df = data_processor.df
        filters = {}
        
        filter_columns = [
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?',
            'Adakah anda menjalani internship/praktikal sebelum tamat pengajian?'
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