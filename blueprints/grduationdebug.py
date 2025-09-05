# Add this debug function to your backend or run it separately
import pandas as pd
import os

def debug_graduation_data():
    """Debug function to check graduation year data specifically"""
    
    # Load data
    EXCEL_FILE_PATH = 'data/Questionnaire.xlsx'
    
    if not os.path.exists(EXCEL_FILE_PATH):
        print(f"❌ Excel file not found at: {EXCEL_FILE_PATH}")
        return
    
    try:
        df = pd.read_excel(EXCEL_FILE_PATH)
        print(f"✓ Data loaded. Shape: {df.shape}")
    except Exception as e:
        print(f"❌ Error loading Excel: {e}")
        return
    
    print("\n" + "="*50)
    print("GRADUATION YEAR COLUMN DEBUG")
    print("="*50)
    
    # Show all columns
    print(f"Total columns: {len(df.columns)}")
    print("\nAll columns (first 20):")
    for i, col in enumerate(df.columns[:20]):
        print(f"  {i+1:2d}. '{col}'")
    
    # Look for graduation-related columns
    grad_keywords = ['tahun', 'grad', 'year', 'tamat']
    matching_cols = []
    
    for col in df.columns:
        for keyword in grad_keywords:
            if keyword.lower() in col.lower():
                matching_cols.append(col)
                break
    
    print(f"\n📚 Columns containing graduation keywords: {len(matching_cols)}")
    for i, col in enumerate(matching_cols):
        print(f"  {i+1}. '{col}'")
    
    # Check the specific graduation column
    target_col = 'Tahun graduasi anda?'
    print(f"\n🎯 Target column: '{target_col}'")
    
    if target_col in df.columns:
        print("✓ Target column found!")
        
        grad_data = df[target_col]
        total_rows = len(grad_data)
        non_null_rows = grad_data.notna().sum()
        null_rows = grad_data.isna().sum()
        
        print(f"  - Total rows: {total_rows}")
        print(f"  - Non-null rows: {non_null_rows}")
        print(f"  - Null rows: {null_rows}")
        print(f"  - Data coverage: {non_null_rows/total_rows*100:.1f}%")
        
        if non_null_rows > 0:
            # Show sample values
            print(f"\n📋 Sample values (first 10 non-null):")
            sample_values = grad_data.dropna().head(10)
            for i, val in enumerate(sample_values):
                print(f"  {i+1:2d}. '{val}' (type: {type(val).__name__})")
            
            # Show unique values
            unique_values = grad_data.dropna().unique()
            print(f"\n📊 All unique values ({len(unique_values)} total):")
            for i, val in enumerate(sorted(unique_values)):
                print(f"  {i+1:2d}. '{val}' (type: {type(val).__name__})")
            
            # Test processing logic
            print(f"\n🔧 Testing processing logic...")
            processed_years = []
            
            for val in unique_values:
                if pd.notna(val):
                    val_str = str(val).strip()
                    print(f"  Processing: '{val_str}'")
                    
                    # Test different processing approaches
                    if val_str.replace('.', '').replace(',', '').isdigit():
                        try:
                            year = int(float(val_str.replace(',', '')))
                            if 1990 <= year <= 2030:  # Expanded range for testing
                                processed_years.append(year)
                                print(f"    ✓ Extracted year: {year}")
                            else:
                                print(f"    ❌ Year out of range: {year}")
                        except:
                            print(f"    ❌ Could not convert to year")
                    
                    elif '/' in val_str or '-' in val_str:
                        import re
                        years_found = re.findall(r'\b(19|20)\d{2}\b', val_str)
                        if years_found:
                            for year_str in years_found:
                                year = int(year_str)
                                if 1990 <= year <= 2030:
                                    processed_years.append(year)
                                    print(f"    ✓ Extracted from date: {year}")
                        else:
                            print(f"    ❌ No years found in date format")
                    
                    else:
                        print(f"    ❌ Could not process format")
            
            final_years = sorted(list(set(processed_years)))
            print(f"\n🎯 Final processed years: {final_years}")
            print(f"   Count: {len(final_years)} unique years")
            
        else:
            print("❌ No non-null data in graduation column!")
    else:
        print("❌ Target column NOT found!")
        print("\n💡 Searching for similar columns...")
        
        # Fuzzy search for similar columns
        similar_cols = []
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['tahun', 'grad', 'year']):
                similar_cols.append(col)
        
        if similar_cols:
            print("Found similar columns:")
            for col in similar_cols:
                print(f"  - '{col}'")
                sample_data = df[col].dropna().head(3)
                for val in sample_data:
                    print(f"      Sample: '{val}' (type: {type(val).__name__})")
        else:
            print("No similar columns found")
    
    print("\n" + "="*50)
    print("DEBUG COMPLETE")
    print("="*50)

# Run the debug
if __name__ == "__main__":
    debug_graduation_data()