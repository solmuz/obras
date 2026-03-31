# OBRAS Development - Quick Reference

Reference guide for common development tasks. Save this for quick lookup!

---

## Starting Development

### First Time Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
docker-compose up -d
alembic upgrade head
python seed_admin.py

# Frontend
cd frontend
npm install
```

### Daily Startup (2 terminals)

**Terminal 1:**
```bash
cd backend
uvicorn app.main:app --reload
# Backend ready at http://localhost:8000
# API docs at http://localhost:8000/docs
```

**Terminal 2:**
```bash
cd frontend
npm run dev
# Frontend ready at http://localhost:5173
```

### Login Demo
- URL: http://localhost:5173
- Email: admin@example.com
- Password: ChangeMe123!

---

## Frontend Development

### Creating a New Page

```typescript
// src/pages/[module]/[PageName].tsx
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';

export default function MyPage() {
  const navigate = useNavigate();
  const { user } = useAuthStore();

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold">Page Title</h1>
      {/* Content here */}
    </div>
  );
}
```

### Using API Services

```typescript
import { projectsApi } from '@/services/projectsApi';
import { useQuery } from '@tanstack/react-query';

// In your component:
const { data, isLoading, error } = useQuery({
  queryKey: ['projects'],
  queryFn: () => projectsApi.listProjects(),
});

if (isLoading) return <div>Loading...</div>;
if (error) return <div>Error: {error.message}</div>;
return <div>{data.items.map(...)}</div>;
```

### Form Handling

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

const schema = z.object({
  email: z.string().email(),
  name: z.string().min(1),
});

type FormData = z.infer<typeof schema>;

export default function MyForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    // API call here
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} />
      {errors.email && <span>{errors.email.message}</span>}
      <button type="submit">Submit</button>
    </form>
  );
}
```

### Using Global State

```typescript
import { useAuthStore } from '@/store/authStore';
import { useUIStore } from '@/store/uiStore';

export default function MyComponent() {
  // Auth state
  const { user, isAuthenticated, logout } = useAuthStore();
  
  // UI state
  const { sidebarOpen, toggleSidebar } = useUIStore();

  return (
    <div>
      <button onClick={toggleSidebar}>
        {sidebarOpen ? 'Hide' : 'Show'} Sidebar
      </button>
      <p>{user?.full_name}</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### Tailwind CSS Classes

```typescript
// Colors available:
// bg-semaforo-verde, bg-semaforo-amarillo, bg-semaforo-rojo
// text-semaforo-verde, text-semaforo-amarillo, text-semaforo-rojo

<div className="bg-semaforo-verde text-white rounded-lg p-4">
  Vigente (Valid)
</div>

<div className="bg-semaforo-amarillo text-white rounded-lg p-4">
  Por Vencer (Due Soon)
</div>

<div className="bg-semaforo-rojo text-white rounded-lg p-4">
  Vencido (Expired)
</div>
```

### Date Formatting

```typescript
import { formatDateShort, getDaysUntil, getRelativeTime } from '@/utils/dateUtils';

const date = '2024-12-31T10:30:00Z';

formatDateShort(date);           // "31/12/2024"
getDaysUntil(date);              // 45
getRelativeTime(date);            // "45 días" or "Vencido"
```

### Semáforo Status

```typescript
import { calculateSemaforoStatus, getColorForStatus } from '@/utils/semaforoUtils';

const status = calculateSemaforoStatus(
  externalInspectionDate,
  siteInspectionDate,
  isDecommissioned
);

// Returns: 'VERDE' | 'AMARILLO' | 'ROJO'

const color = getColorForStatus(status);  // hex color
```

### PDF Export

```typescript
import { exportReportToPDF } from '@/utils/pdfUtils';

const handleExport = () => {
  exportReportToPDF(data, 'my-report.pdf');
};
```

---

## Backend Development

### Creating a New Service

```python
# backend/app/services/my_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import MyModel

class MyService:
    @staticmethod
    async def get_by_id(db: AsyncSession, id: UUID) -> Optional[MyModel]:
        result = await db.execute(
            select(MyModel).where(MyModel.id == id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: MyModelCreate) -> MyModel:
        db_obj = MyModel(**data.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
```

### Creating a New Router

```python
# backend/app/api/v1/my_router.py
from fastapi import APIRouter, Depends
from app.core.dependencies import get_db
from app.services.my_service import MyService
from app.schemas.my_schema import MyResponse

router = APIRouter()

@router.get("/")
async def list_items(db = Depends(get_db)):
    items = await MyService.list_all(db)
    return {"items": items}

@router.post("/")
async def create_item(data: MyCreate, db = Depends(get_db)):
    item = await MyService.create(db, data)
    return item
```

### Register Router in Main

```python
# backend/app/main.py
from app.api.v1 import my_router

# Add this line with other router registrations:
app.include_router(my_router.router, prefix="/my", tags=["my-module"])
```

### Database Migration

```bash
# Create migration
alembic revision --autogenerate -m "add_new_table"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View current migration
alembic current
```

### Testing Auth

```bash
# Test login endpoint
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"ChangeMe123!"}'

# Test protected endpoint with token
curl -H "Authorization: Bearer <your_token>" \
  http://localhost:8000/api/v1/users/
```

---

## Common Tasks

### Build Frontend for Production

```bash
cd frontend
npm run build
# Creates optimized dist/ folder ready for deployment
```

### Check TypeScript Errors

```bash
cd frontend
npm run type-check
# Shows any TypeScript errors without building
```

### Format Code

```bash
cd frontend
npm run format
# Automatically formats all files with Prettier
```

### Lint Code

```bash
cd frontend
npm run lint
# Shows code quality issues
```

### View API Documentation

```
Open: http://localhost:8000/docs
Shows interactive Swagger UI with all endpoints
```

### Check Database

```bash
docker-compose exec postgres psql -U postgres -d obras
\dt              # List tables
\d users         # Show users table structure
SELECT * FROM users;  # View users
\q               # Exit
```

### View Backend Logs

```bash
# Current logs
docker-compose logs backend

# Follow logs (real-time)
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Clear Node Cache

```bash
cd frontend
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

---

## Port Reference

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:5173 | React application |
| Backend API | http://localhost:8000 | FastAPI server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| PostgreSQL | localhost:5432 | Database |
| PgAdmin | http://localhost:5050 | DB management (if running) |

---

## Debugging Tips

### Frontend Debug Console
```typescript
// In console or component:
localStorage.getItem('accessToken');     // Check token
localStorage.getItem('user');            // Check user object
fetch('http://localhost:8000/docs');     // Test backend connection
```

### Backend Debug Logging
```python
# Add to router:
import logging
logger = logging.getLogger(__name__)

@router.post("/")
async def my_endpoint(data):
    logger.info(f"Received data: {data}")  # Shows in logs
    return {"status": "ok"}
```

### Check Network Requests
1. Open DevTools (F12)
2. Go to Network tab
3. Perform action
4. Look for `/api/v1/...` requests
5. Check:
   - Status code (200, 401, 500, etc.)
   - Request headers (Authorization, Content-Type)
   - Response body (error messages)

### Token Issues
1. Open DevTools
2. Application tab → LocalStorage
3. Check keys exist: accessToken, refreshToken, user
4. If missing, login again
5. If token is invalid, backend returns 401

---

## Architecture Reminders

### API Flow
```
Frontend Button Click
  ↓ useQuery/useMutation
  ↓ API Service (projectsApi.list())
  ↓ Axios client
  ↓ JWT Interceptor adds header
  ↓ Backend receives request
  ↓ Validates token + data
  ↓ Returns response
  ↓ Axios checks for 401
  ↓ React Query caches result
  ↓ Component re-renders
```

### Token Lifecycle
```
1. Login → Returns access + refresh tokens
2. Store → Zustand + localStorage
3. Use → Axios adds to all requests
4. Expires → 401 response triggers refresh
5. Refresh → Auto-call new access token
6. Retry → Original request with new token
7. Logout → Clear tokens + redirect to login
```

### State Persistence
```
Zustand Store
  ↓ JSON.stringify()
  ↓ localStorage.setItem()
  ↓ Browser refresh
  ↓ localStorage.getItem()
  ↓ JSON.parse()
  ↓ Zustand hydrates
  ↓ App continues as if never refreshed
```

---

## File Structure Quick Reference

```
Create new page?
→ src/pages/[module]/[PageName].tsx

Create API service?
→ src/services/[module]Api.ts

Need a utility function?
→ src/utils/[name]Utils.ts

Create component?
→ src/components/[type]/[ComponentName].tsx

Need a custom hook?
→ src/hooks/use[Name].ts

Add type definition?
→ src/types/index.ts (add interface)
```

---

## Common Errors & Solutions

| Error | Solution |
|-------|----------|
| "Cannot find module '@/...'" | Check tsconfig.json paths, restart dev server |
| "401 Unauthorized" | Run `python seed_admin.py`, restart backend |
| "Cannot connect to database" | Check `docker-compose ps`, ensure postgres running |
| "Port 8000 already in use" | Find process: `lsof -i :8000`, kill it |
| "npm ERR! code ERESOLVE" | Run `npm install --legacy-peer-deps` |
| "localStorage is undefined" | Only available in browser, not SSR |
| "Token refresh failing" | Check JWT_SECRET_KEY in .env matches backend |

---

## Performance Checklist

- [ ] TypeScript strict mode enabled
- [ ] Unused imports removed
- [ ] Large lists use React.memo()
- [ ] API results cached with React Query
- [ ] Images optimized (use Vite imports)
- [ ] Components lazy loaded at routes
- [ ] bundle size < 500KB (JS), < 100KB (CSS)
- [ ] No console errors or warnings
- [ ] Dev server hot reload < 1s
- [ ] Page load time < 3s

---

## Best Practices

1. **Always use TypeScript** - Catch errors early
2. **Component + Hook pattern** - Separate logic from UI
3. **api.ts first** - Define API before component
4. **Type everything** - Don't use `any`
5. **Error boundaries** - Wrap page components
6. **Lazy load routes** - Split code at pages
7. **Memoize expensive renders** - Use React.memo()
8. **Cache API results** - Use React Query staleTime
9. **Validate on backend** - Never trust frontend
10. **Log errors properly** - Console, Sentry, etc.

---

## Useful Extensions for VS Code

- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- Thunder Client (API testing)
- Prettier - Code formatter
- ESLint
- Path Intellisense

---

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes
# ... edit files ...

# Commit
git add .
git commit -m "feat: add new feature"

# Push
git push origin feature/my-feature

# Create pull request on GitHub
```

**.gitignore includes:**
- node_modules/
- dist/
- .env.local
- .vscode/
- .DS_Store

---

## Resources

- **Frontend docs:** frontend/README.md
- **Backend API:** http://localhost:8000/docs (Swagger)
- **Full specs:** context.md
- **Architecture:** frontend/ARCHITECTURE.md
- **React docs:** https://react.dev/
- **Tailwind:** https://tailwindcss.com/docs
- **Zustand:** https://github.com/pmndrs/zustand
- **React Query:** https://tanstack.com/query/latest

---

**Last Updated:** December 2024  
**Version:** Quick Reference 1.0  
**Print or Bookmark This! 📌**
