import os
import pandas as pd
import numpy as np

STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
]

def generate_synthetic_data():
    """Generates 2 years of monthly data for each state."""
    data = []
    years = [2022, 2023]
    months = list(range(1, 13))
    
    for state in STATES:
        base_demand = np.random.randint(5000, 20000)
        base_supply = base_demand + np.random.randint(-2000, 2000) # Some surplus, some deficit
        
        for year in years:
            for month in months:
                # Add seasonality: Summer (Apr-Jun) and Post-Monsoon (Sep-Oct) have high demand.
                # Winter (Dec-Feb) has lower demand generally.
                if month in [4, 5, 6]:
                    seasonality_factor = 1.35  # Summer peak
                elif month in [9, 10]:
                    seasonality_factor = 1.15  # Post monsoon peak
                elif month in [12, 1, 2]:
                    seasonality_factor = 0.85  # Winter dip
                else:
                    seasonality_factor = 1.0   # Normal
                
                demand = int(base_demand * seasonality_factor + np.random.randint(-1000, 1000))
                # Supply is usually stable but can dip slightly in summer due to high demand stress
                supply = int(base_supply * (0.95 if month in [4, 5, 6] else 1.0) + np.random.randint(-500, 500)) 
                
                data.append({
                    'state_name': state, # Using non-standard column to test standardizer
                    'year': year,
                    'month': month,
                    'power_demand': demand,
                    'power_supply': supply
                })
                
    df = pd.DataFrame(data)
    
    # Save to raw csv folder
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(base_dir, 'data', 'raw', 'csv', 'mock_historical_data.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Mock data generated at: {output_path}")

if __name__ == "__main__":
    generate_synthetic_data()
