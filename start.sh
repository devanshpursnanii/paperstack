#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting PaperStack...${NC}\n"

# Trap to kill both processes on exit
trap 'echo -e "\n${RED}Shutting down servers...${NC}"; kill $(jobs -p) 2>/dev/null; exit' INT TERM

# Start backend
echo -e "${GREEN}Starting Backend (Port 8000)...${NC}"
cd "$(dirname "$0")" && uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 2

# Start frontend
echo -e "${GREEN}Starting Frontend (Port 3000)...${NC}"
cd frontend && npm run dev &
FRONTEND_PID=$!

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Backend running at http://localhost:8000${NC}"
echo -e "${GREEN}✓ Frontend running at http://localhost:3000${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
echo -e "Press ${RED}Ctrl+C${NC} to stop both servers\n"

# Wait for both processes
wait
