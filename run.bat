@echo off
REM LIMS-QMS Platform Startup Script for Windows

echo ================================================
echo   LIMS-QMS Platform - Solar PV Testing Lab
echo ================================================
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
pip install -r requirements.txt --quiet

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file from example...
    copy .env.example .env
    echo Please configure .env file with your settings!
)

REM Create necessary directories
echo Creating output directories...
mkdir reports\pdf 2>nul
mkdir reports\graphs 2>nul
mkdir reports\certificates 2>nul
mkdir reports\certificates\qr_codes 2>nul
mkdir temp_data 2>nul

echo.
echo ================================================
echo   Starting Services
echo ================================================
echo.

REM Start FastAPI
echo Starting FastAPI server on http://localhost:8000...
start "FastAPI Server" cmd /k python -m app.main

REM Wait for API to be ready
timeout /t 3 /nobreak >nul

REM Start Streamlit
echo Starting Streamlit UI on http://localhost:8501...
start "Streamlit UI" cmd /k streamlit run streamlit_app/main.py

echo.
echo ================================================
echo   Services Running
echo ================================================
echo.
echo   API Server:    http://localhost:8000
echo   API Docs:      http://localhost:8000/docs
echo   Streamlit UI:  http://localhost:8501
echo.
echo   Close the command windows to stop services
echo ================================================
echo.

pause
