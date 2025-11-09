#!/bin/bash

# LIMS-QMS Frontend Startup Script
# Starts the Streamlit frontend application

echo "🚀 Starting LIMS-QMS Streamlit Frontend..."

# Set environment variables
export BACKEND_URL=${BACKEND_URL:-"http://localhost:8000"}

# Check if backend is running
echo "📡 Checking backend connectivity..."
if curl -s "${BACKEND_URL}/health" > /dev/null; then
    echo "✅ Backend is running at ${BACKEND_URL}"
else
    echo "⚠️  Warning: Backend may not be running at ${BACKEND_URL}"
    echo "   Please start the backend first or set BACKEND_URL environment variable"
fi

# Start Streamlit
echo "🎨 Starting Streamlit application..."
cd frontend
streamlit run app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --browser.gatherUsageStats=false \
    --theme.primaryColor="#1f77b4" \
    --theme.backgroundColor="#ffffff"
