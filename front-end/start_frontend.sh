#!/bin/bash
# Start NHScribe Frontend on Raspberry Pi

echo "🎨 Starting NHScribe Frontend..."
echo "📍 Frontend will be accessible at http://10.249.84.213:3000"
echo ""

# Navigate to the script directory
cd "$(dirname "$0")"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Set API URL environment variable
export REACT_APP_API_URL=http://10.249.84.213:8000

# Start React development server
echo ""
echo "✅ Starting React development server..."
echo "🌐 Access the app at: http://10.249.84.213:3000"
echo ""
npm start

