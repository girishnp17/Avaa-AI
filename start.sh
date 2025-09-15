#!/bin/bash

# =============================================================================
# Unified AI Tools - Quick Start Script (for already set up environments)
# =============================================================================

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting Unified AI Tools...${NC}"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
else
    echo -e "${RED}❌ Virtual environment not found. Run ./setup_and_run.sh first${NC}"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Start backend
echo -e "${BLUE}🔧 Starting backend server...${NC}"
nohup python3 run_app.py > logs/backend.log 2>&1 &
echo $! > backend.pid

# Start frontend
echo -e "${BLUE}🎨 Starting frontend server...${NC}"
cd web-ui
nohup npm run dev > ../logs/frontend.log 2>&1 &
echo $! > ../frontend.pid
cd ..

# Wait for services to start
sleep 8

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                   SERVERS RUNNING                ║${NC}"
echo -e "${CYAN}╠══════════════════════════════════════════════════╣${NC}"
echo -e "${CYAN}║${NC} 🌐 Frontend: ${GREEN}http://localhost:3000${NC}              ${CYAN}║${NC}"
echo -e "${CYAN}║${NC} 🔧 Backend:  ${GREEN}http://localhost:8000${NC}              ${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}🎯 Use ./stop.sh to stop all services${NC}"
echo -e "${GREEN}🚀 Open http://localhost:3000 in your browser!${NC}"