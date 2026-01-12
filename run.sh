#!/bin/bash
# Project AXON - Run Script

set -e

echo "🚀 Starting Project AXON..."

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Run the server
echo "✨ AXON is online at http://localhost:8000"
echo "📊 API docs at http://localhost:8000/docs"
echo ""
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
