import os
import pandas as pd
import numpy as np
import json
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'final', 'unified_dataset.csv')
MODEL_OUTPUT_DIR = os.path.join(BASE_DIR, 'ml', 'lstm', 'models')

def create_sequences(data, months, seq_length):
    xs = []
    ys = []
    for i in range(len(data)-seq_length):
        features = list(data[i:(i+seq_length)]) + [months[i+seq_length]]
        xs.append(features)
        ys.append(data[i+seq_length])
    return np.array(xs), np.array(ys)

def train_advanced_models():
    if not os.path.exists(DATA_FILE):
        return

    df = pd.read_csv(DATA_FILE)
    states = df['state'].unique()
    os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)
    results = []

    for state in states:
        state_df = df[df['state'] == state].copy()
        state_df = state_df.sort_values(by=['year', 'month'])
        
        demand = state_df['demand_mw'].values
        months = state_df['month'].values
        
        seq_length = 3
        if len(demand) <= seq_length + 2:
            continue
            
        X, y = create_sequences(demand, months, seq_length)
        
        try:
            train_size = int(len(X) * 0.8)
            X_train, X_test = X[:train_size], X[train_size:]
            y_train, y_test = y[:train_size], y[train_size:]
            
            model = MLPRegressor(hidden_layer_sizes=(50, 50), max_iter=1000, random_state=42)
            model.fit(X_train, y_train)
            
            preds = model.predict(X_test)
            mae = mean_absolute_error(y_test, preds)
            rmse = np.sqrt(mean_squared_error(y_test, preds))
            
            # Predict next
            model.fit(X, y)
            next_month = months[-1] + 1 if months[-1] < 12 else 1
            last_seq = list(demand[-seq_length:]) + [next_month]
            forecast = model.predict([last_seq])[0]
            
            results.append({
                'state': state,
                'predicted_demand_mw': float(forecast),
                'last_actual_demand_mw': float(demand[-1]),
                'mae': float(mae),
                'rmse': float(rmse),
                'seasonality_included': True
            })
        except Exception as e:
            pass
            
    output_file = os.path.join(MODEL_OUTPUT_DIR, 'latest_predictions.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
        
    print(f"Saved advanced predictions to {output_file}")

if __name__ == "__main__":
    train_advanced_models()
