#!/bin/bash
# Run Streamlit Frontend

echo "Starting LIMS-QMS Frontend (Streamlit)..."

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run streamlit
streamlit run frontend/app.py --server.port 8501
