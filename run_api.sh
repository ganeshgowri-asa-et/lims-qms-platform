#!/bin/bash

# Run FastAPI backend server

echo "Starting LIMS-QMS Document Management API..."
echo "API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""

# Create storage directories
mkdir -p storage/documents
mkdir -p storage/signatures
mkdir -p storage/search_index

# Run uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
