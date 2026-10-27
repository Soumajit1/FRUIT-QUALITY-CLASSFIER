FRUIT QUALITY CLASSIFIER — MULTIMODAL VISION AI & QUALITY INSPECTION SYSTEM

OVERVIEW
Fruit Quality Classifier is an advanced diagnostic inspection platform powered by Google Gemini Vision AI
(Multimodal LLM) with an offline local CNN fallback. It performs automatic fruit taxonomy identification,
freshness verification, surface defect and rot detection, ripeness grading, and shelf-life estimation.

ENVIRONMENT & SETUP
1. The isolated virtual environment is located at:
   .venv (Python 3.12 64-bit with TensorFlow 2.21, Streamlit, Requests, Pillow, Pandas, NumPy)

2. Configuration:
   - Gemini API Key is configured in .env and loaded automatically.
   - Dual-Engine Support: Users can toggle between "Gemini Vision AI (Active)" and "Local CNN (Offline)" in the sidebar.

3. To run the server:
   - Double-click "run_app.bat"
   OR
   - Open Command Prompt in this folder and run:
     .\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8501

4. Live Access:
   - Local Browser URL: http://localhost:8501
   - Network URL: http://172.20.10.2:8501

PROJECT ARCHITECTURE
- app.py: Main application frontend and multimodal vision inspection engine
- .env: Environment configuration storing GEMINI_API_KEY
- fruit_quality_model.keras: Local CNN model for offline fallback
- fruit_quality_users.db: SQLite database storing authentication credentials and detailed inspection history
- assets/logo.png: Official system brand logo
- run_app.bat: One-click launcher script
