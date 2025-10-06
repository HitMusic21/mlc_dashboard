# BWARM Dashboard

A full-stack web application for matching music publisher catalogs against BWARM's musical works database. Built with FastAPI, React, and PostgreSQL.

## Features

- **Musical Works Database**: Browse and search BWARM's comprehensive database of musical works with metadata, contributors, and rights information
- **Catalog Matching**: Upload music catalogs in multiple formats (CSV, Excel, JSON, XML) and match against BWARM works using advanced similarity algorithms
- **Real-time Processing**: Asynchronous catalog processing with progress tracking and status updates
- **Confidence Scoring**: Multi-level confidence indicators (high/medium/low) for match results
- **Role-based Access**: Publisher and admin roles with appropriate permissions
- **Export Capabilities**: Download match results in CSV or Excel format
- **Full-text Search**: Elasticsearch-powered search across work titles and contributors
- **Analytics Dashboard**: View statistics and trends for works and matches

## Tech Stack

### Backend
- **FastAPI 0.118**: Modern async web framework with automatic API documentation
- **SQLModel 0.0.25**: Type-safe ORM combining SQLAlchemy and Pydantic
- **PostgreSQL 15+**: Primary database with asyncpg driver
- **Celery 5.4**: Async task queue for catalog processing
- **Redis 7**: Message broker and caching layer
- **Elasticsearch 8**: Full-text search engine
- **JWT Authentication**: Secure token-based auth with refresh tokens

### Frontend
- **React 19**: UI framework with hooks
- **TypeScript 5.9**: Type-safe JavaScript
- **Vite 7.1**: Lightning-fast build tool and dev server
- **TanStack Query**: Server state management with caching
- **React Router**: Client-side routing
- **Axios**: HTTP client with interceptors

### Matching Algorithms
- **Jaro-Winkler**: String similarity for titles
- **Levenshtein Distance**: Edit distance for fuzzy matching
- **TF-IDF Cosine Similarity**: Semantic similarity for text fields
- **Multi-factor Scoring**: Combines title, contributor, duration, and ISWC matches

## Quick Start

**Fastest way to get started:**

```bash
# Clone and enter directory
git clone <repository-url>
cd mlc_dashboard

# Run the quick start script
./quick-start.sh
```

The script will guide you through starting the full stack, backend only, frontend only, or running tests.

## Getting Started

### Prerequisites

- Docker & Docker Compose (recommended)
- OR:
  - Python 3.11+
  - Node.js 20+
  - PostgreSQL 15+
  - Redis 7+
  - Elasticsearch 8+ (optional, for full-text search)

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mlc_dashboard
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env and update SECRET_KEY and other values
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Initialize database**
   ```bash
   docker-compose exec backend python scripts/seed_database.py
   ```

5. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Alternative API Docs: http://localhost:8000/redoc

6. **Login with test accounts**
   - Admin: `admin@test.com` / `password`
   - Publisher: `publisher@test.com` / `password`

### Manual Setup (Development)

#### Backend Setup

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start PostgreSQL, Redis, Elasticsearch**
   ```bash
   # Using Docker for services only
   docker-compose up -d postgres redis elasticsearch
   ```

4. **Set up environment**
   ```bash
   cp ../.env.example ../.env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python scripts/seed_database.py
   ```

6. **Run backend server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Start Celery worker (separate terminal)**
   ```bash
   celery -A celery_app worker --loglevel=info -Q catalog,cleanup
   ```

8. **Start Celery beat (separate terminal, optional)**
   ```bash
   celery -A celery_app beat --loglevel=info
   ```

#### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Create environment file**
   ```bash
   echo "VITE_API_URL=http://localhost:8000/api/v1" > .env
   ```

3. **Run development server**
   ```bash
   npm run dev
   ```

## Project Structure

```
mlc_dashboard/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API route handlers
│   │   │   └── routes/        # Endpoint definitions
│   │   ├── core/              # Core config & security
│   │   ├── crud/              # Database operations
│   │   ├── db/                # Database session management
│   │   ├── models/            # SQLModel database models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── services/          # Business logic services
│   │   │   ├── matching/      # Matching algorithms
│   │   │   └── parsers/       # File format parsers
│   │   └── tasks/             # Celery async tasks
│   ├── scripts/               # Utility scripts
│   ├── main.py                # FastAPI app entry point
│   ├── celery_app.py          # Celery configuration
│   └── requirements.txt       # Python dependencies
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # Reusable React components
│   │   │   ├── common/        # Generic components
│   │   │   ├── layout/        # Layout components
│   │   │   ├── results/       # Match results components
│   │   │   └── upload/        # File upload components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── pages/             # Page components
│   │   ├── services/          # API client & services
│   │   ├── types/             # TypeScript type definitions
│   │   ├── App.tsx            # Main app component
│   │   └── main.tsx           # React entry point
│   └── package.json           # Node dependencies
├── docker-compose.yml         # Docker services configuration
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/login` - Login with email/password
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Get current user

#### Musical Works
- `GET /api/v1/works` - List works (with search & filters)
- `GET /api/v1/works/{work_id}` - Get work details
- `GET /api/v1/works/statistics` - Dashboard statistics

#### Catalog Matching
- `POST /api/v1/catalog/upload` - Upload catalog file
- `GET /api/v1/catalog/uploads` - List user uploads
- `GET /api/v1/catalog/uploads/{upload_id}` - Get upload status
- `GET /api/v1/catalog/uploads/{upload_id}/results` - Get match results
- `GET /api/v1/catalog/uploads/{upload_id}/export` - Export results

#### Admin (requires admin role)
- `GET /api/v1/admin/uploads` - List all uploads
- `GET /api/v1/admin/users` - List all users
- `DELETE /api/v1/admin/uploads/{upload_id}` - Delete upload

## Catalog Upload Format

The system supports multiple file formats with flexible field mapping.

### Required Fields
- **title**: Track title (required)
- **artist** OR **composer**: At least one contributor (required)

### Optional Fields
- **iswc**: International Standard Musical Work Code
- **duration**: Duration in seconds or MM:SS format
- **year**: Release/composition year
- **alternate_titles**: Alternative track names

### Example CSV Format
```csv
title,artist,composer,iswc,duration,year
"Bohemian Rhapsody","Queen","Freddie Mercury","T-070.244.478-1",354,1975
"Imagine","John Lennon","John Lennon, Yoko Ono","T-070.244.479-1","3:03",1971
```

### Example JSON Format
```json
[
  {
    "title": "Bohemian Rhapsody",
    "artist": "Queen",
    "composer": "Freddie Mercury",
    "iswc": "T-070.244.478-1",
    "duration": 354,
    "year": 1975
  }
]
```

## Development

### Code Quality

**Backend (Python)**
```bash
# Format code
black backend/
isort backend/

# Lint code
flake8 backend/

# Run tests
pytest backend/tests/
```

**Frontend (TypeScript)**
```bash
# Lint code
npm run lint

# Type check
npm run type-check

# Build for production
npm run build
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret (change in production!)
- `REDIS_HOST`, `REDIS_PORT`: Redis configuration
- `ELASTICSEARCH_HOST`, `ELASTICSEARCH_PORT`: Elasticsearch configuration
- `MAX_UPLOAD_SIZE_MB`: Maximum catalog file size
- `MATCH_CONFIDENCE_THRESHOLD`: Minimum match confidence (0.0-1.0)

## Deployment

### Production Considerations

1. **Security**
   - Change `SECRET_KEY` to a strong random value
   - Set `DEBUG=false`
   - Use HTTPS only
   - Configure proper CORS origins
   - Use environment variables for secrets

2. **Database**
   - Use managed PostgreSQL service (AWS RDS, Cloud SQL, etc.)
   - Enable connection pooling
   - Set up automated backups
   - Configure appropriate indexes

3. **Caching & Queue**
   - Use managed Redis service
   - Configure Redis persistence
   - Set up Celery worker auto-scaling

4. **Search**
   - Use managed Elasticsearch service
   - Configure proper cluster settings
   - Set up index templates

5. **File Storage**
   - Use S3 or similar object storage for uploaded files
   - Configure lifecycle policies for old uploads

6. **Monitoring**
   - Set up application performance monitoring
   - Configure logging aggregation
   - Set up error tracking (Sentry, etc.)
   - Monitor Celery queue health

## Documentation

Comprehensive documentation is available in the following files:

- **[API Documentation](./API_DOCUMENTATION.md)** - Complete REST API reference with examples
- **[Component Documentation](./COMPONENTS.md)** - Frontend component library guide
- **[User Guide](./USER_GUIDE.md)** - End-user documentation and tutorials
- **[Deployment Guide](./DEPLOYMENT.md)** - Production deployment instructions
- **[Performance Report](./PERFORMANCE.md)** - Bundle analysis and optimization guide
- **[Production Readiness](./PRODUCTION_READINESS.md)** - Pre-launch checklist
- **[Project Summary](./PROJECT_SUMMARY.md)** - Complete implementation overview

### Quick Reference Scripts

- **`./quick-start.sh`** - Interactive development environment setup
- **`./scripts/deploy-prepare.sh`** - Deployment preparation automation
- **`.github/workflows/ci-cd.yml`** - CI/CD pipeline configuration

## Testing

### E2E Tests with Playwright

```bash
cd frontend

# Install browsers (first time only)
npx playwright install

# Run all tests
npx playwright test

# Run specific test file
npx playwright test tests/e2e/auth.spec.ts

# Run in UI mode (interactive)
npx playwright test --ui

# Run in headed mode (see browser)
npx playwright test --headed
```

**Test Coverage:**
- 83 E2E tests covering all major user flows
- Multi-browser testing (Chrome, Firefox, Safari, Edge)
- Mobile device testing (Pixel 5, iPhone 12)

### Backend Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

## CI/CD Pipeline

The project includes a complete GitHub Actions workflow (`.github/workflows/ci-cd.yml`):

- **Automated Testing**: Backend, frontend, and E2E tests
- **Security Scanning**: Trivy vulnerability scanning
- **Build & Deploy**: Automated Docker image builds
- **Environment Deployments**:
  - Staging: Auto-deploy on `develop` branch
  - Production: Manual approval on `main` branch

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]

## Support

For issues and questions, please [create an issue](https://github.com/your-org/mlc_dashboard/issues).
# mlc_dashboard
# mlc_dashboard
