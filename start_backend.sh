#!/bin/bash

# Food Ordering App Startup Script

echo "🍽️  Starting Food Ordering App..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
echo "Checking dependencies..."
pip install -q -r requirements.txt

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "⚠️  Warning: PostgreSQL is not running!"
    echo "Please start PostgreSQL and ensure the database is configured."
    echo "See README.md for database setup instructions."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Copying .env.example to .env..."
    cp .env.example .env
    echo "Please configure .env with your settings before running."
    exit 1
fi

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Start the backend server
echo "🚀 Starting FastAPI backend..."
echo "API will be available at http://localhost:8000"
echo "API Docs at http://localhost:8000/api/docs"
echo ""
echo "Press Ctrl+C to stop the server"

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
