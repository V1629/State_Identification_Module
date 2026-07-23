#!/bin/bash

# Quick Start Script for State Identification Module
# Usage: ./start.sh

echo "=================================="
echo "State Identification Module"
echo "Full Stack Startup Script"
echo "=================================="
echo ""

# Check if venv is activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "⚠️  Virtual environment not activated!"
    echo "Activating venv..."
    source venv/bin/activate
fi

# Install dependencies if needed
echo "📦 Checking Python dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

echo "📦 Checking Frontend dependencies..."
cd frontend
npm install > /dev/null 2>&1
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting services..."
echo ""

# Start backend in background
echo "Starting Backend (FastAPI) on http://localhost:8000..."
python -m uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!

# Give backend time to start
sleep 3

# Start frontend
echo "Starting Frontend (React) on http://localhost:5173..."
cd frontend
npm run dev

# Cleanup on exit
trap "kill $BACKEND_PID 2>/dev/null" EXIT
