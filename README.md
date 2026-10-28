# Fruit Quality Classifier



An intelligent, dual-engine visual inspection platform designed to identify fruit varieties and accurately classify freshness quality (Fresh vs. Rotten) with automated decay analysis, mold detection, and shelf-life estimation.

---

## Features

- **Dual AI Inference Engines**:
  - **Google Gemini Vision AI (Active - High Precision)**: Multimodal LLM analysis providing precise fruit taxonomy identification, detailed physical condition reports, defect localization (mold, rot, bruising), ripeness stage grading, and shelf-life estimation.
  - **Local Deep CNN (Offline Fallback)**: Built on TensorFlow / Keras 3 with aspect-ratio preserving center crop and Test-Time Augmentation (TTA).
- **Zero-Friction Authentication**: Local SQLite user authentication with PBKDF2-HMAC password hashing.
- **Audit Records & Export**: Full chronological history tracking with one-click CSV export.
- **Classic Minimalist UI/UX**: Clean dark aesthetic designed with custom CSS, fluid scrolling, and responsive layout.

---

## Project Structure

```text
FRUIT-QUALITY-CLASSIFIER/
├── assets/
│   └── logo.png                 # Official brand logo & favicon
├── app.py                       # Main Streamlit application & inference engine
├── fruit_quality_model.keras    # Pretrained local CNN model
├── fruit_quality_users.db       # SQLite database for accounts & inspection logs
├── requirements.txt             # Python dependencies
├── run_app.bat                  # One-click Windows launch script
├── .env                         # API key configuration
├── .gitignore                   # Ignored files (virtual environment, cache)
└── README.md                    # Project documentation
```

---

## Step-by-Step Installation & Run Guide

### Option 1: Quick Start (Windows)
If you are on Windows, simply double-click **`run_app.bat`**.

---

### Option 2: Manual Terminal Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/Soumajit1/FRUIT-QUALITY-CLASSFIER.git
cd FRUIT-QUALITY-CLASSFIER
```

#### 2. Create and Activate a Virtual Environment
> **Note:** Python 3.10 to 3.12 is recommended for TensorFlow compatibility.

On Windows:
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

On macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configure Your API Key (Optional but Recommended)
Open or create `.env` in the root folder and add your Gemini API key:
```env
GEMINI_API_KEY=---
```
*(You can also paste your API key directly into the sidebar in the running app).*

#### 5. Launch the Application
```bash
streamlit run app.py
```
Open your browser and navigate to:
```
http://localhost:8501
```

---

## Technology Stack

- **Frontend & App Framework**: Streamlit
- **Vision AI Models**: Google Gemini Vision (`gemini-flash-lite-latest` / `gemini-flash-latest`), TensorFlow / Keras 3
- **Data & Image Processing**: Pillow, NumPy, Pandas, Requests
- **Database**: SQLite3

by,
108001240139,108001240150,108001240135,108001240191,108001240151
