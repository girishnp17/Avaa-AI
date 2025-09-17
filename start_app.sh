#!/bin/bash

# Avaa-AI Voice Interview Application Startup Script
# This script automatically sets up and starts both backend and frontend

set -e  # Exit on any error

echo "🚀 Starting Avaa-AI Voice Interview Application Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [[ ! -f "requirements.txt" ]] || [[ ! -d "web-ui" ]]; then
    print_error "Please run this script from the Avaa-AI project root directory"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check required dependencies
print_status "Checking system dependencies..."

if ! command_exists python3; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

if ! command_exists node; then
    print_error "Node.js is required but not installed"
    exit 1
fi

if ! command_exists npm; then
    print_error "npm is required but not installed"
    exit 1
fi

if ! command_exists ffmpeg; then
    print_warning "ffmpeg not found - audio conversion may not work"
    print_status "Install ffmpeg with: sudo apt-get install ffmpeg (Ubuntu/Debian) or brew install ffmpeg (macOS)"
fi

print_success "System dependencies check completed"

# Kill existing processes
print_status "Cleaning up existing processes..."
pkill -f "python.*run_app.py" 2>/dev/null || true
pkill -f "npm.*run.*dev" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

# Wait a moment for processes to terminate
sleep 2

# Setup Python virtual environment
print_status "Setting up Python virtual environment..."

if [[ ! -d "venv" ]]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
print_success "Virtual environment activated"

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt
print_success "Python dependencies installed"

# Setup Node.js dependencies
print_status "Setting up frontend dependencies..."
cd web-ui

if [[ ! -d "node_modules" ]]; then
    print_status "Installing Node.js dependencies..."
    npm install
    print_success "Node.js dependencies installed"
else
    print_status "Node.js dependencies already installed"
    print_status "Updating dependencies..."
    npm install
fi

cd ..

# Check for environment variables
print_status "Checking environment configuration..."

if [[ ! -f ".env" ]]; then
    print_warning ".env file not found"
    print_status "Please create a .env file with your API keys:"
    print_status "  GOOGLE_API_KEY=your_gemini_api_key"
    print_status "  GEMINI_API_KEY=your_gemini_api_key"
    print_status ""
    read -p "Press Enter to continue anyway, or Ctrl+C to exit and setup .env file..."
else
    print_success "Environment file found"
fi

# Create resume.pdf if it doesn't exist
if [[ ! -f "resume.pdf" ]]; then
    print_warning "resume.pdf not found - creating placeholder"
    echo "This is a placeholder resume file for testing. Please replace with actual resume." > resume.txt
    print_status "Please add a resume.pdf file to the project root for interview functionality"
fi

# Start the application
print_status "Starting Avaa-AI Voice Interview Application..."

echo ""
echo "=================================="
echo "🎤 AVAA-AI VOICE INTERVIEW SYSTEM"
echo "=================================="
echo ""

# Function to start backend
start_backend() {
    print_status "Starting Python backend server..."
    source venv/bin/activate
    python run_app.py
}

# Start backend in background
start_backend &
BACKEND_PID=$!

# Wait for backend to start
print_status "Waiting for backend to initialize..."
sleep 5

# Check if backend is still running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    print_error "Backend failed to start"
    exit 1
fi

print_success "Backend started successfully (PID: $BACKEND_PID)"

# Function to cleanup on exit
cleanup() {
    print_status "Shutting down application..."
    kill $BACKEND_PID 2>/dev/null || true
    pkill -f "python.*run_app.py" 2>/dev/null || true
    pkill -f "npm.*run.*dev" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    print_success "Application stopped"
    exit 0
}

# Set trap to cleanup on script termination
trap cleanup SIGINT SIGTERM

print_success "🎉 Avaa-AI Voice Interview Application is now running!"
echo ""
echo "📱 Frontend: The app will automatically open in your browser"
echo "🔧 Backend: Running with WebSocket support"
echo "🎙️ Voice Interview: Ready for use"
echo ""
echo "🛑 To stop the application, press Ctrl+C"
echo ""

# Keep script running and show status
while true; do
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        print_error "Backend process died unexpectedly"
        exit 1
    fi

    sleep 10
done