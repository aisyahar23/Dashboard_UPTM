import pandas as pd
import numpy as np
import os  # Add this import
from typing import Dict, List, Optional, Union
from datetime import datetime
import json

class DataProcessor:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.filtered_df = df.copy()
    
    def apply_filters(self, filters: Dict) -> 'DataProcessor':
        """Apply filters and return new instance for method chaining"""
        filtered_df = self.df.copy()
        
        for filter_key, filter_values in filters.items():
            if filter_values and len(filter_values) > 0:
                if filter_key in filtered_df.columns:
                    # Convert filter values to match column data type
                    if filtered_df[filter_key].dtype in ['int64', 'float64']:
                        try:
                            converted_values = [int(float(v)) for v in filter_values]
                            filtered_df = filtered_df[filtered_df[filter_key].isin(converted_values)]
                        except:
                            filtered_df = filtered_df[filtered_df[filter_key].astype(str).isin([str(v) for v in filter_values])]
                    else:
                        filtered_df = filtered_df[filtered_df[filter_key].isin(filter_values)]
        
        new_processor = DataProcessor(filtered_df)
        new_processor.filtered_df = filtered_df
        return new_processor
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics"""
        return {
            'total_records': len(self.filtered_df),
            'columns': list(self.filtered_df.columns),
            'last_updated': datetime.now().isoformat()
        }
    
    def get_chart_data(self, chart_type: str, x_col: str, y_col: str = None, 
                      group_by: str = None) -> Dict:
        """Generic chart data generator"""
        try:
            if chart_type == 'bar':
                return self._get_bar_chart_data(x_col, y_col)
            elif chart_type == 'pie':
                return self._get_pie_chart_data(x_col)
            elif chart_type == 'stacked_bar':
                return self._get_stacked_bar_data(x_col, group_by)
            elif chart_type == 'line':
                return self._get_line_chart_data(x_col, y_col)
        except Exception as e:
            print(f"Error generating chart data: {e}")
            return {'error': str(e), 'labels': ['No Data'], 'datasets': [{'data': [1], 'backgroundColor': '#6b7280'}]}
    
    def _get_bar_chart_data(self, x_col: str, y_col: str = None) -> Dict:
        if x_col not in self.filtered_df.columns:
            return {'labels': ['No Data'], 'datasets': [{'data': [1], 'backgroundColor': '#6b7280'}]}
            
        if y_col and y_col in self.filtered_df.columns:
            grouped = self.filtered_df.groupby(x_col)[y_col].mean()
        else:
            grouped = self.filtered_df[x_col].value_counts().sort_index()
        
        return {
            'labels': [str(label) for label in grouped.index.tolist()],
            'datasets': [{
                'data': grouped.values.tolist(),
                'backgroundColor': '#074e7e',
                'borderColor': '#053a5f',
                'borderWidth': 2,
                'borderRadius': 8,
                'borderSkipped': False
            }]
        }
    
    def _get_pie_chart_data(self, x_col: str) -> Dict:
        if x_col not in self.filtered_df.columns:
            return {'labels': ['No Data'], 'datasets': [{'data': [1], 'backgroundColor': ['#6b7280']}]}
            
        value_counts = self.filtered_df[x_col].value_counts()
        colors = ['#074e7e', '#c92427', '#10b981', '#f59e0b', '#3b82f6', '#6b7280']
        
        return {
            'labels': [str(label) for label in value_counts.index.tolist()],
            'datasets': [{
                'data': value_counts.values.tolist(),
                'backgroundColor': colors[:len(value_counts)],
                'borderWidth': 3,
                'borderColor': '#ffffff'
            }]
        }
    
    def _get_stacked_bar_data(self, x_col: str, group_by: str) -> Dict:
        if x_col not in self.filtered_df.columns or group_by not in self.filtered_df.columns:
            return {'labels': ['No Data'], 'datasets': [{'label': 'No Data', 'data': [1], 'backgroundColor': '#6b7280'}]}
            
        try:
            pivot_data = self.filtered_df.groupby([x_col, group_by]).size().unstack(fill_value=0)
            colors = ['#074e7e', '#c92427', '#10b981', '#f59e0b', '#3b82f6']
            
            datasets = []
            for i, col in enumerate(pivot_data.columns):
                datasets.append({
                    'label': str(col),
                    'data': pivot_data[col].tolist(),
                    'backgroundColor': colors[i % len(colors)],
                    'borderWidth': 0
                })
            
            return {
                'labels': [str(label) for label in pivot_data.index.tolist()],
                'datasets': datasets
            }
        except Exception as e:
            print(f"Error creating stacked bar data: {e}")
            return {'labels': ['No Data'], 'datasets': [{'label': 'No Data', 'data': [1], 'backgroundColor': '#6b7280'}]}
    
    def get_table_data(self, page: int = 1, per_page: int = 50, 
                      search: str = None, columns: List[str] = None) -> Dict:
        """Get paginated table data"""
        df = self.filtered_df.copy()
        
        if columns:
            # Only use columns that exist in the dataframe
            existing_columns = [col for col in columns if col in df.columns]
            if existing_columns:
                df = df[existing_columns]
        
        if search:
            mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
            df = df[mask]
        
        total = len(df)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        paginated_df = df.iloc[start_idx:end_idx]
        
        return {
            'data': paginated_df.to_dict('records'),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page if total > 0 else 0
            },
            'columns': list(df.columns)
        }
    
    def export_data(self, format: str = 'csv', columns: List[str] = None) -> bytes:
        """Export filtered data"""
        df = self.filtered_df.copy()
        
        if columns:
            # Only use columns that exist in the dataframe
            existing_columns = [col for col in columns if col in df.columns]
            if existing_columns:
                df = df[existing_columns]
        
        if format == 'csv':
            return df.to_csv(index=False).encode('utf-8')
        elif format == 'excel':
            import io
            buffer = io.BytesIO()
            df.to_excel(buffer, index=False, engine='openpyxl')
            return buffer.getvalue()
        elif format == 'json':
            return df.to_json(orient='records', indent=2).encode('utf-8')


# Load from Excel file
def load_excel_data(file_path):
    """Load data from Excel file"""
    try:
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            print(f"Loaded {len(df)} records from {file_path}")
            print(f"Columns: {list(df.columns)}")
            return df
        else:
            print(f"Excel file not found: {file_path}. Using sample data.")
            return generate_sample_data()
    except Exception as e:
        print(f"Error loading Excel file: {e}. Using sample data.")
        return generate_sample_data()

def generate_sample_data():
    """Generate sample data as fallback"""
    np.random.seed(42)
    
    sample_data = {
        'Pendapatan isi rumah bulanan keluarga anda?': np.random.choice(
            ['RM 2000-3000', 'RM 3000-4000', 'RM 4000-5000', 'RM 5000-6000', 'RM 6000+'], 300
        ),
        'Pekerjaan bapa anda': np.random.choice(
            ['Penjawat Awam', 'Swasta', 'Berniaga', 'Pencen', 'Lain-lain'], 300
        ),
        'Pekerjaan ibu anda?': np.random.choice(
            ['Suri Rumah', 'Penjawat Awam', 'Swasta', 'Berniaga', 'Pencen'], 300
        ),
        'Bagaimana anda membiayai pendidikan anda?': np.random.choice(
            ['Biasiswa', 'Pinjaman pendidikan', 'Keluarga', 'Sendiri'], 300
        ),
        'Tahun graduasi anda?': np.random.choice([2020, 2021, 2022, 2023, 2024], 300),
        'Jantina anda?': np.random.choice(['Lelaki', 'Perempuan'], 300),
        'Umur anda?': np.random.randint(22, 28, 300),
        'Institusi pendidikan MARA yang anda hadiri?': np.random.choice(
            ['Universiti Poly-Tech Malaysia (UPTM)', 'Kolej Poly-Tech MARA'], 300
        ),
        'Bidang pengajian utama anda?': np.random.choice(
            ['Kejuruteraan', 'Perniagaan', 'IT', 'Seni', 'Sains'], 300
        )
    }
    return pd.DataFrame(sample_data)