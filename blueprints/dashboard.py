from flask import Blueprint, render_template, request, jsonify, send_file
from models.data_processor import DataProcessor, load_excel_data
import io
import os
import pandas as pd
from collections import Counter
import numpy as np

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    """Main  dashboard page"""
    return render_template('dashboard.html')


    """Test endpoint to verify the blueprint is working"""
    try:
        # Debug column names
        all_columns = list(df.columns) if not df.empty else []
        
        # Check for similar column names
        relevant_patterns = ['Tahun', 'Umur', 'Jantina', 'Institusi', 'Bidang']
        matching_columns = {}
        
        for pattern in relevant_patterns:
            matching_columns[pattern] = [col for col in all_columns if pattern.lower() in col.lower()]
        
        return jsonify({
            'status': 'success',
            'message': 'Demografi API is working',
            'total_records': len(df),
            'all_columns': all_columns,
            'matching_columns': matching_columns,
            'sample_data': df.head(2).to_dict('records') if not df.empty else []
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'total_records': 0
        }), 500

    """Get age distribution by graduation year - enhanced-stacked-bar (STANDARDIZED)"""
    try:
        filters = {k: request.args.getlist(k) for k in request.args.keys()}
        filtered_processor = data_processor.apply_filters(filters)
        filtered_df = filtered_processor.filtered_df
        
        # Try multiple possible column names
        year_columns = ['Tahun graduasi anda?', 'Tahun graduasi anda? ', 'Tahun graduasi anda']
        age_columns = ['Umur anda?', 'Umur anda? ', 'Umur anda']
        
        year_column = None
        age_column = None
        
        # Find the correct column names
        for col in year_columns:
            if col in filtered_df.columns:
                year_column = col
                break
                
        for col in age_columns:
            if col in filtered_df.columns:
                age_column = col
                break
        
        print(f"Available columns: {list(filtered_df.columns)}")
        print(f"Year column found: {year_column}")
        print(f"Age column found: {age_column}")
        
        if year_column is None or age_column is None:
            print("Column not found - available columns:", list(filtered_df.columns))
            return jsonify({
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1]
                }]
            })
        
        # Group by graduation year and age (EXACT COLAB REPLICATION)
        grouped_data = filtered_df.groupby([year_column, age_column]).size().unstack(fill_value=0)
        
        print(f"Grouped data shape: {grouped_data.shape}")
        print(f"Grouped data:\n{grouped_data}")
        
        if grouped_data.empty:
            return jsonify({
                'labels': ['No Data'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [1]
                }]
            })
        
        # Prepare datasets for stacked bar chart (STANDARDIZED FORMAT)
        datasets = []
        for age_group in grouped_data.columns:
            datasets.append({
                'label': str(age_group),
                'data': [int(val) for val in grouped_data[age_group].values.tolist()]
            })
        
        chart_data = {
            'labels': [str(label) for label in grouped_data.index.tolist()],
            'datasets': datasets
        }
        
        print(f"Chart data: {chart_data}")
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in age by graduation year endpoint: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'labels': ['Error'],
            'datasets': [{
                'label': 'Error',
                'data': [1]
            }]
        }), 500


    """Get available filter options for demografi data"""
    try:
        sample_df = data_processor.df
        filters = {}
        
        print(f"All available columns: {list(sample_df.columns)}")
        
        # Define multiple possible column names for each filter
        filter_mappings = {
            'graduation_years': ['Tahun graduasi anda?', 'Tahun graduasi anda? ', 'Tahun graduasi anda'],
            'genders': ['Jantina anda?', 'Jantina anda? ', 'Jantina anda'],
            'age_groups': ['Umur anda?', 'Umur anda? ', 'Umur anda'],
            'institutions': ['Institusi pendidikan MARA yang anda hadiri?', 'Institusi pendidikan MARA yang anda hadiri? ', 'Institusi pendidikan MARA yang anda hadiri'],
            'fields_of_study': ['Bidang pengajian utama anda?', 'Bidang pengajian utama anda? ', 'Bidang pengajian utama anda'],
            'programs': ['Program pengajian yang anda ikuti?', 'Program pengajian yang anda ikuti? ', 'Program pengajian yang anda ikuti']
        }
        
        for filter_key, possible_columns in filter_mappings.items():
            found_column = None
            for col in possible_columns:
                if col in sample_df.columns:
                    found_column = col
                    break
            
            if found_column:
                unique_values = sample_df[found_column].dropna().unique().tolist()
                if isinstance(unique_values[0] if unique_values else None, (int, float)):
                    unique_values = sorted(unique_values)
                else:
                    unique_values = sorted([str(val) for val in unique_values])
                filters[filter_key] = unique_values
                print(f"Found {filter_key} in column '{found_column}': {len(unique_values)} values")
            else:
                print(f"Column not found for {filter_key}")
                filters[filter_key] = []
        
        return jsonify(filters)
        
    except Exception as e:
        print(f"Error loading filters: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e), 'filters': {}}), 500