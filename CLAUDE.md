# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **mlc_dashboard**, a full-stack web application using:
- **Backend**: FastAPI with SQLModel (PostgreSQL via asyncpg)
- **Frontend**: React 19 + TypeScript + Vite

The project was initialized using the setup.sh script but backend implementation has not yet been created (only frontend is set up).

## Development Commands

### Backend (FastAPI)
The backend directory structure is planned but not yet created. When implemented:
```bash
# Activate virtual environment (required for all Python commands)
source venv/bin/activate

# Run backend dev server (from project root, after backend is implemented)
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Backend will be available at:
# - API: http://localhost:8000
# - Auto-generated docs: http://localhost:8000/docs
# - Alternative docs: http://localhost:8000/redoc
```

### Frontend (React + Vite)
```bash
# Run frontend dev server
cd frontend && npm run dev
# Available at http://localhost:5173

# Build for production
cd frontend && npm run build

# Lint frontend code
cd frontend && npm run lint

# Install frontend dependencies
cd frontend && npm install
```

### Database (PostgreSQL)
The setup.sh script creates a docker-compose.yml for PostgreSQL, but it's not currently in the repository.
When needed:
```bash
# Start PostgreSQL container
docker-compose up -d

# Stop containers
docker-compose down
```

### Code Quality (Python)

**Formatting:**
```bash
# Format Python code with Black (line length: 100)
black backend/

# Sort imports with isort
isort backend/
```

**Linting:**
```bash
# Lint with flake8 (configured in .flake8)
flake8 backend/
```

Configuration enforces:
- Line length: 100 characters (Black and isort aligned)
- Import sorting: STDLIB → THIRDPARTY → FIRSTPARTY
- First-party imports: `mlc_dashboard` package
- Black-compatible settings (E203, W503 ignored)

## Architecture

### Backend Structure (Planned)
```
backend/
├── main.py              # FastAPI app entry point with CORS
├── app/
│   ├── api/            # API route handlers
│   ├── core/           # Core config, security, utilities
│   ├── models/         # SQLModel database models
│   ├── schemas/        # Pydantic schemas for API requests/responses
│   ├── crud/           # Database operations
│   └── db/             # Database connection and session management
└── tests/              # Test files
```

### Frontend Structure
```
frontend/
├── src/
│   ├── App.tsx         # Main app component
│   ├── main.tsx        # React entry point
│   ├── assets/         # Static assets
│   └── ...             # Additional components/pages to be organized
├── public/             # Public static files
└── vite.config.ts      # Vite configuration
```

### Key Technologies

**Backend:**
- FastAPI 0.118.0 - Modern async web framework
- SQLModel 0.0.25 - SQLAlchemy + Pydantic for database models
- asyncpg 0.30.0 - Async PostgreSQL driver
- uvicorn 0.37.0 - ASGI server
- Pydantic 2.11.10 - Data validation

**Frontend:**
- React 19.1.1 - UI library
- TypeScript 5.9.3 - Type safety
- Vite 7.1.7 - Build tool and dev server
- ESLint - Code linting

### Environment Configuration

Environment variables are managed via `.env` file (not in repository). Required variables:
- `DATABASE_URL` - PostgreSQL connection string
- `FRONTEND_URL` - CORS origin (default: http://localhost:5173)
- `SECRET_KEY` - API secret key
- `API_HOST` / `API_PORT` - Backend server config
- `DEBUG` - Debug mode flag

### CORS Setup

The FastAPI backend (when implemented) will allow CORS from the frontend URL specified in `.env`, enabling local development with separate dev servers on different ports.

## Project Initialization

This project uses Specify for project planning and task management. The `.specify/` directory contains templates for specifications, plans, and tasks.

## Development Workflow

1. Ensure virtual environment is activated for Python work: `source venv/bin/activate`
2. Frontend and backend run on separate dev servers (5173 and 8000)
3. Database runs in Docker container (PostgreSQL on 5432)
4. Use Black and isort for Python formatting before committing
5. Use ESLint for frontend code quality
