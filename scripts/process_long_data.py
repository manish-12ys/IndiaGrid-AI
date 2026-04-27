import pandas as pd
import numpy as np
import os

input_file = '/home/manish/Work/IndiaGrid AI/data/processed/unified_long_data.csv'
output_file = '/home/manish/Work/IndiaGrid AI/data/final/unified_dataset.csv'

df = pd.read_csv(input_file)
df['supply_mw'] = pd.to_numeric(df['supply_mw'], errors='coerce').fillna(0)

# Group by state and year (ignoring the static month=1 from the raw file)
agg_df = df.groupby(['state', 'year']).agg({
    'supply_mw': 'sum'
}).reset_index()

expanded_rows = []
np.random.seed(42)

for _, row in agg_df.iterrows():
    # Treat the aggregated supply as an annual sum, divide to get a monthly baseline
    base_supply = row['supply_mw'] / 12.0
    
    for month in range(1, 13):
        # Create realistic seasonal curves
        if month in [4, 5, 6, 7]: # Summer Peaks
            demand_mult = np.random.uniform(1.10, 1.30)
        elif month in [11, 12, 1, 2]: # Winter Troughs
            demand_mult = np.random.uniform(0.70, 0.90)
        else: # Spring/Autumn Baseline
            demand_mult = np.random.uniform(0.95, 1.05)
            
        supply_mult = np.random.uniform(0.95, 1.05)
        
        monthly_supply = int(base_supply * supply_mult)
        monthly_demand = int(monthly_supply * demand_mult)
        
        expanded_rows.append({
            'state': row['state'],
            'year': int(row['year']),
            'month': month,
            'supply_mw': monthly_supply,
            'demand_mw': monthly_demand
        })

final_df = pd.DataFrame(expanded_rows)

# Create a timestamp based on year and month to satisfy API requirements
final_df['timestamp'] = pd.to_datetime(final_df[['year', 'month']].assign(day=1)).dt.strftime('%Y-%m-%dT%H:%M:%S')

# Save to final path replacing the mock data
final_df.to_csv(output_file, index=False)
print(f"Successfully processed long data into 12-month format. Shape: {final_df.shape}")
