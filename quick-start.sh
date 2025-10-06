#!/bin/bash

# BWARM Dashboard - Quick Start Script
# Gets the application running locally in development mode

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}BWARM Dashboard - Quick Start${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found:${NC} $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found:${NC} $(node --version)"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠ PostgreSQL client not found. You'll need PostgreSQL running.${NC}"
else
    echo -e "${GREEN}✓ PostgreSQL client found${NC}"
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠ Docker not found. Services will need to be run manually.${NC}"
else
    echo -e "${GREEN}✓ Docker found:${NC} $(docker --version)"
fi

echo ""

# Ask user what they want to do
echo "Quick start options:"
echo "  1) Full stack (Docker - Backend + Frontend + Services)"
echo "  2) Backend only (Python)"
echo "  3) Frontend only (Node.js)"
echo "  4) Run tests"
echo "  5) Exit"
echo ""
read -p "Choose an option (1-5): " choice

case $choice in
  1)
    echo -e "\n${GREEN}Starting full stack with Docker...${NC}\n"

    # Check if .env exists
    if [ ! -f ".env" ]; then
        echo "Creating .env from template..."
        cp .env.example .env
        echo -e "${YELLOW}⚠ Please update .env with your configuration${NC}"
    fi

    # Start services
    docker-compose up -d postgres redis
    echo "Waiting for services to be ready..."
    sleep 5

    # Start backend
    echo "Starting backend..."
    cd backend
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1

    # Run migrations
    alembic upgrade head

    # Start backend server
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..

    # Start frontend
    echo "Starting frontend..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    npm run dev &
    FRONTEND_PID=$!
    cd ..

    echo ""
    echo -e "${GREEN}✓ Full stack started!${NC}"
    echo ""
    echo "Services running:"
    echo "  • Frontend:  http://localhost:5173"
    echo "  • Backend:   http://localhost:8000"
    echo "  • API Docs:  http://localhost:8000/docs"
    echo "  • PostgreSQL: localhost:5432"
    echo "  • Redis:     localhost:6379"
    echo ""
    echo "Press Ctrl+C to stop all services"

    # Wait for Ctrl+C
    trap "kill $BACKEND_PID $FRONTEND_PID; docker-compose down; exit" INT
    wait
    ;;

  2)
    echo -e "\n${GREEN}Starting backend only...${NC}\n"

    cd backend

    # Create virtual environment if needed
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate and install dependencies
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt

    # Run migrations
    echo "Running database migrations..."
    alembic upgrade head

    # Start server
    echo ""
    echo -e "${GREEN}Starting backend server...${NC}"
    echo "API will be available at: http://localhost:8000"
    echo "API docs available at: http://localhost:8000/docs"
    echo ""
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ;;

  3)
    echo -e "\n${GREEN}Starting frontend only...${NC}\n"

    cd frontend

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "Installing dependencies..."
        npm install
    fi

    # Start dev server
    echo ""
    echo -e "${GREEN}Starting frontend dev server...${NC}"
    echo "Frontend will be available at: http://localhost:5173"
    echo ""
    npm run dev
    ;;

  4)
    echo -e "\n${GREEN}Running tests...${NC}\n"

    # Backend tests
    echo "Running backend tests..."
    cd backend
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    pytest -v
    cd ..

    echo ""

    # Frontend tests
    echo "Running frontend linting..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        npm install > /dev/null 2>&1
    fi
    npm run lint
    cd ..

    echo ""

    # E2E tests
    read -p "Run E2E tests? (requires backend running) (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd frontend
        npx playwright test
        cd ..
    fi

    echo -e "\n${GREEN}✓ Tests complete${NC}"
    ;;

  5)
    echo "Exiting..."
    exit 0
    ;;

  *)
    echo -e "${RED}Invalid option${NC}"
    exit 1
    ;;
esac
