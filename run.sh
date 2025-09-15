#!/bin/bash

# =============================================================================
# Unified AI Tools - Simple Install & Run Script
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Unified AI Tools - Auto Setup & Launch${NC}"
echo "=============================================="

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required commands exist
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

if ! command -v node &> /dev/null; then
    print_error "Node.js is required but not installed"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    print_error "npm is required but not installed"
    exit 1
fi

# Kill any existing processes on ports 3000 and 8000
print_status "Cleaning up existing processes..."
pkill -f "node.*3000" 2>/dev/null || true
pkill -f "python.*8000" 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 2

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python requirements
print_status "Installing Python dependencies..."
pip install flask flask-cors python-dotenv google-generativeai google-genai \
    beautifulsoup4 selenium webdriver-manager fake-useragent lxml requests \
    pandas numpy PyPDF2 pyaudio keyboard reportlab || true

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
cd web-ui
npm install
cd ..

# Create logs directory
mkdir -p logs

# Create resume.pdf if it doesn't exist
if [ ! -f "resume.pdf" ]; then
    print_status "Creating sample resume.pdf..."
    python3 -c "
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    c = canvas.Canvas('resume.pdf', pagesize=letter)
    c.drawString(100, 750, 'Sample Resume')
    c.drawString(100, 700, 'Name: John Doe')
    c.drawString(100, 680, 'Email: john.doe@email.com')
    c.drawString(100, 660, 'Skills: Python, React, AI/ML')
    c.drawString(100, 640, 'Experience: Software Developer')
    c.save()
    print('✅ Sample resume.pdf created')
except:
    with open('resume.pdf', 'w') as f:
        f.write('%PDF-1.4\\n1 0 obj\\n<<\\n/Type /Catalog\\n/Pages 2 0 R\\n>>\\nendobj\\n2 0 obj\\n<<\\n/Type /Pages\\n/Kids [3 0 R]\\n/Count 1\\n>>\\nendobj\\n3 0 obj\\n<<\\n/Type /Page\\n/Parent 2 0 R\\n/MediaBox [0 0 612 792]\\n>>\\nendobj\\nxref\\n0 4\\n0000000000 65535 f \\n0000000010 00000 n \\n0000000053 00000 n \\n0000000125 00000 n \\ntrailer\\n<<\\n/Size 4\\n/Root 1 0 R\\n>>\\nstartxref\\n174\\n%%EOF')
    print('✅ Basic resume.pdf created')
" 2>/dev/null || echo "⚠️ Could not create resume.pdf"
fi

# Check .env file
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    echo "GEMINI_API_KEY=your_api_key_here" > .env
    print_status "Created .env template. Please add your API key."
    exit 1
fi

# Start backend
print_status "Starting backend server..."
nohup python3 run_app.py > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid

# Wait for backend to start
print_status "Waiting for backend to initialize..."
sleep 5

# Start frontend
print_status "Starting frontend server..."
cd web-ui
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
cd ..

# Wait for frontend to start
print_status "Waiting for frontend to initialize..."
sleep 8

# Display final status
echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           🎉 READY TO USE!             ║${NC}"
echo -e "${GREEN}╠════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║${NC} 🌐 Frontend: http://localhost:3000   ${GREEN}║${NC}"
echo -e "${GREEN}║${NC} 🔧 Backend:  http://localhost:8000   ${GREEN}║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
print_success "All services are running!"
echo ""
echo -e "${YELLOW}Features Available:${NC}"
echo "  🎯 Career Guidance AI"
echo "  📚 Learning Roadmap Generator"
echo "  🔍 Job Search Engine"
echo "  📄 Resume Generator"
echo "  🎙️ AVA Voice Interview System"
echo ""
echo -e "${BLUE}To stop all services: Ctrl+C or run: pkill -f 'node.*3000'; pkill -f 'python.*8000'${NC}"
echo ""
echo -e "${GREEN}🚀 Open http://localhost:3000 in your browser!${NC}"

# Keep script running and handle Ctrl+C
trap 'echo -e "\n🛑 Shutting down..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; pkill -f "node.*3000"; pkill -f "python.*8000"; exit 0' INT

# Keep the script running
while true; do
    sleep 1
done