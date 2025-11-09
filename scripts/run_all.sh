#!/bin/bash

# Script to run both backend and frontend

echo "=== Starting LIMS & QMS Platform ==="

# Initialize database
echo "Initializing database..."
cd /home/user/lims-qms-platform/scripts
python init_db.py

# Start backend in background
echo "Starting backend API..."
cd /home/user/lims-qms-platform/backend
python run.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend
echo "Starting frontend UI..."
cd /home/user/lims-qms-platform/frontend
streamlit run app.py &
FRONTEND_PID=$!

echo ""
echo "=== LIMS & QMS Platform Started ==="
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Frontend UI: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
