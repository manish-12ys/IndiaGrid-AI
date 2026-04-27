from flask import Blueprint, jsonify, request, send_file
import os
import sys
import pandas as pd
import json
import subprocess
from werkzeug.utils import secure_filename
from services.analysis_engine import get_state_analysis, get_seasonal_trends
from services.distribution_engine import optimize_distribution
from google import genai

api_bp = Blueprint('api', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
from ingestion.api_fetcher import get_live_grid_data

DATA_FILE = os.path.join(BASE_DIR, 'data', 'final', 'unified_dataset.csv')
PREDICTIONS_FILE = os.path.join(BASE_DIR, 'ml', 'lstm', 'models', 'latest_predictions.json')

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame()

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "IndiaGrid AI API is running"}), 200

@api_bp.route('/live-data', methods=['GET'])
def live_data():
    try:
        # Poll the live Grid-India API (or fallback simulator)
        live_df = get_live_grid_data()
        
        if live_df.empty:
            return jsonify({"error": "No data available"}), 404
            
        return jsonify(live_df.to_dict(orient='records')), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/predict', methods=['GET'])
def get_predictions():
    if os.path.exists(PREDICTIONS_FILE):
        with open(PREDICTIONS_FILE, 'r') as f:
            predictions = json.load(f)
        return jsonify(predictions), 200
    return jsonify({"error": "No predictions available"}), 404

@api_bp.route('/surplus-deficit', methods=['GET'])
def surplus_deficit():
    try:
        # Analysis should also use live data for accurate mapping
        live_df = get_live_grid_data()
        
        if live_df.empty:
            return jsonify({"error": "No data available"}), 404
            
        analysis = get_state_analysis(live_df)
        return jsonify(analysis), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/seasonal-trends', methods=['GET'])
def seasonal_trends():
    df = load_data()
    if df.empty:
        return jsonify({}), 200
        
    trends = get_seasonal_trends(df)
    return jsonify(trends), 200

@api_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if ext == 'csv':
        save_path = os.path.join(BASE_DIR, 'data', 'raw', 'csv', filename)
    elif ext in ['xls', 'xlsx']:
        save_path = os.path.join(BASE_DIR, 'data', 'raw', 'excel', filename)
    else:
        return jsonify({"error": "Invalid file type. Only CSV and Excel are supported."}), 400
        
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    file.save(save_path)
    
    # Run the ingestion script
    try:
        subprocess.run([sys.executable, os.path.join(BASE_DIR, 'ingestion', 'file_loader.py')], check=True)
        return jsonify({"message": "File uploaded and data ingested successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Ingestion failed: {str(e)}"}), 500

@api_bp.route('/download-unified', methods=['GET'])
def download_unified():
    if os.path.exists(DATA_FILE):
        return send_file(DATA_FILE, as_attachment=True, download_name='unified_dataset.csv')
    return jsonify({"error": "Dataset not found"}), 404

@api_bp.route('/optimize', methods=['GET', 'POST'])
def optimize():
    try:
        # Optimization engine triggers based on the live API feed
        live_df = get_live_grid_data()
        
        if live_df.empty:
            return jsonify({"error": "No data available"}), 404
            
        analysis = get_state_analysis(live_df)
        transfers = optimize_distribution(analysis)
        return jsonify(transfers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/ai-insights', methods=['POST'])
def ai_insights():
    data = request.json
    query = data.get('query', '')
    frontend_analysis = data.get('analysis', [])
    frontend_transfers = data.get('transfers', [])
    seasonal_trends = data.get('seasonalTrends', {})
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
        
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return jsonify({"error": "GEMINI_API_KEY environment variable not set. Please set it in your .env file to use AI Insights."}), 500
        
    try:
        # Build live context directly from the exact frontend state
        live_context = ""
        if frontend_analysis:
            total_demand = sum(s['demand_mw'] for s in frontend_analysis)
            total_supply = sum(s['supply_mw'] for s in frontend_analysis)
            
            worst_deficit = min(frontend_analysis, key=lambda x: x['surplus_mw'])
            best_surplus = max(frontend_analysis, key=lambda x: x['surplus_mw'])
            
            # Format a breakdown of all states for the AI to read
            state_breakdown = ", ".join([f"{s['state']}: {s['surplus_mw']:,.0f} MW" for s in frontend_analysis])
            
            # Get recommended power optimization transfers
            transfer_breakdown = "\n".join([f"Transfer {t['power_mw']:,.0f} MW from {t['from_state']} to {t['to_state']}" for t in frontend_transfers])
            if not transfer_breakdown:
                transfer_breakdown = "Grid is completely balanced, no transfers required."
            
            # Format seasonal trends
            seasonal_context = ""
            if seasonal_trends and 'monthly_data' in seasonal_trends:
                monthly_data = seasonal_trends['monthly_data']
                months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                monthly_breakdown = ", ".join([f"{months[m['month']-1]}: {m['demand_mw']:,.0f} MW" for m in monthly_data if 1 <= m['month'] <= 12])
                seasonal_context = f"""
            HISTORICAL / SEASONAL TRENDS:
            Peak Demand Month: {months[seasonal_trends.get('peak_month', 1)-1]}
            Lowest Demand Month: {months[seasonal_trends.get('lowest_month', 1)-1]}
            Monthly Demand Breakdown: {monthly_breakdown}
            """
            
            live_context = f"""
            --- CURRENT GRID STATUS ---
            Total National Demand: {total_demand:,.0f} MW
            Total National Supply: {total_supply:,.0f} MW
            Most Critical Deficit: {worst_deficit['state']} ({worst_deficit['surplus_mw']:,.0f} MW)
            Highest Surplus Source: {best_surplus['state']} (+{best_surplus['surplus_mw']:,.0f} MW)
            
            FULL STATE BREAKDOWN (Surplus/Deficit MW):
            {state_breakdown}
            
            RECOMMENDED POWER DISTRIBUTION OPTIMIZATIONS:
            {transfer_breakdown}
            {seasonal_context}
            ---------------------------
            """
            
        client = genai.Client(api_key=api_key)
        
        # Give some context to the model
        context = f"You are IndiaGrid AI, an expert intelligence system managing India's electricity grid. Base your answers strictly on the following live context if relevant:\n{live_context}\n\nUSER QUERY: "
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=context + query
        )
        return jsonify({"insight": response.text}), 200
    except Exception as e:
        error_message = str(e)
        if "429" in error_message and "RESOURCE_EXHAUSTED" in error_message:
            friendly_error = "AI Quota Exceeded: The Gemini API free-tier rate limit has been reached (15 requests/minute). Please wait roughly 60 seconds before asking another question."
            return jsonify({"error": friendly_error}), 429
        return jsonify({"error": error_message}), 500
