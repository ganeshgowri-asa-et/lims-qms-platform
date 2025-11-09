#!/bin/bash
# Run FastAPI Backend

echo "Starting LIMS-QMS Backend Server..."

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run uvicorn server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
