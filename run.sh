#!/bin/bash

# LIMS-QMS Platform Startup Script

echo "=========================================="
echo "LIMS-QMS Platform - Starting Services"
echo "=========================================="
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
pip install -q -r requirements.txt

# Check if database exists
if [ ! -f "lims_qms.db" ]; then
    echo ""
    echo "Database not found. Generating sample data..."
    python scripts/generate_sample_data.py
fi

echo ""
echo "=========================================="
echo "Starting Backend API..."
echo "=========================================="
echo "API will be available at: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""

# Start backend in background
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

echo ""
echo "=========================================="
echo "Starting Streamlit Frontend..."
echo "=========================================="
echo "Web App will be available at: http://localhost:8501"
echo ""
echo "To stop services: Press Ctrl+C"
echo "=========================================="
echo ""

# Start Streamlit
streamlit run streamlit_app/app.py

# Cleanup on exit
kill $BACKEND_PID 2>/dev/null
