"""BWARM Dashboard FastAPI application."""

import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.middleware.activity_logger import ActivityLoggerMiddleware
from app.api.middleware.rate_limiter import limiter, rate_limit_exceeded_handler
from app.api.middleware.security_headers import SecurityHeadersMiddleware
from app.api.routes import (
    admin,
    auth,
    catalog,
    notifications,
    preferences,
    saved_searches,
    search,
    works,
)
from app.core.config import settings
from app.core.exceptions import (
    database_exception_handler,
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.db.init_db import check_db_connection, init_db_data
from app.db.session import AsyncSessionLocal, close_db, init_db
from app.services.search_service import search_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="BWARM Dashboard API",
    version="1.0.0",
    description="""
# BWARM Dashboard API

A comprehensive API for music catalog matching against BWARM's musical works database.

## Features

* 🔐 **JWT Authentication** - Secure token-based authentication with refresh tokens
* 🎵 **Musical Works Database** - Search and browse musical works with metadata
* 📤 **Catalog Matching** - Upload catalogs in multiple formats (CSV, Excel, JSON, XML)
* 🎯 **Multi-Algorithm Matching** - Jaro-Winkler, Levenshtein, and TF-IDF similarity
* 📊 **Confidence Scoring** - High/medium/low confidence levels for matches
* 📥 **Export Results** - Download match results in CSV or Excel format
* 👥 **Role-Based Access** - Publisher and admin roles with appropriate permissions
* 🔍 **Full-Text Search** - Elasticsearch-powered search across works

## Authentication Flow

1. **Login** - POST `/api/v1/auth/login` with email/password
2. **Receive Tokens** - Get access_token (30 min) and refresh_token (7 days)
3. **Authenticated Requests** - Include `Authorization: Bearer <access_token>` header
4. **Refresh Token** - POST `/api/v1/auth/refresh` when access token expires
5. **Logout** - POST `/api/v1/auth/logout` to invalidate tokens

## Rate Limiting

Default rate limits apply to protect the API:
- Authentication endpoints: 5 requests/minute
- Upload endpoints: 10 requests/hour
- Other endpoints: 100 requests/minute

## Supported File Formats

**Upload Formats**: CSV, Excel (.xlsx, .xls), JSON, XML
**Export Formats**: CSV, Excel (.xlsx)
**Maximum File Size**: 500MB

## Example Workflow

1. Authenticate to get JWT token
2. Upload catalog file with publisher name
3. Poll upload status until processing completes
4. Retrieve match results with pagination
5. Filter results by confidence level
6. Export results to CSV/Excel

## Links

* **Documentation**: [Swagger UI](/docs) | [ReDoc](/redoc)
* **Health Check**: [/health](/health)
* **GitHub**: [Repository](https://github.com/your-org/mlc_dashboard)
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json",
    contact={
        "name": "BWARM Dashboard Team",
        "email": "support@bwarm.com",
    },
    license_info={
        "name": "Proprietary",
    },
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User authentication and authorization. Includes login, token refresh, and logout endpoints.",
        },
        {
            "name": "Works",
            "description": "Musical works database operations. Search, browse, and retrieve musical works with metadata, contributors, and rights information.",
        },
        {
            "name": "Catalog",
            "description": "Catalog upload and matching operations. Upload music catalogs, track processing status, retrieve match results, and export data.",
        },
        {
            "name": "Admin",
            "description": "Administrative operations (admin role required). Manage users, view all uploads, and access system statistics.",
        },
        {
            "name": "Health",
            "description": "Health check and system status endpoints.",
        },
        {
            "name": "Root",
            "description": "API root and general information.",
        },
        {
            "name": "User Preferences",
            "description": "User preferences and customization settings. Manage dashboard layout, theme, saved searches, pagination settings, and notification preferences.",
        },
        {
            "name": "Notifications",
            "description": "User notifications and alerts. View, mark as read, and manage notifications for catalog uploads, matches, and system events.",
        },
        {
            "name": "Search",
            "description": "Full-text search operations using Elasticsearch. Search musical works with fuzzy matching, relevance scoring, and autocomplete suggestions.",
        },
        {
            "name": "Saved Searches",
            "description": "Save and manage filter configurations. Create reusable searches with AND/OR logic, mark favorites, track usage, and bulk delete searches.",
        },
    ],
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware (first to ensure all responses have security headers)
app.add_middleware(SecurityHeadersMiddleware)

# Add activity logging middleware
app.add_middleware(ActivityLoggerMiddleware)

# Add rate limiting
app.state.limiter = limiter

# Register exception handlers
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(works.router, prefix=settings.API_PREFIX)
app.include_router(catalog.router, prefix=settings.API_PREFIX)
app.include_router(admin.router, prefix=settings.API_PREFIX)
app.include_router(preferences.router, prefix=settings.API_PREFIX)
app.include_router(notifications.router, prefix=settings.API_PREFIX)
app.include_router(saved_searches.router, prefix=settings.API_PREFIX)
app.include_router(search.router, prefix=settings.API_PREFIX)


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    logger.info("Starting BWARM Dashboard API...")

    # Initialize database
    if settings.DEBUG:
        logger.info("Creating database tables (DEBUG mode)...")
        await init_db()

    # Check database connection
    async with AsyncSessionLocal() as session:
        db_connected = await check_db_connection(session)
        if db_connected:
            logger.info("Database connection successful")

            # Initialize seed data
            if settings.DEBUG:
                await init_db_data(session)
        else:
            logger.error("Database connection failed!")

    # Initialize Elasticsearch connection
    try:
        await search_service.connect()
        await search_service.create_index()
        logger.info("Elasticsearch connection successful")
    except Exception as e:
        logger.warning(f"Elasticsearch initialization failed: {e}")
        logger.warning("Search functionality will be unavailable")

    logger.info("BWARM Dashboard API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down BWARM Dashboard API...")

    # Close database connections
    await close_db()

    # Close Elasticsearch connection
    try:
        await search_service.disconnect()
        logger.info("Elasticsearch connection closed")
    except Exception as e:
        logger.error(f"Error closing Elasticsearch connection: {e}")

    logger.info("BWARM Dashboard API shut down successfully")


@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="Check the health status of the API and its dependencies (database connection).",
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "database": "connected",
                        "version": "1.0.0",
                    }
                }
            },
        },
        503: {
            "description": "Service is unhealthy (database connection failed)",
            "content": {
                "application/json": {
                    "example": {
                        "status": "unhealthy",
                        "database": "disconnected",
                        "version": "1.0.0",
                    }
                }
            },
        },
    },
)
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    async with AsyncSessionLocal() as session:
        db_healthy = await check_db_connection(session)

    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "version": "1.0.0",
    }


@app.get(
    "/",
    tags=["Root"],
    summary="API Root",
    description="Get API information and available endpoints.",
    responses={
        200: {
            "description": "API information",
            "content": {
                "application/json": {
                    "example": {
                        "name": "BWARM Dashboard API",
                        "version": "1.0.0",
                        "docs": "/docs",
                        "health": "/health",
                    }
                }
            },
        }
    },
)
async def root():
    """API root endpoint with basic information and navigation."""
    return {
        "name": "BWARM Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
