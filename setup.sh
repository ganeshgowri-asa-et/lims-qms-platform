#!/bin/bash
# Setup script for LIMS QMS Platform

echo "🔧 Setting up LIMS QMS Platform..."
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env file with your configuration before running the application"
else
    echo ""
    echo "✓ .env file already exists"
fi

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p frontend/utils
mkdir -p backend/api/routes
mkdir -p backend/database
mkdir -p backend/services

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your database and API configuration"
echo "2. Run './run.sh' to start the application"
echo ""
echo "For more information, see README.md or SETUP_GUIDE.md"
