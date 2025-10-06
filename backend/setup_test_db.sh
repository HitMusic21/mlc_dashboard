#!/bin/bash
# Setup PostgreSQL test database for contract tests

set -e

echo "🔧 Setting up PostgreSQL test database..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Start PostgreSQL container
echo "📦 Starting PostgreSQL container..."
cd /Users/carlosmescalona/Documents/Projects/mlc_dashboard
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker exec bwarm_postgres pg_isready -U postgres > /dev/null 2>&1; then
        echo "✓ PostgreSQL is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Timeout waiting for PostgreSQL"
        exit 1
    fi
    sleep 1
done

# Create test database
echo "🗄️  Creating test database..."
docker exec bwarm_postgres psql -U postgres -c "DROP DATABASE IF EXISTS bwarm_test;" 2>/dev/null || true
docker exec bwarm_postgres psql -U postgres -c "CREATE DATABASE bwarm_test;"

echo "✅ Test database ready!"
echo ""
echo "You can now run contract tests:"
echo "  cd backend && pytest tests/contract/ -v"
