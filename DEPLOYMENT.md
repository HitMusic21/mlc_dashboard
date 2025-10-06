# Production Deployment Guide

This guide covers deploying the BWARM Dashboard to production environments.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Database Setup](#database-setup)
- [Backend Deployment](#backend-deployment)
- [Frontend Deployment](#frontend-deployment)
- [Infrastructure Services](#infrastructure-services)
- [Security Checklist](#security-checklist)
- [Monitoring & Logging](#monitoring--logging)
- [Scaling Considerations](#scaling-considerations)
- [Disaster Recovery](#disaster-recovery)

---

## Prerequisites

### Required Services
- PostgreSQL 15+ (managed service recommended)
- Redis 7+ (managed service recommended)
- Elasticsearch 8+ (managed service recommended)
- Docker (for containerized deployment)
- Load balancer (AWS ALB, nginx, etc.)
- Object storage (S3, GCS, etc.) for uploaded files
- SSL/TLS certificates

### Recommended Platforms
- **AWS**: RDS (PostgreSQL), ElastiCache (Redis), OpenSearch/ES, ECS/EKS, S3
- **GCP**: Cloud SQL, Memorystore, Elasticsearch, GKE, Cloud Storage
- **Azure**: Database for PostgreSQL, Cache for Redis, Elasticsearch, AKS, Blob Storage
- **DigitalOcean**: Managed Databases, Kubernetes, Spaces

---

## Environment Setup

### 1. Create Production Environment File

```bash
# Production .env file
PROJECT_NAME=bwarm_dashboard

# Database - Use managed PostgreSQL
DATABASE_URL=postgresql+asyncpg://username:password@prod-db.region.provider.com:5432/bwarm_prod

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1
DEBUG=false

# Security - CRITICAL: Use strong random keys
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS - Set to your frontend domain
FRONTEND_URL=https://dashboard.yourdomain.com
ALLOWED_ORIGINS=https://dashboard.yourdomain.com,https://www.yourdomain.com

# Redis - Use managed Redis
REDIS_HOST=prod-redis.region.provider.com
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=<strong-password>

# Celery
CELERY_BROKER_URL=redis://:password@prod-redis.region.provider.com:6379/0
CELERY_RESULT_BACKEND=redis://:password@prod-redis.region.provider.com:6379/0

# Elasticsearch - Use managed Elasticsearch
ELASTICSEARCH_HOST=prod-es.region.provider.com
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_INDEX_PREFIX=bwarm_prod_

# File Upload - Increase for production
MAX_UPLOAD_SIZE_MB=1000
ALLOWED_FILE_EXTENSIONS=csv,xlsx,xls,json,xml

# Catalog Matching
MATCH_CONFIDENCE_THRESHOLD=0.6
MAX_MATCHES_PER_TRACK=10

# Logging
LOG_LEVEL=INFO
```

### 2. Generate Secret Key

```bash
# Generate secure SECRET_KEY
openssl rand -hex 32
```

---

## Database Setup

### 1. Create Production Database

**PostgreSQL managed service** (recommended):
```sql
CREATE DATABASE bwarm_prod;
CREATE USER bwarm_user WITH PASSWORD 'strong-password-here';
GRANT ALL PRIVILEGES ON DATABASE bwarm_prod TO bwarm_user;
```

### 2. Run Database Migrations

```bash
cd backend
source venv/bin/activate

# Run migrations
alembic upgrade head

# Verify migration
alembic current
```

### 3. Add Database Indexes

```bash
python scripts/add_indexes.py
```

### 4. Seed Initial Data (Optional)

```bash
# Only if you want sample data in production
python scripts/seed_database.py
```

### 5. Configure Connection Pooling

Update `backend/app/db/session.py`:
```python
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Disable SQL logging in production
    pool_pre_ping=True,
    pool_size=20,  # Adjust based on load
    max_overflow=40,
    pool_recycle=3600,  # Recycle connections every hour
)
```

### 6. Enable pg_stat_statements

```sql
-- Monitor slow queries
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

---

## Backend Deployment

### Option 1: Docker Deployment (Recommended)

#### 1. Build Production Docker Image

```dockerfile
# backend/Dockerfile.prod
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:8000/health')"

# Run with production settings
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### 2. Build and Push

```bash
# Build image
docker build -f Dockerfile.prod -t bwarm-backend:latest .

# Tag for registry
docker tag bwarm-backend:latest your-registry.com/bwarm-backend:v1.0.0

# Push to registry
docker push your-registry.com/bwarm-backend:v1.0.0
```

#### 3. Deploy with Docker Compose (Production)

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    image: your-registry.com/bwarm-backend:v1.0.0
    restart: always
    env_file: .env.prod
    ports:
      - "8000:8000"
    depends_on:
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 2G

  celery_worker:
    image: your-registry.com/bwarm-backend:v1.0.0
    restart: always
    env_file: .env.prod
    command: celery -A celery_app worker --loglevel=info -Q catalog,cleanup --concurrency=8
    depends_on:
      - redis
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '4'
          memory: 4G

  celery_beat:
    image: your-registry.com/bwarm-backend:v1.0.0
    restart: always
    env_file: .env.prod
    command: celery -A celery_app beat --loglevel=info
    depends_on:
      - redis
    deploy:
      replicas: 1

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  redis_data:
```

### Option 2: Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests (create these as needed).

### Option 3: Platform-as-a-Service

**AWS Elastic Beanstalk**, **Google Cloud Run**, **Azure App Service**, etc.

---

## Frontend Deployment

### 1. Build Production Frontend

```bash
cd frontend

# Install dependencies
npm ci

# Build for production
VITE_API_URL=https://api.yourdomain.com/api/v1 npm run build

# Output is in dist/ directory
```

### 2. Deploy to CDN/Static Hosting

#### Option A: AWS S3 + CloudFront

```bash
# Upload to S3
aws s3 sync dist/ s3://your-bucket-name --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

#### Option B: Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=dist
```

#### Option C: Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

#### Option D: nginx

```nginx
# /etc/nginx/sites-available/bwarm-frontend
server {
    listen 80;
    server_name dashboard.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name dashboard.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    root /var/www/bwarm-frontend/dist;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

---

## Infrastructure Services

### PostgreSQL (Managed)

**AWS RDS Configuration**:
- Instance class: db.t3.medium or larger
- Storage: 100GB SSD, auto-scaling enabled
- Multi-AZ: Yes (for high availability)
- Automated backups: Daily, 7-day retention
- Read replicas: Optional for read-heavy workloads

### Redis (Managed)

**AWS ElastiCache Configuration**:
- Node type: cache.t3.medium or larger
- Cluster mode: Enabled for high availability
- Automatic failover: Yes
- Snapshot retention: 7 days

### Elasticsearch (Managed)

**AWS OpenSearch Configuration**:
- Instance type: t3.medium.search or larger
- Number of nodes: 3 (for high availability)
- Dedicated master nodes: Yes
- Snapshot retention: Daily, 14-day retention

---

## Security Checklist

### Required Security Measures

- [ ] **Environment Variables**: Never commit `.env` files
- [ ] **Secret Key**: Use strong random key (32+ bytes)
- [ ] **HTTPS Only**: Force HTTPS, use SSL/TLS certificates
- [ ] **CORS**: Whitelist only production frontend domain
- [ ] **Database**: Use strong passwords, enable SSL connections
- [ ] **Redis**: Enable authentication with strong password
- [ ] **API Rate Limiting**: Implement rate limiting (slowapi, nginx)
- [ ] **Input Validation**: Validate all user inputs
- [ ] **SQL Injection**: Use parameterized queries (SQLModel does this)
- [ ] **XSS Protection**: Sanitize outputs, set Content-Security-Policy
- [ ] **File Upload**: Validate file types, scan for malware
- [ ] **Secrets Management**: Use AWS Secrets Manager, HashiCorp Vault, etc.
- [ ] **Network Security**: Use VPC, security groups, firewall rules
- [ ] **DDoS Protection**: Use CloudFlare, AWS Shield, etc.
- [ ] **Audit Logging**: Log all admin actions, API requests
- [ ] **Regular Updates**: Keep dependencies updated (Dependabot)

### Recommended Security Headers

Add to nginx or application:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'
Referrer-Policy: no-referrer-when-downgrade
```

---

## Monitoring & Logging

### Application Monitoring

**Recommended Tools**:
- **APM**: New Relic, DataDog, Sentry
- **Logging**: ELK Stack, CloudWatch, Stackdriver
- **Uptime**: UptimeRobot, Pingdom
- **Metrics**: Prometheus + Grafana

### Key Metrics to Monitor

**Backend**:
- API response times (p50, p95, p99)
- Error rate (4xx, 5xx)
- Database query times
- Celery queue length and processing time
- Memory and CPU usage

**Database**:
- Connection pool usage
- Slow queries (>1 second)
- Deadlocks
- Replication lag (if using replicas)

**Redis**:
- Memory usage
- Evicted keys
- Connected clients

**Elasticsearch**:
- Query latency
- Index size
- JVM heap usage

### Logging Configuration

```python
# backend/main.py
import logging
from logging.config import dictConfig

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",  # Use JSON in production
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": settings.LOG_LEVEL,
        "handlers": ["console"],
    },
}

dictConfig(LOGGING_CONFIG)
```

### Health Check Endpoint

```python
# Add to backend/main.py
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }
```

---

## Scaling Considerations

### Horizontal Scaling

**Backend API**:
- Deploy multiple instances behind load balancer
- Stateless design (use Redis for sessions)
- Use connection pooling for database

**Celery Workers**:
- Scale workers based on queue depth
- Separate workers for different queue priorities
- Use autoscaling groups

### Database Scaling

- **Read Replicas**: For read-heavy workloads
- **Connection Pooling**: Use PgBouncer
- **Partitioning**: Partition large tables (catalogmatch) by upload_id or date
- **Indexes**: Maintain and optimize indexes regularly

### Caching Strategy

- **Redis**: Cache query results, session data
- **CDN**: Cache static frontend assets
- **Browser**: Set appropriate Cache-Control headers

### Performance Targets

- API response time: <500ms (p95)
- Page load time: <3 seconds
- Catalog processing: >1,000 tracks/minute
- Database queries: <100ms (p95)

---

## Disaster Recovery

### Backup Strategy

**Database**:
- Automated daily backups (RDS automatic backups)
- Manual snapshots before major changes
- Test restore process monthly
- Retention: 7 days minimum

**Redis**:
- Daily snapshots (ElastiCache automatic backups)
- Retention: 7 days

**Elasticsearch**:
- Daily snapshots to S3
- Retention: 14 days

**Uploaded Files** (S3):
- Enable versioning
- Cross-region replication (optional)
- Lifecycle policies for old files

### Recovery Procedures

1. **Database Failure**:
   - Restore from latest snapshot
   - Run migrations: `alembic upgrade head`
   - Re-index Elasticsearch: `python scripts/setup_elasticsearch.py`

2. **Application Failure**:
   - Rollback to previous container version
   - Check logs for root cause
   - Deploy fix

3. **Data Loss**:
   - Restore from backup
   - Verify data integrity
   - Communicate with users if necessary

### Disaster Recovery Testing

- Run DR drills quarterly
- Document recovery procedures
- Measure RTO (Recovery Time Objective) and RPO (Recovery Point Objective)
- Target: RTO <1 hour, RPO <5 minutes

---

## Deployment Checklist

### Pre-Deployment
- [ ] Run all tests (`pytest`, `npm test`)
- [ ] Update CHANGELOG.md
- [ ] Tag release in git
- [ ] Review code changes
- [ ] Update documentation
- [ ] Create database backup
- [ ] Test in staging environment

### Deployment
- [ ] Set maintenance mode (optional)
- [ ] Run database migrations
- [ ] Deploy backend containers
- [ ] Deploy Celery workers
- [ ] Deploy frontend to CDN
- [ ] Run smoke tests
- [ ] Monitor error rates

### Post-Deployment
- [ ] Verify health checks
- [ ] Test critical user flows
- [ ] Monitor performance metrics
- [ ] Check error logs
- [ ] Remove maintenance mode
- [ ] Notify team of successful deployment

---

## Rollback Procedure

If issues arise after deployment:

1. **Immediate**: Rollback to previous container version
   ```bash
   docker pull your-registry.com/bwarm-backend:v1.0.0-previous
   docker-compose up -d
   ```

2. **Database**: Restore from snapshot if schema changed
   ```bash
   alembic downgrade -1
   ```

3. **Frontend**: Revert to previous CDN version
   ```bash
   aws s3 sync s3://backup-bucket/previous-version/ s3://production-bucket/
   ```

4. **Notify**: Inform team and users of rollback

---

## Support & Troubleshooting

### Common Issues

**Issue**: High API latency
- **Solution**: Check database query times, add indexes, scale workers

**Issue**: Celery queue backing up
- **Solution**: Scale workers, optimize task processing time

**Issue**: Out of memory errors
- **Solution**: Increase container memory, optimize code, check for memory leaks

**Issue**: Database connection errors
- **Solution**: Increase connection pool size, check database health

### Getting Help

- Review application logs
- Check monitoring dashboards
- Consult documentation
- Contact development team

---

## Additional Resources

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Production Build](https://vitejs.dev/guide/build.html)
- [PostgreSQL Production Checklist](https://www.postgresql.org/docs/current/runtime-config.html)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
