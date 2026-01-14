#!/bin/bash

# PaperStack Installation Verification Script
# This script checks if all dependencies are properly installed

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   PaperStack Installation Verification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Python version
echo -n "Checking Python version... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3.10+ required but not found"
    exit 1
fi

# Check Node.js version
echo -n "Checking Node.js version... "
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js $NODE_VERSION"
else
    echo -e "${RED}✗${NC} Node.js 18+ required but not found"
    exit 1
fi

# Check .env file
echo -n "Checking .env configuration... "
if [ -f .env ]; then
    if grep -q "GOOGLE_API_KEY=" .env && ! grep -q "your_api_key_here" .env; then
        echo -e "${GREEN}✓${NC} API key configured"
    else
        echo -e "${YELLOW}⚠${NC} .env exists but API key not set"
        echo "  Please add your Google API key to .env"
    fi
else
    echo -e "${RED}✗${NC} .env file not found"
    echo "  Run: cp .env.example .env"
    echo "  Then add your Google API key"
    exit 1
fi

# Check Python dependencies
echo -n "Checking Python dependencies... "
if pip show fastapi llama-index google-generativeai chromadb &> /dev/null; then
    echo -e "${GREEN}✓${NC} Core packages installed"
else
    echo -e "${RED}✗${NC} Missing Python packages"
    echo "  Run: pip install -r requirements.txt"
    exit 1
fi

# Check frontend dependencies
echo -n "Checking frontend dependencies... "
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✓${NC} Node modules installed"
else
    echo -e "${YELLOW}⚠${NC} Frontend dependencies not installed"
    echo "  Run: cd frontend && npm install"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓ Installation verification complete!${NC}"
echo ""
echo "To start the application, run:"
echo "  ./start.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
