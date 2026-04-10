# AgriSense AI – AI Crop Intelligence System

AgriSense AI is an AI-powered crop disease detection and yield prediction platform. It provides actionable insights to farmers by analyzing plant images, environmental factors, and market data.

## Features
- **Crop Disease Detection:** Upload an image of a plant leaf, and the system uses Deep Learning (PyTorch) to identify diseases, provide a confidence score, and recommend treatments.
- **Yield Prediction:** Predict crop yield based on area, soil conditions, climate data, and crop type using Machine Learning (XGBoost/Scikit-Learn).
- **Weather Advisories:** Real-time and 5-day weather forecasts via OpenWeatherMap API with automated agronomic warnings (e.g., frost, heavy rain, pest risks).
- **Market Prices:** Live market commodity prices integration (via OGD API / data.gov.in).

## Tech Stack
- **Frontend:** React, Vite, Recharts, React Router
- **Backend API Gateway:** Go (Golang)
- **ML Services:** Python, FastAPI, PyTorch, Scikit-Learn, XGBoost

## Project Structure
- `src/` & `public/` - React Frontend UI and components
- `backend/` - Go API Gateway (routes, external APIs proxy)
- `ml/` - Python ML Models & FastAPI endpoints

## Setup & Running Locally

### 1. ML Microservices (Python)
Navigate to the `ml` directory, install dependencies, and start the FastAPI servers:
```bash
cd ml
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

pip install -r requirements.txt

# Start the disease detection service
uvicorn disease_detection:app --port 8000 --reload

# Start the yield prediction service (in another terminal)
uvicorn yield_prediction:app --port 8001 --reload
```

### 2. API Gateway (Go)
Navigate to the `backend` directory and start the Go server:
```bash
cd backend
go run main.go
```
The backend gateway will run on `http://localhost:8080`.

### 3. Frontend (React)
Navigate to the root directory, install npm packages, and start the dev server:
```bash
npm install
npm run dev
```
The React frontend will be available at `http://localhost:5173`.
