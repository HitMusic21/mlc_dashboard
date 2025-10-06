#!/bin/bash

# FastAPI + React Project Setup Script for mlc_dashboard
# Run this script from your project root directory

set -e  # Exit on any error

echo "🚀 Setting up mlc_dashboard - FastAPI + React project"

# 1. Create and activate Python virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo "✅ Virtual environment created and activated"

# 2. Install backend Python dependencies
echo "📦 Installing backend Python dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn[standard] sqlmodel asyncpg pydantic python-multipart python-dotenv
pip freeze > requirements.txt
echo "✅ Backend dependencies installed"

# 3. Initialize React app with Vite and TypeScript
echo "⚛️  Creating React app with Vite and TypeScript..."
npm create vite@latest frontend -- --template react-ts
echo "✅ React app created"

# 4. Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
npm install axios zustand
npm install -D tailwindcss postcss autoprefixer @types/node
npx tailwindcss init -p
# Install shadcn/ui
npx shadcn-ui@latest init --yes --defaults
cd ..
echo "✅ Frontend dependencies installed"

# 5. Initialize git repository and create .gitignore
echo "🔧 Initializing git repository..."
git init
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
venv/
env/
ENV/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.DS_Store
.vscode/

# Frontend build
frontend/dist/
frontend/build/

# Database
*.db
*.sqlite
*.sqlite3

# IDE
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
EOF
echo "✅ Git repository initialized with .gitignore"

# 6. Create .env file with PostgreSQL placeholders
echo "🔧 Creating .env file..."
cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/mlc_dashboard
POSTGRES_USER=mlc_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=mlc_dashboard

# FastAPI Configuration
SECRET_KEY=your-secret-key-here-generate-a-secure-one
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# CORS
FRONTEND_URL=http://localhost:5173

# Optional: Add other service configurations here
# REDIS_URL=redis://localhost:6379
# JWT_SECRET=your-jwt-secret
EOF
echo "✅ .env file created with placeholders"

# 7. Create basic project structure
echo "🏗️  Creating project structure..."
mkdir -p backend/{app,tests}
mkdir -p backend/app/{api,core,models,schemas,crud,db}

# Create basic FastAPI main.py
cat > backend/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="MLC Dashboard API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "MLC Dashboard API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
EOF

echo "✅ Project structure created"

# 8. Create docker-compose for PostgreSQL
echo "🐳 Creating docker-compose.yml for PostgreSQL..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: mlc_dashboard_postgres
    environment:
      POSTGRES_USER: mlc_user
      POSTGRES_PASSWORD: your_secure_password
      POSTGRES_DB: mlc_dashboard
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: mlc_dashboard_redis
    ports:
      - "6379:6379"
    restart: unless-stopped

volumes:
  postgres_data:
EOF
echo "✅ docker-compose.yml created"

# 9. Create package.json script for easier management
echo "🔧 Creating package.json for project management..."
cat > package.json << 'EOF'
{
  "name": "mlc_dashboard",
  "version": "1.0.0",
  "description": "FastAPI + React Dashboard",
  "scripts": {
    "dev:backend": "cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000",
    "dev:frontend": "cd frontend && npm run dev",
    "dev": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\"",
    "build:frontend": "cd frontend && npm run build",
    "install:frontend": "cd frontend && npm install",
    "docker:up": "docker-compose up -d",
    "docker:down": "docker-compose down"
  },
  "devDependencies": {
    "concurrently": "^8.2.0"
  }
}
EOF
npm install
echo "✅ Project package.json created"

echo ""
echo "🎉 Setup completed! Your mlc_dashboard project is ready."
echo ""
echo "📋 Next steps:"
echo "1. Review and update the .env file with your actual database credentials"
echo "2. Start PostgreSQL: docker-compose up -d"
echo "3. Start backend server: source venv/bin/activate && cd backend && uvicorn main:app --reload"
echo "4. Start frontend server: cd frontend && npm run dev"
echo ""
echo "🔗 URLs:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Useful commands:"
echo "   # Start both servers concurrently"
echo "   npm run dev"
echo "   "
echo "   # Start database"
echo "   docker-compose up -d"
echo "   "
echo "   # Stop database"
echo "   docker-compose down"
echo "   "
echo "   # Install frontend dependencies"
echo "   npm run install:frontend"
echo ""
echo "Happy coding! 🚀"