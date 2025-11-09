#!/bin/bash
# Setup LIMS-QMS Platform

echo "Setting up LIMS-QMS Platform..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p uploads/certificates uploads/qsf_forms uploads/documents assets

# Copy example env file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please update .env file with your configuration"
fi

# Initialize database (create tables)
echo "Database initialization..."
echo "Please ensure PostgreSQL is running and update DATABASE_URL in .env"
echo "Then run: python -c 'from backend.app.database import init_db; init_db()'"

# Make run scripts executable
chmod +x run_backend.sh run_frontend.sh

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your database credentials"
echo "2. Create PostgreSQL database: createdb lims_qms_db"
echo "3. Run database schema: psql lims_qms_db < database/schema.sql"
echo "4. Start backend: ./run_backend.sh"
echo "5. Start frontend: ./run_frontend.sh (in another terminal)"
echo ""
