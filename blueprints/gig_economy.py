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
        """Format data for vertical bar charts - compatible with centralized config"""
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

# ===== IMPROVED FILTER PROCESSING =====

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
    
    print(f"=== PROCESSING FILTERS (V2) - GIG ECONOMY ===")
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
    
    print(f"=== APPLYING IMPROVED FILTERS - GIG ECONOMY ===")
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

# ===== END IMPROVED FILTER PROCESSING =====

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

@gig_economy_bp.route('/api/test')
def api_test():
    """Test endpoint to verify the blueprint is working"""
    return jsonify({
        'status': 'success',
        'message': 'Gig Economy API is working',
        'available_columns': list(df.columns) if not df.empty else [],
        'total_records': len(df)
    })

@gig_economy_bp.route('/api/debug-data')
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

@gig_economy_bp.route('/api/summary')
def api_summary():
    """Get summary statistics for gig economy data"""
    try:
        # Use improved filter processing
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
        print(f"=== API SUMMARY DEBUG - GIG ECONOMY ===")
        print(f"Processed filters: {filters}")
        print(f"Filtered DF shape: {filtered_df.shape}")
        print(f"Original DF shape: {df.shape}")
        
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
                
                filtered_df_copy = filtered_df.copy()
                filtered_df_copy['gig_clean'] = filtered_df_copy[gig_column].apply(clean_gig)
                
                # Calculate participation rates
                gig_interested = len(filtered_df_copy[filtered_df_copy['gig_clean'] != 'Tidak Berminat'])
                gig_participation_rate = (gig_interested / total_records) * 100 if total_records > 0 else 0
                
                # Count entrepreneurs specifically
                entrepreneur_count = len(filtered_df_copy[filtered_df_copy['gig_clean'].str.contains('Usahawan', na=False)])
                entrepreneurship_rate = (entrepreneur_count / total_records) * 100 if total_records > 0 else 0
                
                gig_stats['gig_participation_rate'] = gig_participation_rate
                gig_stats['gig_participation_count'] = gig_interested
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
        enhanced_stats = {
            'total_records': total_records,
            'gig_participation_rate': round(gig_stats.get('gig_participation_rate', 0), 1),
            'gig_participation_count': gig_stats.get('gig_participation_count', 0),
            'entrepreneurship_rate': round(gig_stats.get('entrepreneurship_rate', 0), 1),
            'university_support_rate': round(gig_stats.get('university_support_rate', 0), 1),
            'avg_income': gig_stats.get('avg_income', 'RM0'),
            'job_preference_rate': round(gig_stats.get('job_preference_rate', 0), 1),
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
            'gig_participation_rate': 0,
            'gig_participation_count': 0,
            'entrepreneurship_rate': 0,
            'university_support_rate': 0,
            'avg_income': 'RM0',
            'job_preference_rate': 0
        }), 500

@gig_economy_bp.route('/api/gig-types')
def api_gig_types():
    """Get gig economy work types data - Returns vertical bar chart data"""
    try:
        # Use improved filter processing
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
        gig_column = 'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?'
        
        if gig_column not in filtered_df.columns:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Data Available']),
                "Gig Economy Types"
            ))
        
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
        
        df_work = filtered_df.copy()
        df_work['gig_clean'] = df_work[gig_column].apply(clean_gig)
        
        # Filter out 'Tidak Berminat'
        df_gig_filtered = df_work[df_work['gig_clean'] != 'Tidak Berminat'].copy()
        
        if df_gig_filtered.empty:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Interested Participants']),
                "Gig Economy Types"
            ))
        
        # Calculate frequency
        all_gigs = []
        for gig_cell in df_gig_filtered['gig_clean'].dropna():
            if pd.notna(gig_cell) and gig_cell.strip():
                gigs = [g.strip() for g in str(gig_cell).split(';') if g.strip()]
                all_gigs.extend(gigs)
        
        if not all_gigs:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Gig Data']),
                "Gig Economy Types"
            ))
        
        gig_counts = pd.Series(all_gigs).value_counts()
        
        # Use centralized formatter for vertical bar chart
        chart_data = formatter.format_bar_chart(
            gig_counts,
            "Gig Economy Types",
            sort_desc=True
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in gig types endpoint: {str(e)}")
        return jsonify(formatter.format_bar_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@gig_economy_bp.route('/api/university-support')
def api_university_support():
    """Get university entrepreneurship support data - Uses 'university-support' color scheme"""
    try:
        # Use improved filter processing
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
        support_column = 'Adakah universiti anda menawarkan kursus atau latihan berkaitan keusahawanan?'
        
        if support_column not in filtered_df.columns:
            return jsonify(formatter.format_pie_chart(
                pd.Series([1], index=['No Data Available']),
                "University Support"
            ))
        
        support_counts = filtered_df[support_column].value_counts()
        
        # Use centralized formatter
        chart_data = formatter.format_pie_chart(
            support_counts,
            "University Entrepreneurship Support"
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in university support endpoint: {str(e)}")
        return jsonify(formatter.format_pie_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@gig_economy_bp.route('/api/university-programs')
def api_university_programs():
    """Get university business programs data - Uses 'university-programs' color scheme"""
    try:
        # Use improved filter processing
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
        programs_column = 'Adakah universiti anda pernah menganjurkan program berkaitan perniagaan atau ekonomi gig seperti hackathon, bootcamp, atau geran permulaan perniagaan?'
        
        if programs_column not in filtered_df.columns:
            return jsonify(formatter.format_pie_chart(
                pd.Series([1], index=['No Data Available']),
                "University Programs"
            ))
        
        programs_counts = filtered_df[programs_column].value_counts()
        
        # Use centralized formatter
        chart_data = formatter.format_pie_chart(
            programs_counts,
            "University Business Programs"
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in university programs endpoint: {str(e)}")
        return jsonify(formatter.format_pie_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@gig_economy_bp.route('/api/program-effectiveness')
def api_program_effectiveness():
    """Get program effectiveness data - Uses 'program-effectiveness' color scheme"""
    try:
        # Use improved filter processing
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
        programs_column = 'Adakah universiti anda pernah menganjurkan program berkaitan perniagaan atau ekonomi gig seperti hackathon, bootcamp, atau geran permulaan perniagaan?'
        effectiveness_column = 'Adakah program berkaitan perniagaan atau ekonomi gig di universiti membantu anda dalam memulakan atau mengembangkan pekerjaan bebas anda?'
        
        # Filter out those who didn't hear about programs
        df_filtered = filtered_df[
            filtered_df[programs_column] != 'Tidak, saya tidak pernah dengar tentang program seperti ini.'
        ].copy()
        
        if df_filtered.empty or effectiveness_column not in df_filtered.columns:
            return jsonify(formatter.format_pie_chart(
                pd.Series([1], index=['No Relevant Data']),
                "Program Effectiveness"
            ))
        
        effectiveness_counts = df_filtered[effectiveness_column].value_counts()
        
        # Use centralized formatter
        chart_data = formatter.format_pie_chart(
            effectiveness_counts,
            "Program Effectiveness"
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in program effectiveness endpoint: {str(e)}")
        return jsonify(formatter.format_pie_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@gig_economy_bp.route('/api/gig-motivations')
def api_gig_motivations():
    """Get gig economy motivations data - Returns vertical bar chart data"""
    try:
        # Use improved filter processing
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
        # Try both possible column names
        motivations_columns = [
            'Apakah sebab utama anda memilih untuk bekerja dalam ekonomi gig? ',
            'Apakah sebab utama anda memilih untuk bekerja dalam ekonomi gig?'
        ]
        
        motivations_column = None
        for col in motivations_columns:
            if col in filtered_df.columns:
                motivations_column = col
                break
        
        if motivations_column is None:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['Column not found']),
                "Gig Motivations"
            ))
        
        # Get all non-null values first
        all_responses = filtered_df[motivations_column].dropna()
        
        if all_responses.empty:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No responses in column']),
                "Gig Motivations"
            ))
        
        # Process all responses, including those with "Tidak relevan"
        all_motivations = []
        for motivations_cell in all_responses:
            if pd.notna(motivations_cell) and str(motivations_cell).strip():
                # Split by comma and clean each motivation
                motivations = [m.strip() for m in str(motivations_cell).split(',')]
                # Filter out empty strings
                motivations = [m for m in motivations if m and len(m.strip()) > 0]
                all_motivations.extend(motivations)
        
        if not all_motivations:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No motivations found after processing']),
                "Gig Motivations"
            ))
        
        motivations_counts = pd.Series(all_motivations).value_counts()
        
        # Filter out "Tidak relevan" responses
        relevant_motivations = motivations_counts[~motivations_counts.index.str.contains('Tidak relevan', case=False, na=False)]
        
        if relevant_motivations.empty:
            # If all responses are "Tidak relevan", show the original counts for debugging
            top_motivations = motivations_counts.head(5)
        else:
            # Show top 10 relevant motivations
            top_motivations = relevant_motivations.head(10)
        
        # Use centralized formatter for vertical bar chart
        chart_data = formatter.format_bar_chart(
            top_motivations,
            "Gig Economy Motivations",
            sort_desc=True
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in gig motivations endpoint: {str(e)}")
        return jsonify(formatter.format_bar_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@gig_economy_bp.route('/api/skill-acquisition')
def api_skill_acquisition():
    """Get skill acquisition methods data - Returns vertical bar chart data"""
    try:
        # Use improved filter processing
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
        skills_column = 'Bagaimanakah anda memperoleh kemahiran untuk bekerja dalam ekonomi gig?'
        
        if skills_column not in filtered_df.columns:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Data Available']),
                "Skill Acquisition"
            ))
        
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
        
        df_work = filtered_df.copy()
        df_work['skills_acquisition_clean'] = df_work[skills_column].apply(clean_skills_acquisition)
        
        # Calculate frequency
        all_skills = []
        for skills_cell in df_work['skills_acquisition_clean'].dropna():
            if pd.notna(skills_cell) and skills_cell.strip():
                skills = [s.strip() for s in str(skills_cell).split(';') if s.strip()]
                all_skills.extend(skills)
        
        if not all_skills:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Skills Data']),
                "Skill Acquisition"
            ))
        
        skills_counts = pd.Series(all_skills).value_counts()
        
        # Use centralized formatter for vertical bar chart
        chart_data = formatter.format_bar_chart(
            skills_counts,
            "Skill Acquisition Methods",
            sort_desc=True
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in skill acquisition endpoint: {str(e)}")
        return jsonify(formatter.format_bar_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@gig_economy_bp.route('/api/gig-challenges')
def api_gig_challenges():
    """Get gig economy challenges data - Returns vertical bar chart data"""
    try:
        # Use improved filter processing
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
        challenges_column = 'Apakah cabaran utama yang anda hadapi dalam keusahawanan atau ekonomi gig?'
        
        if challenges_column not in filtered_df.columns:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Data Available']),
                "Gig Challenges"
            ))
        
        # Process comma-separated challenges
        all_challenges = []
        for challenges_cell in filtered_df[challenges_column].dropna():
            if pd.notna(challenges_cell):
                challenges = [c.strip() for c in str(challenges_cell).split(',')]
                challenges = [c for c in challenges if c]
                all_challenges.extend(challenges)
        
        if not all_challenges:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Challenges Data']),
                "Gig Challenges"
            ))
        
        challenges_counts = pd.Series(all_challenges).value_counts()
        
        # Use centralized formatter for vertical bar chart
        chart_data = formatter.format_bar_chart(
            challenges_counts,
            "Gig Economy Challenges",
            sort_desc=True
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in gig challenges endpoint: {str(e)}")
        return jsonify(formatter.format_bar_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@gig_economy_bp.route('/api/support-needed')
def api_support_needed():
    """Get support needed data - Returns vertical bar chart data"""
    try:
        # Use improved filter processing
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
        support_column = 'Apakah bantuan atau sokongan yang anda rasa perlu untuk berjaya dalam keusahawanan dan ekonomi gig?'
        
        if support_column not in filtered_df.columns:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Data Available']),
                "Support Needed"
            ))
        
        # Categorization mapping for support needs
        support_categories = {
            'Latihan teknikal spesifik': [
                'latihan teknikal',
                'latihan kemahiran',
                'kursus profesional',
                'teknikal dalam bidang',
                'kemahiran khusus',
                'latihan praktis'
            ],
            'Bimbingan kewangan dan cukai': [
                'panduan menguruskan kewangan',
                'nasihat cukai',
                'bimbingan kewangan',
                'pengurusan kewangan',
                'panduan cukai',
                'bantuan kewangan',
                'pengurusan wang'
            ],
            'Platform khas graduan MARA': [
                'platform',
                'direktori',
                'graduan MARA',
                'rangkaian graduan',
                'network graduan',
                'komuniti MARA'
            ],
            'Pinjaman/geran untuk gig': [
                'modal permulaan',
                'pinjaman',
                'geran',
                'perniagaan',
                'startup',
                'dana permulaan',
                'pembiayaan',
                'modal awal'
            ],
            'Perlindungan sosial (KWSP, PERKESO, insurans)': [
                'perlindungan sosial',
                'kwsp',
                'perkeso',
                'insurans',
                'insurance',
                'jaminan sosial',
                'perlindungan pekerja',
                'benefit',
                'kesihatan'
            ]
        }
        
        # Process comma-separated support needs with categorization
        all_support = []
        uncategorized_items = []  # For debugging
        
        for support_cell in filtered_df[support_column].dropna():
            if pd.notna(support_cell):
                support_items = [s.strip() for s in str(support_cell).split(',')]
                
                for item in support_items:
                    if not item or 'tidak relevan' in item.lower():
                        continue
                    
                    # Try to categorize
                    categorized = False
                    item_lower = item.lower()
                    
                    for category, keywords in support_categories.items():
                        # Check if any keyword matches
                        if any(keyword in item_lower for keyword in keywords):
                            all_support.append(category)
                            categorized = True
                            break
                    
                    # If not categorized, add to Lain-lain
                    if not categorized:
                        all_support.append('Lain-lain')
                        uncategorized_items.append(item)
        
        # Print uncategorized items for debugging
        if uncategorized_items:
            print(f"Uncategorized support items ({len(uncategorized_items)}): {set(uncategorized_items)}")
        
        if not all_support:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No Support Data']),
                "Support Needed"
            ))
        
        support_counts = pd.Series(all_support).value_counts()
        
        # Use centralized formatter for vertical bar chart
        chart_data = formatter.format_bar_chart(
            support_counts,
            "Support Needed",
            sort_desc=True
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in support needed endpoint: {str(e)}")
        return jsonify(formatter.format_bar_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@gig_economy_bp.route('/api/monthly-income')
def api_monthly_income():
    """Get monthly income from gig economy data - Returns vertical bar chart data"""
    try:
        # Use improved filter processing
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
        # Try multiple possible column names
        income_columns = [
            'Berapakah purata pendapatan bulan anda daripada ekonomi gig?',
            'Berapakah purata pendapatan bulanan anda daripada ekonomi gig?',
            'Purata pendapatan bulanan dari ekonomi gig',
            'Pendapatan bulanan ekonomi gig'
        ]
        
        income_column = None
        for col in income_columns:
            if col in filtered_df.columns:
                income_column = col
                break
        
        if income_column is None:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['Column not found']),
                "Monthly Income"
            ))
        
        # Get all non-null values
        all_income_data = filtered_df[income_column].dropna()
        
        if all_income_data.empty:
            return jsonify(formatter.format_bar_chart(
                pd.Series([1], index=['No income data found']),
                "Monthly Income"
            ))
        
        # Filter out 'Tidak relevan' and similar responses
        df_income_filtered = all_income_data[
            ~all_income_data.str.contains('Tidak relevan', na=False, case=False)
        ]
        
        if df_income_filtered.empty:
            # If no relevant data, show sample of what we have for debugging
            sample_responses = all_income_data.value_counts().head(3)
            chart_data = formatter.format_bar_chart(
                sample_responses,
                "Income Data (including non-relevant)",
                sort_desc=True
            )
            return jsonify(chart_data)
        
        income_counts = df_income_filtered.value_counts()
        
        # Use centralized formatter for vertical bar chart (keep logical order for income)
        chart_data = formatter.format_bar_chart(
            income_counts,
            "Monthly Income from Gig Economy",
            sort_desc=False  # Keep income in logical order, not by count
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in monthly income endpoint: {str(e)}")
        return jsonify(formatter.format_bar_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

@gig_economy_bp.route('/api/job-preference')
def api_job_preference():
    """Get job preference data - Uses 'job-preference' color scheme"""
    try:
        # Use improved filter processing
        filters = process_filters_with_conversion_v2(request.args)
        filtered_df = apply_improved_filters(df, filters)
        
        preference_column = 'Jika diberikan peluang pekerjaan tetap dengan gaji setanding ekonomi gig, adakah anda akan menerimanya?'
        
        if preference_column not in filtered_df.columns:
            return jsonify(formatter.format_pie_chart(
                pd.Series([1], index=['No Data Available']),
                "Job Preference"
            ))
        
        # Filter out 'Tidak relevan'
        df_preference_filtered = filtered_df[
            filtered_df[preference_column] != 'Tidak relevan'
        ].copy()
        
        if df_preference_filtered.empty:
            return jsonify(formatter.format_pie_chart(
                pd.Series([1], index=['No Relevant Data']),
                "Job Preference"
            ))
        
        preference_counts = df_preference_filtered[preference_column].value_counts()
        
        # Use centralized formatter
        chart_data = formatter.format_pie_chart(
            preference_counts,
            "Job Preference: Permanent vs Gig"
        )
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in job preference endpoint: {str(e)}")
        return jsonify(formatter.format_pie_chart(
            pd.Series([1], index=['Error Loading Data']),
            "Error"
        )), 500

# Chart-specific table data endpoints
@gig_economy_bp.route('/api/chart-table-data/<chart_type>')
def api_chart_table_data(chart_type):
    """Get table data specific to each chart type"""
    try:
        # Use improved filter processing
        filters = process_filters_with_conversion_v2(
            request.args, 
            exclude_keys=['page', 'per_page', 'search']
        )
        filtered_df = apply_improved_filters(df, filters)
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 100))
        search = request.args.get('search', '')
        
        # Define chart-specific columns
        chart_columns = {
            'gig-types': [
                'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?',
                'Tahun graduasi anda?',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?',
                'Program pengajian yang anda ikuti?'
            ],
            'gig-motivations': [
                'Apakah sebab utama anda memilih untuk bekerja dalam ekonomi gig? ',
                'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?',
                'Tahun graduasi anda?',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?'
            ],
            'university-support': [
                'Adakah universiti anda menawarkan kursus atau latihan berkaitan keusahawanan?',
                'Tahun graduasi anda?',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?',
                'Program pengajian yang anda ikuti?'
            ],
            'university-programs': [
                'Adakah universiti anda pernah menganjurkan program berkaitan perniagaan atau ekonomi gig seperti hackathon, bootcamp, atau geran permulaan perniagaan?',
                'Tahun graduasi anda?',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?'
            ],
            'program-effectiveness': [
                'Adakah program berkaitan perniagaan atau ekonomi gig di universiti membantu anda dalam memulakan atau mengembangkan pekerjaan bebas anda?',
                'Adakah universiti anda pernah menganjurkan program berkaitan perniagaan atau ekonomi gig seperti hackathon, bootcamp, atau geran permulaan perniagaan?',
                'Tahun graduasi anda?',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?'
            ],
            'skill-acquisition': [
                'Bagaimanakah anda memperoleh kemahiran untuk bekerja dalam ekonomi gig?',
                'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?',
                'Tahun graduasi anda?',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?'
            ],
            'gig-challenges': [
                'Apakah cabaran utama yang anda hadapi dalam keusahawanan atau ekonomi gig?',
                'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?',
                'Tahun graduasi anda?',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?'
            ],
            'support-needed': [
                'Apakah bantuan atau sokongan yang anda rasa perlu untuk berjaya dalam keusahawanan dan ekonomi gig?',
                'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?',
                'Tahun graduasi anda?',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?'
            ],
            'monthly-income': [
                'Berapakah purata pendapatan bulan anda daripada ekonomi gig?',
                'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?',
                'Tahun graduasi anda?',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?'
            ],
            'job-preference': [
                'Jika diberikan peluang pekerjaan tetap dengan gaji setanding ekonomi gig, adakah anda akan menerimanya?',
                'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?',
                'Tahun graduasi anda?',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?'
            ]
        }
        
        # Get columns for this chart type
        relevant_columns = chart_columns.get(chart_type, [])
        available_columns = [col for col in relevant_columns if col in filtered_df.columns]
        
        if not available_columns:
            # Fallback to common columns
            fallback_columns = [
                'Tahun graduasi anda?',
                'Jantina anda?',
                'Institusi pendidikan MARA yang anda hadiri?'
            ]
            available_columns = [col for col in fallback_columns if col in filtered_df.columns]
        
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
            'pagination': {'page': 1, 'per_page': 100, 'total': 0, 'pages': 0},
            'columns': []
        }), 500

@gig_economy_bp.route('/api/table-data')
def api_table_data():
    """Get paginated table data for gig economy"""
    try:
        # Use improved filter processing
        filters = process_filters_with_conversion_v2(
            request.args,
            exclude_keys=['page', 'per_page', 'search']
        )
        filtered_df = apply_improved_filters(df, filters)
        
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
        
        available_columns = [col for col in relevant_columns if col in filtered_df.columns]
        
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
        print(f"Error in table data: {str(e)}")
        import traceback
        print(traceback.format_exc())
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
        # Use improved filter processing
        filters = process_filters_with_conversion_v2(
            request.args,
            exclude_keys=['format', 'chart_type']
        )
        filtered_df = apply_improved_filters(df, filters)
        
        format_type = request.args.get('format', 'csv')
        chart_type = request.args.get('chart_type')
        
        # Use chart-specific columns if chart_type is provided
        if chart_type:
            chart_columns = {
                'gig-types': [
                    'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?',
                    'Tahun graduasi anda?',
                    'Jantina anda?',
                    'Institusi pendidikan MARA yang anda hadiri?'
                ],
                'gig-motivations': [
                    'Apakah sebab utama anda memilih untuk bekerja dalam ekonomi gig? ',
                    'Apakah bentuk pekerjaan bebas yang anda ceburi sekarang atau bercadang untuk ceburi dalam masa terdekat?',
                    'Tahun graduasi anda?',
                    'Jantina anda?'
                ],
                'university-support': [
                    'Adakah universiti anda menawarkan kursus atau latihan berkaitan keusahawanan?',
                    'Tahun graduasi anda?',
                    'Jantina anda?',
                    'Institusi pendidikan MARA yang anda hadiri?'
                ],
                'university-programs': [
                    'Adakah universiti anda pernah menganjurkan program berkaitan perniagaan atau ekonomi gig seperti hackathon, bootcamp, atau geran permulaan perniagaan?',
                    'Tahun graduasi anda?',
                    'Jantina anda?',
                    'Institusi pendidikan MARA yang anda hadiri?'
                ],
                'program-effectiveness': [
                    'Adakah program berkaitan perniagaan atau ekonomi gig di universiti membantu anda dalam memulakan atau mengembangkan pekerjaan bebas anda?',
                    'Adakah universiti anda pernah menganjurkan program berkaitan perniagaan atau ekonomi gig seperti hackathon, bootcamp, atau geran permulaan perniagaan?',
                    'Tahun graduasi anda?',
                    'Jantina anda?'
                ],
                'skill-acquisition': [
                    'Bagaimanakah anda memperoleh kemahiran untuk bekerja dalam ekonomi gig?',
                    'Tahun graduasi anda?',
                    'Jantina anda?',
                    'Institusi pendidikan MARA yang anda hadiri?'
                ],
                'gig-challenges': [
                    'Apakah cabaran utama yang anda hadapi dalam keusahawanan atau ekonomi gig?',
                    'Tahun graduasi anda?',
                    'Jantina anda?',
                    'Institusi pendidikan MARA yang anda hadiri?'
                ],
                'support-needed': [
                    'Apakah bantuan atau sokongan yang anda rasa perlu untuk berjaya dalam keusahawanan dan ekonomi gig?',
                    'Tahun graduasi anda?',
                    'Jantina anda?',
                    'Institusi pendidikan MARA yang anda hadiri?'
                ],
                'monthly-income': [
                    'Berapakah purata pendapatan bulan anda daripada ekonomi gig?',
                    'Tahun graduasi anda?',
                    'Jantina anda?',
                    'Institusi pendidikan MARA yang anda hadiri?'
                ],
                'job-preference': [
                    'Jika diberikan peluang pekerjaan tetap dengan gaji setanding ekonomi gig, adakah anda akan menerimanya?',
                    'Tahun graduasi anda?',
                    'Jantina anda?',
                    'Institusi pendidikan MARA yang anda hadiri?'
                ]
            }
            relevant_columns = chart_columns.get(chart_type, [])
        else:
            # Default columns for general export
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
        
        available_columns = [col for col in relevant_columns if col in filtered_df.columns]
        export_df = filtered_df[available_columns]
        
        # Create export data
        if format_type == 'csv':
            output = io.StringIO()
            export_df.to_csv(output, index=False)
            data = output.getvalue().encode('utf-8')
            mimetype = 'text/csv'
            filename = f'gig_economy_{chart_type or "data"}.csv'
        elif format_type == 'excel':
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Gig Economy Data')
            data = output.getvalue()
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f'gig_economy_{chart_type or "data"}.xlsx'
        else:
            data = export_df.to_json(orient='records', indent=2).encode('utf-8')
            mimetype = 'application/json'
            filename = f'gig_economy_{chart_type or "data"}.json'
        
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

@gig_economy_bp.route('/api/filters/available')
def api_available_filters():
    """Get available filter options for gig economy data"""
    try:
        sample_df = df.copy()
        filters = {}
        
        filter_columns = [
            'Tahun graduasi anda?',
            'Jantina anda?',
            'Institusi pendidikan MARA yang anda hadiri?'
        ]
        
        # Debug: Print all column names to see exact format
        print("Available columns in gig economy dataset:")
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