#!/bin/bash

# Kivy App Startup Script

echo "🍽️  Starting Food Ordering Kivy App..."

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

# Start the Kivy app
echo "🚀 Starting Kivy application..."
python kivy_app/main.py
