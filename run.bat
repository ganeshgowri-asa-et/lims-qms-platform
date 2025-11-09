@echo off
REM LIMS-QMS Platform Startup Script for Windows

echo ==========================================
echo LIMS-QMS Platform - Starting Services
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

REM Check if database exists
if not exist "lims_qms.db" (
    echo.
    echo Database not found. Generating sample data...
    python scripts\generate_sample_data.py
)

echo.
echo ==========================================
echo Starting Backend API...
echo ==========================================
echo API will be available at: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.

REM Start backend in new window
start "LIMS-QMS Backend" cmd /k "cd backend && python main.py"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

echo.
echo ==========================================
echo Starting Streamlit Frontend...
echo ==========================================
echo Web App will be available at: http://localhost:8501
echo.
echo To stop services: Close both windows
echo ==========================================
echo.

REM Start Streamlit
streamlit run streamlit_app\app.py
