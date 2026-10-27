@echo off
cd /d "%~dp0"
echo ========================================================
echo    Starting Fruit Quality Classifier Server
echo ========================================================

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [INFO] Virtual environment not found. Setting up .venv...
    py -3.12 -m venv .venv 2>nul || python -m venv .venv
    echo [INFO] Installing required dependencies...
    .\.venv\Scripts\python.exe -m pip install --upgrade pip
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
)

echo [INFO] Launching Streamlit Application...
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
pause
