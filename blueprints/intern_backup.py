# Fixed intern routes with comprehensive debugging
from flask import Blueprint, render_template, request, jsonify, send_file
from models.data_processor import DataProcessor, load_excel_data
import io
import os
import pandas as pd
import numpy as np
import re
from collections import Counter

intern_bp = Blueprint('intern', __name__)

# Load data from Excel file
EXCEL_FILE_PATH = 'data/Questionnaire.xlsx'
df = load_excel_data(EXCEL_FILE_PATH)
data_processor = DataProcessor(df)



# Check key columns
key_columns = [
    'Tahun graduasi anda?',
    'Apakah cabaran utama yang anda hadapi dalam mendapatkan pekerjaan?',
    'Jantina anda?',
    'Institusi pendidikan MARA yang anda hadiri?',
    'Adakah anda menjalani internship/praktikal sebelum tamat pengajian?'
]

for col in key_columns:
    if col in df.columns:
        non_null = df[col].notna().sum()
        print(f"✓ {col}: {non_null}/{len(df)} non-null values")
        if col == 'Adakah anda menjalani internship/praktikal sebelum tamat pengajian?':
            print(f"    Values: {df[col].value_counts().to_dict()}")
    else:
        print(f"✗ {col}: NOT FOUND")

print("="*50)

# Centralized Chart Data Formatter
class ChartDataFormatter:
    @staticmethod
    def format_pie_chart(data_series, title="Distribution"):
        return {
            'labels': data_series.index.tolist(),
            'datasets': [{
                'label': title,
                'data': data_series.values.tolist()
            }]
        }
    
    @staticmethod  
    def format_bar_chart(data_series, title="Chart", sort_desc=True):
        if sort_desc:
            data_series = data_series.sort_values(ascending=False)
        
        return {
            'labels': data_series.index.tolist(),
            'datasets': [{
                'label': title,
                'data': data_series.values.tolist()
            }]
        }

formatter = ChartDataFormatter()

@intern_bp.route('/')
def index():
    return render_template('intern.html')

@intern_bp.route('/table')
def table_view():
    return render_template('data_table.html', 
                         page_title='Internship & Employment Challenges Data Table',
                         api_endpoint='/intern/api/table-data')

def debug_filter_application(df_original, filters):
    """Debug filter application step by step"""
    print(f"\n=== FILTER DEBUG ===")
    print(f"Original data shape: {df_original.shape}")
    print(f"Filters received: {filters}")
    
    df_result = df_original.copy()
    
    for column, values in filters.items():
        if not values or len(values) == 0:
            continue
            
        print(f"\nApplying filter: {column} = {values}")
        print(f"Column exists: {column in df_result.columns}")
        
        if column in df_result.columns:
            print(f"Before filter - rows: {len(df_result)}")
            print(f"Column data type: {df_result[column].dtype}")
            print(f"Unique values in column: {df_result[column].unique()}")
            print(f"Looking for values: {values}")
            
            # Convert filter values to match column data type
            if df_result[column].dtype in ['int64', 'float64']:
                try:
                    converted_values = [int(float(v)) for v in values]
                    print(f"Converted filter values to int: {converted_values}")
                    df_result = df_result[df_result[column].isin(converted_values)]
                except:
                    print(f"Failed to convert values to int, using as string")
                    df_result = df_result[df_result[column].astype(str).isin([str(v) for v in values])]
            else:
                # String matching
                df_result = df_result[df_result[column].isin(values)]
            
            print(f"After filter - rows: {len(df_result)}")
            
            if len(df_result) == 0:
                print("WARNING: Filter eliminated all rows!")
                break
        else:
            print(f"WARNING: Column {column} not found!")
    
    print(f"Final filtered shape: {df_result.shape}")
    print("=== END FILTER DEBUG ===\n")
    
    return df_result

@intern_bp.route('/api/summary')
def api_summary():
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        print(f"\nSUMMARY DEBUG: Received filters: {filters}")
        
        # Use debug filter application
        df_filtered = debug_filter_application(data_processor.df, filters)
        total_records = len(df_filtered)
        
        print(f"SUMMARY DEBUG: Processing {total_records} records")
        
        kpis = {
            'total_records': total_records,
            'internship_rate': 0,
            'no_experience_rate': 0,
            'market_competition_rate': 0
        }
        
        if total_records > 0:
            # Internship participation rate - FIXED LOGIC
            internship_column = 'Adakah anda menjalani internship/praktikal sebelum tamat pengajian?'
            if internship_column in df_filtered.columns:
                internship_counts = df_filtered[internship_column].value_counts()
                print(f"Internship counts: {dict(internship_counts)}")
                
                # Count all "Ya" responses (any type of internship)
                internship_yes = 0
                for value, count in internship_counts.items():
                    if pd.notna(value) and 'ya' in str(value).lower():
                        internship_yes += count
                        print(f"  Adding {count} from '{value}'")
                
                print(f"Total 'Ya' responses: {internship_yes}")
                kpis['internship_rate'] = round((internship_yes / total_records) * 100, 1)
            
            # Experience challenges
            challenge_column = 'Apakah cabaran utama yang anda hadapi dalam mendapatkan pekerjaan?'
            if challenge_column in df_filtered.columns:
                experience_respondents = 0
                market_respondents = 0
                
                for challenges_cell in df_filtered[challenge_column].dropna():
                    if pd.notna(challenges_cell):
                        challenges_str = str(challenges_cell).lower()
                        
                        if 'pengalaman' in challenges_str or 'berpengalaman' in challenges_str:
                            experience_respondents += 1
                        
                        if ('persaingan' in challenges_str or 
                            'ekonomi' in challenges_str or 
                            'gaji' in challenges_str):
                            market_respondents += 1
                
                total_challenge_responses = len(df_filtered[challenge_column].dropna())
                if total_challenge_responses > 0:
                    kpis['no_experience_rate'] = round((experience_respondents / total_challenge_responses) * 100, 1)
                    kpis['market_competition_rate'] = round((market_respondents / total_challenge_responses) * 100, 1)
        
        print(f"SUMMARY RESULT: {kpis}")
        return jsonify(kpis)
        
    except Exception as e:
        print(f"SUMMARY ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'total_records': 0,
            'internship_rate': 0,
            'no_experience_rate': 0,
            'market_competition_rate': 0,
            'error': str(e)
        }), 500

@intern_bp.route('/api/grouped-challenges')
def api_grouped_challenges():
    """Get grouped challenges with enhanced debugging"""
    try:
        print("\nGROUPED CHALLENGES DEBUG:")
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        print(f"Filters applied: {filters}")
        
        # Use debug filter application
        df_filtered = debug_filter_application(data_processor.df, filters)
        
        print(f"Filtered data shape: {df_filtered.shape}")
        
        challenge_column = 'Apakah cabaran utama yang anda hadapi dalam mendapatkan pekerjaan?'
        
        if challenge_column not in df_filtered.columns:
            print(f"ERROR: Challenge column not found")
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['Column Not Found']),
                "Grouped Challenges"
            ))
        
        print(f"Challenge column found. Non-null values: {df_filtered[challenge_column].notna().sum()}")
        
        # Challenge mapping
        challenge_mapping = {
            'Tiada pengalaman kerja yang mencukupi': 'Tiada Pengalaman',
            'Terlalu banyak persaingan dalam bidang saya': 'Persaingan',
            'Kekurangan kemahiran yang dicari majikan': 'Kurang Kemahiran',
            'Gaji yang ditawarkan terlalu rendah': 'Gaji Rendah',
            'Saya tidak tahu bagaimana mencari pekerjaan yang sesuai': 'Tiada Pengetahuan',
            'Tiada rangkaian atau hubungan yang boleh membantu saya mendapatkan pekerjaan': 'Tiada Rangkaian',
            'Kriteria pekerjaan tidak sesuai dengan kelayakan akademik saya': 'Kelayakan Tidak Sepadan',
            'Kebanyakan syarikat lebih memilih pekerja yang sudah berpengalaman': 'Tiada Pengalaman',
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
        
        # Process challenges
        all_raw_challenges = []
        all_mapped_challenges = []
        all_grouped_challenges = []
        
        for challenges_cell in df_filtered[challenge_column].dropna():
            if pd.notna(challenges_cell):
                raw_challenges = [c.strip() for c in str(challenges_cell).split(',')]
                all_raw_challenges.extend([c for c in raw_challenges if c])
                
                # Map challenges
                mapped_challenges = [challenge_mapping.get(c, c) for c in raw_challenges if c]
                all_mapped_challenges.extend(mapped_challenges)
                
                # Group challenges
                grouped_challenges = [grouping_mapping.get(c, c) for c in mapped_challenges]
                all_grouped_challenges.extend(grouped_challenges)
        
        print(f"Raw challenges extracted: {len(all_raw_challenges)}")
        print(f"Mapped challenges: {len(all_mapped_challenges)}")
        print(f"Grouped challenges: {len(all_grouped_challenges)}")
        
        if not all_grouped_challenges:
            print("ERROR: No grouped challenges created")
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Challenges Data']),
                "Grouped Challenges"
            ))
        
        grouped_challenge_counts = pd.Series(all_grouped_challenges).value_counts()
        print(f"Final grouped categories: {dict(grouped_challenge_counts)}")
        
        chart_data = formatter.format_bar_chart(
            grouped_challenge_counts,
            "Grouped Employment Challenges",
            sort_desc=True
        )
        
        print("SUCCESS: Grouped challenges chart data created")
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"GROUPED CHALLENGES ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(formatter.format_bar_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@intern_bp.route('/api/filters/available')
def api_available_filters():
    """Enhanced filter debugging for graduation years"""
    try:
        print("\nFILTER DEBUG START:")
        sample_df = data_processor.df
        filters = {}
        
        print(f"DataFrame shape: {sample_df.shape}")
        
        filter_columns = [
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?',
            'Program pengajian yang anda ikuti?',
            'Adakah anda menjalani internship/praktikal sebelum tamat pengajian?'
        ]
        
        for column in filter_columns:
            print(f"\n--- Processing: {column} ---")
            
            if column in sample_df.columns:
                non_null_data = sample_df[column].dropna()
                print(f"Non-null values: {len(non_null_data)}/{len(sample_df)}")
                
                if len(non_null_data) == 0:
                    filters[column] = []
                    continue
                
                unique_values = non_null_data.unique()
                print(f"Unique values: {len(unique_values)}")
                
                # Show sample values
                sample_values = list(unique_values)[:5]
                print(f"Sample values: {sample_values}")
                
                # Special handling for graduation year
                if 'Tahun graduasi' in column or 'graduasi' in column.lower():
                    print("GRADUATION YEAR PROCESSING:")
                    processed_years = set()
                    
                    for val in unique_values:
                        if pd.notna(val):
                            year = extract_graduation_year(val)
                            if year:
                                processed_years.add(year)
                                print(f"  '{val}' -> {year}")
                            else:
                                print(f"  '{val}' -> FAILED")
                    
                    final_years = sorted(list(processed_years))
                    print(f"FINAL YEARS: {final_years}")
                    filters[column] = final_years
                    
                elif isinstance(unique_values[0] if len(unique_values) > 0 else None, (int, float)):
                    # Other numeric columns
                    unique_values = sorted([val for val in unique_values if pd.notna(val)])
                    filters[column] = unique_values
                else:
                    # String columns
                    unique_values = sorted([str(val) for val in unique_values if pd.notna(val) and str(val).strip()])
                    filters[column] = unique_values
                    
                print(f"Final filter values: {len(filters[column])} items")
                
            else:
                print(f"COLUMN NOT FOUND: {column}")
                filters[column] = []
        
        print(f"\nFILTER SUMMARY:")
        for col, values in filters.items():
            print(f"  {col}: {len(values)} values")
            if 'graduasi' in col.lower() and values:
                print(f"    Graduation years: {values}")
        
        return jsonify(filters)
        
    except Exception as e:
        print(f"FILTER ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'filters': {}}), 500

def extract_graduation_year(val):
    """Enhanced graduation year extraction with debugging"""
    if pd.isna(val):
        return None
    
    val_str = str(val).strip()
    
    # Method 1: Direct number
    try:
        # Remove commas and decimal points
        clean_val = val_str.replace(',', '').replace('.0', '')
        if clean_val.isdigit():
            year = int(clean_val)
            if 1990 <= year <= 2030:
                return year
    except:
        pass
    
    # Method 2: Extract 4-digit years using regex
    year_pattern = r'\b(19|20)\d{2}\b'
    matches = re.findall(year_pattern, val_str)
    if matches:
        for match in matches:
            year = int(match)
            if 1990 <= year <= 2030:
                return year
    
    # Method 3: Handle decimal/float format
    try:
        float_val = float(val_str.replace(',', ''))
        year = int(float_val)
        if 1990 <= year <= 2030:
            return year
    except:
        pass
    
    return None

# Fixed internship participation with debug filter
@intern_bp.route('/api/internship-participation')
def api_internship_participation():
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        df_filtered = debug_filter_application(data_processor.df, filters)
        
        internship_column = 'Adakah anda menjalani internship/praktikal sebelum tamat pengajian?'
        if internship_column not in df_filtered.columns:
            return jsonify(formatter.format_pie_chart(
                pd.Series([1], index=['No Data Available']),
                "Internship Participation"
            ))
        
        participation_counts = df_filtered[internship_column].value_counts()
        chart_data = formatter.format_pie_chart(participation_counts, "Internship Participation")
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify(formatter.format_pie_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@intern_bp.route('/api/internship-benefits')
def api_internship_benefits():
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        df_filtered = debug_filter_application(data_processor.df, filters)
        
        # Include all respondents (both with and without internship)
        df_internship = df_filtered.copy()
        
        benefits_column = 'Bagaimana internship membantu anda dalam mendapatkan pekerjaan?'
        
        if benefits_column not in df_internship.columns or df_internship.empty:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Data Available']),
                "Internship Benefits"
            ))
        
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
        chart_data = formatter.format_bar_chart(benefits_counts, "Internship Benefits", sort_desc=True)
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify(formatter.format_bar_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@intern_bp.route('/api/no-internship-reasons')
def api_no_internship_reasons():
    try:
        print("\n=== DEBUG: Starting api_no_internship_reasons ===")
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        df_filtered = debug_filter_application(data_processor.df, filters)
        
        print(f"Total filtered records: {len(df_filtered)}")
        
        # More flexible matching for the internship column
        internship_column = 'Adakah anda menjalani internship/praktikal sebelum tamat pengajian?'
        print(f"Internship column values: {df_filtered[internship_column].unique()}")
        
        # Handle case-insensitive matching and different variations
        df_no_internship = df_filtered[
            df_filtered[internship_column].astype(str).str.lower().str.contains('tidak|no|tidak menjalani', na=False, regex=True)
        ].copy()
        
        print(f"Number of respondents without internship: {len(df_no_internship)}")
        
        reasons_column = 'Jika tidak menjalani internship, apakah sebab utama?'
        
        if reasons_column not in df_no_internship.columns or df_no_internship.empty:
            print("No internship data or reasons column not found")
            return jsonify({
                'labels': ['Tiada data'],
                'datasets': [{'data': [0], 'label': 'Tiada data'}]
            })
        
        # Get the raw reasons data
        reasons_data = df_no_internship[reasons_column].dropna().astype(str)
        print(f"Raw reasons data:\n{reasons_data}")
        
        # Split and clean the reasons
        all_reasons = []
        for reasons_cell in reasons_data:
            # Clean and split the cell content
            reasons = [r.strip() for r in str(reasons_cell).replace(';', ',').split(',') if r.strip()]
            all_reasons.extend(reasons)
        
        print(f"Processed reasons: {all_reasons}")
        
        if not all_reasons:
            print("No valid reasons found after processing")
            return jsonify({
                'labels': ['Tiada maklumat'],
                'datasets': [{'data': [0], 'label': 'Tiada maklumat'}]
            })
        
        # Count occurrences of each reason
        reasons_counts = pd.Series(all_reasons).value_counts()
        print(f"Reason counts before processing:\n{reasons_counts}")
        
        # Clean up the reason texts
        cleaned_reasons = {}
        for reason, count in reasons_counts.items():
            # Clean up the reason text
            clean_reason = reason.strip()
            if clean_reason.lower() in ['nan', 'none', '']:
                continue
                
            # Group similar reasons
            found = False
            for existing in cleaned_reasons:
                if clean_reason.lower() in existing.lower() or existing.lower() in clean_reason.lower():
                    cleaned_reasons[existing] += count
                    found = True
                    break
            if not found:
                cleaned_reasons[clean_reason] = count
        
        print(f"Cleaned reasons: {cleaned_reasons}")
        
        if not cleaned_reasons:
            return jsonify({
                'labels': ['Tiada maklumat'],
                'datasets': [{'data': [0], 'label': 'Tiada maklumat'}]
            })
        
        # Convert to percentage of total respondents without internship
        reasons_series = pd.Series(cleaned_reasons)
        if not reasons_series.empty and len(df_no_internship) > 0:
            reasons_series = (reasons_series / len(df_no_internship)) * 100
        
        print(f"Final reason percentages:\n{reasons_series}")
        
        # Create chart data
        chart_data = formatter.format_bar_chart(
            reasons_series, 
            "Sebab Tiada Latihan Industri", 
            sort_desc=True
        )
        
        print("=== DEBUG: End of api_no_internship_reasons ===\n")
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in api_no_internship_reasons: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'labels': ['Ralat memuat data'],
            'datasets': [{'data': [0], 'label': 'Ralat'}]
        }), 500

@intern_bp.route('/api/employment-challenges')
def api_employment_challenges():
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        df_filtered = debug_filter_application(data_processor.df, filters)
        
        challenge_column = 'Apakah cabaran utama yang anda hadapi dalam mendapatkan pekerjaan?'
        
        if challenge_column not in df_filtered.columns:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Data Available']),
                "Employment Challenges"
            ))
        
        # Challenge mapping
        challenge_mapping = {
            'Tiada pengalaman kerja yang mencukupi': 'Tiada Pengalaman',
            'Terlalu banyak persaingan dalam bidang saya': 'Persaingan',
            'Kekurangan kemahiran yang dicari majikan': 'Kurang Kemahiran',
            'Gaji yang ditawarkan terlalu rendah': 'Gaji Rendah',
            'Saya tidak tahu bagaimana mencari pekerjaan yang sesuai': 'Tiada Pengetahuan',
            'Tiada rangkaian atau hubungan yang boleh membantu saya mendapatkan pekerjaan': 'Tiada Rangkaian',
            'Kriteria pekerjaan tidak sesuai dengan kelayakan akademik saya': 'Kelayakan Tidak Sepadan',
            'Kebanyakan syarikat lebih memilih pekerja yang sudah berpengalaman': 'Tiada Pengalaman',
            'Tiada peluang pekerjaan dalam bidang saya di kawasan tempat tinggal saya': 'Lokasi Pekerjaan',
            'Saya perlu menjaga keluarga dan sukar untuk bekerja di luar kawasan': 'Isu Keluarga',
            'Proses permohonan kerja terlalu kompleks atau mengambil masa yang lama': 'Proses Permohonan',
            'Keadaan ekonomi semasa menyukarkan peluang pekerjaan': 'Ekonomi'
        }
        
        all_challenges = []
        for challenges_cell in df_filtered[challenge_column].dropna():
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
        chart_data = formatter.format_bar_chart(challenge_counts, "Employment Challenges", sort_desc=True)
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify(formatter.format_bar_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

# Keep existing table-data, export endpoints but with debug filter
@intern_bp.route('/api/table-data')
def api_table_data():
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() 
                   if k not in ['page', 'per_page', 'search', 'chartType']}
        
        # Get chart type if specified
        chart_type = request.args.get('chartType', '')
        
        # Apply filters using debug function
        df_filtered = debug_filter_application(data_processor.df, filters)
        
        # Filter data based on chart type
        if chart_type == 'no-internship-reasons':
            # Filter for respondents who didn't do internship
            df_filtered = df_filtered[
                df_filtered['Adakah anda menjalani internship/praktikal sebelum tamat pengajian?']
                .astype(str).str.lower().str.contains('tidak|no|tidak menjalani', na=False)
            ]
            relevant_columns = [
                'Tahun graduasi anda?',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?',
                'Jika tidak menjalani internship, apakah sebab utama?'
            ]
        elif chart_type == 'employment-challenges':
            relevant_columns = [
                'Tahun graduasi anda?',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?',
                'Apakah cabaran utama yang anda hadapi dalam mendapatkan pekerjaan?'
            ]
        elif chart_type == 'internship-benefits':
            df_filtered = df_filtered[
                df_filtered['Adakah anda menjalani internship/praktikal sebelum tamat pengajian?']
                .astype(str).str.lower().str.contains('ya|yes|pernah', na=False)
            ]
            relevant_columns = [
                'Tahun graduasi anda?',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?',
                'Bagaimana internship membantu anda dalam mendapatkan pekerjaan?'
            ]
        else:
            # Default columns if no specific chart type
            relevant_columns = [
                'Tahun graduasi anda?',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?',
                'Adakah anda menjalani internship/praktikal sebelum tamat pengajian?',
                'Bagaimana internship membantu anda dalam mendapatkan pekerjaan?',
                'Jika tidak menjalani internship, apakah sebab utama?',
                'Apakah cabaran utama yang anda hadapi dalam mendapatkan pekerjaan?'
            ]
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        
        # Ensure we only include columns that exist in the dataframe
        available_columns = [col for col in relevant_columns if col in df_filtered.columns]
        
        available_columns = [col for col in relevant_columns if col in df_filtered.columns]
        
        # Manual pagination and search implementation
        if search:
            search_mask = df_filtered[available_columns].astype(str).apply(
                lambda x: x.str.contains(search, case=False, na=False)
            ).any(axis=1)
            df_filtered = df_filtered[search_mask]
        
        total_records = len(df_filtered)
        total_pages = (total_records + per_page - 1) // per_page
        
        # Apply pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        df_page = df_filtered[available_columns].iloc[start_idx:end_idx]
        
        # Convert to records
        records = df_page.to_dict('records')
        
        data = {
            'data': records,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_records,
                'pages': total_pages
            },
            'columns': available_columns
        }
        
        return jsonify(data)
        
    except Exception as e:
        print(f"TABLE DATA ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'data': [],
            'pagination': {'page': 1, 'per_page': 50, 'total': 0, 'pages': 0},
            'columns': []
        }), 500

@intern_bp.route('/api/export')
def api_export():
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys() if k != 'format'}
        df_filtered = debug_filter_application(data_processor.df, filters)
        
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
        
        available_columns = [col for col in relevant_columns if col in df_filtered.columns]
        export_df = df_filtered[available_columns]
        
        # Create export data
        buffer = io.BytesIO()
        
        if format_type == 'csv':
            export_df.to_csv(buffer, index=False, encoding='utf-8')
            mimetype = 'text/csv'
            filename = 'internship_employment_challenges.csv'
        elif format_type == 'excel':
            export_df.to_excel(buffer, index=False, engine='openpyxl')
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = 'internship_employment_challenges.xlsx'
        else:
            export_df.to_json(buffer, orient='records', indent=2)
            mimetype = 'application/json'
            filename = 'internship_employment_challenges.json'
        
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"EXPORT ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500