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

### 💻 **Frontend React Dashboard (The Command Center)**
A data-heavy web dashboard for deep analysis and market tracking.
*   **Interactive Analytics:** Visualizing market price trends and yield forecasts.
*   **Cloud Diagnostics:** High-resolution image analysis for complex multi-symptom diagnostics.
*   **Weather Dynamics:** Advanced agronomic alerts and threshold monitoring.

---

## 🚀 Key Modules & Intelligence

### 🧬 **Disease Detection 2.0 (ResNet + Hybrid AI)**
We've evolved from simple LLM guessing to a specialized computer vision pipeline:
1.  **ResNet Engine:** A high-precision **ResNet** model trained on **85,000+ plant images** identifying 38+ disease classes with >95% accuracy.
2.  **Edge Detection:** Optimized TFLite deployment for sub-second inference on mobile or CPU.
3.  **AI Insight:** The detected label is passed to a reasoning model to generate a localized **Treatment Prescription**.

### 📊 **Yield Prediction (ML Forecasting)**
Predict harvest outcomes before you plant.
*   **Ensemble ML:** Uses Random Forest and XGBoost to predict yield based on climate, soil, and fertilizer usage.
*   **Data-Driven:** Analyzes historically successful harvest patterns to provide tonnage-per-hectare forecasts.

### 🔬 **Early Crop Disease Detection (Pre-Symptomatic)**
Detect diseases before they are visible to the human eye.
*   **HSI Analysis:** Our **3D-CNN Hyperspectral Imaging** analyzes "Red Edge" and "Infrared" spectral bands to identify cellular stress days before physical spots appear.
*   **ResNet Diagnosis:** High-speed classification of 38+ existing diseases using a model trained on 85,000+ images.

### 🩺 **AgriSense Rx (24/7 Expert Advice)**
A digital "Prescription Pad" for your crops. 
*   **Virtual Doctor:** Describe symptoms and receive a professional medical-style prescription.
*   **Expert Advice:** 24/7 AI-driven diagnostic support available in multiple regional languages.
*   **Actionable Plans:** Phase-by-phase recovery schedules (Chemical + Biological).

### 🌦️ **Sentinel Weather & Danger Alerts**
Intelligent field monitoring that goes beyond simple forecasts.
*   **Dangerous Weather Alerts:** Automatically identifies and warns users about upcoming **Heatwaves**, **Frost**, and **Storms** within a 5-day window.
*   **Agronomic Advice:** Provides real-time suggestions like "Apply light irrigation" during heat spikes or "Secure structures" during high winds.

### 💰 **Mandi Price Analytics**
Real-time pricing intelligence from across the country.
*   **State-wise Comparison:** Automatically fetch and compare a crop's price across different states (e.g., Punjab vs. Karnataka).
*   **Mandi Insights:** Live data from the Government API (**data.gov.in**) showing current market rates, minimum and maximum fluctuations.
*   **Visual Analytics:** Integrated bar charts and trend lines to help farmers decide which market offers the best return for their harvest.

### 🛒 **AgriMart (Marketplace)**
A specialized portal for buying and selling agricultural assets.
*   **Direct Redirection:** Seamlessly connects farmers to "Marts" and marketplaces for essential fertilizers, equipment, and seeds.
*   **Price Awareness:** Integrated with MSP data to ensure farmers get the best value before buying or selling.

### 🏛️ **Personalized Government Schemes (RAG)**
A specialized Matchmaker for agricultural subsidies and benefits.
*   **Profile-Based Matching:** Enter your crop type, land size, and location to find schemes specifically tailored to your needs.
*   **AI Retrieval (RAG):** Uses **Semantic Search** to scan a database of hundreds of government schemes (PM-Kisan, Fasal Bima, etc.) and match you with the highest relevancy.
*   **Application Guidance:** Provides summarized eligibility criteria and step-by-step application instructions for each scheme.

### 🛰️ **Hyperspectral Imaging (HSI)**
AgriSense supports the next frontier of soil science. Our **3D-CNN model** analyzes hyperspectral data to detect "hidden stress" — identifying water deficiency or nutrient imbalances before they manifest visibly on the leaf.

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