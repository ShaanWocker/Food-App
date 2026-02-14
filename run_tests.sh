#!/bin/bash

# Test Runner Script

echo "🧪 Running Food Ordering App Tests..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Please run: python3 -m venv venv"
    exit 1
fi

# Install dev dependencies
echo "📦 Installing test dependencies..."
pip install -q -r requirements-dev.txt

# Run tests
echo ""
echo "🔍 Running pytest..."
pytest tests/ -v --tb=short

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
else
    echo ""
    echo "❌ Some tests failed. Please review the output above."
    exit 1
fi

# Optional: Run with coverage
echo ""
echo "📊 Running tests with coverage..."
pytest tests/ --cov=app --cov-report=term-missing --cov-report=html

echo ""
echo "✨ Test run complete!"
echo "📈 Coverage report generated in htmlcov/index.html"
