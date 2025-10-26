#!/bin/bash
# Start NHScribe Backend on Raspberry Pi

echo "🚀 Starting NHScribe Backend..."
echo "📍 Server will be accessible at http://10.249.84.213:8000"
echo ""

# Navigate to the script directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create letters directory if it doesn't exist
mkdir -p letters

# Start the backend
echo ""
echo "✅ Starting FastAPI server..."
echo "📖 API Documentation: http://10.249.84.213:8000/docs"
echo ""
python app.py

