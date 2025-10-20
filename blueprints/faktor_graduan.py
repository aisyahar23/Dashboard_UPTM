from flask import Blueprint, render_template, request, jsonify, send_file
from models.data_processor import DataProcessor, load_excel_data
import io
import os
import pandas as pd
from collections import Counter
import numpy as np

faktor_graduan_bp = Blueprint('faktor-graduan', __name__)

# Load data from Excel file
EXCEL_FILE_PATH = 'data/Questionnaire.xlsx'
df = load_excel_data(EXCEL_FILE_PATH)
data_processor = DataProcessor(df)

@faktor_graduan_bp.route('/')
def index():
    """Main faktor graduan dashboard page"""
    return render_template('faktor_graduan.html')

@faktor_graduan_bp.route('/api/summary')
def api_summary():
    """Get enhanced summary statistics for employability factors"""
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
        
        # Define employability impact columns
        employability_columns = [
            'Sejauh mana latihan industri/praktikal mempengaruhi kebolehpasaran anda?',
            'Sejauh mana kemahiran komunikasi  mempengaruhi kebolehpasaran anda?',
            'Sejauh mana kemahiran teknikal mempengaruhi kebolehpasaran anda?',
            'Sejauh mana rangkaian peribadi (networking) mempengaruhi kebolehpasaran anda?',
            'Sejauh mana kelayakan akademik mempengaruhi kebolehpasaran anda?'
        ]
        
        # Calculate average scores for each factor
        factor_averages = {}
        highest_impact_factor = "N/A"
        lowest_impact_factor = "N/A"
        overall_preparedness = 0
        
        if total_records > 0:
            for column in employability_columns:
                if column in filtered_df.columns:
                    # Calculate average (excluding non-numeric values)
                    numeric_values = pd.to_numeric(filtered_df[column], errors='coerce').dropna()
                    if len(numeric_values) > 0:
                        avg_score = numeric_values.mean()
                        factor_averages[column] = avg_score
                        print(f"Factor {column}: {len(numeric_values)} values, avg: {avg_score}")
            
            if factor_averages:
                highest_impact_factor = max(factor_averages, key=factor_averages.get)
                lowest_impact_factor = min(factor_averages, key=factor_averages.get)
                overall_preparedness = sum(factor_averages.values()) / len(factor_averages)
        
        # University preparedness analysis
        prep_column = 'Sejauh mana anda bersetuju bahawa universiti telah menyediakan anda untuk pasaran kerja?'
        university_preparedness_avg = 0
        high_preparedness_rate = 0
        
        if prep_column in filtered_df.columns:
            prep_values = pd.to_numeric(filtered_df[prep_column], errors='coerce').dropna()
            if len(prep_values) > 0:
                university_preparedness_avg = prep_values.mean()
                high_preparedness_rate = (len(prep_values[prep_values >= 4]) / len(prep_values)) * 100
        
        # Professional certificates analysis
        cert_column = 'Adakah anda memiliki sijil profesional tambahan selain ijazah/diploma?'
        cert_impact_column = 'Adakah sijil profesional ini membantu anda dalam mendapatkan pekerjaan?'
        
        cert_ownership_rate = 0
        cert_impact_rate = 0
        
        if cert_column in filtered_df.columns:
            # Standardize 'Ya' responses
            filtered_df_copy = filtered_df.copy()
            filtered_df_copy[cert_column] = filtered_df_copy[cert_column].replace(
                'Ya, contoh: ACCA, CFA, PMP, Cisco, Google Certification', 'Ya'
            )
            
            cert_responses = filtered_df_copy[cert_column].dropna()
            if len(cert_responses) > 0:
                # Count people with certificates
                with_certs = len(cert_responses[cert_responses == 'Ya'])
                cert_ownership_rate = (with_certs / len(cert_responses)) * 100
                
                # For impact rate, only consider those WITH certificates
                if cert_impact_column in filtered_df_copy.columns and with_certs > 0:
                    # Filter to only those who have certificates
                    with_certs_df = filtered_df_copy[filtered_df_copy[cert_column] == 'Ya'].copy()
                    cert_impact_responses = with_certs_df[cert_impact_column].dropna()
                    
                    if len(cert_impact_responses) > 0:
                        # Count how many said certificates helped
                        helped_count = len(cert_impact_responses[cert_impact_responses.str.contains('Ya', na=False)])
                        cert_impact_rate = (helped_count / len(cert_impact_responses)) * 100
                        print(f"Certificate impact: {helped_count} out of {len(cert_impact_responses)} = {cert_impact_rate}%")
        
        # Most requested additional skill analysis - matching the chart API
        skills_column = 'Kemahiran tambahan manakah yang paling banyak diminta oleh majikan semasa temu duga? '
        most_requested_skill = "N/A"
        
        # Try to find the column with variations
        if skills_column not in filtered_df.columns:
            similar_columns = [col for col in filtered_df.columns if 'kemahiran tambahan' in col.lower()]
            print(f"Skills column not found. Similar columns: {similar_columns}")
            if similar_columns:
                skills_column = similar_columns[0]
                print(f"Using column: {skills_column}")
        
        if skills_column in filtered_df.columns:
            print(f"Processing skills from column: {skills_column}")
            # Use the same categorization as the chart
            additional_skills_grouping = {
                'Kemahiran Komunikasi': 'Kemahiran Komunikasi & Interpersonal',
                'Kemahiran Pembentangan': 'Kemahiran Komunikasi & Interpersonal',
                'Kemahiran Penulisan profesional': 'Kemahiran Komunikasi & Interpersonal',
                'Kemahiran Perundingan dan diplomasi': 'Kemahiran Komunikasi & Interpersonal',
                'Pemikiran kritis dan penyelesaian masalah': 'Pemikiran Kritis & Penyelesaian Masalah',
                'Keupayaan membuat keputusan berasaskan data': 'Pemikiran Kritis & Penyelesaian Masalah',
                'Analisis data dan penyelidikan': 'Pemikiran Kritis & Penyelesaian Masalah',
                'Kepimpinan dan pengurusan projek': 'Kemahiran Kepimpinan & Pengurusan Diri',
                'Pengurusan masa dan multitasking': 'Kemahiran Kepimpinan & Pengurusan Diri',
                'Keusahawanan dan pengurusan perniagaan': 'Kemahiran Kepimpinan & Pengurusan Diri',
                'Kemahiran bekerja dalam pasukan': 'Kemahiran Bekerja Dalam Pasukan',
                'Penggunaan perisian pejabat (Microsoft Office, Google Workspace)': 'Kemahiran Digital & Teknologi',
                'Kecekapan dalam perisian industri (AutoCAD, Photoshop, QuickBooks)': 'Kemahiran Digital & Teknologi',
                'Pemasaran digital dan media sosial': 'Kemahiran Digital & Teknologi',
                'Kemahiran pengaturcaraan (Python, SQL, Java)': 'Kemahiran Digital & Teknologi'
            }
            
            skills_data = filtered_df[skills_column].dropna()
            print(f"Skills data count: {len(skills_data)}")
            if len(skills_data) > 0:
                print(f"Sample skills data: {skills_data.head(3).tolist()}")
                # Count occurrences using the same grouping logic
                all_skills = []
                for cell in skills_data:
                    if pd.isnull(cell):
                        continue
                    text = str(cell)
                    matched_groups = set()
                    
                    for keyword, group in additional_skills_grouping.items():
                        if keyword in text:
                            matched_groups.add(group)
                    
                    if matched_groups:
                        all_skills.extend(matched_groups)
                    else:
                        all_skills.append('Lain-lain')
                        print(f"Uncategorized skill: {text[:100]}")
                
                if all_skills:
                    skill_counts = Counter(all_skills)
                    most_requested_skill = skill_counts.most_common(1)[0][0]
                    print(f"Most requested skill: {most_requested_skill} from {len(all_skills)} responses")
                    print(f"All skill counts: {dict(skill_counts)}")
                else:
                    print(f"No skills data found after processing {len(skills_data)} responses")
            else:
                print(f"Skills column found but no data: {len(skills_data)} responses")
        else:
            print(f"Skills column '{skills_column}' not found in dataframe. Available columns: {list(filtered_df.columns)}")
        
        enhanced_stats = {
            'total_records': total_records,
            'highest_impact_factor': highest_impact_factor.replace('Sejauh mana ', '').replace(' mempengaruhi kebolehpasaran anda?', '') if highest_impact_factor != "N/A" else "N/A",
            'lowest_impact_factor': lowest_impact_factor.replace('Sejauh mana ', '').replace(' mempengaruhi kebolehpasaran anda?', '') if lowest_impact_factor != "N/A" else "N/A",
            'overall_preparedness_score': round(overall_preparedness, 2),
            'university_preparedness_avg': round(university_preparedness_avg, 2),
            'high_preparedness_rate': round(high_preparedness_rate, 1),
            'cert_ownership_rate': round(cert_ownership_rate, 1),
            'cert_impact_rate': round(cert_impact_rate, 1),
            'most_requested_skill': most_requested_skill,
            'filter_applied': len([f for f in filters.values() if f]) > 0
        }
        
        print(f"Returning enhanced stats: {enhanced_stats}")
        return jsonify(enhanced_stats)
        
    except Exception as e:
        print(f"Error in api_summary: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'total_records': 0,
            'highest_impact_factor': 'N/A',
            'lowest_impact_factor': 'N/A',
            'overall_preparedness_score': 0,
            'university_preparedness_avg': 0,
            'high_preparedness_rate': 0,
            'cert_ownership_rate': 0,
            'cert_impact_rate': 0
        }), 500

@faktor_graduan_bp.route('/api/employability-factor/<factor_id>')
def api_individual_employability_factor(factor_id):
    """Get individual employability factor analysis for separate bar charts"""
    try:
        # Fixed filter handling
        filters = {}
        for key in request.args.keys():
            values = request.args.getlist(key)
            # Convert graduation year strings back to integers if needed
            if key == 'Tahun graduasi anda?':
                try:
                    values = [int(float(v)) for v in values if v.strip()]
                except (ValueError, TypeError):
                    print(f"Warning: Could not convert graduation years to int: {values}")
                    pass
            filters[key] = values
        
        print(f"API Individual Factor {factor_id} - Received filters: {filters}")
        
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        print(f"Individual factor {factor_id} - Filtered data shape: {filtered_df.shape}")
        
        employability_columns = {
            'industrial-training': 'Sejauh mana latihan industri/praktikal mempengaruhi kebolehpasaran anda?',
            'communication-skills': 'Sejauh mana kemahiran komunikasi  mempengaruhi kebolehpasaran anda?',
            'technical-skills': 'Sejauh mana kemahiran teknikal mempengaruhi kebolehpasaran anda?',
            'networking': 'Sejauh mana rangkaian peribadi (networking) mempengaruhi kebolehpasaran anda?',
            'academic-qualifications': 'Sejauh mana kelayakan akademik mempengaruhi kebolehpasaran anda?'
        }
        
        if factor_id not in employability_columns:
            return jsonify({
                'labels': ['Invalid Factor'],
                'datasets': [{
                    'label': 'Error',
                    'data': [1]
                }]
            }), 400
            
        column = employability_columns[factor_id]
        print(f"Looking for column: {column}")
        
        if column not in filtered_df.columns:
            print(f"Column not found. Available columns: {list(filtered_df.columns)}")
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': f"Faktor: {factor_id.replace('-', ' ').title()}",
                    'data': [1]
                }]
            })
        
        # Get value counts for scale 1-5
        print(f"Processing column {column} with {len(filtered_df)} rows")
        values = pd.to_numeric(filtered_df[column], errors='coerce').dropna()
        print(f"Numeric values found: {len(values)} out of {len(filtered_df)}")
        print(f"Sample values: {values.head().tolist() if len(values) > 0 else 'None'}")
        
        if len(values) == 0:
            print("No numeric values found")
            return jsonify({
                'labels': ['No Numeric Data'],
                'datasets': [{
                    'label': f"Faktor: {factor_id.replace('-', ' ').title()}",
                    'data': [1]
                }]
            })
            
        value_counts = values.value_counts().sort_index()
        print(f"Value counts: {dict(value_counts)}")
        
        # Ensure we have all scale points 1-5
        labels = []
        data = []
        scale_labels = {
            1: '1 - Sangat Rendah',
            2: '2 - Rendah', 
            3: '3 - Sederhana',
            4: '4 - Tinggi',
            5: '5 - Sangat Tinggi'
        }
        
        for i in range(1, 6):
            labels.append(scale_labels[i])
            # Convert to int to avoid JSON serialization issues
            count = int(value_counts.get(i, 0))
            data.append(count)
            print(f"Scale {i}: {count} responses")
        
        chart_data = {
            'labels': labels,
            'datasets': [{
                'label': column.replace('Sejauh mana ', '').replace(' mempengaruhi kebolehpasaran anda?', '').title(),
                'data': data
            }]
        }
        
        print(f"Returning chart data for {factor_id}: {chart_data}")
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in individual factor endpoint for {factor_id}: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error Loading Data',
                'data': [1]
            }]
        }), 500

@faktor_graduan_bp.route('/api/professional-certificates')
def api_professional_certificates():
    """Get professional certificates impact analysis - Bar Chart"""
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
        
        # Filter for working respondents with certificates
        cert_column = 'Adakah anda memiliki sijil profesional tambahan selain ijazah/diploma?'
        impact_column = 'Adakah sijil profesional ini membantu anda dalam mendapatkan pekerjaan?'
        
        if cert_column not in filtered_df.columns or impact_column not in filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Kesan Sijil Profesional',
                    'data': [1]
                }]
            })
        
        # Standardize 'Ya' responses
        filtered_df_copy = filtered_df.copy()
        filtered_df_copy[cert_column] = filtered_df_copy[cert_column].replace(
            'Ya, contoh: ACCA, CFA, PMP, Cisco, Google Certification', 'Ya'
        )
        
        # Filter for respondents with certificates
        with_certs_df = filtered_df_copy[filtered_df_copy[cert_column] == 'Ya'].copy()
        
        if with_certs_df.empty:
            return jsonify({
                'labels': ['Tiada Data Sijil'],
                'datasets': [{
                    'label': 'Kesan Sijil Profesional',
                    'data': [1]
                }]
            })
        
        # Get impact counts
        impact_counts = with_certs_df[impact_column].value_counts()
        
        chart_data = {
            'labels': [str(label) for label in impact_counts.index.tolist()],
            'datasets': [{
                'label': 'Kesan Sijil Profesional',
                'data': [int(val) for val in impact_counts.values.tolist()]
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in professional certificates endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

@faktor_graduan_bp.route('/api/employer-requirements')
def api_employer_requirements():
    """Get employer additional requirements analysis - Bar Chart"""
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
        
        req_column = 'Adakah majikan anda meminta kelayakan tambahan selain daripada ijazah anda?'
        
        if req_column not in filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Kelayakan Tambahan',
                    'data': [1]
                }]
            })
        
        # Standardize responses
        filtered_df_copy = filtered_df.copy()
        filtered_df_copy[req_column] = filtered_df_copy[req_column].replace({
            'Ya, kemahiran teknikal tertentu (contoh: Python, Data Analytics)': 'Ya, kemahiran teknikal',
            'Ya, sijil profesional (contoh: CFA, PMP, ACCA)': 'Ya, sijil profesional'
        })
        
        req_counts = filtered_df_copy[req_column].value_counts()
        
        chart_data = {
            'labels': [str(label) for label in req_counts.index.tolist()],
            'datasets': [{
                'label': 'Kelayakan Tambahan Majikan',
                'data': [int(val) for val in req_counts.values.tolist()]
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in employer requirements endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

@faktor_graduan_bp.route('/api/university-preparedness')
def api_university_preparedness():
    """Get university preparedness analysis - Bar Chart"""
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
        
        prep_column = 'Sejauh mana anda bersetuju bahawa universiti telah menyediakan anda untuk pasaran kerja?'
        
        if prep_column not in filtered_df.columns:
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Persediaan Universiti',
                    'data': [1]
                }]
            })
        
        prep_values = pd.to_numeric(filtered_df[prep_column], errors='coerce').dropna()
        if len(prep_values) == 0:
            return jsonify({
                'labels': ['No Numeric Data'],
                'datasets': [{
                    'label': 'Persediaan Universiti',
                    'data': [1]
                }]
            })
            
        prep_counts = prep_values.value_counts().sort_index()
        
        # Convert numeric scale to descriptive labels
        labels = []
        data = []
        scale_labels = {
            1: '1 - Sangat Tidak Setuju',
            2: '2 - Tidak Setuju', 
            3: '3 - Neutral',
            4: '4 - Setuju',
            5: '5 - Sangat Setuju'
        }
        
        for i in range(1, 6):
            labels.append(scale_labels[i])
            # Convert to int to avoid JSON serialization issues
            data.append(int(prep_counts.get(i, 0)))
        
        chart_data = {
            'labels': labels,
            'datasets': [{
                'label': 'Persediaan Universiti',
                'data': data
            }]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in university preparedness endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

@faktor_graduan_bp.route('/api/additional-skills')
def api_additional_skills():
    """Get additional skills analysis with grouped categories - Horizontal Bar Chart - Exact Colab Replication"""
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
        
        # Find the skills column - try exact match first, then similar
        skills_column = 'Kemahiran tambahan manakah yang paling banyak diminta oleh majikan semasa temu duga? '
        
        if skills_column not in filtered_df.columns:
            # Try to find similar column names
            similar_columns = [col for col in filtered_df.columns if 'kemahiran tambahan' in col.lower()]
            print(f"Similar columns found: {similar_columns}")
            
            if similar_columns:
                skills_column = similar_columns[0]
                print(f"Using column: {skills_column}")
            else:
                print(f"Available columns: {list(filtered_df.columns)}")
                return jsonify({
                    'labels': ['Skills Column Not Found'],
                    'datasets': [{
                        'label': 'Kemahiran Tambahan',
                        'data': [1]
                    }]
                })
        
        # EXACT COLAB REPLICATION - Define the grouping mapping exactly as in Colab
        additional_skills_grouping = {
            'Kemahiran Komunikasi': 'Kemahiran Komunikasi & Interpersonal',
            'Kemahiran Pembentangan': 'Kemahiran Komunikasi & Interpersonal',
            'Kemahiran Penulisan profesional': 'Kemahiran Komunikasi & Interpersonal',
            'Kemahiran Perundingan dan diplomasi': 'Kemahiran Komunikasi & Interpersonal',
            'Pemikiran kritis dan penyelesaian masalah': 'Pemikiran Kritis & Penyelesaian Masalah',
            'Keupayaan membuat keputusan berasaskan data': 'Pemikiran Kritis & Penyelesaian Masalah',
            'Analisis data dan penyelidikan': 'Pemikiran Kritis & Penyelesaian Masalah',
            'Kepimpinan dan pengurusan projek': 'Kemahiran Kepimpinan & Pengurusan Diri',
            'Pengurusan masa dan multitasking': 'Kemahiran Kepimpinan & Pengurusan Diri',
            'Keusahawanan dan pengurusan perniagaan': 'Kemahiran Kepimpinan & Pengurusan Diri',
            'Kemahiran bekerja dalam pasukan': 'Kemahiran Bekerja Dalam Pasukan',
            'Penggunaan perisian pejabat (Microsoft Office, Google Workspace)': 'Kemahiran Digital & Teknologi',
            'Kecekapan dalam perisian industri (AutoCAD, Photoshop, QuickBooks)': 'Kemahiran Digital & Teknologi',
            'Pemasaran digital dan media sosial': 'Kemahiran Digital & Teknologi',
            'Kemahiran pengaturcaraan (Python, SQL, Java)': 'Kemahiran Digital & Teknologi'
        }
        
        # EXACT COLAB REPLICATION - Function to clean and group skills
        def group_additional_skills(cell):
            if pd.isnull(cell):
                return ''
            text = str(cell)
            matched_groups = set()

            for keyword, group in additional_skills_grouping.items():
                if keyword in text:
                    matched_groups.add(group)

            return '; '.join(sorted(matched_groups)) if matched_groups else 'Lain-lain'
        
        # EXACT COLAB REPLICATION - Apply the grouping function to the column
        filtered_df_copy = filtered_df.copy()
        filtered_df_copy['Additional_Skills_Grouped'] = filtered_df_copy[skills_column].apply(group_additional_skills)
        
        print(f"Skills grouping results:")
        print(filtered_df_copy['Additional_Skills_Grouped'].value_counts())
        
        # EXACT COLAB REPLICATION - Step 1: Drop NaNs and split cells with multiple categories
        split_skills = filtered_df_copy['Additional_Skills_Grouped'].dropna().apply(lambda x: [i.strip() for i in x.split(';')])
        
        # EXACT COLAB REPLICATION - Step 2: Flatten the list to get all individual skills
        all_skills = [skill for sublist in split_skills for skill in sublist]
        
        print(f"All skills extracted: {all_skills}")
        
        if not all_skills:
            return jsonify({
                'labels': ['No Skills Found'],
                'datasets': [{
                    'label': 'Kemahiran Tambahan',
                    'data': [1]
                }]
            })
        
        # EXACT COLAB REPLICATION - Step 3: Count the frequency of each skill group
        skill_counts = pd.Series(Counter(all_skills)).sort_values(ascending=True)
        
        print(f"Skill counts: {dict(skill_counts)}")
        
        if skill_counts.empty:
            return jsonify({
                'labels': ['No Skill Counts'],
                'datasets': [{
                    'label': 'Kemahiran Tambahan',
                    'data': [1]
                }]
            })
        
        # Prepare data for horizontal bar chart (smallest to largest from bottom to top)
        labels = [str(skill) for skill in skill_counts.index.tolist()]
        data = [int(count) for count in skill_counts.values.tolist()]
        
        chart_data = {
            'labels': labels,
            'datasets': [{
                'label': 'Kekerapan Diminta',
                'data': data
            }]
        }
        
        print(f"Final chart data: {chart_data}")
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in additional skills endpoint: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'labels': ['Error Loading Skills Data'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500

# Keep existing endpoints (table, export, filters) with fixed filter handling
@faktor_graduan_bp.route('/api/table-data')
def api_table_data():
    """Get paginated table data for faktor graduan"""
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
        
        # Define relevant columns for faktor graduan
        relevant_columns = [
            'Sejauh mana latihan industri/praktikal mempengaruhi kebolehpasaran anda?',
            'Sejauh mana kemahiran komunikasi  mempengaruhi kebolehpasaran anda?',
            'Sejauh mana kemahiran teknikal mempengaruhi kebolehpasaran anda?',
            'Sejauh mana rangkaian peribadi (networking) mempengaruhi kebolehpasaran anda?',
            'Sejauh mana kelayakan akademik mempengaruhi kebolehpasaran anda?',
            'Adakah anda memiliki sijil profesional tambahan selain ijazah/diploma?',
            'Adakah sijil profesional ini membantu anda dalam mendapatkan pekerjaan?',
            'Adakah majikan anda meminta kelayakan tambahan selain daripada ijazah anda?',
            'Kemahiran tambahan manakah yang paling banyak diminta oleh majikan semasa temu duga? ',
            'Sejauh mana anda bersetuju bahawa universiti telah menyediakan anda untuk pasaran kerja?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?'
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

@faktor_graduan_bp.route('/api/export')
def api_export():
    """Export faktor graduan data in various formats"""
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
            'Sejauh mana latihan industri/praktikal mempengaruhi kebolehpasaran anda?',
            'Sejauh mana kemahiran komunikasi  mempengaruhi kebolehpasaran anda?',
            'Sejauh mana kemahiran teknikal mempengaruhi kebolehpasaran anda?',
            'Sejauh mana rangkaian peribadi (networking) mempengaruhi kebolehpasaran anda?',
            'Sejauh mana kelayakan akademik mempengaruhi kebolehpasaran anda?',
            'Adakah anda memiliki sijil profesional tambahan selain ijazah/diploma?',
            'Adakah sijil profesional ini membantu anda dalam mendapatkan pekerjaan?',
            'Adakah majikan anda meminta kelayakan tambahan selain daripada ijazah anda?',
            'Kemahiran tambahan manakah yang paling banyak diminta oleh majikan semasa temu duga? ',
            'Sejauh mana anda bersetuju bahawa universiti telah menyediakan anda untuk pasaran kerja?',
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?'
        ]
        
        available_columns = [col for col in relevant_columns if col in filtered_processor.filtered_df.columns]
        
        data = filtered_processor.export_data(format_type, available_columns)
        
        if format_type == 'csv':
            mimetype = 'text/csv'
            filename = 'faktor_kebolehpasaran_graduan_data.csv'
        elif format_type == 'excel':
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = 'faktor_kebolehpasaran_graduan_data.xlsx'
        else:
            mimetype = 'application/json'
            filename = 'faktor_kebolehpasaran_graduan_data.json'
        
        return send_file(
            io.BytesIO(data),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@faktor_graduan_bp.route('/api/filters/available')
def api_available_filters():
    """Get available filter options for faktor graduan data"""
    try:
        sample_df = data_processor.df
        filters = {}
        
        filter_columns = [
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?',
            'Adakah anda memiliki sijil profesional tambahan selain ijazah/diploma?'
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