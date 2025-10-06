#!/bin/bash

# BWARM Dashboard - Deployment Preparation Script
# This script prepares the application for deployment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}BWARM Dashboard - Deployment Preparation${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check current directory
if [ ! -f "package.json" ] && [ ! -f "backend/requirements.txt" ]; then
    print_error "Must be run from project root directory"
    exit 1
fi

print_status "Starting deployment preparation..."
echo ""

# ============================================================================
# 1. Environment Check
# ============================================================================
echo -e "${YELLOW}[1/8] Checking environment...${NC}"

if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    cp .env.example .env
    print_warning "Please update .env with production values!"
else
    print_status ".env file exists"
fi

# Check required environment variables
if [ -f ".env" ]; then
    source .env

    if [ "$SECRET_KEY" == "your_secret_key_here_please_change_this_in_production" ]; then
        print_error "SECRET_KEY not changed! Generate with: openssl rand -hex 32"
        exit 1
    fi

    if [ "$DEBUG" == "true" ]; then
        print_warning "DEBUG is enabled. Should be false in production!"
    fi
fi

print_status "Environment check complete"
echo ""

# ============================================================================
# 2. Backend Dependencies
# ============================================================================
echo -e "${YELLOW}[2/8] Checking backend dependencies...${NC}"

if [ -f "backend/requirements.txt" ]; then
    cd backend

    if [ ! -d "venv" ]; then
        print_warning "Virtual environment not found. Creating..."
        python3 -m venv venv
    fi

    source venv/bin/activate
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt > /dev/null 2>&1
    print_status "Backend dependencies installed"

    cd ..
else
    print_warning "Backend not found, skipping..."
fi

echo ""

# ============================================================================
# 3. Frontend Dependencies
# ============================================================================
echo -e "${YELLOW}[3/8] Checking frontend dependencies...${NC}"

if [ -f "frontend/package.json" ]; then
    cd frontend

    if [ ! -d "node_modules" ]; then
        print_warning "Node modules not found. Installing..."
        npm ci
    else
        print_status "Frontend dependencies exist"
    fi

    cd ..
else
    print_warning "Frontend not found, skipping..."
fi

echo ""

# ============================================================================
# 4. Database Migrations
# ============================================================================
echo -e "${YELLOW}[4/8] Checking database migrations...${NC}"

if [ -f "backend/alembic.ini" ]; then
    cd backend
    source venv/bin/activate

    # Check migration status
    echo "Current migration:"
    alembic current

    echo ""
    read -p "Run migrations? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        alembic upgrade head
        print_status "Database migrations applied"
    else
        print_warning "Migrations skipped"
    fi

    cd ..
else
    print_warning "Alembic not configured, skipping..."
fi

echo ""

# ============================================================================
# 5. Build Frontend
# ============================================================================
echo -e "${YELLOW}[5/8] Building frontend...${NC}"

if [ -f "frontend/package.json" ]; then
    cd frontend

    # Build production bundle
    npm run build

    # Show bundle size
    echo ""
    echo "Production bundle sizes:"
    du -sh dist/

    print_status "Frontend build complete"
    cd ..
else
    print_warning "Frontend not found, skipping..."
fi

echo ""

# ============================================================================
# 6. Run Tests
# ============================================================================
echo -e "${YELLOW}[6/8] Running tests...${NC}"

read -p "Run tests before deployment? (Y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    # Backend tests
    if [ -f "backend/pytest.ini" ]; then
        cd backend
        source venv/bin/activate
        echo "Running backend tests..."
        pytest -v
        cd ..
    fi

    # Frontend tests (if they exist)
    if [ -f "frontend/package.json" ]; then
        cd frontend
        if grep -q '"test"' package.json; then
            echo "Running frontend tests..."
            npm test
        fi
        cd ..
    fi

    print_status "Tests complete"
else
    print_warning "Tests skipped"
fi

echo ""

# ============================================================================
# 7. Security Check
# ============================================================================
echo -e "${YELLOW}[7/8] Security checklist...${NC}"

echo ""
echo "Manual security checks:"
echo "  □ SECRET_KEY is strong and unique"
echo "  □ DEBUG is false in production"
echo "  □ CORS only allows production domains"
echo "  □ Database uses SSL connection"
echo "  □ Redis has authentication enabled"
echo "  □ File upload size limits are set"
echo "  □ Rate limiting is enabled"
echo "  □ HTTPS is enforced"
echo ""

read -p "Have you completed all security checks? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_error "Please complete security checks before deploying"
    exit 1
fi

print_status "Security checks confirmed"
echo ""

# ============================================================================
# 8. Generate Deployment Package
# ============================================================================
echo -e "${YELLOW}[8/8] Generating deployment package...${NC}"

DEPLOY_DIR="deploy-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$DEPLOY_DIR"

# Copy backend
if [ -d "backend" ]; then
    cp -r backend "$DEPLOY_DIR/"
    rm -rf "$DEPLOY_DIR/backend/venv"  # Don't include venv
    rm -rf "$DEPLOY_DIR/backend/__pycache__"
    rm -rf "$DEPLOY_DIR/backend/**/__pycache__"
fi

# Copy frontend build
if [ -d "frontend/dist" ]; then
    cp -r frontend/dist "$DEPLOY_DIR/frontend-dist"
fi

# Copy configuration files
cp docker-compose.yml "$DEPLOY_DIR/" 2>/dev/null || true
cp .env.example "$DEPLOY_DIR/"
cp README.md "$DEPLOY_DIR/"
cp DEPLOYMENT.md "$DEPLOY_DIR/"

# Create deployment info
cat > "$DEPLOY_DIR/DEPLOY_INFO.txt" << EOF
Deployment Package
==================
Generated: $(date)
Git Commit: $(git rev-parse HEAD 2>/dev/null || echo "N/A")
Git Branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "N/A")

Contents:
- backend/          Backend application code
- frontend-dist/    Built frontend assets
- docker-compose.yml Docker deployment config
- .env.example      Environment template
- DEPLOYMENT.md     Deployment guide

Next Steps:
1. Copy this package to your server
2. Create .env file from .env.example
3. Run: docker-compose up -d
4. Check: http://your-server:8000/docs
EOF

print_status "Deployment package created: $DEPLOY_DIR"
echo ""

# ============================================================================
# Summary
# ============================================================================
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Preparation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Deployment package: $DEPLOY_DIR"
echo ""
echo "Next steps:"
echo "  1. Review $DEPLOY_DIR/DEPLOY_INFO.txt"
echo "  2. Transfer package to server"
echo "  3. Follow DEPLOYMENT.md guide"
echo "  4. Monitor logs after deployment"
echo ""
echo "Quick deploy commands:"
echo "  scp -r $DEPLOY_DIR user@server:/opt/bwarm/"
echo "  ssh user@server 'cd /opt/bwarm/$DEPLOY_DIR && docker-compose up -d'"
echo ""
