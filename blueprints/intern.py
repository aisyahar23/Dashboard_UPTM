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

@intern_bp.route('/api/summary')
def api_summary():
    """Get summary statistics for intern data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        stats = filtered_processor.get_summary_stats()
        filtered_df = filtered_processor.filtered_df
        
        total_records = len(filtered_df)
        
        # Calculate internship statistics
        internship_stats = {}
        challenge_stats = {}
        
        if total_records > 0:
            # Internship participation rate
            internship_column = 'Adakah anda menjalani internship/praktikal sebelum tamat pengajian?'
            if internship_column in filtered_df.columns:
                internship_counts = filtered_df[internship_column].value_counts()
                total_responses = internship_counts.sum()
                
                # Calculate internship rate (excluding "Tidak menjalani internship")
                internship_yes = 0
                for response, count in internship_counts.items():
                    if str(response).lower() not in ['tidak menjalani internship', 'no']:
                        internship_yes += count
                
                internship_rate = (internship_yes / total_responses) * 100 if total_responses > 0 else 0
                internship_stats['internship_rate'] = internship_rate
            
            # Employment challenges analysis
            challenge_column = 'Apakah cabaran utama yang anda hadapi dalam mendapatkan pekerjaan?'
            if challenge_column in filtered_df.columns:
                # Apply the challenge mapping and grouping logic from the provided code
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
                
                # Group mapping
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
                
                # Process challenges
                all_challenges = []
                for challenges_cell in filtered_df[challenge_column].dropna():
                    if pd.notna(challenges_cell):
                        # Split by comma and map
                        raw_challenges = [c.strip() for c in str(challenges_cell).split(',')]
                        mapped_challenges = [challenge_mapping.get(c, c) for c in raw_challenges]
                        all_challenges.extend(mapped_challenges)
                
                if all_challenges:
                    challenge_counts = pd.Series(all_challenges).value_counts()
                    total_challenge_mentions = len(all_challenges)
                    
                    # Calculate specific challenge rates
                    no_experience_count = challenge_counts.get('Tiada Pengalaman', 0) + challenge_counts.get('Tiada Pengalaman 2', 0)
                    market_issues_count = (challenge_counts.get('Persaingan', 0) + 
                                         challenge_counts.get('Gaji Rendah', 0) + 
                                         challenge_counts.get('Ekonomi', 0))
                    
                    challenge_stats = {
                        'no_experience_rate': (no_experience_count / total_challenge_mentions) * 100,
                        'market_competition_rate': (market_issues_count / total_challenge_mentions) * 100
                    }
        
        # Update stats with calculated values
        stats.update({
            'total_records': total_records,
            'internship_rate': round(internship_stats.get('internship_rate', 0), 1),
            'no_experience_rate': round(challenge_stats.get('no_experience_rate', 0), 1),
            'market_competition_rate': round(challenge_stats.get('market_competition_rate', 0), 1)
        })
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'total_records': 0,
            'internship_rate': 0,
            'no_experience_rate': 0,
            'market_competition_rate': 0
        }), 500

@intern_bp.route('/api/internship-participation')
def api_internship_participation():
    """Get internship participation data (Pie Chart)"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        internship_column = 'Adakah anda menjalani internship/praktikal sebelum tamat pengajian?'
        if internship_column not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderWidth': 2,
                    'borderColor': '#ffffff'
                }]
            })
        
        data = filtered_processor.get_chart_data('pie', internship_column)
        
        # Use brand colors - primary blue and red with supporting colors
        brand_colors = ['#074e7e', '#c92427', '#0ea5e9', '#ef4444', '#06b6d4', '#f97316']
        if data.get('datasets') and len(data['datasets']) > 0:
            data['datasets'][0]['backgroundColor'] = brand_colors[:len(data.get('labels', []))]
            data['datasets'][0]['borderColor'] = '#ffffff'
            data['datasets'][0]['borderWidth'] = 3
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'labels': ['Error Loading Data'],
            'datasets': [{
                'data': [1],
                'backgroundColor': ['#ef4444'],
                'borderWidth': 2,
                'borderColor': '#ffffff'
            }]
        }), 500

@intern_bp.route('/api/internship-benefits')
def api_internship_benefits():
    """Get internship benefits data (Bar Chart)"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        # Filter to only those who completed internship and are working
        df_filtered = filtered_processor.filtered_df
        df_internship = df_filtered[
            df_filtered['Adakah anda menjalani internship/praktikal sebelum tamat pengajian?'] != 'Tidak menjalani internship'
        ].copy()
        
        benefits_column = 'Bagaimana internship membantu anda dalam mendapatkan pekerjaan?'
        
        if benefits_column not in df_internship.columns or df_internship.empty:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        # Process comma-separated benefits
        all_benefits = []
        for benefits_cell in df_internship[benefits_column].dropna():
            if pd.notna(benefits_cell):
                benefits = [b.strip() for b in str(benefits_cell).split(',')]
                all_benefits.extend([b for b in benefits if b])
        
        if not all_benefits:
            return jsonify({
                'labels': ['No Benefits Data'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        benefits_counts = pd.Series(all_benefits).value_counts()
        
        chart_data = {
            'labels': benefits_counts.index.tolist(),
            'datasets': [{
                'data': benefits_counts.values.tolist(),
                'backgroundColor': '#074e7e',
                'borderColor': '#063a5f',
                'borderWidth': 1
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
                'borderWidth': 1
            }]
        }), 500

@intern_bp.route('/api/no-internship-reasons')
def api_no_internship_reasons():
    """Get reasons for not doing internship (Bar Chart)"""
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
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        # Process comma-separated reasons
        all_reasons = []
        for reasons_cell in df_no_internship[reasons_column].dropna():
            if pd.notna(reasons_cell):
                reasons = [r.strip() for r in str(reasons_cell).split(',')]
                all_reasons.extend([r for r in reasons if r])
        
        if not all_reasons:
            return jsonify({
                'labels': ['No Reasons Data'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        reasons_counts = pd.Series(all_reasons).value_counts()
        
        chart_data = {
            'labels': reasons_counts.index.tolist(),
            'datasets': [{
                'data': reasons_counts.values.tolist(),
                'backgroundColor': '#c92427',
                'borderColor': '#a91e22',
                'borderWidth': 1
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
                'borderWidth': 1
            }]
        }), 500

@intern_bp.route('/api/employment-challenges')
def api_employment_challenges():
    """Get employment challenges data (Bar Chart)"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        challenge_column = 'Apakah cabaran utama yang anda hadapi dalam mendapatkan pekerjaan?'
        
        if challenge_column not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        # Apply challenge mapping
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
        
        # Process challenges
        all_challenges = []
        for challenges_cell in filtered_processor.filtered_df[challenge_column].dropna():
            if pd.notna(challenges_cell):
                raw_challenges = [c.strip() for c in str(challenges_cell).split(',')]
                mapped_challenges = [challenge_mapping.get(c, c) for c in raw_challenges]
                all_challenges.extend(mapped_challenges)
        
        if not all_challenges:
            return jsonify({
                'labels': ['No Challenges Data'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        challenge_counts = pd.Series(all_challenges).value_counts()
        
        chart_data = {
            'labels': challenge_counts.index.tolist(),
            'datasets': [{
                'data': challenge_counts.values.tolist(),
                'backgroundColor': '#0ea5e9',
                'borderColor': '#0284c7',
                'borderWidth': 1
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
                'borderWidth': 1
            }]
        }), 500

@intern_bp.route('/api/grouped-challenges')
def api_grouped_challenges():
    """Get grouped challenges data (Bar Chart)"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        challenge_column = 'Apakah cabaran utama yang anda hadapi dalam mendapatkan pekerjaan?'
        
        if challenge_column not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
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
            return jsonify({
                'labels': ['No Challenges Data'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        grouped_challenge_counts = pd.Series(all_grouped_challenges).value_counts()
        
        # Brand color scheme for grouped data
        brand_colors = ['#074e7e', '#c92427', '#0ea5e9', '#ef4444', '#06b6d4', '#f97316', '#10b981']
        
        chart_data = {
            'labels': grouped_challenge_counts.index.tolist(),
            'datasets': [{
                'data': grouped_challenge_counts.values.tolist(),
                'backgroundColor': brand_colors[:len(grouped_challenge_counts.index)],
                'borderColor': '#ffffff',
                'borderWidth': 1
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
                'borderWidth': 1
            }]
        }), 500

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