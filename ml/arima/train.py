import os
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error
import json
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'final', 'unified_dataset.csv')
MODEL_OUTPUT_DIR = os.path.join(BASE_DIR, 'ml', 'arima', 'models')

def train_arima_models():
    if not os.path.exists(DATA_FILE):
        print(f"Data file not found at {DATA_FILE}")
        return

    df = pd.read_csv(DATA_FILE)
    states = df['state'].unique()
    
    os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)
    results = []

    for state in states:
        state_df = df[df['state'] == state].copy()
        state_df = state_df.sort_values(by=['year', 'month'])
        
        demand = state_df['demand_mw'].values
        
        if len(demand) < 12:
            continue
            
        try:
            # Train/test split for evaluation
            train_size = int(len(demand) * 0.8)
            train, test = demand[:train_size], demand[train_size:]
            
            model = ARIMA(train, order=(1,1,1))
            model_fit = model.fit()
            predictions = model_fit.forecast(steps=len(test))
            
            mae = mean_absolute_error(test, predictions)
            rmse = np.sqrt(mean_squared_error(test, predictions))
            
            # Forecast next month using all data
            full_model = ARIMA(demand, order=(1,1,1))
            full_fit = full_model.fit()
            forecast = full_fit.forecast(steps=1)[0]
            
            results.append({
                'state': state,
                'predicted_demand_mw': float(forecast),
                'last_actual_demand_mw': float(demand[-1]),
                'mae': float(mae),
                'rmse': float(rmse)
            })
            
        except Exception as e:
            pass
            
    output_file = os.path.join(MODEL_OUTPUT_DIR, 'latest_predictions.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
        
    print(f"Saved latest predictions to {output_file}")

if __name__ == "__main__":
    train_arima_models()
