# OBRAS Frontend - File Inventory & Architecture

## 📁 Complete Directory Structure

```
frontend/
├── src/
│   ├── pages/                          (Page components for each module)
│   │   ├── auth/
│   │   │   └── LoginPage.tsx           ✅ DONE - Login form with validation
│   │   ├── projects/                   (Pending)
│   │   ├── accessories/                (Pending)
│   │   ├── inspections/                (Pending - external + site)
│   │   ├── decommissions/              (Pending)
│   │   ├── reports/                    (Pending)
│   │   ├── audit/                      (Pending - admin only)
│   │   ├── users/                      (Pending - admin only)
│   │   └── DashboardPage.tsx           ✅ DONE - Main dashboard
│   │
│   ├── components/                     (Reusable UI components)
│   │   ├── layout/                     (Pending)
│   │   │   ├── AppShell.tsx            (Main layout wrapper)
│   │   │   ├── Sidebar.tsx             (Navigation menu)
│   │   │   └── TopBar.tsx              (User profile + logout)
│   │   ├── forms/                      (Pending)
│   │   │   ├── FileUpload.tsx
│   │   │   ├── DateField.tsx
│   │   │   └── ... (form inputs)
│   │   ├── semaforo/                   (Pending)
│   │   │   ├── SemaforoBadge.tsx       (Status indicator)
│   │   │   ├── SemaforoFilter.tsx
│   │   │   └── SemaforoChart.tsx
│   │   ├── tables/                     (Pending)
│   │   │   ├── AccessoryTable.tsx
│   │   │   ├── InspectionTable.tsx
│   │   │   └── AuditTable.tsx
│   │   └── ui/                         (Pending)
│   │       ├── Modal.tsx               (Dialog wrapper)
│   │       ├── ConfirmDialog.tsx
│   │       ├── StatusChip.tsx
│   │       ├── Badge.tsx
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       ├── Spinner.tsx
│   │       └── Alert.tsx
│   │
│   ├── services/                       (API client layer)
│   │   ├── api.ts                      ✅ Axios + JWT interceptor
│   │   ├── authApi.ts                  ✅ Login, refresh, logout, profile
│   │   ├── usersApi.ts                 ✅ User CRUD + activate/deactivate
│   │   ├── projectsApi.ts              ✅ Project CRUD + employee management
│   │   └── accessoriesApi.ts           ✅ Accessory CRUD + photo upload
│   │
│   ├── store/                          (Zustand global state)
│   │   ├── authStore.ts                ✅ Auth state (user, tokens, loading)
│   │   └── uiStore.ts                  ✅ UI state (sidebar, active items)
│   │
│   ├── hooks/                          (Custom React hooks)
│   │   └── useAuth.ts                  ✅ useLogin, useLogout, useRefreshToken
│   │
│   ├── types/                          (TypeScript type definitions)
│   │   └── index.ts                    ✅ All domain types + enums
│   │
│   ├── utils/                          (Utility functions)
│   │   ├── semaforoUtils.ts            ✅ Status calculation logic
│   │   ├── dateUtils.ts                ✅ Timezone-aware formatting
│   │   └── pdfUtils.ts                 ✅ PDF export with jsPDF
│   │
│   ├── routes/                         (Route definitions)
│   │   └── ProtectedRoute.tsx          ✅ Auth guard wrapper
│   │
│   ├── styles/                         (Global CSS)
│   │   └── index.css                   ✅ Tailwind + base styles
│   │
│   ├── App.tsx                         ✅ Root component with routing
│   └── main.tsx                        ✅ React 18 entry point
│
├── public/                             (Static assets)
│
├── Configuration Files:
│   ├── package.json                    ✅ 43 npm dependencies + scripts
│   ├── vite.config.ts                  ✅ Vite + API proxy
│   ├── tsconfig.json                   ✅ TypeScript strict mode
│   ├── tailwind.config.ts              ✅ Tailwind + semáforo colors
│   ├── .eslintrc.cjs                   ✅ ESLint configuration
│   ├── .prettierrc.js                  ✅ Prettier configuration
│   ├── .prettierignore                 ✅ Prettier ignore rules
│   ├── .env.example                    ✅ Environment template
│   ├── .gitignore                      ✅ Git ignore rules
│   └── index.html                      ✅ HTML entry point
│
├── Documentation:
│   ├── README.md                       ✅ Detailed frontend docs
│   └── VERIFICATION.md                 ✅ Testing & verification checklist
│
└── node_modules/                       (After npm install)
```

---

## 📦 npm Dependencies (43 Total)

### Core Framework (3)
- `react` 18.3.1
- `react-dom` 18.3.1
- `react-router-dom` 6.23.0

### TypeScript (1)
- `typescript` 5.4.5

### Build & Dev (4)
- `vite` 5.2.13
- `@vitejs/plugin-react` 4.3.0
- `@types/react` 18.3.3
- `@types/react-dom` 18.3.0

### Styling (2)
- `tailwindcss` 3.4.3
- `autoprefixer` 10.4.19

### State Management (1)
- `zustand` 4.5.0

### Server State & Caching (1)
- `@tanstack/react-query` 5.40.1

### HTTP Client (1)
- `axios` 1.7.2

### Form Handling & Validation (2)
- `react-hook-form` 7.51.4
- `zod` 3.23.8

### UI Components (2)
- `@headlessui/react` 2.1.6
- `lucide-react` 0.408.0

### Date & Time (2)
- `date-fns` 3.6.0
- `date-fns-tz` 3.1.3

### PDF Export (2)
- `jspdf` 2.5.1
- `jspdf-autotable` 3.8.1

### Development Tools (15)
- `@typescript-eslint/eslint-plugin` 7.0.0
- `@typescript-eslint/parser` 7.0.0
- `eslint` 8.57.0
- `eslint-plugin-react-hooks` 4.6.0
- `@types/node` 20.11.20
- `prettier` 3.2.5
- `tailwindcss` (included above)
- `postcss` 8.4.38
- `@vitejs/plugin-react-swc` 3.5.0
- Plus dev-only types and utilities

---

## 🔧 Configuration Details

### vite.config.ts ✅
```typescript
// Key features:
- API proxy: /api → http://localhost:8000
- Path alias: @/* → src/*
- React plugin with JSX support
- Code splitting for vendor bundles
- Dev server on port 5173
```

### tsconfig.json ✅
```json
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### tailwind.config.ts ✅
```typescript
// Theme extensions:
colors: {
  semaforo: {
    verde: '#10b981',
    amarillo: '#f59e0b',
    rojo: '#ef4444'
  }
}
// Content configured for src/
```

### package.json Scripts ✅
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext .ts,.tsx",
    "format": "prettier --write \"src/**/*.{ts,tsx}\"",
    "type-check": "tsc --noEmit"
  }
}
```

---

## 🧩 Component Architecture

### State Flow
```
User Input (Form)
    ↓
useLogin() Hook (React Query Mutation)
    ↓
authApi.login(credentials) (Axios POST)
    ↓
Backend API (http://localhost:8000/api/v1/auth/login)
    ↓
Response with tokens
    ↓
useAuthStore.setTokens() (Zustand)
    ↓
localStorage.setItem('accessToken', ...) (Persist)
    ↓
useAuthStore.setUser() (Zustand)
    ↓
Navigate('/dashboard')
    ↓
ProtectedRoute validates isAuthenticated
    ↓
DashboardPage renders
```

### API Request Flow
```
Frontend Component
    ↓
API Service Method (e.g., projectsApi.listProjects())
    ↓
apiClient.get('/projects', { ... })
    ↓
Axios Request Interceptor
    ↓ Adds: Authorization: Bearer <accessToken>
    ↓
HTTP Request to Backend
    ↓
Backend API Response
    ↓
Axios Response Interceptor
    ↓ On 401: Refresh token, retry request
    ↓
Component receives data
    ↓
React Query caches result
```

### Type Safety
```typescript
// Example: LoginRequest → Backend API → TokenResponse → Zustand Store
LoginRequest {
  email: string
  password: string
}
    ↓
POST /auth/login
    ↓
TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}
    ↓
useAuthStore.setTokens(access_token, refresh_token)
    ↓
Stored as: { accessToken, refreshToken, isAuthenticated: true }
```

---

## 📊 Implementation Status by File

### ✅ COMPLETE (21 files)

**Entry Point & Root:**
- src/main.tsx (React 18 entry with Tailwind import)
- src/App.tsx (Root with QueryClientProvider + Router)

**Pages (2 of 10):**
- src/pages/auth/LoginPage.tsx
- src/pages/DashboardPage.tsx

**Services (1 of 5):**
- src/services/api.ts (Axios + interceptor)
- src/services/authApi.ts
- src/services/usersApi.ts
- src/services/projectsApi.ts
- src/services/accessoriesApi.ts

**State Management (2 of 2):**
- src/store/authStore.ts
- src/store/uiStore.ts

**Hooks (1 of 10):**
- src/hooks/useAuth.ts

**Utils (3 of 3):**
- src/utils/semaforoUtils.ts
- src/utils/dateUtils.ts
- src/utils/pdfUtils.ts

**Routes (1 of 1):**
- src/routes/ProtectedRoute.tsx

**Types (1 of 1):**
- src/types/index.ts

**Styling (1 of 1):**
- src/styles/index.css

**Config (8 of 8):**
- vite.config.ts
- tsconfig.json
- tailwind.config.ts
- package.json
- .env.example
- .eslintrc.cjs
- .prettierrc.js
- index.html

### 🟡 PENDING (20+ files)

**Pages (8):**
- src/pages/projects/ProjectsPage.tsx
- src/pages/projects/ProjectFormPage.tsx
- src/pages/projects/ProjectDetailPage.tsx
- src/pages/accessories/AccessoriesPage.tsx
- src/pages/accessories/AccessoryFormPage.tsx
- src/pages/accessories/AccessoryDetailPage.tsx
- src/pages/inspections/ExternalInspectionForm.tsx
- src/pages/inspections/SiteInspectionForm.tsx
- (+ more for reports, decommissions, audit, users)

**Layout Components (3):**
- src/components/layout/AppShell.tsx
- src/components/layout/Sidebar.tsx
- src/components/layout/TopBar.tsx

**Data Tables (3):**
- src/components/tables/AccessoryTable.tsx
- src/components/tables/InspectionTable.tsx
- src/components/tables/AuditTable.tsx

**Forms (5):**
- src/components/forms/FileUpload.tsx
- src/components/forms/DateField.tsx
- src/components/forms/Input.tsx
- src/components/forms/Select.tsx
- src/components/forms/Textarea.tsx

**Semáforo Components (3):**
- src/components/semaforo/SemaforoBadge.tsx
- src/components/semaforo/SemaforoFilter.tsx
- src/components/semaforo/SemaforoChart.tsx

**UI Components (10+):**
- src/components/ui/Modal.tsx
- src/components/ui/ConfirmDialog.tsx
- src/components/ui/Button.tsx
- src/components/ui/Card.tsx
- src/components/ui/Badge.tsx
- src/components/ui/Spinner.tsx
- src/components/ui/Alert.tsx
- src/components/ui/Tabs.tsx
- src/components/ui/Dropdown.tsx
- src/components/ui/TooltipProvider.tsx

**Additional Hooks (3+):**
- src/hooks/useApiQuery.ts
- src/hooks/useApiMutation.ts
- src/hooks/usePagination.ts

---

## 🚀 What's Ready to Use

### Immediate Development

```typescript
// 1. Authentication
import { useLogin, useLogout } from '@/hooks/useAuth';
import { useAuthStore } from '@/store/authStore';

const { isAuthenticated, user } = useAuthStore();
const loginMutation = useLogin();

// 2. API Calls
import { projectsApi } from '@/services/projectsApi';
const projects = await projectsApi.listProjects();

// 3. Date Formatting
import { formatDateShort, getDaysUntil } from '@/utils/dateUtils';
const formatted = formatDateShort('2024-12-31T10:00:00Z');

// 4. Semáforo Status
import { calculateSemaforoStatus } from '@/utils/semaforoUtils';
const status = calculateSemaforoStatus(extDate, siteDate, false);

// 5. PDF Export
import { exportReportToPDF } from '@/utils/pdfUtils';
exportReportToPDF(data, 'report.pdf');
```

---

## ✨ Key Features Implemented

✅ **Authentication**
- Email/password login form
- JWT token management
- Auto-refresh on token expiry
- Logout with cleanup
- Protected routes

✅ **API Integration**
- Axios HTTP client
- JWT interceptor
- 401 error handling
- Request/response typing
- Error messages

✅ **State Management**
- Zustand stores
- localStorage persistence
- Type-safe selectors
- Computed state

✅ **Developer Experience**
- TypeScript strict mode
- Path aliases (@/*)
- ESLint + Prettier
- Vite hot reload
- API documentation in code

---

## 🔗 Dependencies between Files

```
main.tsx
  ├→ App.tsx
  │   ├→ Router (React Router)
  │   ├→ QueryClientProvider (React Query)
  │   ├→ ProtectedRoute.tsx
  │   └→ LoginPage.tsx, DashboardPage.tsx
  │
  └→ styles/index.css (Tailwind)

App.tsx
  ├→ store/authStore.ts (useAuthStore)
  ├→ routes/ProtectedRoute.tsx
  │   ├→ store/authStore.ts
  │   └→ React Router useNavigate()
  │
  └→ pages/auth/LoginPage.tsx
      ├→ hooks/useAuth.ts (useLogin)
      │   ├→ services/authApi.ts
      │   │   └→ services/api.ts (Axios)
      │   └→ store/authStore.ts (setTokens, setUser)
      ├→ types/index.ts (LoginRequest)
      └→ store/authStore.ts (setError, setLoading)

DashboardPage.tsx
  ├→ store/authStore.ts (user, logout)
  ├→ store/uiStore.ts (sidebarOpen)
  └→ React Router useNavigate()
```

---

## 📈 Scalability Considerations

### Code Splitting
```typescript
// Use React.lazy() for route components (pending)
const ProjectsPage = lazy(() => import('@/pages/projects/ProjectsPage'));

<Route path="/projects" element={<Suspense fallback={<Spinner />}><ProjectsPage /></Suspense>} />
```

### Caching Strategy
```typescript
// React Query default options (pending fine-tuning)
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,  // 5 minutes
      gcTime: 10 * 60 * 1000,    // 10 minutes (was cacheTime)
    },
  },
});
```

### Component Optimization
```typescript
// Memoization for expensive renders (pending)
const ProjectsList = memo(({ projects }) => {
  return <div>{projects.map(...)}</div>;
}, (prev, next) => {
  return prev.projects === next.projects;
});
```

---

## 📋 Pre-Development Checklist

Before adding more components:

- [ ] Test npm install and npm run dev
- [ ] Verify login works with backend
- [ ] Check localStorage has tokens
- [ ] Confirm dashboard loads
- [ ] Test Tailwind CSS colors
- [ ] Verify TypeScript strict mode
- [ ] Check console for errors
- [ ] Review component architecture
- [ ] Plan page structure
- [ ] Design data table layouts

---

**Frontend Architecture Version:** 1.0  
**Total Files:** 51 (21 existing + 30 pending)  
**LOC (Existing):** ~1500 lines  
**LOC (Pending):** ~3000-4000 lines  
**Time to Complete:** ~20-30 hours