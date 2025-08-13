from flask import Blueprint, render_template, request, jsonify, send_file
from models.data_processor import DataProcessor, load_excel_data
import io
import os
import pandas as pd
import numpy as np

gig_economy_bp = Blueprint('gig_economy', __name__)

# Load data from Excel file
EXCEL_FILE_PATH = 'data/Questionnaire.xlsx'
df = load_excel_data(EXCEL_FILE_PATH)
data_processor = DataProcessor(df)

@gig_economy_bp.route('/')
def index():
    """Main gig economy dashboard page"""
    return render_template('gig_economy.html')

@gig_economy_bp.route('/table')
def table_view():
    """Table view for gig economy data"""
    return render_template('data_table.html', 
                         page_title='Gig Economy & Entrepreneurship Data Table',
                         api_endpoint='/gig-economy/api/table-data')

@gig_economy_bp.route('/api/summary')
def api_summary():
    """Get summary statistics for gig economy data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        stats = filtered_processor.get_summary_stats()
        filtered_df = filtered_processor.filtered_df
        
        total_records = len(filtered_df)
        
        # Calculate gig economy statistics
        gig_stats = {}
        
        if total_records > 0:
            # Gig economy participation rate
            gig_column = 'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?'
            if gig_column in filtered_df.columns:
                # Apply gig mapping
                gig_mapping = {
                    'Ekonomi Gig: Penghantaran & e-hailing (Grab, FoodPanda, Lalamove)': 'Penghantaran',
                    'Keusahawanan: Mengusahakan perniagaan sendiri (produk, perkhidmatan, syarikat)': 'Usahawan',
                    'Ekonomi Gig: Pendidikan & konsultasi (tutor online, coaching, kursus digital)': 'Pendidikan',
                    'Ekonomi Gig: Pembuatan kandungan (YouTube, TikTok, streaming)': 'Pembuatan Kandungan',
                    'Ekonomi Gig: Freelancing digital (design, copywriting, programming, social media marketing)': 'Digital',
                    'Ekonomi Gig: E-commerce & dropshipping (Shopee, Lazada, TikTok Shop)': 'E-commerce',
                    'Saya tidak bercadang untuk terlibat dalam mana-mana pekerjaan bebas': 'Tidak Berminat'
                }
                
                def clean_gig(cell):
                    if pd.isnull(cell):
                        return ''
                    found = []
                    for full_string, label in gig_mapping.items():
                        if full_string in str(cell):
                            found.append(label)
                    found = list(dict.fromkeys(found))
                    return '; '.join(found)
                
                filtered_df['gig_clean'] = filtered_df[gig_column].apply(clean_gig)
                
                # Calculate participation rates
                gig_interested = len(filtered_df[filtered_df['gig_clean'] != 'Tidak Berminat'])
                gig_participation_rate = (gig_interested / total_records) * 100 if total_records > 0 else 0
                
                # Count entrepreneurs specifically
                entrepreneur_count = len(filtered_df[filtered_df['gig_clean'].str.contains('Usahawan', na=False)])
                entrepreneurship_rate = (entrepreneur_count / total_records) * 100 if total_records > 0 else 0
                
                gig_stats['gig_participation_rate'] = gig_participation_rate
                gig_stats['entrepreneurship_rate'] = entrepreneurship_rate
            
            # University support rate
            university_support_column = 'Adakah universiti anda menawarkan kursus atau latihan berkaitan keusahawanan?'
            if university_support_column in filtered_df.columns:
                support_yes = len(filtered_df[filtered_df[university_support_column].str.contains('Ya', na=False)])
                university_support_rate = (support_yes / total_records) * 100 if total_records > 0 else 0
                gig_stats['university_support_rate'] = university_support_rate
            
            # Average income calculation
            income_column = 'Berapakah purata pendapatan bulan anda daripada ekonomi gig?'
            if income_column in filtered_df.columns:
                # Filter out 'Tidak relevan' and extract numeric values
                income_data = filtered_df[filtered_df[income_column] != 'Tidak relevan'][income_column].dropna()
                
                # Simple income estimation based on ranges
                income_mapping = {
                    'RM500 - RM1000': 750,
                    'RM1001 - RM2000': 1500,
                    'RM2001 - RM3000': 2500,
                    'RM3001 - RM5000': 4000,
                    'Lebih daripada RM5000': 6000
                }
                
                avg_income = 0
                valid_income_count = 0
                for income_str in income_data:
                    for range_str, avg_val in income_mapping.items():
                        if range_str in str(income_str):
                            avg_income += avg_val
                            valid_income_count += 1
                            break
                
                if valid_income_count > 0:
                    avg_income = avg_income / valid_income_count
                    gig_stats['avg_income'] = f'RM{int(avg_income)}'
                else:
                    gig_stats['avg_income'] = 'RM0'
            
            # Job preference rate
            job_pref_column = 'Jika diberikan peluang pekerjaan tetap dengan gaji setanding ekonomi gig, adakah anda akan menerimanya?'
            if job_pref_column in filtered_df.columns:
                prefer_permanent = len(filtered_df[filtered_df[job_pref_column].str.contains('Ya', na=False)])
                job_preference_rate = (prefer_permanent / total_records) * 100 if total_records > 0 else 0
                gig_stats['job_preference_rate'] = job_preference_rate
        
        # Update stats with calculated values
        stats.update({
            'total_records': total_records,
            'gig_participation_rate': round(gig_stats.get('gig_participation_rate', 0), 1),
            'entrepreneurship_rate': round(gig_stats.get('entrepreneurship_rate', 0), 1),
            'university_support_rate': round(gig_stats.get('university_support_rate', 0), 1),
            'avg_income': gig_stats.get('avg_income', 'RM0'),
            'job_preference_rate': round(gig_stats.get('job_preference_rate', 0), 1)
        })
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'total_records': 0,
            'gig_participation_rate': 0,
            'entrepreneurship_rate': 0,
            'university_support_rate': 0,
            'avg_income': 'RM0',
            'job_preference_rate': 0
        }), 500

@gig_economy_bp.route('/api/gig-types')
def api_gig_types():
    """Get gig economy work types data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        gig_column = 'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?'
        
        if gig_column not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        # Apply gig mapping and filtering
        gig_mapping = {
            'Ekonomi Gig: Penghantaran & e-hailing (Grab, FoodPanda, Lalamove)': 'Penghantaran',
            'Keusahawanan: Mengusahakan perniagaan sendiri (produk, perkhidmatan, syarikat)': 'Usahawan',
            'Ekonomi Gig: Pendidikan & konsultasi (tutor online, coaching, kursus digital)': 'Pendidikan',
            'Ekonomi Gig: Pembuatan kandungan (YouTube, TikTok, streaming)': 'Pembuatan Kandungan',
            'Ekonomi Gig: Freelancing digital (design, copywriting, programming, social media marketing)': 'Digital',
            'Ekonomi Gig: E-commerce & dropshipping (Shopee, Lazada, TikTok Shop)': 'E-commerce',
            'Saya tidak bercadang untuk terlibat dalam mana-mana pekerjaan bebas': 'Tidak Berminat'
        }
        
        def clean_gig(cell):
            if pd.isnull(cell):
                return ''
            found = []
            for full_string, label in gig_mapping.items():
                if full_string in str(cell):
                    found.append(label)
            found = list(dict.fromkeys(found))
            return '; '.join(found)
        
        df_work = filtered_processor.filtered_df.copy()
        df_work['gig_clean'] = df_work[gig_column].apply(clean_gig)
        
        # Filter out 'Tidak Berminat'
        df_gig_filtered = df_work[df_work['gig_clean'] != 'Tidak Berminat'].copy()
        
        if df_gig_filtered.empty:
            return jsonify({
                'labels': ['No Interested Participants'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        # Calculate frequency
        all_gigs = []
        for gig_cell in df_gig_filtered['gig_clean'].dropna():
            if pd.notna(gig_cell) and gig_cell.strip():
                gigs = [g.strip() for g in str(gig_cell).split(';') if g.strip()]
                all_gigs.extend(gigs)
        
        if not all_gigs:
            return jsonify({
                'labels': ['No Gig Data'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        gig_counts = pd.Series(all_gigs).value_counts()
        
        # Use brand colors
        brand_colors = ['#074e7e', '#c92427', '#0ea5e9', '#ef4444', '#06b6d4', '#f97316']
        
        chart_data = {
            'labels': gig_counts.index.tolist(),
            'datasets': [{
                'data': gig_counts.values.tolist(),
                'backgroundColor': brand_colors[:len(gig_counts.index)],
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

@gig_economy_bp.route('/api/university-support')
def api_university_support():
    """Get university entrepreneurship support data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        support_column = 'Adakah universiti anda menawarkan kursus atau latihan berkaitan keusahawanan?'
        
        if support_column not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderWidth': 2,
                    'borderColor': '#ffffff'
                }]
            })
        
        data = filtered_processor.get_chart_data('pie', support_column)
        
        # Use brand colors
        brand_colors = ['#074e7e', '#c92427', '#0ea5e9']
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

@gig_economy_bp.route('/api/university-programs')
def api_university_programs():
    """Get university business programs data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        programs_column = 'Adakah universiti anda pernah menganjurkan program berkaitan perniagaan atau ekonomi gig seperti hackathon, bootcamp, atau geran permulaan perniagaan?'
        
        if programs_column not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderWidth': 2,
                    'borderColor': '#ffffff'
                }]
            })
        
        data = filtered_processor.get_chart_data('pie', programs_column)
        
        # Use brand colors
        brand_colors = ['#074e7e', '#c92427', '#0ea5e9', '#ef4444']
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

@gig_economy_bp.route('/api/program-effectiveness')
def api_program_effectiveness():
    """Get program effectiveness data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        programs_column = 'Adakah universiti anda pernah menganjurkan program berkaitan perniagaan atau ekonomi gig seperti hackathon, bootcamp, atau geran permulaan perniagaan?'
        effectiveness_column = 'Adakah program berkaitan perniagaan atau ekonomi gig di universiti membantu anda dalam memulakan atau mengembangkan pekerjaan bebas anda?'
        
        # Filter out those who didn't hear about programs
        df_filtered = filtered_processor.filtered_df[
            filtered_processor.filtered_df[programs_column] != 'Tidak, saya tidak pernah dengar tentang program seperti ini.'
        ].copy()
        
        if df_filtered.empty or effectiveness_column not in df_filtered.columns:
            return jsonify({
                'labels': ['No Relevant Data'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderWidth': 2,
                    'borderColor': '#ffffff'
                }]
            })
        
        effectiveness_counts = df_filtered[effectiveness_column].value_counts()
        
        # Use brand colors
        brand_colors = ['#074e7e', '#c92427', '#0ea5e9', '#ef4444']
        
        chart_data = {
            'labels': effectiveness_counts.index.tolist(),
            'datasets': [{
                'data': effectiveness_counts.values.tolist(),
                'backgroundColor': brand_colors[:len(effectiveness_counts.index)],
                'borderColor': '#ffffff',
                'borderWidth': 3
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
                'borderWidth': 2,
                'borderColor': '#ffffff'
            }]
        }), 500

@gig_economy_bp.route('/api/gig-motivations')
def api_gig_motivations():
    """Get gig economy motivations data with proper comma-separated processing"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        # Try both possible column names
        motivations_columns = [
            'Apakah sebab utama anda memilih untuk bekerja dalam ekonomi gig? ',
            'Apakah sebab utama anda memilih untuk bekerja dalam ekonomi gig?'
        ]
        
        motivations_column = None
        for col in motivations_columns:
            if col in filtered_processor.filtered_df.columns:
                motivations_column = col
                break
        
        if motivations_column is None:
            # Debug: return available columns
            available_cols = [col for col in filtered_processor.filtered_df.columns if 'gig' in col.lower() or 'sebab' in col.lower()]
            return jsonify({
                'labels': [f'Column not found. Available: {", ".join(available_cols[:3])}'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        # Get all non-null values first
        all_responses = filtered_processor.filtered_df[motivations_column].dropna()
        
        if all_responses.empty:
            return jsonify({
                'labels': ['No responses in column'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        # Process all responses, including those with "Tidak relevan"
        all_motivations = []
        for motivations_cell in all_responses:
            if pd.notna(motivations_cell) and str(motivations_cell).strip():
                # Split by comma and clean each motivation
                motivations = [m.strip() for m in str(motivations_cell).split(',')]
                # Filter out empty strings but keep all responses initially for debugging
                motivations = [m for m in motivations if m and len(m.strip()) > 0]
                all_motivations.extend(motivations)
        
        if not all_motivations:
            return jsonify({
                'labels': ['No motivations found after processing'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        motivations_counts = pd.Series(all_motivations).value_counts()
        
        # Filter out "Tidak relevan" AFTER counting for debugging
        relevant_motivations = motivations_counts[~motivations_counts.index.str.contains('Tidak relevan', case=False, na=False)]
        
        if relevant_motivations.empty:
            # If all responses are "Tidak relevan", show the original counts for debugging
            top_motivations = motivations_counts.head(5)
        else:
            # Show top 10 relevant motivations
            top_motivations = relevant_motivations.head(10)
        
        # Convert pandas data to native Python types to avoid JSON serialization issues
        motivation_labels = [str(label) for label in top_motivations.index.tolist()]
        motivation_values = [int(value) for value in top_motivations.values.tolist()]
        
        # Use a more diverse color palette for motivations
        motivation_colors = [
            '#074e7e',  # Primary blue
            '#c92427',  # Primary red
            '#0ea5e9',  # Sky blue
            '#ef4444',  # Red
            '#06b6d4',  # Cyan
            '#f97316',  # Orange
            '#10b981',  # Emerald
            '#8b5cf6',  # Violet
            '#ec4899',  # Pink
            '#84cc16'   # Lime
        ]
        
        chart_data = {
            'labels': motivation_labels,
            'datasets': [{
                'label': 'Number of Responses',
                'data': motivation_values,
                'backgroundColor': motivation_colors[:len(motivation_labels)],
                'borderColor': '#ffffff',
                'borderWidth': 2,
                'borderRadius': 6
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify({
            'error': f'Error: {str(e)}',
            'labels': ['Error Loading Data'],
            'datasets': [{
                'data': [1],
                'backgroundColor': ['#ef4444'],
                'borderColor': '#dc2626',
                'borderWidth': 1
            }]
        }), 500

@gig_economy_bp.route('/api/skill-acquisition')
def api_skill_acquisition():
    """Get skill acquisition methods data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        skills_column = 'Bagaimanakah anda memperoleh kemahiran untuk bekerja dalam ekonomi gig?'
        
        if skills_column not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        # Apply skills mapping
        skills_mapping = {
            'Belajar sendiri melalui internet (YouTube, blog, forum).': 'Belajar Sendiri',
            'Mengikuti kursus atau latihan khusus (online atau offline).': 'Latihan',
            'Pengalaman kerja sebelum ini dalam bidang yang sama.': 'Pengalaman',
            'Rakan/keluarga mengajar atau berkongsi pengalaman.': 'Rakan/Keluarga',
            'Kursus atau bimbingan dari universiti.': 'Universiti'
        }
        
        def clean_skills_acquisition(cell):
            if pd.isnull(cell):
                return ''
            found = []
            for full_string, label in skills_mapping.items():
                if full_string in str(cell):
                    found.append(label)
            found = list(dict.fromkeys(found))
            return '; '.join(found)
        
        df_work = filtered_processor.filtered_df.copy()
        df_work['skills_acquisition_clean'] = df_work[skills_column].apply(clean_skills_acquisition)
        
        # Calculate frequency
        all_skills = []
        for skills_cell in df_work['skills_acquisition_clean'].dropna():
            if pd.notna(skills_cell) and skills_cell.strip():
                skills = [s.strip() for s in str(skills_cell).split(';') if s.strip()]
                all_skills.extend(skills)
        
        if not all_skills:
            return jsonify({
                'labels': ['No Skills Data'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        skills_counts = pd.Series(all_skills).value_counts()
        
        # Use brand colors
        brand_colors = ['#074e7e', '#c92427', '#0ea5e9', '#ef4444', '#06b6d4']
        
        chart_data = {
            'labels': skills_counts.index.tolist(),
            'datasets': [{
                'data': skills_counts.values.tolist(),
                'backgroundColor': brand_colors[:len(skills_counts.index)],
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

@gig_economy_bp.route('/api/gig-challenges')
def api_gig_challenges():
    """Get gig economy challenges data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        challenges_column = 'Apakah cabaran utama yang anda hadapi dalam keusahawanan atau ekonomi gig?'
        
        if challenges_column not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        # Process comma-separated challenges
        all_challenges = []
        for challenges_cell in filtered_processor.filtered_df[challenges_column].dropna():
            if pd.notna(challenges_cell):
                challenges = [c.strip() for c in str(challenges_cell).split(',')]
                challenges = [c for c in challenges if c]
                all_challenges.extend(challenges)
        
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
        
        challenges_counts = pd.Series(all_challenges).value_counts()
        
        # Use brand colors
        brand_colors = ['#074e7e', '#c92427', '#0ea5e9', '#ef4444', '#06b6d4', '#f97316', '#10b981']
        
        chart_data = {
            'labels': challenges_counts.index.tolist(),
            'datasets': [{
                'data': challenges_counts.values.tolist(),
                'backgroundColor': brand_colors[:len(challenges_counts.index)],
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

@gig_economy_bp.route('/api/support-needed')
def api_support_needed():
    """Get support needed data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        support_column = 'Apakah bantuan atau sokongan yang anda rasa perlu untuk berjaya dalam keusahawanan dan ekonomi gig?'
        
        if support_column not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        # Process comma-separated support needs
        all_support = []
        for support_cell in filtered_processor.filtered_df[support_column].dropna():
            if pd.notna(support_cell):
                support_items = [s.strip() for s in str(support_cell).split(',')]
                support_items = [s for s in support_items if s and 'Tidak relevan' not in s]
                all_support.extend(support_items)
        
        if not all_support:
            return jsonify({
                'labels': ['No Support Data'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        support_counts = pd.Series(all_support).value_counts()
        
        # Use brand colors
        brand_colors = ['#074e7e', '#c92427', '#0ea5e9', '#ef4444', '#06b6d4', '#f97316', '#10b981']
        
        chart_data = {
            'labels': support_counts.index.tolist(),
            'datasets': [{
                'data': support_counts.values.tolist(),
                'backgroundColor': brand_colors[:len(support_counts.index)],
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

@gig_economy_bp.route('/api/monthly-income')
def api_monthly_income():
    """Get monthly income from gig economy data with proper ordering"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        # Try multiple possible column names
        income_columns = [
            'Berapakah purata pendapatan bulan anda daripada ekonomi gig?',
            'Berapakah purata pendapatan bulanan anda daripada ekonomi gig?',
            'Purata pendapatan bulanan dari ekonomi gig',
            'Pendapatan bulanan ekonomi gig'
        ]
        
        income_column = None
        for col in income_columns:
            if col in filtered_processor.filtered_df.columns:
                income_column = col
                break
        
        if income_column is None:
            # Debug: find income-related columns
            income_related_cols = [col for col in filtered_processor.filtered_df.columns 
                                 if any(keyword in col.lower() for keyword in ['pendapatan', 'income', 'gaji', 'salary', 'gig'])]
            return jsonify({
                'labels': [f'Column not found. Found: {", ".join(income_related_cols[:3])}'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        # Get all non-null values
        all_income_data = filtered_processor.filtered_df[income_column].dropna()
        
        if all_income_data.empty:
            return jsonify({
                'labels': ['No income data found'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        # Filter out 'Tidak relevan' and similar responses
        df_income_filtered = all_income_data[
            ~all_income_data.str.contains('Tidak relevan', na=False, case=False)
        ]
        
        if df_income_filtered.empty:
            # If no relevant data, show sample of what we have for debugging
            sample_responses = all_income_data.value_counts().head(3)
            sample_list = [str(idx) for idx in sample_responses.index.tolist()]
            return jsonify({
                'labels': sample_list,
                'datasets': [{
                    'data': [int(val) for val in sample_responses.values.tolist()],
                    'backgroundColor': ['#6b7280', '#9ca3af', '#d1d5db'][:len(sample_list)],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        income_counts = df_income_filtered.value_counts()
        
        # Convert pandas data to native Python types to avoid JSON serialization issues
        income_labels = [str(label) for label in income_counts.index.tolist()]
        income_values = [int(value) for value in income_counts.values.tolist()]
        
        # Define proper order for income ranges - more flexible matching
        income_patterns = [
            ('Kurang daripada RM500', ['kurang', 'less', '<', 'rm500']),
            ('RM500 - RM1000', ['rm500', '500', '1000']), 
            ('RM1001 - RM2000', ['1001', '1000', '2000']),
            ('RM2001 - RM3000', ['2001', '2000', '3000']),
            ('RM3001 - RM5000', ['3001', '3000', '5000']),
            ('Lebih daripada RM5000', ['lebih', 'more', '>', '5000'])
        ]
        
        # Match income ranges flexibly
        ordered_labels = []
        ordered_values = []
        matched_ranges = set()
        
        for pattern_label, keywords in income_patterns:
            for i, actual_range in enumerate(income_labels):
                actual_lower = actual_range.lower()
                if any(keyword in actual_lower for keyword in keywords) and actual_range not in matched_ranges:
                    ordered_labels.append(actual_range)
                    ordered_values.append(income_values[i])
                    matched_ranges.add(actual_range)
                    break
        
        # Add any remaining unmatched categories
        for i, income_range in enumerate(income_labels):
            if income_range not in matched_ranges:
                ordered_labels.append(income_range)
                ordered_values.append(income_values[i])
        
        if not ordered_labels:
            return jsonify({
                'labels': ['No valid income ranges found'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderColor': '#374151',
                    'borderWidth': 1
                }]
            })
        
        # Use gradient colors for income ranges (low to high)
        income_colors = [
            '#ef4444',  # Red for low income
            '#f97316',  # Orange for lower-mid
            '#eab308',  # Yellow for mid
            '#22c55e',  # Green for upper-mid
            '#059669',  # Dark green for high
            '#047857'   # Very dark green for highest
        ]
        
        chart_data = {
            'labels': ordered_labels,
            'datasets': [{
                'label': 'Number of Respondents',
                'data': ordered_values,
                'backgroundColor': income_colors[:len(ordered_labels)],
                'borderColor': '#ffffff',
                'borderWidth': 2,
                'borderRadius': 6
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify({
            'error': f'Error: {str(e)}',
            'labels': ['Error Loading Data'],
            'datasets': [{
                'data': [1],
                'backgroundColor': ['#ef4444'],
                'borderColor': '#dc2626',
                'borderWidth': 1
            }]
        }), 500

@gig_economy_bp.route('/api/job-preference')
def api_job_preference():
    """Get job preference data (permanent vs gig)"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        preference_column = 'Jika diberikan peluang pekerjaan tetap dengan gaji setanding ekonomi gig, adakah anda akan menerimanya?'
        
        if preference_column not in filtered_processor.filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderWidth': 2,
                    'borderColor': '#ffffff'
                }]
            })
        
        # Filter out 'Tidak relevan'
        df_preference_filtered = filtered_processor.filtered_df[
            filtered_processor.filtered_df[preference_column] != 'Tidak relevan'
        ].copy()
        
        if df_preference_filtered.empty:
            return jsonify({
                'labels': ['No Relevant Data'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['#6b7280'],
                    'borderWidth': 2,
                    'borderColor': '#ffffff'
                }]
            })
        
        preference_counts = df_preference_filtered[preference_column].value_counts()
        
        # Use brand colors
        brand_colors = ['#074e7e', '#c92427', '#0ea5e9']
        
        chart_data = {
            'labels': preference_counts.index.tolist(),
            'datasets': [{
                'data': preference_counts.values.tolist(),
                'backgroundColor': brand_colors[:len(preference_counts.index)],
                'borderColor': '#ffffff',
                'borderWidth': 3
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
                'borderWidth': 2,
                'borderColor': '#ffffff'
            }]
        }), 500

@gig_economy_bp.route('/api/table-data')
def api_table_data():
    """Get paginated table data for gig economy"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() 
                   if k not in ['page', 'per_page', 'search']}
        filtered_processor = data_processor.apply_filters(filters)
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        
        # Define relevant columns for gig economy analysis
        relevant_columns = [
            'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?',
            'Adakah universiti anda menawarkan kursus atau latihan berkaitan keusahawanan?',
            'Adakah universiti anda pernah menganjurkan program berkaitan perniagaan atau ekonomi gig seperti hackathon, bootcamp, atau geran permulaan perniagaan?',
            'Adakah program berkaitan perniagaan atau ekonomi gig di universiti membantu anda dalam memulakan atau mengembangkan pekerjaan bebas anda?',
            'Apakah sebab utama anda memilih untuk bekerja dalam ekonomi gig? ',
            'Bagaimanakah anda memperoleh kemahiran untuk bekerja dalam ekonomi gig?',
            'Apakah cabaran utama yang anda hadapi dalam keusahawanan atau ekonomi gig?',
            'Apakah bantuan atau sokongan yang anda rasa perlu untuk berjaya dalam keusahawanan dan ekonomi gig?',
            'Berapakah purata pendapatan bulan anda daripada ekonomi gig?',
            'Jika diberikan peluang pekerjaan tetap dengan gaji setanding ekonomi gig, adakah anda akan menerimanya?',
            'Tahun graduasi anda?',
            'Jantina anda?'
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

@gig_economy_bp.route('/api/export')
def api_export():
    """Export gig economy data in various formats"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() if k != 'format'}
        filtered_processor = data_processor.apply_filters(filters)
        
        format_type = request.args.get('format', 'csv')
        
        relevant_columns = [
            'Timestamp',
            'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?',
            'Adakah universiti anda menawarkan kursus atau latihan berkaitan keusahawanan?',
            'Adakah universiti anda pernah menganjurkan program berkaitan perniagaan atau ekonomi gig seperti hackathon, bootcamp, atau geran permulaan perniagaan?',
            'Adakah program berkaitan perniagaan atau ekonomi gig di universiti membantu anda dalam memulakan atau mengembangkan pekerjaan bebas anda?',
            'Apakah sebab utama anda memilih untuk bekerja dalam ekonomi gig? ',
            'Bagaimanakah anda memperoleh kemahiran untuk bekerja dalam ekonomi gig?',
            'Apakah cabaran utama yang anda hadapi dalam keusahawanan atau ekonomi gig?',
            'Apakah bantuan atau sokongan yang anda rasa perlu untuk berjaya dalam keusahawanan dan ekonomi gig?',
            'Berapakah purata pendapatan bulan anda daripada ekonomi gig?',
            'Jika diberikan peluang pekerjaan tetap dengan gaji setanding ekonomi gig, adakah anda akan menerimanya?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?'
        ]
        
        available_columns = [col for col in relevant_columns if col in filtered_processor.filtered_df.columns]
        
        data = filtered_processor.export_data(format_type, available_columns)
        
        if format_type == 'csv':
            mimetype = 'text/csv'
            filename = 'gig_economy_entrepreneurship_data.csv'
        elif format_type == 'excel':
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = 'gig_economy_entrepreneurship_data.xlsx'
        else:
            mimetype = 'application/json'
            filename = 'gig_economy_entrepreneurship_data.json'
        
        return send_file(
            io.BytesIO(data),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gig_economy_bp.route('/api/filters/available')
def api_available_filters():
    """Get available filter options for gig economy data"""
    try:
        sample_df = data_processor.df
        filters = {}
        
        filter_columns = [
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?'
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