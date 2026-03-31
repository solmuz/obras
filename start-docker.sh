#!/bin/bash

# OBRAS Development Environment Setup Script
# This script sets up and starts the Docker Compose services

set -e

echo "================================"
echo "OBRAS — Backend Setup"
echo "================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✓ Docker found"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker Compose found"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✓ .env file created. Make sure to update sensitive values if needed."
fi

echo ""
echo "Starting Docker Compose services..."
echo "  - PostgreSQL (port 5432)"
echo "  - FastAPI Backend (port 8000)"
echo "  - MinIO S3 Storage (port 9000, optional)"
echo ""

# Start services
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Check if backend is healthy
echo "✓ Services started!"
echo ""
echo "================================"
echo "🎉 Backend is ready!"
echo "================================"
echo ""
echo "Available endpoints:"
echo "  - API: http://localhost:8000"
echo "  - Swagger UI: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo "  - Database: localhost:5432"
echo ""
echo "View logs:"
echo "  docker-compose logs -f backend"
echo ""
echo "Stop services:"
echo "  docker-compose down"
echo ""
