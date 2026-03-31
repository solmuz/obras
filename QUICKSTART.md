# OBRAS Development Quick Reference

## 🚀 Quick Start Commands

### Windows (PowerShell)
```powershell
cd c:\Users\Josmuz\OBRAS
.\start-docker.ps1
```

### macOS/Linux
```bash
cd ~/path/to/OBRAS
chmod +x start-docker.sh
./start-docker.sh
```

### Manual Start (All Platforms)
```bash
cd c:\Users\Josmuz\OBRAS
docker-compose up -d
```

---

## 📍 Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Backend API | http://localhost:8000 | FastAPI application |
| Swagger Docs | http://localhost:8000/docs | Interactive API documentation |
| ReDoc | http://localhost:8000/redoc | Alternative API documentation |
| PostgreSQL | localhost:5432 | Database |
| MinIO Console | http://localhost:9001 | Optional S3 storage UI |

---

## 📊 Database Access

### Via Docker
```bash
docker-compose exec postgres psql -U obras_user -d obras_db
```

### Via Local Client
- Host: `localhost`
- Port: `5432`
- User: `obras_user`
- Password: `obras_password`
- Database: `obras_db`

---

## 🐳 Docker Commands

| Command | Purpose |
|---------|---------|
| `docker-compose up -d` | Start all services in background |
| `docker-compose down` | Stop all services |
| `docker-compose logs -f backend` | View backend logs in real-time |
| `docker-compose ps` | List running containers |
| `docker-compose restart backend` | Restart backend service |
| `docker-compose build --no-cache` | Rebuild all images |
| `docker-compose exec backend bash` | Access backend container shell |

---

## 🧪 Testing

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=app tests/

# Watch mode (auto-run on change)
pytest-watch tests/
```

---

## 🔄 Backend Development Workflow

1. **Create migration:**
   ```bash
   cd backend
   alembic revision --autogenerate -m "add new table"
   ```

2. **Apply migration:**
   ```bash
   alembic upgrade head
   ```

3. **Create models** in `app/models/`
4. **Create schemas** in `app/schemas/`
5. **Create services** in `app/services/`
6. **Create routers** in `app/api/v1/`
7. **Write tests** in `tests/`

---

## 📝 Environment Variables

Location: `.env` (or use `.env.example` as template)

Key variables:
- `DATABASE_URL` — PostgreSQL connection string
- `JWT_SECRET` — Secret for JWT signing (change in production!)
- `TIMEZONE` — Default timezone (America/Bogota)
- `ENVIRONMENT` — dev/prod/staging

---

## 🐛 Troubleshooting

### Issue: "Cannot connect to PostgreSQL"
**Solution:**
```bash
docker-compose ps  # Check if postgres is running
docker-compose logs postgres  # View postgres logs
docker-compose restart postgres
```

### Issue: "Port 8000 already in use"
```bash
# Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: "ModuleNotFoundError" in backend
```bash
docker-compose rebuild --no-cache backend
docker-compose up -d backend
```

### Issue: Database connection timeout
```bash
# Ensure database is healthy
docker-compose exec postgres pg_isready
```

---

## 📚 Next: Frontend Setup

```bash
# In a new terminal
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:5173`

---

## 💾 File Structure Reference

```
backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── core/                # Config, security, dependencies
│   ├── api/v1/              # API routers (MOD-01 through MOD-09)
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── services/            # Business logic layer
│   └── db/                  # Database session & config
├── tests/                   # Pytest test suite
├── alembic/                 # Database migrations
├── storage/                 # File uploads (dev)
├── Dockerfile               # Container image
├── requirements.txt         # Python dependencies
└── pytest.ini              # Pytest config
```

---

## 🎯 Development Priorities

1. ✅ **Backend initialization** (YOU ARE HERE)
2. [ ] Create SQLAlchemy models (User, Project, Accessory, etc.)
3. [ ] Configure Alembic migrations
4. [ ] Implement auth router (MOD-01)
5. [ ] Implement user management (MOD-02)
6. [ ] Implement projects module (MOD-03)
7. [ ] Setup frontend with React + Vite
8. [ ] Integrate frontend with backend API
9. [ ] Full end-to-end testing

---

**Last Updated:** March 20, 2026
