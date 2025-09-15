#!/bin/bash

# =============================================================================
# Unified AI Tools - Complete Setup and Launch Script
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to kill existing processes
cleanup_existing_processes() {
    print_status "Cleaning up existing processes..."
    
    # Kill existing Flask processes on port 8000
    if lsof -ti:8000 >/dev/null 2>&1; then
        print_warning "Killing existing Flask server on port 8000"
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    fi
    
    # Kill existing React processes on port 3000
    if lsof -ti:3000 >/dev/null 2>&1; then
        print_warning "Killing existing React server on port 3000"
        lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    fi
    
    sleep 2
}

# Function to setup Python environment
setup_python_env() {
    print_header "🐍 Setting up Python Virtual Environment"
    
    # Check if Python 3 is installed
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    # Get Python version
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Found Python $PYTHON_VERSION"
    
    # Remove existing venv if it exists
    if [ -d "venv" ]; then
        print_warning "Removing existing virtual environment"
        rm -rf venv
    fi
    
    # Create new virtual environment
    print_status "Creating new virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    print_success "Python virtual environment created and activated"
}

# Function to install Python dependencies
install_python_deps() {
    print_header "📦 Installing Python Dependencies"
    
    # Install main requirements
    if [ -f "requirements.txt" ]; then
        print_status "Installing main requirements..."
        pip install -r requirements.txt
    else
        print_warning "requirements.txt not found, installing core dependencies..."
        pip install flask flask-cors python-dotenv google-generativeai google-genai
    fi
    
    # Install AVA voice dependencies
    if [ -f "ai-modules/AVA_voice/requirements.txt" ]; then
        print_status "Installing AVA Voice Interview dependencies..."
        # Filter out built-in modules and install only external packages
        grep -E "(PyPDF2|python-dotenv|google-genai|google-generativeai|pyaudio|keyboard)" ai-modules/AVA_voice/requirements.txt > temp_requirements.txt || true
        if [ -s temp_requirements.txt ]; then
            pip install -r temp_requirements.txt
        fi
        rm -f temp_requirements.txt
    fi
    
    # Install additional dependencies that might be needed
    print_status "Installing additional AI dependencies..."
    pip install beautifulsoup4 selenium webdriver-manager fake-useragent lxml requests pandas numpy || true
    
    print_success "Python dependencies installed"
}

# Function to setup Node.js environment
setup_node_env() {
    print_header "📱 Setting up Node.js Environment"
    
    # Check if Node.js is installed
    if ! command_exists node; then
        print_error "Node.js is not installed. Please install Node.js 16+ first."
        exit 1
    fi
    
    # Check if npm is installed
    if ! command_exists npm; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    print_status "Found Node.js $NODE_VERSION and npm $NPM_VERSION"
    
    # Navigate to web-ui directory
    cd web-ui
    
    # Install Node.js dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Go back to root directory
    cd ..
    
    print_success "Node.js environment setup complete"
}

# Function to check environment file
check_env_file() {
    print_header "🔑 Checking Environment Configuration"
    
    if [ ! -f ".env" ]; then
        print_error ".env file not found!"
        print_status "Creating .env template..."
        cat > .env << EOF
# Gemini API Key (Required)
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Other API keys
GOOGLE_API_KEY=your_google_api_key_here
SERPAPI_KEY=your_serpapi_key_here
EOF
        print_warning "Please edit .env file and add your API keys before running again."
        exit 1
    fi
    
    # Check if GEMINI_API_KEY is set
    if grep -q "GEMINI_API_KEY=your_gemini_api_key_here" .env || ! grep -q "GEMINI_API_KEY=" .env; then
        print_warning "GEMINI_API_KEY not properly configured in .env file"
        print_status "Please set your Gemini API key in .env file"
    else
        print_success "Environment configuration looks good"
    fi
}

# Function to create resume.pdf if it doesn't exist
setup_resume_file() {
    print_header "📄 Setting up Resume File"
    
    if [ ! -f "resume.pdf" ]; then
        print_status "Creating placeholder resume.pdf for voice interview..."
        # Create a simple placeholder PDF using Python
        python3 -c "
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

try:
    c = canvas.Canvas('resume.pdf', pagesize=letter)
    c.drawString(100, 750, 'Sample Resume')
    c.drawString(100, 700, 'Name: John Doe')
    c.drawString(100, 680, 'Email: john.doe@email.com')
    c.drawString(100, 660, 'Skills: Python, React, AI/ML')
    c.drawString(100, 640, 'Experience: Software Developer')
    c.drawString(100, 600, 'This is a placeholder resume for testing.')
    c.drawString(100, 580, 'Please replace with your actual resume.')
    c.save()
    print('✅ Placeholder resume.pdf created')
except ImportError:
    print('⚠️ reportlab not available, creating text file instead')
    with open('resume.txt', 'w') as f:
        f.write('Sample Resume\\nName: John Doe\\nEmail: john.doe@email.com\\nSkills: Python, React, AI/ML\\nExperience: Software Developer')
" 2>/dev/null || echo "⚠️ Could not create placeholder resume, please add your resume.pdf manually"
    fi
}

# Function to start the backend
start_backend() {
    print_header "🚀 Starting Backend Server"
    
    # Activate virtual environment
    source venv/bin/activate
    
    print_status "Starting Flask backend on http://localhost:8000..."
    
    # Start backend in background
    nohup python3 run_app.py > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    
    # Wait for backend to start
    print_status "Waiting for backend to start..."
    sleep 5
    
    # Check if backend is running
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        print_success "Backend server started successfully (PID: $BACKEND_PID)"
        echo $BACKEND_PID > backend.pid
    else
        print_error "Backend failed to start. Check logs/backend.log"
        exit 1
    fi
}

# Function to start the frontend
start_frontend() {
    print_header "🎨 Starting Frontend Server"
    
    # Navigate to web-ui directory
    cd web-ui
    
    print_status "Starting React frontend on http://localhost:3000..."
    
    # Start frontend in background
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    # Go back to root directory
    cd ..
    
    # Wait for frontend to start
    print_status "Waiting for frontend to start..."
    sleep 8
    
    # Check if frontend is running
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend server started successfully (PID: $FRONTEND_PID)"
        echo $FRONTEND_PID > frontend.pid
    else
        print_warning "Frontend may still be starting. Check logs/frontend.log if issues persist."
    fi
}

# Function to display final status
display_final_status() {
    print_header "🎉 Unified AI Tools - Setup Complete!"
    
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                   SERVER STATUS                  ║${NC}"
    echo -e "${CYAN}╠══════════════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║${NC} 🌐 Frontend: ${GREEN}http://localhost:3000${NC}              ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC} 🔧 Backend:  ${GREEN}http://localhost:8000${NC}              ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC} 📊 API Health: ${GREEN}http://localhost:8000/api/health${NC}  ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
    echo ""
    
    print_success "All services are running!"
    echo ""
    echo -e "${YELLOW}Available Features:${NC}"
    echo -e "  🎯 Career Guidance AI"
    echo -e "  📚 Learning Roadmap Generator"
    echo -e "  🔍 Job Search Engine"
    echo -e "  📄 Resume Generator"
    echo -e "  🎙️ AVA Voice Interview System"
    echo ""
    echo -e "${BLUE}Control Commands:${NC}"
    echo -e "  📋 View backend logs: ${CYAN}tail -f logs/backend.log${NC}"
    echo -e "  📋 View frontend logs: ${CYAN}tail -f logs/frontend.log${NC}"
    echo -e "  🛑 Stop all services: ${CYAN}./stop.sh${NC} (or Ctrl+C)"
    echo ""
    echo -e "${GREEN}🚀 Open your browser to http://localhost:3000 to get started!${NC}"
}

# Function to create stop script
create_stop_script() {
    cat > stop.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping Unified AI Tools servers..."

# Kill backend
if [ -f backend.pid ]; then
    BACKEND_PID=$(cat backend.pid)
    kill $BACKEND_PID 2>/dev/null && echo "✅ Backend stopped" || echo "⚠️ Backend already stopped"
    rm -f backend.pid
fi

# Kill frontend
if [ -f frontend.pid ]; then
    FRONTEND_PID=$(cat frontend.pid)
    kill $FRONTEND_PID 2>/dev/null && echo "✅ Frontend stopped" || echo "⚠️ Frontend already stopped"
    rm -f frontend.pid
fi

# Kill any remaining processes on the ports
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

echo "🎯 All services stopped"
EOF
    chmod +x stop.sh
}

# Main execution
main() {
    print_header "🚀 Unified AI Tools - Complete Setup & Launch"
    print_header "============================================="
    
    # Create logs directory
    mkdir -p logs
    
    # Cleanup existing processes
    cleanup_existing_processes
    
    # Setup Python environment
    setup_python_env
    
    # Install Python dependencies
    install_python_deps
    
    # Setup Node.js environment
    setup_node_env
    
    # Check environment configuration
    check_env_file
    
    # Setup resume file for voice interview
    setup_resume_file
    
    # Create stop script
    create_stop_script
    
    # Start backend
    start_backend
    
    # Start frontend
    start_frontend
    
    # Display final status
    display_final_status
    
    # Keep script running and handle Ctrl+C
    trap 'echo -e "\n🛑 Shutting down..."; ./stop.sh; exit 0' INT
    
    print_status "Press Ctrl+C to stop all services"
    
    # Keep the script running
    while true; do
        sleep 1
    done
}

# Run main function
main "$@"