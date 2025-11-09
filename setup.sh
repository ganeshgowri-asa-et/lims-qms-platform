#!/bin/bash

# LIMS-QMS Platform - Session 8: Audit & Risk Management
# Setup Script

set -e

echo "=========================================="
echo "LIMS-QMS Platform Setup"
echo "Session 8: Audit & Risk Management System"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

if ! python3 -c 'import sys; assert sys.version_info >= (3,9)' 2>/dev/null; then
    echo "Error: Python 3.9 or higher is required"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
echo "Virtual environment created successfully"

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Dependencies installed successfully"

# Create .env file if not exists
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ".env file created. Please update with your configuration."
else
    echo ""
    echo ".env file already exists. Skipping..."
fi

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p uploads
mkdir -p backups
echo "Directories created successfully"

# Database setup
echo ""
echo "=========================================="
echo "Database Setup"
echo "=========================================="
echo ""
echo "To set up the database, run the following commands:"
echo ""
echo "1. Create database:"
echo "   createdb lims_qms"
echo ""
echo "2. Run schema:"
echo "   psql -U postgres -d lims_qms -f database/schema/08_audit_risk.sql"
echo ""
echo "Or if using Docker PostgreSQL:"
echo "   docker exec -i postgres_container psql -U postgres -c 'CREATE DATABASE lims_qms;'"
echo "   docker exec -i postgres_container psql -U postgres -d lims_qms < database/schema/08_audit_risk.sql"
echo ""

# Instructions to run
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start the application:"
echo ""
echo "1. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Start backend API:"
echo "   cd backend && python main.py"
echo "   API will be available at: http://localhost:8000"
echo ""
echo "3. Start frontend (in a new terminal):"
echo "   source venv/bin/activate"
echo "   cd frontend && streamlit run app.py"
echo "   UI will be available at: http://localhost:8501"
echo ""
echo "4. Access API documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "=========================================="
echo "Happy auditing and risk management! 🔍⚠️"
echo "=========================================="
