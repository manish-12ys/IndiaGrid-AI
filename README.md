# ⚡ IndiaGrid AI

**IndiaGrid AI** is a comprehensive, AI-powered national electricity intelligence platform designed to monitor, forecast, and optimize the power grid across all 36 Indian states and union territories. It ingests heterogeneous historical grid data, leverages machine learning models to predict power demand/supply, and provides an actionable, real-time distribution strategy to balance deficits and surpluses.

## 🌟 Key Features

* **Real-time Grid Monitoring**: Track total national demand, supply, and net grid status dynamically.
* **National Grid Map (State Status)**: A visual heatmap analyzing exactly which states are running on surplus power and which are in deficit.
* **Seasonal Demand Dynamics**: Integrated ML predictions and historical analysis showcasing demand shifts (e.g., Summer peaks, Winter dips).
* **Automated Distribution Engine**: A greedy optimization algorithm recommending active megawatt (MW) power transfers from surplus states to deficit states to ensure a perfectly balanced national grid.
* **Seamless Data Integration**: Directly upload `.csv` or `.xlsx` files from the dashboard to re-trigger the ingestion and ML training pipelines automatically.
* **AI Insights (Powered by Gemini)**: A built-in natural language chat assistant. Ask questions like *"What states need critical power today?"* and get contextual, data-driven answers.
* **Premium UI/UX**: Built with modern web aesthetics—deep radial gradients, cascading glassmorphism panels, and highly responsive micro-animations.

---

## 🛠️ Technology Stack

**Backend**
* Python 3.14+
* Flask & Flask-CORS
* Pandas & Numpy (Data Ingestion & Transformation)
* Scikit-Learn & Statsmodels (Machine Learning: ARIMA & MLP/LSTM-proxies)
* Google GenAI SDK (Gemini AI Integration)

**Frontend**
* React 18 + Vite
* Vanilla CSS (Glassmorphism design)
* Recharts (Data Visualization)
* Lucide React (Icons)

---

## 🚀 Setup & Installation

### 1. Clone & Set Up Backend Environment

```bash
# Clone the repository (if applicable)
git clone https://github.com/manish-12ys/IndiaGrid-AI.git
cd "IndiaGrid AI"

# Activate your virtual environment
source venv/bin/activate

# Install the Python dependencies
pip install -r requirements.txt
```

### 2. Configure Gemini AI Insights (Optional but recommended)
To use the AI chat feature in the dashboard, you must provide a valid Gemini API key.
1. Create a `.env` file in the root directory.
2. Add your API key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### 3. Run the Backend Server
```bash
cd backend
python app.py
```
*The Flask API will start on `http://localhost:5000`.*

### 4. Run the Frontend Dashboard
Open a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
*The Vite React dashboard will start on `http://localhost:5173` (or `5174`).*

---

## 📂 Project Structure

```text
IndiaGrid AI/
├── backend/
│   ├── app.py                     # Main Flask entrypoint
│   ├── routes/
│   │   └── api.py                 # API endpoints (live-data, AI, optimization, upload)
│   └── services/
│       ├── analysis_engine.py     # Computes state-level & seasonal supply/demand logic
│       └── distribution_engine.py # Recommends surplus-to-deficit power transfers
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Main React Dashboard UI
│   │   └── index.css              # Premium Glassmorphism Styles
│   └── package.json
├── ingestion/
│   ├── file_loader.py             # Parses/Standardizes uploaded CSVs/Excel datasets
│   └── api_fetcher.py             # Mock API polling integration
├── ml/
│   ├── arima/                     # Baseline predictive models
│   └── lstm/                      # Advanced predictive models (Seasonality tracking)
├── scripts/
│   └── generate_mock_data.py      # Generates synthetic electrical data for 36 states
├── data/                          # Raw, processed, and final exported unified_dataset
├── docs/                          # Original architectural blueprint (plan.md)
└── requirements.txt               # Backend Dependencies
```

---

## 👨‍💻 How the Data Pipeline Works

1. **Ingestion**: Raw `.csv` and `.xlsx` files in `/data/raw/` are ingested and standardized into MW measurements.
2. **Unified Dataset**: The `file_loader.py` merges all data into `/data/final/unified_dataset.csv`.
3. **ML Training**: The `/ml/` scripts use this unified dataset to train both baseline (ARIMA) and advanced (MLP-proxy) models to predict future demands.
4. **Insights Engine**: The backend reads these outputs and serves `JSON` payloads over RESTful APIs to the React dashboard. 

---

*Designed and Developed for National Power Grid Optimization.*
