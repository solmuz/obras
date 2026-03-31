# OBRAS Development Environment Setup Script (Windows PowerShell)
# This script sets up and starts the Docker Compose services

Write-Host "================================" -ForegroundColor Cyan
Write-Host "OBRAS -- Backend Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✓ Docker found" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker is not installed. Please install Docker first." -ForegroundColor Red
    exit 1
}

# Check if Docker Compose is installed
try {
    docker-compose --version | Out-Null
    Write-Host "✓ Docker Compose found" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker Compose is not installed. Please install Docker Compose first." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check if .env file exists
if (!(Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created. Make sure to update sensitive values if needed." -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting Docker Compose services..." -ForegroundColor Cyan
Write-Host "  - PostgreSQL (port 5432)" -ForegroundColor Gray
Write-Host "  - FastAPI Backend (port 8000)" -ForegroundColor Gray
Write-Host "  - MinIO S3 Storage (port 9000, optional)" -ForegroundColor Gray
Write-Host ""

# Start services
docker-compose up -d

# Wait for database to be ready
Write-Host "⏳ Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if backend is healthy
$healthCheck = docker-compose exec -T backend curl -s http://localhost:8000/health
if ($healthCheck -match "healthy") {
    Write-Host "✓ Services started!" -ForegroundColor Green
}
else {
    Write-Host "⚠️  Services started but health check may still be loading. Check logs with:" -ForegroundColor Yellow
    Write-Host "   docker-compose logs -f backend" -ForegroundColor Gray
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "🎉 Backend is ready!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Available endpoints:" -ForegroundColor Cyan
Write-Host "  - API: http://localhost:8000" -ForegroundColor Gray
Write-Host "  - Swagger UI: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "  - ReDoc: http://localhost:8000/redoc" -ForegroundColor Gray
Write-Host "  - Database: localhost:5432" -ForegroundColor Gray
Write-Host ""
Write-Host "View logs:" -ForegroundColor Cyan
Write-Host "  docker-compose logs -f backend" -ForegroundColor Gray
Write-Host ""
Write-Host "Stop services:" -ForegroundColor Cyan
Write-Host "  docker-compose down" -ForegroundColor Gray
Write-Host ""
