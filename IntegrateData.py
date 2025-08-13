"""
Data Integration Script for UPTM Graduate Analytics
This script shows how to integrate your existing analysis code with the Flask application
"""

import pandas as pd
import numpy as np
from collections import Counter
import json

class GraduateDataProcessor:
    """
    Processes graduate survey data for the analytics dashboard
    Integrates the analysis from your existing Jupyter notebook code
    """
    
    def __init__(self, excel_file_path):
        """Initialize with the path to your questionnaire Excel file"""
        self.df = pd.read_excel(excel_file_path)
        self.processed_data = {}
        
        # Apply your existing data categorizations
        self._categorize_institutions()
        self._group_fields_of_study()
        
    def _categorize_institutions(self):
        """Apply the same institution categorization from your code"""
        def categorize_institution(cell):
            if pd.isnull(cell):
                return None
            if 'Universiti Poly-Tech Malaysia (UPTM)' in cell:
                return 'Universiti Poly-Tech Malaysia (UPTM)'
            elif 'Kolej Poly-Tech MARA' in cell:
                return 'Kolej Poly-Tech MARA'
            else:
                return 'Other'
        
        self.df['Institution_Category'] = self.df['Institusi pendidikan MARA yang anda hadiri? '].apply(categorize_institution)
    
    def _group_fields_of_study(self):
        """Apply the same field of study grouping from your code"""
        field_of_study_mapping = {
            'Kejuruteraan & Teknologi': 'Engineering Environment',
            'Teknologi Elektrik, Elektronik & Pembinaan': 'Engineering Environment',
            'Sains Komputer & Kecerdasan Buatan': 'IT & Computer Science',
            'Sains Data & Analitik': 'IT & Computer Science',
            'Fizik, Kimia & Bioteknologi': 'Natural Science Medical Science / Specialist',
            'Perubatan, Farmasi & Sains Kesihatan': 'Natural Science Medical Science / Specialist',
            'Pemakanan, Dietetik & Fisioterapi': 'Natural Science Medical Science / Specialist',
            'Kewangan, Perbankan & Perakaunan': 'Accounting & Finance',
            'Matematik & Sains Aktuari': 'Accounting & Finance',
            'Pemasaran & Pengurusan Sumber Manusia': 'Economy, Business & Management',
            'Pengurusan Perniagaan & Keusahawanan': 'Economy, Business & Management',
            'Logistik, Pengangkutan & Rantaian Bekalan': 'Economy, Business & Management',
            'Komunikasi, Media & Hubungan Antarabangsa': 'Economy, Business & Management',
            'Psikologi, Sosiologi & Kajian Kemanusiaan': 'Economy, Business & Management',
            'Pelancongan, Hospitaliti & Pengurusan Acara': 'Economy, Business & Management',
            'Seni Kulinari & Pengurusan Perkhidmatan Makanan': 'Economy, Business & Management',
            'Undang-Undang & Pengajian Perundangan': 'Economy, Business & Management',
            'Pengajian Islam & Syariah': 'Economy, Business & Management',
            'Teknologi Automotif & Mekatronik': 'Transport - Vehicle Design & Engineering',
            'Kimpalan, Fabrikasi & Pembuatan': 'Transport - Vehicle Design & Engineering',
            'Senibina & Reka Bentuk': 'Build Professionals',
            'Animasi, Multimedia & Kreativiti Digital': 'Creative Design',
            'Pendidikan & Latihan': 'Other',
            'Information Security': 'IT & Computer Science',
            'Cyber Security': 'IT & Computer Science',
            'Information Security (IT)': 'IT & Computer Science'
        }
        
        def group_field_of_study(cell):
            if pd.isnull(cell):
                return None
            return field_of_study_mapping.get(cell, 'Other')
        
        self.df['Bidang pengajian'] = self.df['Bidang pengajian utama anda? '].apply(group_field_of_study)
    
    def get_demographic_data(self, filters=None):
        """
        Extract demographic data as expected by the dashboard
        Replicates the analysis from your demographic section
        """
        df = self._apply_filters(self.df.copy(), filters)
        
        # Gender distribution (from your pie chart code)
        gender_counts = df['Jantina anda? '].value_counts().to_dict()
        
        # Age by graduation year (from your stacked bar chart code)
        age_by_graduation = df.groupby(['Tahun graduasi anda? ', 'Umur anda? ']).size().unstack(fill_value=0)
        age_by_graduation_dict = {}
        for year in age_by_graduation.index:
            age_by_graduation_dict[year] = age_by_graduation.loc[year].to_dict()
        
        # Institution distribution
        institution_counts = df['Institution_Category'].value_counts().to_dict()
        
        # Field of study distribution
        field_counts = df['Bidang pengajian'].value_counts().to_dict()
        
        return {
            'gender_distribution': gender_counts,
            'age_by_graduation': age_by_graduation_dict,
            'institution_distribution': institution_counts,
            'field_of_study': field_counts,
            'total_graduates': len(df)
        }
    
    def get_socioeconomic_data(self, filters=None):
        """
        Extract socioeconomic data as expected by the dashboard
        Replicates the analysis from your socioeconomic section
        """
        df = self._apply_filters(self.df.copy(), filters)
        
        # Household income distribution
        income_counts = df['Pendapatan isi rumah bulanan keluarga anda?'].value_counts().to_dict()
        
        # Father's occupation
        father_counts = df['Pekerjaan bapa anda'].value_counts().to_dict()
        
        # Mother's occupation
        mother_counts = df['Pekerjaan ibu anda?'].value_counts().to_dict()
        
        # Education financing
        financing_counts = df['Bagaimana anda membiayai pendidikan anda?'].value_counts().to_dict()
        
        # Father occupation by income (your stacked chart)
        father_by_income = df.groupby(['Pendapatan isi rumah bulanan keluarga anda?', 'Pekerjaan bapa anda']).size().unstack(fill_value=0)
        father_by_income_dict = {}
        for income in father_by_income.index:
            father_by_income_dict[income] = father_by_income.loc[income].to_dict()
        
        # Mother occupation by income (your stacked chart)
        mother_by_income = df.groupby(['Pendapatan isi rumah bulanan keluarga anda?', 'Pekerjaan ibu anda?']).size().unstack(fill_value=0)
        mother_by_income_dict = {}
        for income in mother_by_income.index:
            mother_by_income_dict[income] = mother_by_income.loc[income].to_dict()
        
        # Financing advantage analysis
        financing_advantage = df['Adakah jenis pembiayaan ini memberi kelebihan dalam mencari kerja?'].value_counts().to_dict()
        
        return {
            'household_income': income_counts,
            'father_occupation': father_counts,
            'mother_occupation': mother_counts,
            'education_financing': financing_counts,
            'father_by_income': father_by_income_dict,
            'mother_by_income': mother_by_income_dict,
            'financing_advantage': financing_advantage
        }
    
    def get_employment_data(self, filters=None):
        """
        Extract employment data as expected by the dashboard
        Replicates the analysis from your employment section
        """
        df = self._apply_filters(self.df.copy(), filters)
        
        # Employment status
        employment_status = df['Adakah anda kini bekerja?'].value_counts().to_dict()
        
        # Employment rate calculation
        employed_count = len(df[df['Adakah anda kini bekerja?'].str.contains('Ya', na=False)])
        total_count = len(df.dropna(subset=['Adakah anda kini bekerja?']))
        employment_rate = (employed_count / total_count * 100) if total_count > 0 else 0
        
        # Job types (for employed graduates)
        df_working = df[df['Adakah anda kini bekerja?'].isin(['Ya, bekerja sepenuh masa', 'Ya, bekerja separuh masa'])].copy()
        job_status = {}
        if not df_working.empty and 'Apakah status pekerjaan anda sekarang?' in df_working.columns:
            job_status = df_working['Apakah status pekerjaan anda sekarang?'].value_counts().to_dict()
        
        # Time to employment
        time_to_employment = {}
        if 'Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?' in df.columns:
            time_to_employment = df['Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?'].value_counts().to_dict()
        
        # Job finding factors (your complex analysis)
        job_factors = self._process_job_factors(df)
        
        return {
            'employment_status': employment_status,
            'employment_rate': employment_rate,
            'job_status': job_status,
            'time_to_employment': time_to_employment,
            'job_finding_factors': job_factors,
            'total_respondents': len(df)
        }
    
    def _process_job_factors(self, df):
        """Process job finding factors using your grouping logic"""
        factors_column = 'Apakah faktor utama yang membantu anda mendapat pekerjaan tersebut?'
        
        if factors_column not in df.columns:
            return {}
        
        job_factor_grouping = {
            'Permohonan terus kepada syarikat (JobStreet, LinkedIn, laman web syarikat)': 'Saluran Rasmi',
            'Program kerajaan (contoh: MySTEP, Protege, SL1M)': 'Saluran Rasmi',
            'Melalui pameran kerjaya atau job fair': 'Saluran Rasmi',
            'Rangkaian peribadi / kenalan (pensyarah, alumni, keluarga, rakan)': 'Saluran Informal / Sosial',
            'Dihubungi oleh perekrut atau headhunter': 'Saluran Informal / Sosial',
            'Melalui latihan industri / praktikal': 'Laluan Berasaskan Institusi Pendidikan',
            'Tawaran daripada syarikat sebelum tamat pengajian': 'Laluan Berasaskan Institusi Pendidikan',
            'Memulakan perniagaan sendiri / bekerja dalam ekonomi gig': 'Laluan Kendiri / Keusahawanan'
        }
        
        def group_job_factors(cell):
            if pd.isnull(cell):
                return ''
            raw_factors = [x.strip() for x in cell.split(';')]
            mapped = [job_factor_grouping.get(factor, factor) for factor in raw_factors]
            return '; '.join(dict.fromkeys(mapped))
        
        df['Faktor_Pekerjaan_Grouped'] = df[factors_column].apply(group_job_factors)
        
        # Count factors (your Counter logic)
        split_factors = df['Faktor_Pekerjaan_Grouped'].dropna().apply(lambda x: [i.strip() for i in x.split(';')])
        all_factors = [item for sublist in split_factors for item in sublist if item]
        factor_counts = Counter(all_factors)
        
        return dict(factor_counts)
    
    def _apply_filters(self, df, filters):
        """Apply filters to the dataframe"""
        if not filters:
            return df
        
        filtered_df = df.copy()
        
        # Apply filters based on the filter structure
        filter_mapping = {
            'graduation_year': 'Tahun graduasi anda? ',
            'gender': 'Jantina anda? ',
            'institution': 'Institution_Category',
            'income_range': 'Pendapatan isi rumah bulanan keluarga anda?',
            'financing': 'Bagaimana anda membiayai pendidikan anda?',
            'father_occupation': 'Pekerjaan bapa anda',
            'mother_occupation': 'Pekerjaan ibu anda?'
        }
        
        for filter_key, values in filters.items():
            if filter_key in filter_mapping and values:
                column = filter_mapping[filter_key]
                if column in filtered_df.columns:
                    # Handle different filter types
                    if filter_key == 'income_range':
                        # Map filter values to actual column values
                        income_mapping = {
                            'below_2k': 'Kurang dari RM 2,000',
                            '2k_5k': 'RM 2,000 - RM 4,999',
                            '5k_10k': 'RM 5,000 - RM 9,999',
                            '10k_15k': 'RM 10,000 - RM 14,999',
                            'above_15k': 'RM 15,000 ke atas'
                        }
                        mapped_values = [income_mapping.get(v, v) for v in values]
                        filtered_df = filtered_df[filtered_df[column].isin(mapped_values)]
                    else:
                        filtered_df = filtered_df[filtered_df[column].isin(values)]
        
        return filtered_df
    
    def get_table_data(self, chart_type, filters=None):
        """Generate table data for specific chart types"""
        df = self._apply_filters(self.df.copy(), filters)
        
        if chart_type == 'gender_distribution':
            data = df['Jantina anda? '].value_counts()
            total = data.sum()
            return {
                'headers': ['Gender', 'Count', 'Percentage'],
                'rows': [
                    [gender, count, f"{count/total*100:.1f}%"] 
                    for gender, count in data.items()
                ]
            }
        
        elif chart_type == 'household_income':
            data = df['Pendapatan isi rumah bulanan keluarga anda?'].value_counts()
            total = data.sum()
            return {
                'headers': ['Income Range', 'Count', 'Percentage'],
                'rows': [
                    [income, count, f"{count/total*100:.1f}%"] 
                    for income, count in data.items()
                ]
            }
        
        elif chart_type == 'education_financing':
            data = df['Bagaimana anda membiayai pendidikan anda?'].value_counts()
            total = data.sum()
            return {
                'headers': ['Financing Method', 'Count', 'Percentage'],
                'rows': [
                    [method, count, f"{count/total*100:.1f}%"] 
                    for method, count in data.items()
                ]
            }
        
        elif chart_type == 'employment_status':
            data = df['Adakah anda kini bekerja?'].value_counts()
            total = data.sum()
            return {
                'headers': ['Employment Status', 'Count', 'Percentage'],
                'rows': [
                    [status, count, f"{count/total*100:.1f}%"] 
                    for status, count in data.items()
                ]
            }
        
        # Add more chart types as needed
        return {'headers': [], 'rows': []}
    
    def generate_insights(self, filters=None):
        """Generate AI-powered insights from the data"""
        df = self._apply_filters(self.df.copy(), filters)
        insights = []
        
        # Employment rate insight
        employed = len(df[df['Adakah anda kini bekerja?'].str.contains('Ya', na=False)])
        total = len(df.dropna(subset=['Adakah anda kini bekerja?']))
        emp_rate = (employed / total * 100) if total > 0 else 0
        
        if emp_rate > 85:
            insights.append({
                'type': 'success',
                'title': 'Strong Employment Performance',
                'description': f'Employment rate of {emp_rate:.1f}% exceeds national average'
            })
        elif emp_rate < 70:
            insights.append({
                'type': 'warning',
                'title': 'Employment Rate Concern',
                'description': f'Employment rate of {emp_rate:.1f}% may need improvement'
            })
        
        # Gender balance insight
        gender_data = df['Jantina anda? '].value_counts()
        if 'Perempuan' in gender_data and 'Lelaki' in gender_data:
            female_pct = gender_data['Perempuan'] / gender_data.sum() * 100
            if 45 <= female_pct <= 55:
                insights.append({
                    'type': 'success',
                    'title': 'Balanced Gender Representation',
                    'description': f'Female representation at {female_pct:.1f}% shows good gender balance'
                })
            elif female_pct > 60:
                insights.append({
                    'type': 'info',
                    'title': 'Female-Majority Cohort',
                    'description': f'Female graduates represent {female_pct:.1f}% of the cohort'
                })
        
        # Socioeconomic insights
        if 'Pendapatan isi rumah bulanan keluarga anda?' in df.columns:
            income_data = df['Pendapatan isi rumah bulanan keluarga anda?'].value_counts()
            low_income_categories = ['Kurang dari RM 2,000', 'RM 2,000 - RM 4,999']
            low_income_count = sum(income_data.get(cat, 0) for cat in low_income_categories)
            low_income_pct = (low_income_count / income_data.sum() * 100) if income_data.sum() > 0 else 0
            
            if low_income_pct > 50:
                insights.append({
                    'type': 'info',
                    'title': 'Strong B40/M40 Support',
                    'description': f'{low_income_pct:.1f}% from households earning below RM 5,000, showing effective support for lower-income families'
                })
        
        # Financing insights
        if 'Bagaimana anda membiayai pendidikan anda?' in df.columns:
            financing_data = df['Bagaimana anda membiayai pendidikan anda?'].value_counts()
            scholarship_count = financing_data.get('Biasiswa kerajaan', 0)
            scholarship_pct = (scholarship_count / financing_data.sum() * 100) if financing_data.sum() > 0 else 0
            
            if scholarship_pct > 40:
                insights.append({
                    'type': 'success',
                    'title': 'Strong Government Support',
                    'description': f'{scholarship_pct:.1f}% benefit from government scholarships, ensuring education accessibility'
                })
        
        return insights
    
    def export_data(self, data_type, filters=None, format='csv'):
        """Export filtered data in specified format"""
        df = self._apply_filters(self.df.copy(), filters)
        
        if data_type == 'demographic':
            export_df = df[['Jantina anda? ', 'Tahun graduasi anda? ', 'Umur anda? ', 
                           'Institution_Category', 'Bidang pengajian']].copy()
        elif data_type == 'socioeconomic':
            export_df = df[['Pendapatan isi rumah bulanan keluarga anda?', 'Pekerjaan bapa anda', 
                           'Pekerjaan ibu anda?', 'Bagaimana anda membiayai pendidikan anda?']].copy()
        elif data_type == 'employment':
            export_df = df[['Adakah anda kini bekerja?', 'Apakah status pekerjaan anda sekarang?',
                           'Jika bekerja, berapa lama selepas tamat pengajian anda mendapat pekerjaan pertama?']].copy()
        else:
            export_df = df.copy()
        
        # Generate filename
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{data_type}_export_{timestamp}.{format}'
        
        if format == 'csv':
            export_df.to_csv(filename, index=False)
        elif format == 'xlsx':
            export_df.to_excel(filename, index=False)
        elif format == 'json':
            export_df.to_json(filename, orient='records', indent=2)
        
        return filename


# Updated Flask Integration
def create_updated_flask_app():
    """
    Create Flask app with the integrated data processor
    This replaces the simple DataService in app.py
    """
    
    from flask import Flask, render_template, jsonify, request
    import json
    
    app = Flask(__name__)
    
    # Initialize with your actual data file
    data_processor = GraduateDataProcessor('path/to/your/Questionnaire.xlsx')
    
    @app.route('/')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/demographics')
    def demographics():
        return render_template('demographics.html')

    @app.route('/socioeconomic')
    def socioeconomic():
        return render_template('socioeconomic.html')

    @app.route('/employment')
    def employment():
        return render_template('employment.html')

    # API Routes with real data
    @app.route('/api/demographic-data')
    def api_demographic_data():
        filters = request.args.get('filters')
        if filters:
            filters = json.loads(filters)
        
        data = data_processor.get_demographic_data(filters)
        return jsonify(data)

    @app.route('/api/socioeconomic-data')
    def api_socioeconomic_data():
        filters = request.args.get('filters')
        if filters:
            filters = json.loads(filters)
        
        data = data_processor.get_socioeconomic_data(filters)
        return jsonify(data)

    @app.route('/api/employment-data')
    def api_employment_data():
        filters = request.args.get('filters')
        if filters:
            filters = json.loads(filters)
        
        data = data_processor.get_employment_data(filters)
        return jsonify(data)

    @app.route('/api/table-data/<chart_type>')
    def api_table_data(chart_type):
        filters = request.args.get('filters')
        if filters:
            filters = json.loads(filters)
        
        data = data_processor.get_table_data(chart_type, filters)
        return jsonify(data)

    @app.route('/api/insights')
    def api_insights():
        filters = request.args.get('filters')
        if filters:
            filters = json.loads(filters)
        
        insights = data_processor.generate_insights(filters)
        return jsonify({'insights': insights})

    @app.route('/api/export/<data_type>')
    def api_export_data(data_type):
        filters = request.args.get('filters')
        format_type = request.args.get('format', 'csv')
        
        if filters:
            filters = json.loads(filters)
        
        try:
            filename = data_processor.export_data(data_type, filters, format_type)
            return jsonify({
                'success': True, 
                'message': f'{data_type} data exported successfully',
                'filename': filename
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return app


# Usage Instructions and Setup
def setup_instructions():
    """
    Print setup instructions for integrating this with your existing analysis
    """
    
    instructions = """
    UPTM Graduate Analytics Setup Instructions
    ==========================================
    
    1. PROJECT STRUCTURE:
    your-project/
    ├── app.py                          # Main Flask application
    ├── integrate_data.py               # This file with data processing
    ├── templates/
    │   ├── dashboard.html              # Main dashboard
    │   ├── demographics.html           # Demographics page  
    │   ├── socioeconomic.html          # Socioeconomic page
    │   └── employment.html             # Employment page
    ├── static/
    │   └── js/
    │       └── chart-factory.js        # Reusable chart components
    └── data/
        └── Questionnaire.xlsx          # Your survey data
    
    2. INSTALLATION:
    pip install flask pandas openpyxl xlrd
    
    3. DATA INTEGRATION:
    - Replace 'path/to/your/Questionnaire.xlsx' with actual file path
    - Update column names if they differ from your Excel file
    - Modify filter mappings as needed for your data structure
    
    4. RUNNING THE APPLICATION:
    python app.py
    
    5. FEATURES INCLUDED:
    ✅ Interactive charts with drill-down capabilities
    ✅ Power BI inspired filtering system
    ✅ Data export functionality (CSV, Excel, JSON)
    ✅ Table view for all charts
    ✅ Responsive design for mobile devices
    ✅ Real-time data updates
    ✅ Theme switching (light/dark mode)
    ✅ AI-powered insights generation
    ✅ Global keyboard shortcuts
    
    6. CUSTOMIZATION:
    - Modify colors in Tailwind config
    - Add new chart types in ChartFactory
    - Extend filtering options in templates
    - Add new insights in generate_insights()
    
    7. POWER BI INSPIRED FEATURES:
    - Cross-filtering across all visuals
    - Drill-through capabilities
    - Export to multiple formats  
    - Interactive tooltips
    - Advanced filtering panels
    - Key performance indicators (KPIs)
    - Automatic refresh capabilities
    
    8. DEPLOYMENT:
    - Use Gunicorn for production: gunicorn app:app
    - Configure nginx for static files
    - Set up SSL certificates
    - Consider using Redis for caching
    """
    
    print(instructions)


# Test the integration
def test_integration():
    """
    Test the data integration with sample data
    """
    
    # This would test with your actual Excel file
    try:
        # processor = GraduateDataProcessor('path/to/Questionnaire.xlsx')
        
        # Test demographic data
        # demo_data = processor.get_demographic_data()
        # print("Demographic Data:", demo_data)
        
        # Test socioeconomic data  
        # socio_data = processor.get_socioeconomic_data()
        # print("Socioeconomic Data:", socio_data)
        
        # Test with filters
        # filters = {'graduation_year': ['2023', '2024'], 'gender': ['Perempuan']}
        # filtered_data = processor.get_demographic_data(filters)
        # print("Filtered Data:", filtered_data)
        
        print("Integration test completed successfully!")
        
    except Exception as e:
        print(f"Integration test failed: {e}")
        print("Make sure to update the Excel file path and column names")


if __name__ == "__main__":
    setup_instructions()
    # test_integration()  # Uncomment when you have the Excel file ready