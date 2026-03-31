# OBRAS Frontend

React + TypeScript + Vite frontend for the OBRAS (Obras de Accesorios de Izaje) management system.

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env.local`:

```bash
cp .env.example .env.local
```

Update `VITE_API_BASE_URL` if backend is running on a different URL (default: `http://localhost:8000/api/v1`).

### 3. Start Development Server

```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

The Vite proxy will forward `/api/*` requests to `http://localhost:8000`.

### 4. Build for Production

```bash
npm run build
```

### 5. Preview Production Build

```bash
npm run preview
```

## Project Structure

```
src/
├── pages/              # Page components (LoginPage, DashboardPage, etc.)
├── components/         # Reusable UI components
│   ├── layout/        # AppShell, Sidebar, TopBar
│   ├── forms/         # Form components
│   ├── semaforo/      # Semáforo status components
│   ├── tables/        # Data table components
│   └── ui/            # Basic UI components (Modal, Button, etc.)
├── services/          # API service layer (Axios client + endpoints)
├── store/             # Zustand global state stores
├── hooks/             # Custom React hooks
├── types/             # TypeScript type definitions
├── utils/             # Utility functions (date, PDF export, etc.)
├── routes/            # Route definitions and guards
├── styles/            # Global CSS
├── App.tsx            # Root component
└── main.tsx           # Entry point
```

## Key Technologies

- **React 18.3** - UI library
- **TypeScript 5.4** - Type safety
- **Vite 5.2** - Build tool & dev server
- **Tailwind CSS 3.4** - Styling
- **React Router DOM 6.23** - Client-side routing
- **Zustand 4.5** - Lightweight state management
- **TanStack React Query 5.40** - Server state management
- **Axios 1.7** - HTTP client with JWT interceptor
- **React Hook Form 7.51** - Form handling
- **Zod 3.23** - Schema validation
- **date-fns 3.6** + **date-fns-tz 3.1** - Date formatting with timezones
- **jsPDF 2.5** + **jspdf-autotable 3.8** - PDF export
- **Lucide React** - Icons
- **Headless UI 2.1** - Accessible components

## Development Workflow

### Authentication Flow

1. User navigates to `/login`
2. Submits credentials (email/password)
3. `useLogin()` hook calls `authApi.login()`
4. On success, tokens stored in Zustand + localStorage
5. Axios interceptor automatically adds `Authorization: Bearer <token>` header
6. If token expires (401 response), interceptor calls `authApi.refresh()`
7. New token stored, original request retried

### State Management

- **Auth State (Zustand)**: User data, tokens, authentication status
- **UI State (Zustand)**: Sidebar toggle, active project/accessory
- **Server State (React Query)**: Data fetching, caching, pagination

### API Service Layer

All API calls go through `src/services/api.ts`:

```typescript
import { authApi } from '@/services/authApi';
import { projectsApi } from '@/services/projectsApi';
import { accessoriesApi } from '@/services/accessoriesApi';

// Login
const { access_token, refresh_token } = await authApi.login({ email, password });

// Fetch user
const user = await authApi.getProfile();

// List projects
const projects = await projectsApi.listProjects();

// Create project
const newProject = await projectsApi.createProject({ name, location, ... });

// Upload photo
const formData = new FormData();
formData.append('file', photoFile);
await accessoriesApi.uploadPhoto(accessoryId, formData);
```

### Timezone Handling

All dates are formatted using `America/Bogota` timezone by default. Use date utils:

```typescript
import { formatDateInTZ, formatDateShort, getDaysUntil } from '@/utils/dateUtils';

formatDateInTZ('2024-12-31T10:30:00Z', 'America/Bogota');  // "31/12/2024 05:30:00"
formatDateShort('2024-12-31T10:30:00Z', 'America/Bogota'); // "31/12/2024"
getDaysUntil('2024-12-31T10:30:00Z');                      // 45
```

### Semáforo Status Calculation

Accessories have a semáforo status (Verde/Amarillo/Rojo) based on inspection dates:

```typescript
import { calculateSemaforoStatus, getColorForStatus } from '@/utils/semaforoUtils';

const status = calculateSemaforoStatus(
  '2024-08-01T10:30:00Z', // last external inspection date
  '2024-08-01T10:30:00Z', // last site inspection date
  false                     // is_decommissioned
);
// Returns: 'VERDE' (current) | 'AMARILLO' (due soon) | 'ROJO' (expired)

const color = getColorForStatus(status); // '#10b981' | '#f59e0b' | '#ef4444'
```

## CLI Commands

```bash
# Development
npm run dev           # Start Vite dev server
npm run preview       # Preview production build

# Build
npm run build         # Build for production

# Linting & Formatting
npm run lint          # Run ESLint
npm run format        # Format code with Prettier
npm run format:check  # Check formatting without changes

# Type checking
npm run type-check    # Run TypeScript compiler
```

## Environment Variables

See `.env.example` for available variables. Create `.env.local` to override:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1  # Backend API base URL
VITE_APP_NAME=OBRAS                              # App name for UI
VITE_APP_VERSION=1.2.1                           # App version
```

## API Integration Testing

Once backend is running, test the login flow:

```bash
# Terminal 1: Start backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start frontend
cd frontend
npm run dev
```

Visit `http://localhost:5173` → Navigate to login → Try credentials:
- Email: `admin@example.com`
- Password: `ChangeMe123!`

## Backend Synchronization

The frontend expects the backend API to have these endpoints:

**Auth**:
- `POST /api/v1/auth/login` → `{ access_token, refresh_token, token_type, expires_in }`
- `POST /api/v1/auth/refresh` → `{ access_token, ... }`
- `POST /api/v1/auth/logout` → `{ message }`
- `GET /api/v1/auth/profile` → `{ id, email, full_name, role, ... }`

**Users** (admin only):
- `GET /api/v1/users` → `{ items: User[], total: int }`
- `GET /api/v1/users/{id}` → `User`
- `POST /api/v1/users` → `User`
- `PUT /api/v1/users/{id}` → `User`
- `POST /api/v1/users/{id}/activate` → `User`
- `POST /api/v1/users/{id}/deactivate` → `User`

**Projects**:
- `GET /api/v1/projects` → `{ items: Project[], total: int }`
- `GET /api/v1/projects/{id}` → `Project`
- `POST /api/v1/projects` → `Project`
- `PUT /api/v1/projects/{id}` → `Project`
- `DELETE /api/v1/projects/{id}` → `{ message }`
- `POST /api/v1/projects/{id}/employees/{user_id}` → `{ message }`
- `DELETE /api/v1/projects/{id}/employees/{user_id}` → `{ message }`

**Accessories**:
- `GET /api/v1/accessories` → `{ items: Accessory[], total: int }`
- `GET /api/v1/accessories/{id}` → `Accessory`
- `POST /api/v1/accessories` → `Accessory`
- `PUT /api/v1/accessories/{id}` → `Accessory`
- `DELETE /api/v1/accessories/{id}` → `{ message }`
- `POST /api/v1/accessories/{id}/photo` → `{ photo_url }`

## Troubleshooting

### "Cannot find module '@/...'"

Make sure `tsconfig.json` path aliases are configured and IDE is using correct TypeScript version.

### "API requests fail with CORS error"

Ensure backend is running on port 8000 and Vite proxy is configured in `vite.config.ts`:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

### "401 Unauthorized" on API calls

Check that localStorage persists tokens correctly. Open DevTools → Application → Local Storage and verify:
- `accessToken` exists and is not empty
- `refreshToken` exists and is not empty

### "Cannot read property 'email' of undefined"

The auth store hasn't been initialized with user data. Ensure `loginMutation` successful response includes user profile, and `setUser()` is called after login.

## Git Workflow

Never commit these files:
- `.env.local` (use `.env.example` template)
- `node_modules/`
- `dist/`

```bash
# Add files
git add src/

# Commit
git commit -m "feat: add login page"

# Push
git push origin main
```

## License

© 2024 OBRAS. All rights reserved.
