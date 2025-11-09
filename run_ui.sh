#!/bin/bash

# Run Streamlit frontend

echo "Starting LIMS-QMS Document Management UI..."
echo "UI will be available at: http://localhost:8501"
echo ""
echo "Make sure the API is running at http://localhost:8000"
echo ""

# Run streamlit
streamlit run streamlit_app/app.py
