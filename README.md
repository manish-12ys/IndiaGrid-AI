# ⚡ IndiaGrid AI

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Framework-black?logo=flask)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB?logo=react)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-Build-646CFF?logo=vite)](https://vitejs.dev/)
[![Docker](https://img.shields.io/badge/Docker-Container-2496ED?logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](#)
[![Status](https://img.shields.io/badge/Status-Active-success)](#)

---

## 📌 Overview

IndiaGrid AI is an AI-powered platform that monitors, predicts, and optimizes electricity distribution across Indian states.

---

## 🧠 Features

- Real-time electricity monitoring  
- AI-based demand forecasting  
- Smart distribution optimization  
- State-wise surplus/deficit visualization  
- CSV/XLSX data upload support  

---

## ⚙️ Workflow

```text
Data → Processing → AI → Analysis → Optimization → Dashboard
```
---

🏗️ Tech Stack

Frontend: React + Vite, Recharts, Tailwind
Backend: Python, Flask, Gunicorn
AI/Data: Pandas, NumPy
Deployment: Docker, Render, GitHub


---

🚀 How to Run

1. Clone Repo

git clone https://github.com/manish-12ys/indiagrid-ai.git
cd indiagrid-ai


---

🪟 Windows

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python app.py


---

🐧 Linux

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python app.py


---

🍎 macOS

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python app.py


---

🌐 Frontend

cd frontend
npm install
npm run dev


---

🐳 Docker (Optional)

docker build -t indiagrid-ai .
docker run -p 5000:5000 indiagrid-ai


---

📍 Access

Backend → http://localhost:5000

Frontend → http://localhost:5173



---

📌 Summary

IndiaGrid AI predicts demand, detects shortages, and optimizes electricity distribution using AI.

