# 🌾 AgriSense AI: The Ultimate Precision Agriculture Suite

AgriSense AI is an enterprise-grade agricultural intelligence platform that combines **Hyperspectral Imaging (HSI)**, **Fast TFLite Diagnostics**, and **Generative AI** to revolutionize farming. It provides a seamless ecosystem across Mobile, Web, and Cloud to help farmers detect stress invisible to the naked eye and treat diseases with clinical precision.

---

## 🏗️ Triple-Threat Architecture

### 📱 **Flutter Mobile App (The Field Tool)**
A premium, SaaS-style mobile application designed for on-field use by farmers and agronomists.
*   **Real-time Diagnostics:** Instant leaf disease detection using TFLite.
*   **Hyperspectral Mapping:** Upload `.npy` spectral cubes to visualize plant health signatures.
*   **Voice Assistant:** Multi-lingual voice interface for hands-free query support.
*   **SaaS Aesthetic:** Modern dark mode with Glassmorphism and custom scanning animations.

### 🌐 **FastAPI Backend (The AI Brain)**
A high-performance RAG and Computer Vision server.
*   **HSI Module:** 3D-CNN processing for analyzing hyperspectral data cubes.
*   **TFLite Engine:** Fast, CPU-optimized inference for 38+ plant disease classes.
*   **Hybrid AI RAG:** Uses TFLite for detection and LLMs (Ollama/Gemini) for expert treatment advice.
*   **Scheme Matcher:** Matches farmers to government subsidies using vector-based retrieval.

### 💻 **React Dashboard (The Command Center)**
A data-heavy web dashboard for deep analysis and market tracking.
*   **Interactive Analytics:** Visualizing market price trends and yield forecasts.
*   **Cloud Diagnostics:** High-resolution image analysis for complex multi-symptom diagnostics.
*   **Weather Dynamics:** Advanced agronomic alerts and threshold monitoring.

---

## 🚀 Key Modules & Intelligence

### 🧬 **Disease Detection 2.0 (Hybrid ML)**
We've evolved from simple LLM guessing to a specialized computer vision pipeline:
1.  **Edge Detection:** Fast TFLite model (`model.tflite`) identifies the specific disease with >90% accuracy.
2.  **AI Insight:** The detected label is passed to a reasoning model to generate a localized **Treatment Prescription**.

### 🛰️ **Hyperspectral Imaging (HSI)**
AgriSense supports the next frontier of soil science. Our **3D-CNN model** analyzes hyperspectral data to detect "hidden stress" — identifying water deficiency or nutrient imbalances before they manifest visibly on the leaf.

### 🩺 **AgriSense Rx Doctor**
Automated phase-by-phase recovery schedules including chemical, biological, and cultural treatments.

### 🌦️ **Agronomist Weather & Alerts**
Real-time environmental monitoring with predictive alerts for heatwaves, frost, and wind-shear thresholds, sent via Twilio SMS integration.

---

## 🛠️ Technical Stack

| Category | Technologies |
|---|---|
| **Mobile** | Flutter, GetX, Dio, Flutter Animate, Google Fonts |
| **Backend** | FastAPI, PyTorch, TensorFlow Lite, Ollama, ChromaDB |
| **Frontend** | React 19, Vite, Recharts, Framer Motion |
| **Intelligence** | Gemini Pro, DeepSeek V3, 3D-CNN (HSI), TFLite |
| **Infrastructure** | Docker, .env Security, Twilio API, OpenWeatherMap |

---

## ⚙️ Setup & Installation

### **1. 🔐 Security First**
AgriSense uses a decentralized `.env` system. Ensure you create `.env` files in `app/`, `backend/`, and `frontend/` following the provided templates.

### **2. 📱 Mobile (App)**
```bash
cd app
flutter pub get
flutter run
```

### **3. 🧠 Backend (RAG & CV)**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### **4. 💻 Dashboard (Web)**
```bash
cd frontend
npm install
npm run dev
```

---

## 🌍 Vision
AgriSense AI aims to democratize high-tech precision agriculture. By making advanced tools like Hyperspectral Imaging accessible via a smartphone, we empower small-scale farmers to compete with industrial-scale agribusiness.

**Developed with ❤️ by the AgriSense Engineering Team.**
*Transforming the soil with code.*