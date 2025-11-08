#!/bin/bash

# LIMS-QMS Platform Setup Script
# This script helps set up the development environment

set -e  # Exit on error

echo "🔬 LIMS-QMS Platform Setup"
echo "=========================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please update it with your configuration."
else
    echo "✅ .env file already exists."
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✅ Docker is installed."

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker Compose is installed."

# Ask user if they want to use Docker or manual setup
echo ""
echo "Choose setup method:"
echo "1) Docker Compose (Recommended)"
echo "2) Manual Setup"
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo ""
        echo "🐳 Setting up with Docker Compose..."
        docker-compose up -d
        echo ""
        echo "✅ Setup complete!"
        echo ""
        echo "Services are running:"
        echo "  - Frontend: http://localhost:8501"
        echo "  - Backend API: http://localhost:8000"
        echo "  - API Docs: http://localhost:8000/docs"
        echo "  - Database: localhost:5432"
        ;;
    2)
        echo ""
        echo "🔧 Manual setup..."

        # Setup backend
        echo "Setting up backend..."
        cd backend
        python -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        echo "✅ Backend dependencies installed."
        cd ..

        # Setup frontend
        echo "Setting up frontend..."
        cd frontend
        python -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        echo "✅ Frontend dependencies installed."
        cd ..

        echo ""
        echo "✅ Setup complete!"
        echo ""
        echo "To start the services manually:"
        echo "  Backend:  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
        echo "  Frontend: cd frontend && source venv/bin/activate && streamlit run Home.py"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "🎉 LIMS-QMS Platform is ready!"
