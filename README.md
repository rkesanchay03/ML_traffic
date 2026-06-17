# ASTraM Bengaluru Traffic Command Center 🚔

A police-grade, event-driven traffic congestion forecasting system for Bengaluru. Powered by an XGBoost machine learning model trained on 8,173 real ASTraM traffic events, this system predicts event severity and automatically recommends data-driven police manpower and diversion routes.

## Features
- **Data-Driven Predictions:** Predicts traffic severity (High/Low) based on event cause, time, day, zone, and road closure status.
- **No Hallucinations:** Manpower and barricade recommendations are mathematically derived from historical severity rates in the dataset.
- **Tactical Map:** Visualizes affected corridors and diversion routes using Leaflet.
- **Analytics Dashboard:** Explores historical data patterns, feature importances, and risky corridors.

---

## 🚀 How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/flipkart.git
cd flipkart
```

### 2. Create a Virtual Environment
It is highly recommended to use a virtual environment to manage dependencies.
**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```
**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Paths (Important!)
Before running, you need to update the absolute paths in the code to match where you cloned the repository on your machine.
Update the paths in the following files to point to your local directory:
- `train_model.py` (Lines 36-38: `PROCESSED_DATA`, `MODEL_PATH`, `STATS_PATH`)
- `backend/main.py` (Line 28: `BASE_DIR`)
- `frontend/app.py` (Line 341: inside `load_stats()`)

*Alternatively, you can modify these scripts to use relative paths (`os.path.dirname(__file__)`) for easier portability.*

### 5. Train the Model (Optional)
If you want to retrain the XGBoost model and regenerate the statistics from the CSV:
```bash
python train_model.py
```
*(This will generate a new `model.pkl` and `stats.json` in the root directory)*

---

## 🖥️ Starting the Application

The application consists of a FastAPI backend and a static HTML/JS frontend.

### 1. Start the FastAPI Backend
Keep this terminal running. It serves the ML predictions on port 8000.
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
*You can view the API documentation at http://127.0.0.1:8000/docs*

### 2. Start the Web UI
Open a **new terminal**, activate the virtual environment, and run a static server for the frontend.
```bash
cd web_ui
python -m http.server 3000
```

### 3. Open the Dashboard
Navigate to [http://localhost:3000](http://localhost:3000) in your web browser.

---

## Architecture
- `train_model.py`: Cleans data, trains the XGBoost pipeline, extracts feature importances, and compiles operational rules into `stats.json`.
- `backend/main.py`: A lightweight FastAPI server that loads `model.pkl` and `stats.json` into memory and serves predictions via a `/predict` POST endpoint.
- `web_ui/index.html`: A vanilla HTML/JS single-page application built for speed and aesthetics, acting as the command center dashboard.
- `frontend/app.py`: A legacy Streamlit version of the dashboard.
