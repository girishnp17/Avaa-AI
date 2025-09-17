#!/bin/bash

# Quick Development Start Script for Avaa-AI
# Usage: ./dev.sh

echo "🚀 Quick starting Avaa-AI Voice Interview..."

# Kill existing processes
pkill -f "python.*run_app.py" 2>/dev/null || true
pkill -f "npm.*run.*dev" 2>/dev/null || true

# Wait for processes to stop
sleep 2

# Start in background and show both outputs
echo "🔧 Starting backend and frontend..."

# Activate venv and start backend
source venv/bin/activate && python run_app.py &

echo "✅ Avaa-AI started!"
echo "🌐 Check your browser - the app should open automatically"
echo "⏹️  Press Ctrl+C to stop everything"

# Wait for interrupt
trap 'echo "🛑 Stopping..."; pkill -f "python.*run_app.py"; pkill -f "npm.*run.*dev"; exit 0' SIGINT SIGTERM

# Keep alive
while true; do
    sleep 1
done