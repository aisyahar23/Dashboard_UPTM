import pandas as pd

# Load the Excel file
df = pd.read_excel('data/Questionnaire.xlsx')

# Print all column names
print("All column names:")
for i, col in enumerate(df.columns):
    print(f"{i}: '{col}' (length: {len(col)})")

# Check for graduation year columns specifically
print("\nColumns containing 'graduasi':")
for col in df.columns:
    if 'graduasi' in col.lower():
        print(f"'{col}' - unique values: {df[col].dropna().unique()[:10]}")