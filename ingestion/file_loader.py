import os
import glob
import pandas as pd
from datetime import datetime

# Define standard columns
STANDARD_COLUMNS = ['state', 'year', 'month', 'demand_mw', 'supply_mw', 'source', 'timestamp']

def load_and_standardize_csv(file_path):
    """Loads a CSV file and standardizes its format."""
    try:
        df = pd.read_csv(file_path)
        return _standardize_dataframe(df, file_path)
    except Exception as e:
        print(f"Error loading CSV {file_path}: {e}")
        return None

def load_and_standardize_excel(file_path):
    """Loads an Excel file and standardizes its format."""
    try:
        df = pd.read_excel(file_path)
        return _standardize_dataframe(df, file_path)
    except Exception as e:
        print(f"Error loading Excel {file_path}: {e}")
        return None

def _standardize_dataframe(df, source_name):
    """Applies cleaning rules and standardizes the schema."""
    # 1. Normalize column names (lower case, remove spaces)
    df.columns = [str(c).lower().strip().replace(' ', '_') for c in df.columns]

    # Map possible varying column names to standard ones (basic implementation)
    column_mapping = {
        'state_name': 'state',
        'demand': 'demand_mw',
        'supply': 'supply_mw',
        'power_demand': 'demand_mw',
        'power_supply': 'supply_mw'
    }
    df = df.rename(columns=column_mapping)

    # 2. Add missing standard columns with defaults if necessary
    for col in STANDARD_COLUMNS:
        if col not in df.columns:
            if col == 'source':
                df['source'] = os.path.basename(source_name)
            elif col == 'timestamp':
                df['timestamp'] = datetime.now().isoformat()
            else:
                df[col] = None

    # 3. Keep only standard columns
    df = df[STANDARD_COLUMNS]

    # 4. Cleaning Rules:
    # - Remove nulls & duplicates
    df = df.dropna(subset=['state', 'year', 'month', 'demand_mw', 'supply_mw'])
    df = df.drop_duplicates()

    # - Normalize state names (title case, strip)
    df['state'] = df['state'].astype(str).str.strip().str.title()
    
    # - Ensure numerical types
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['month'] = pd.to_numeric(df['month'], errors='coerce')
    df['demand_mw'] = pd.to_numeric(df['demand_mw'], errors='coerce')
    df['supply_mw'] = pd.to_numeric(df['supply_mw'], errors='coerce')
    
    # Drop any new nulls introduced by conversion
    df = df.dropna()

    return df

def process_all_files(raw_dir, output_file):
    """Processes all raw CSV/Excel files and merges into a final dataset."""
    all_data = []

    # Process CSVs
    csv_files = glob.glob(os.path.join(raw_dir, 'csv', '*.csv'))
    for file in csv_files:
        print(f"Processing CSV: {file}")
        df = load_and_standardize_csv(file)
        if df is not None:
            all_data.append(df)

    # Process Excels
    excel_files = glob.glob(os.path.join(raw_dir, 'excel', '*.xlsx')) + glob.glob(os.path.join(raw_dir, 'excel', '*.xls'))
    for file in excel_files:
        print(f"Processing Excel: {file}")
        df = load_and_standardize_excel(file)
        if df is not None:
            all_data.append(df)

    if not all_data:
        print("No valid data processed.")
        return False

    final_df = pd.concat(all_data, ignore_index=True)
    
    # Save unified dataset
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    final_df.to_csv(output_file, index=False)
    print(f"Successfully saved unified dataset with {len(final_df)} rows to {output_file}")
    return True

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
    FINAL_FILE = os.path.join(BASE_DIR, 'data', 'final', 'unified_dataset.csv')
    process_all_files(RAW_DIR, FINAL_FILE)
