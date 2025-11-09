#!/bin/bash

# LIMS-QMS Platform Startup Script

echo "================================================"
echo "  LIMS-QMS Platform - Solar PV Testing Lab     "
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please configure .env file with your settings!"
fi

# Create necessary directories
echo "Creating output directories..."
mkdir -p reports/pdf
mkdir -p reports/graphs
mkdir -p reports/certificates
mkdir -p reports/certificates/qr_codes
mkdir -p temp_data

# Start services
echo ""
echo "================================================"
echo "  Starting Services                             "
echo "================================================"
echo ""

# Start FastAPI in background
echo "Starting FastAPI server on http://localhost:8000..."
python -m app.main &
API_PID=$!

# Wait for API to be ready
sleep 3

# Start Streamlit
echo "Starting Streamlit UI on http://localhost:8501..."
streamlit run streamlit_app/main.py &
STREAMLIT_PID=$!

echo ""
echo "================================================"
echo "  Services Running                              "
echo "================================================"
echo ""
echo "  API Server:    http://localhost:8000"
echo "  API Docs:      http://localhost:8000/docs"
echo "  Streamlit UI:  http://localhost:8501"
echo ""
echo "  Press Ctrl+C to stop all services"
echo "================================================"

# Wait for interrupt
trap "kill $API_PID $STREAMLIT_PID" EXIT
wait
