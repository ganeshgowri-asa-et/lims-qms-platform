#!/bin/bash
# Script to run both backend and frontend services

echo "🚀 Starting LIMS QMS Platform..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your configuration."
fi

echo "Starting Backend API..."
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

echo ""
echo "Starting Frontend UI..."
cd frontend
streamlit run app.py &
FRONTEND_PID=$!

echo ""
echo "✅ Services started!"
echo ""
echo "📍 Access points:"
echo "   - Frontend UI: http://localhost:8501"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
