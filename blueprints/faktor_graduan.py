from flask import Blueprint, render_template, request, jsonify, send_file
from models.data_processor import DataProcessor, load_excel_data
import io
import os
import pandas as pd
import numpy as np
from collections import Counter

faktor_graduan_bp = Blueprint('faktor_graduan', __name__)

# Load data from Excel file
EXCEL_FILE_PATH = 'data/Questionnaire.xlsx'
df = load_excel_data(EXCEL_FILE_PATH)
data_processor = DataProcessor(df)

# Define the employability impact columns
EMPLOYABILITY_IMPACT_COLUMNS = [
    'Sejauh mana latihan industri/praktikal mempengaruhi kebolehpasaran anda?',
    'Sejauh mana kemahiran komunikasi  mempengaruhi kebolehpasaran anda?',
    'Sejauh mana kemahiran teknikal mempengaruhi kebolehpasaran anda?',
    'Sejauh mana rangkaian peribadi (networking) mempengaruhi kebolehpasaran anda?',
    'Sejauh mana kelayakan akademik mempengaruhi kebolehpasaran anda?'
]

# Additional skills grouping mapping
ADDITIONAL_SKILLS_GROUPING = {
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

def group_additional_skills(cell):
    """Function to clean and group skills"""
    if pd.isnull(cell):
        return ''
    text = str(cell)
    matched_groups = set()

    for keyword, group in ADDITIONAL_SKILLS_GROUPING.items():
        if keyword in text:
            matched_groups.add(group)

    return '; '.join(sorted(matched_groups)) if matched_groups else 'Lain-lain'

@faktor_graduan_bp.route('/')
def index():
    """Main faktor graduan dashboard page"""
    return render_template('faktor_graduan.html')

@faktor_graduan_bp.route('/table')
def table_view():
    """Table view for faktor graduan data"""
    return render_template('data_table.html', 
                         page_title='Faktor Kebolehpasaran Graduan Data Table',
                         api_endpoint='/faktor-graduan/api/table-data')

@faktor_graduan_bp.route('/api/summary')
def api_summary():
    """Get summary statistics for faktor graduan data"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        stats = filtered_processor.get_summary_stats()
        filtered_df = filtered_processor.filtered_df
        
        total_records = len(filtered_df)
        print(f"Total records in filtered data: {total_records}")  # Debug logging
        
        # Calculate employability factors statistics
        employability_stats = {}
        professional_certs_stats = {}
        university_preparation_stats = {}
        
        if total_records > 0:
            # Analyze employability factors impact (scale 1-5)
            for column in EMPLOYABILITY_IMPACT_COLUMNS:
                if column in filtered_df.columns:
                    scores = pd.to_numeric(filtered_df[column], errors='coerce').dropna()
                    if len(scores) > 0:
                        avg_score = scores.mean()
                        high_impact_count = len(scores[scores >= 4])  # Score 4-5 considered high impact
                        high_impact_percentage = (high_impact_count / len(scores)) * 100
                        
                        key = column.split('mempengaruhi')[0].strip().lower()
                        if 'industri' in key or 'praktikal' in key:
                            employability_stats['industrial_training_avg'] = round(avg_score, 2)
                            employability_stats['industrial_training_high_impact'] = round(high_impact_percentage, 1)
                        elif 'komunikasi' in key:
                            employability_stats['communication_skills_avg'] = round(avg_score, 2)
                            employability_stats['communication_skills_high_impact'] = round(high_impact_percentage, 1)
                        elif 'teknikal' in key:
                            employability_stats['technical_skills_avg'] = round(avg_score, 2)
                            employability_stats['technical_skills_high_impact'] = round(high_impact_percentage, 1)
                        elif 'rangkaian' in key or 'networking' in key:
                            employability_stats['networking_avg'] = round(avg_score, 2)
                            employability_stats['networking_high_impact'] = round(high_impact_percentage, 1)
                        elif 'akademik' in key:
                            employability_stats['academic_qualifications_avg'] = round(avg_score, 2)
                            employability_stats['academic_qualifications_high_impact'] = round(high_impact_percentage, 1)
            
            # Professional certificates analysis
            cert_columns = [col for col in filtered_df.columns 
                           if 'sijil profesional' in col.lower() and 'memiliki' in col.lower()]
            
            if cert_columns:
                cert_column = cert_columns[0]
                cert_responses = filtered_df[cert_column].dropna()
                has_certs = len(cert_responses[cert_responses.str.contains('Ya', na=False, case=False)])
                professional_certs_stats['has_professional_certs_rate'] = round((has_certs / len(cert_responses)) * 100, 1) if len(cert_responses) > 0 else 0
            
            # University preparation analysis
            prep_columns = [col for col in filtered_df.columns 
                           if 'universiti' in col.lower() and 'pasaran kerja' in col.lower()]
            
            if prep_columns:
                prep_column = prep_columns[0]
                prep_scores = pd.to_numeric(filtered_df[prep_column], errors='coerce').dropna()
                if len(prep_scores) > 0:
                    avg_prep_score = prep_scores.mean()
                    well_prepared_count = len(prep_scores[prep_scores >= 4])  # Score 4-5 considered well prepared
                    university_preparation_stats['university_preparation_avg'] = round(avg_prep_score, 2)
                    university_preparation_stats['well_prepared_rate'] = round((well_prepared_count / len(prep_scores)) * 100, 1)
        
        # Set default values if no data found
        default_stats = {
            'total_records': total_records,
            'industrial_training_avg': 0,
            'communication_skills_avg': 0,
            'technical_skills_avg': 0,
            'networking_avg': 0,
            'academic_qualifications_avg': 0,
            'has_professional_certs_rate': 0,
            'university_preparation_avg': 0,
            'well_prepared_rate': 0
        }
        
        # Update with calculated stats
        default_stats.update(employability_stats)
        default_stats.update(professional_certs_stats)
        default_stats.update(university_preparation_stats)
        
        print(f"Final stats: {default_stats}")  # Debug logging
        return jsonify(default_stats)
        
    except Exception as e:
        print(f"Error in summary endpoint: {str(e)}")  # Debug logging
        return jsonify({
            'error': str(e),
            'total_records': 0,
            'industrial_training_avg': 0,
            'communication_skills_avg': 0,
            'technical_skills_avg': 0,
            'networking_avg': 0,
            'academic_qualifications_avg': 0,
            'has_professional_certs_rate': 0,
            'university_preparation_avg': 0,
            'well_prepared_rate': 0
        }), 500

@faktor_graduan_bp.route('/api/employability-factors')
def api_employability_factors():
    """Get employability factors impact distribution"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        datasets = []
        labels = ['1', '2', '3', '4', '5']  # Scale 1-5
        
        colors = ['#1e40af', '#7c3aed', '#059669', '#d97706', '#dc2626']
        
        # Check if we have any data at all
        if len(filtered_processor.filtered_df) == 0:
            return jsonify({
                'labels': labels,
                'datasets': [{
                    'label': 'No Data Available',
                    'data': [0, 0, 0, 0, 0],
                    'backgroundColor': '#6b7280',
                    'borderWidth': 0,
                    'borderRadius': 6
                }]
            })
        
        for i, column in enumerate(EMPLOYABILITY_IMPACT_COLUMNS):
            if column in filtered_processor.filtered_df.columns:
                # Get value counts for each scale, handling non-numeric values
                column_data = filtered_processor.filtered_df[column].dropna()
                
                # Convert to numeric, coercing errors to NaN
                numeric_data = pd.to_numeric(column_data, errors='coerce').dropna()
                
                if len(numeric_data) > 0:
                    impact_counts = numeric_data.value_counts().sort_index()
                    
                    # Ensure all scale values are represented
                    data = [int(impact_counts.get(scale, 0)) for scale in [1, 2, 3, 4, 5]]
                    
                    # Create shorter label for legend
                    short_label = column.replace('Sejauh mana ', '').replace(' mempengaruhi kebolehpasaran anda?', '')
                    
                    # Simplify labels further
                    if 'latihan industri' in short_label.lower():
                        short_label = 'Industrial Training'
                    elif 'kemahiran komunikasi' in short_label.lower():
                        short_label = 'Communication Skills'
                    elif 'kemahiran teknikal' in short_label.lower():
                        short_label = 'Technical Skills'
                    elif 'rangkaian peribadi' in short_label.lower() or 'networking' in short_label.lower():
                        short_label = 'Networking'
                    elif 'kelayakan akademik' in short_label.lower():
                        short_label = 'Academic Qualifications'
                    
                    datasets.append({
                        'label': short_label,
                        'data': data,
                        'backgroundColor': colors[i % len(colors)],
                        'borderColor': colors[i % len(colors)],
                        'borderWidth': 0,
                        'borderRadius': 6
                    })
        
        # If no valid datasets found, return sample data
        if not datasets:
            datasets = [{
                'label': 'No Valid Data',
                'data': [0, 0, 0, 0, 0],
                'backgroundColor': '#6b7280',
                'borderWidth': 0,
                'borderRadius': 6
            }]
        
        return jsonify({
            'labels': labels,
            'datasets': datasets
        })
        
    except Exception as e:
        print(f"Error in employability factors: {str(e)}")  # Debug logging
        return jsonify({
            'labels': ['1', '2', '3', '4', '5'],
            'datasets': [{
                'label': 'Error Loading Data',
                'data': [1, 1, 1, 1, 1],
                'backgroundColor': '#ef4444',
                'borderWidth': 0
            }]
        }), 500

@faktor_graduan_bp.route('/api/professional-certificates-impact')
def api_professional_certificates_impact():
    """Get professional certificates impact on employment"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        # Find relevant columns with variations
        cert_columns = [col for col in filtered_processor.filtered_df.columns 
                       if 'sijil profesional' in col.lower() and 'memiliki' in col.lower()]
        
        impact_columns = [col for col in filtered_processor.filtered_df.columns 
                         if 'sijil profesional' in col.lower() and 'membantu' in col.lower()]
        
        if not cert_columns or not impact_columns:
            # Return sample data for demonstration
            return jsonify({
                'labels': ['Ya, sangat membantu', 'Ya, sedikit membantu', 'Tidak membantu', 'Tidak pasti'],
                'datasets': [{
                    'data': [45, 30, 15, 10],
                    'backgroundColor': ['#059669', '#d97706', '#dc2626', '#6b7280'],
                    'borderColor': '#ffffff',
                    'borderWidth': 3
                }]
            })
        
        cert_column = cert_columns[0]
        impact_column = impact_columns[0]
        
        # Filter for respondents with certificates
        df_filtered = filtered_processor.filtered_df.copy()
        
        # Standardize the 'Ya' response
        df_filtered[cert_column] = df_filtered[cert_column].replace({
            'Ya, contoh: ACCA, CFA, PMP, Cisco, Google Certification': 'Ya',
            'ya': 'Ya',
            'YA': 'Ya'
        })
        
        # Filter respondents with certificates
        df_with_certs = df_filtered[df_filtered[cert_column].str.contains('Ya', na=False, case=False)]
        
        if len(df_with_certs) > 0 and impact_column in df_with_certs.columns:
            impact_counts = df_with_certs[impact_column].value_counts()
            
            # Clean up the labels
            cleaned_labels = []
            cleaned_data = []
            
            for label, count in impact_counts.items():
                if pd.notna(label) and str(label).strip():
                    cleaned_labels.append(str(label).strip())
                    cleaned_data.append(int(count))
            
            if cleaned_labels:
                return jsonify({
                    'labels': cleaned_labels,
                    'datasets': [{
                        'data': cleaned_data,
                        'backgroundColor': ['#059669', '#d97706', '#dc2626', '#6b7280'][:len(cleaned_data)],
                        'borderColor': '#ffffff',
                        'borderWidth': 3
                    }]
                })
        
        # Fallback sample data
        return jsonify({
            'labels': ['Limited Data Available'],
            'datasets': [{
                'data': [1],
                'backgroundColor': ['#6b7280'],
                'borderColor': '#ffffff',
                'borderWidth': 3
            }]
        })
        
    except Exception as e:
        print(f"Error in professional certificates: {str(e)}")  # Debug logging
        return jsonify({
            'labels': ['Sample: Very Helpful', 'Sample: Somewhat Helpful', 'Sample: Not Helpful'],
            'datasets': [{
                'data': [50, 30, 20],
                'backgroundColor': ['#059669', '#d97706', '#dc2626'],
                'borderColor': '#ffffff',
                'borderWidth': 3
            }]
        }), 500

@faktor_graduan_bp.route('/api/employer-requirements')
def api_employer_requirements():
    """Get additional qualifications requested by employers"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        # Find relevant columns with variations
        req_columns = [col for col in filtered_processor.filtered_df.columns 
                      if 'majikan' in col.lower() and 'kelayakan' in col.lower()]
        
        if not req_columns:
            # Return sample data for demonstration
            return jsonify({
                'labels': ['Technical Skills', 'Professional Certificates', 'No Additional Requirements', 'Language Skills'],
                'datasets': [{
                    'data': [35, 25, 30, 10],
                    'backgroundColor': ['#1e40af', '#7c3aed', '#059669', '#d97706'],
                    'borderColor': '#374151',
                    'borderWidth': 0,
                    'borderRadius': 8
                }]
            })
        
        req_column = req_columns[0]
        df_filtered = filtered_processor.filtered_df.copy()
        
        if len(df_filtered) > 0:
            # Standardize responses
            df_filtered[req_column] = df_filtered[req_column].replace({
                'Ya, kemahiran teknikal tertentu (contoh: Python, Data Analytics)': 'Technical Skills',
                'Ya, sijil profesional (contoh: CFA, PMP, ACCA)': 'Professional Certificates',
                'Tidak': 'No Additional Requirements',
                'tidak': 'No Additional Requirements'
            })
            
            req_counts = df_filtered[req_column].value_counts()
            
            # Clean up the data
            cleaned_labels = []
            cleaned_data = []
            
            for label, count in req_counts.items():
                if pd.notna(label) and str(label).strip():
                    cleaned_labels.append(str(label).strip())
                    cleaned_data.append(int(count))
            
            if cleaned_labels:
                return jsonify({
                    'labels': cleaned_labels,
                    'datasets': [{
                        'data': cleaned_data,
                        'backgroundColor': ['#1e40af', '#7c3aed', '#059669', '#d97706', '#dc2626'][:len(cleaned_data)],
                        'borderColor': '#374151',
                        'borderWidth': 0,
                        'borderRadius': 8
                    }]
                })
        
        # Fallback sample data
        return jsonify({
            'labels': ['Limited Data Available'],
            'datasets': [{
                'data': [1],
                'backgroundColor': ['#6b7280'],
                'borderColor': '#374151',
                'borderWidth': 0,
                'borderRadius': 8
            }]
        })
        
    except Exception as e:
        print(f"Error in employer requirements: {str(e)}")  # Debug logging
        return jsonify({
            'labels': ['Sample: Technical Skills', 'Sample: Certificates', 'Sample: No Requirements'],
            'datasets': [{
                'data': [40, 35, 25],
                'backgroundColor': ['#1e40af', '#7c3aed', '#059669'],
                'borderColor': '#374151',
                'borderWidth': 0,
                'borderRadius': 8
            }]
        }), 500

@faktor_graduan_bp.route('/api/additional-skills-demand')
def api_additional_skills_demand():
    """Get additional skills demanded by employers"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        # Find relevant columns with variations
        skills_columns = [col for col in filtered_processor.filtered_df.columns 
                         if 'kemahiran tambahan' in col.lower() and 'majikan' in col.lower()]
        
        if not skills_columns:
            # Return sample data for demonstration
            return jsonify({
                'labels': [
                    'Kemahiran Digital & Teknologi',
                    'Kemahiran Komunikasi & Interpersonal', 
                    'Pemikiran Kritis & Penyelesaian Masalah',
                    'Kemahiran Kepimpinan & Pengurusan Diri',
                    'Kemahiran Bekerja Dalam Pasukan'
                ],
                'datasets': [{
                    'data': [45, 35, 30, 25, 20],
                    'backgroundColor': ['#1e40af', '#7c3aed', '#059669', '#d97706', '#dc2626'],
                    'borderColor': '#374151',
                    'borderWidth': 0,
                    'borderRadius': 8
                }]
            })
        
        skills_column = skills_columns[0]
        df_filtered = filtered_processor.filtered_df.copy()
        
        if len(df_filtered) > 0:
            # Apply grouping function
            df_filtered['Additional_Skills_Grouped'] = df_filtered[skills_column].apply(group_additional_skills)
            
            # Split cells with multiple categories and count
            split_skills = df_filtered['Additional_Skills_Grouped'].dropna().apply(
                lambda x: [i.strip() for i in x.split(';')] if x and x != 'Lain-lain' else []
            )
            
            # Flatten and count
            all_skills = [skill for sublist in split_skills for skill in sublist if skill]
            
            if all_skills:
                skill_counts = pd.Series(Counter(all_skills)).sort_values(ascending=False)
                
                # Take top 8 skills
                top_skills = skill_counts.head(8)
                
                return jsonify({
                    'labels': top_skills.index.tolist(),
                    'datasets': [{
                        'data': top_skills.values.tolist(),
                        'backgroundColor': ['#1e40af', '#7c3aed', '#059669', '#d97706', '#dc2626', '#0891b2', '#8b5cf6', '#f59e0b'][:len(top_skills)],
                        'borderColor': '#374151',
                        'borderWidth': 0,
                        'borderRadius': 8
                    }]
                })
        
        # Fallback sample data
        return jsonify({
            'labels': ['Limited Skills Data Available'],
            'datasets': [{
                'data': [1],
                'backgroundColor': ['#6b7280'],
                'borderColor': '#374151',
                'borderWidth': 0,
                'borderRadius': 8
            }]
        })
        
    except Exception as e:
        print(f"Error in additional skills: {str(e)}")  # Debug logging
        return jsonify({
            'labels': [
                'Sample: Digital Skills',
                'Sample: Communication', 
                'Sample: Problem Solving',
                'Sample: Leadership',
                'Sample: Teamwork'
            ],
            'datasets': [{
                'data': [40, 35, 30, 25, 20],
                'backgroundColor': ['#1e40af', '#7c3aed', '#059669', '#d97706', '#dc2626'],
                'borderColor': '#374151',
                'borderWidth': 0,
                'borderRadius': 8
            }]
        }), 500

@faktor_graduan_bp.route('/api/university-preparation')
def api_university_preparation():
    """Get university preparation for job market assessment"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        
        # Find relevant columns with variations
        prep_columns = [col for col in filtered_processor.filtered_df.columns 
                       if 'universiti' in col.lower() and 'pasaran kerja' in col.lower()]
        
        if not prep_columns:
            # Return sample data for demonstration
            return jsonify({
                'labels': ['1', '2', '3', '4', '5'],
                'datasets': [{
                    'label': 'University Preparation Assessment',
                    'data': [5, 15, 35, 30, 15],
                    'backgroundColor': '#1e40af30',
                    'borderColor': '#1e40af',
                    'borderWidth': 3,
                    'tension': 0.4,
                    'fill': True,
                    'pointBackgroundColor': '#ffffff',
                    'pointBorderColor': '#1e40af',
                    'pointBorderWidth': 3,
                    'pointRadius': 6
                }]
            })
        
        prep_column = prep_columns[0]
        
        if len(filtered_processor.filtered_df) > 0:
            # Get numeric data only
            column_data = filtered_processor.filtered_df[prep_column].dropna()
            numeric_data = pd.to_numeric(column_data, errors='coerce').dropna()
            
            if len(numeric_data) > 0:
                prep_counts = numeric_data.value_counts().sort_index()
                
                # Ensure all scale values are represented
                labels = ['1', '2', '3', '4', '5']
                data = [int(prep_counts.get(scale, 0)) for scale in [1, 2, 3, 4, 5]]
                
                return jsonify({
                    'labels': labels,
                    'datasets': [{
                        'label': 'Number of Respondents',
                        'data': data,
                        'backgroundColor': '#1e40af30',
                        'borderColor': '#1e40af',
                        'borderWidth': 3,
                        'tension': 0.4,
                        'fill': True,
                        'pointBackgroundColor': '#ffffff',
                        'pointBorderColor': '#1e40af',
                        'pointBorderWidth': 3,
                        'pointRadius': 6
                    }]
                })
        
        # Fallback sample data
        return jsonify({
            'labels': ['1', '2', '3', '4', '5'],
            'datasets': [{
                'label': 'Limited Data Available',
                'data': [1, 1, 1, 1, 1],
                'backgroundColor': '#6b728030',
                'borderColor': '#6b7280',
                'borderWidth': 3,
                'tension': 0.4,
                'fill': True,
                'pointBackgroundColor': '#ffffff',
                'pointBorderColor': '#6b7280',
                'pointBorderWidth': 3,
                'pointRadius': 6
            }]
        })
        
    except Exception as e:
        print(f"Error in university preparation: {str(e)}")  # Debug logging
        return jsonify({
            'labels': ['1', '2', '3', '4', '5'],
            'datasets': [{
                'label': 'Sample Data',
                'data': [10, 20, 30, 25, 15],
                'backgroundColor': '#1e40af30',
                'borderColor': '#1e40af',
                'borderWidth': 3,
                'tension': 0.4,
                'fill': True,
                'pointBackgroundColor': '#ffffff',
                'pointBorderColor': '#1e40af',
                'pointBorderWidth': 3,
                'pointRadius': 6
            }]
        }), 500

@faktor_graduan_bp.route('/api/table-data')
def api_table_data():
    """Get paginated table data for faktor graduan"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() 
                   if k not in ['page', 'per_page', 'search']}
        filtered_processor = data_processor.apply_filters(filters)
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        
        # Define relevant columns for faktor graduan
        relevant_columns = [
            'Status pekerjaan semasa',
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

@faktor_graduan_bp.route('/api/export')
def api_export():
    """Export faktor graduan data in various formats"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() if k != 'format'}
        filtered_processor = data_processor.apply_filters(filters)
        
        format_type = request.args.get('format', 'csv')
        
        relevant_columns = [
            'Timestamp',
            'Status pekerjaan semasa',
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
            'Umur anda?'
        ]
        
        available_columns = [col for col in relevant_columns if col in filtered_processor.filtered_df.columns]
        
        data = filtered_processor.export_data(format_type, available_columns)
        
        if format_type == 'csv':
            mimetype = 'text/csv'
            filename = 'faktor_graduan_data.csv'
        elif format_type == 'excel':
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = 'faktor_graduan_data.xlsx'
        else:
            mimetype = 'application/json'
            filename = 'faktor_graduan_data.json'
        
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
            'Status pekerjaan semasa',
            'Institusi pendidikan MARA yang anda hadiri?',
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
        
        return jsonify(filters)
        
    except Exception as e:
        return jsonify({'error': str(e), 'filters': {}}), 500