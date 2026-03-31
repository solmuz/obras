# OBRAS — Sistema de Gestión de Accesorios de Izaje

Aplicación web responsiva para gestionar proyectos de construcción, sus accesorios de izaje asignados y las inspecciones requeridas.

**Versión:** 1.2.1  
**Fecha:** Marzo 2026

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development without Docker)
- Node.js 18+ (for frontend development)

### Setup with Docker Compose

1. **Clone the repository and navigate to the workspace:**
   ```bash
   cd c:\Users\Josmuz\OBRAS
   ```

2. **Copy environment variables:**
   ```bash
   # Already provided as .env in the root
   # For backend development without Docker:
   cp backend/.env.example backend/.env
   ```

3. **Start all services:**
   ```bash
   docker-compose up -d
   ```

   Services will be available at:
   - **Backend API:** http://localhost:8000
   - **API Docs (Swagger):** http://localhost:8000/docs
   - **Database:** localhost:5432 (obras_db)
   - **MinIO (optional S3):** http://localhost:9000

4. **Verify health:**
   ```bash
   curl http://localhost:8000/health
   ```

5. **View logs:**
   ```bash
   docker-compose logs -f backend
   ```

---

## 📦 Project Structure

```
obras/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── main.py            # FastAPI entry point
│   │   ├── core/              # Config, security, dependencies
│   │   ├── api/v1/            # API routers
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic request/response
│   │   ├── services/          # Business logic
│   │   └── db/                # Database session
│   ├── tests/                 # Pytest test suite
│   ├── alembic/               # Database migrations
│   ├── storage/               # File uploads (local dev)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                  # React + TypeScript (to be created)
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml         # Docker services orchestration
├── .env                       # Environment variables (development)
├── .env.example               # Environment template
└── README.md                  # This file
```

---

## 🔧 Development Setup (Without Docker)

### Backend (Local Development)

1. **Create virtual environment:**
   ```bash
   cd backend
   python -m venv .venv
   .\.venv\Scripts\activate  # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create .env file:**
   ```bash
   cp .env.example .env
   # Update DATABASE_URL if using local PostgreSQL:
   # DATABASE_URL=postgresql+asyncpg://obras_user:obras_password@localhost:5432/obras_db
   ```

4. **Start the server:**
   ```bash
   fastapi dev app/main.py
   ```

   The API will be available at http://localhost:8000

### Database Migrations (Alembic)

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "initial_schema"

# Apply migration
alembic upgrade head

# Downgrade if needed
alembic downgrade -1
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py -v
```

---

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend

# Access backend container shell
docker-compose exec backend bash

# Access PostgreSQL
docker-compose exec postgres psql -U obras_user -d obras_db

# Rebuild images
docker-compose build --no-cache
```

---

## 🔐 Security Notes

⚠️ **Development Only:**
- The `JWT_SECRET` in `.env` is for development only
- Change `JWT_SECRET` to a strong value in production
- Use strong passwords for database and MinIO

---

## 📝 Environment Variables

See [.env.example](.env.example) for all available configuration options:

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | postgresql://... | PostgreSQL connection string |
| `JWT_SECRET` | value | Secret key for JWT signing (min 32 chars) |
| `TIMEZONE` | America/Bogota | Default timezone for the application |
| `ENVIRONMENT` | development | Deployment environment |
| `FRONTEND_URL` | http://localhost:5173 | Frontend origin for CORS |

---

## 🛠️ Common Issues

### 1. Database Connection Error
```
Error: cannot import name '_application' from 'greenlet'
```
**Solution:** Ensure PostgreSQL is running and DATABASE_URL is correct.

### 2. Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8000   # Windows - then taskkill /PID [PID]
```

### 3. Docker Volume Issues
```bash
docker volume prune  # Remove unused volumes
```

---

## 📖 Next Steps

1. **Backend Development:**
   - Create SQLAlchemy models (`backend/app/models/`)
   - Define Pydantic schemas (`backend/app/schemas/`)
   - Implement service layer (`backend/app/services/`)
   - Create API routers (`backend/app/api/v1/`)
   - Write tests (`backend/tests/`)

2. **Frontend Development:**
   - Initialize React + Vite project
   - Set up Zustand auth store
   - Create page components
   - Implement TanStack Query for data fetching

3. **Database:**
   - Generate Alembic migrations
   - Create seed data for development

---

## 📞 Support

For issues or questions, refer to:
- [context.md](context.md) — Full technical specifications
- FastAPI docs: https://fastapi.tiangolo.com/
- SQLAlchemy async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

---

**Last Updated:** Marzo 2026
