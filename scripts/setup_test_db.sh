#!/bin/bash
# Setup script for test database
# This script helps set up PostgreSQL for running tests

set -e

echo "Setting up test database..."

# Check if Docker Compose is available
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    echo "✓ Docker Compose found"
    
    # Check if postgres container is running
    if docker compose -f docker-compose.local.yml ps postgres | grep -q "Up"; then
        echo "✓ PostgreSQL container is running"
        
        # Get password from .env or use default
        if [ -f .env ]; then
            POSTGRES_PASSWORD=$(grep "^POSTGRES_PASSWORD=" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'")
        fi
        
        if [ -z "$POSTGRES_PASSWORD" ]; then
            POSTGRES_PASSWORD="zapgaze_password"
            echo "⚠ Using default password (set POSTGRES_PASSWORD in .env for production)"
        fi
        
        # Create test database
        echo "Creating test database 'zapgaze_test'..."
        docker compose -f docker-compose.local.yml exec -T postgres psql -U zapgaze_user -d postgres <<EOF
CREATE DATABASE zapgaze_test;
EOF
        
        echo ""
        echo "✅ Test database created!"
        echo ""
        echo "Set this environment variable before running tests:"
        echo "export TEST_DATABASE_URL=\"postgresql://zapgaze_user:${POSTGRES_PASSWORD}@localhost:5432/zapgaze_test\""
        echo ""
    else
        echo "⚠ PostgreSQL container is not running"
        echo "Starting PostgreSQL container..."
        docker compose -f docker-compose.local.yml up -d postgres
        
        echo "Waiting for PostgreSQL to be ready..."
        sleep 5
        
        # Retry creating database
        if [ -f .env ]; then
            POSTGRES_PASSWORD=$(grep "^POSTGRES_PASSWORD=" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'")
        fi
        
        if [ -z "$POSTGRES_PASSWORD" ]; then
            POSTGRES_PASSWORD="zapgaze_password"
        fi
        
        docker compose -f docker-compose.local.yml exec -T postgres psql -U zapgaze_user -d postgres <<EOF
CREATE DATABASE zapgaze_test;
EOF
        
        echo ""
        echo "✅ Test database created!"
        echo ""
        echo "Set this environment variable before running tests:"
        echo "export TEST_DATABASE_URL=\"postgresql://zapgaze_user:${POSTGRES_PASSWORD}@localhost:5432/zapgaze_test\""
        echo ""
    fi
else
    echo "⚠ Docker Compose not found"
    echo ""
    echo "Please set up PostgreSQL manually:"
    echo "1. Start PostgreSQL locally"
    echo "2. Create test database: createdb zapgaze_test"
    echo "3. Set TEST_DATABASE_URL environment variable"
    exit 1
fi
