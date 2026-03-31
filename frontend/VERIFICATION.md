# OBRAS Frontend - Verification Checklist

Follow this checklist to verify the frontend is working correctly.

## Prerequisites ✅

- [ ] Node.js 18+ installed: `node --version`
- [ ] npm 9+ installed: `npm --version`
- [ ] Backend running on port 8000 (separate terminal)
- [ ] PostgreSQL running via Docker: `docker-compose ps`

## Frontend Setup Steps

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

Expected output:
```
added 43 packages, and audited X packages
```

Time: ~2-3 minutes

### Step 2: Verify Configuration Files

```bash
# Check that these files exist:
- vite.config.ts      (Vite configuration with proxy)
- tsconfig.json       (TypeScript strict mode config)
- tailwind.config.ts  (Tailwind CSS setup)
- package.json        (43 dependencies listed)
- tailwind.config.ts  (Colors extended with semáforo)
```

### Step 3: Start Development Server

```bash
npm run dev
```

Expected output:
```
VITE v5.2.x  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

If you see this, the server is running! ✅

### Step 4: Verify Frontend Loads

1. **Open browser:** `http://localhost:5173`
2. **Should see:** Login page with email/password fields
3. **Check for:**
   - OBRAS logo at top
   - "Gestión de Accesorios de Izaje" subtitle
   - Email input field (pre-filled: admin@example.com)
   - Password input field (pre-filled: ChangeMe123!)
   - Blue "Login" button
   - Demo credentials notice at bottom

### Step 5: Test API Connection

1. **Verify backend is running:**
   ```bash
   curl http://localhost:8000/docs
   ```
   Should return Swagger UI HTML

2. **Check Vite proxy:** Open DevTools (F12) → Network tab

3. **Attempt login:**
   - Email: `admin@example.com`
   - Password: `ChangeMe123!`
   - Click "Login" button

### Step 6: Expected Login Behavior

✅ **On Success:**
- Login button shows "Logging in..." briefly
- After 2-3 seconds: Redirects to `/dashboard`
- Dashboard displays welcome message
- Top right shows: `admin@example.com` and `ADMIN` role badge
- Sidebar shows navigation menu (OBRAS title + logout button)

❌ **On Failure:**
- Red error message appears under form
- Check backend logs for error details
- Common issues:
  - Backend not running on port 8000
  - Admin user not created: `python seed_admin.py`
  - Wrong credentials (use defaults)

### Step 7: Verify State Persistence

1. **Open DevTools** (F12)
2. **Go to:** Application tab → LocalStorage → http://localhost:5173
3. **Should see keys:**
   - `accessToken` (JWT token value)
   - `refreshToken` (JWT refresh token)
   - `user` (JSON with user data)
   - `isAuthenticated` (true)

If these exist → tokens are persisting ✅

### Step 8: Test Protected Route

1. **Open DevTools** → Application → LocalStorage
2. **Delete the `accessToken` key** (right-click → Delete)
3. **Refresh page** (F5)
4. **Should see:** Redirected back to `/login`

This confirms ProtectedRoute is working ✅

### Step 9: Verify Build Works

```bash
npm run build
```

Expected output:
```
✓ built in Xs

dist/
├── index.html
├── assets/
│   ├── index-XXXXX.js
│   └── index-XXXXX.css
└── ...
```

If `dist/` folder is created → production build works ✅

### Step 10: Check Console for Errors

1. **Open DevTools** (F12) → Console tab
2. **Should be clean** with no red errors
3. **May see warnings** (yellow) - these are OK for now
4. **Look for:**
   - No CORS errors
   - No "Cannot find module" errors
   - No TypeScript errors

---

## Troubleshooting

### Issue: "Cannot find module '@/...'"

**Solution:** 
- Close dev server (Ctrl+C)
- Clear cache: `rm -rf node_modules/.vite`
- Restart: `npm run dev`
- Check `vite.config.ts` line with `alias:`

### Issue: "network error, failed response"

**Solution:**
- Verify backend is running: `http://localhost:8000/docs`
- Check Vite proxy in `vite.config.ts`:
  ```typescript
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  }
  ```
- DevTools → Network → Look for `/api/v1/auth/login` request
- Should be forwarded to `http://localhost:8000`

### Issue: "401 Unauthorized"

**Solution:**
- Run: `python seed_admin.py` in backend terminal
- Use credentials: admin@example.com / ChangeMe123!
- Check backend logs for auth errors

### Issue: npm install fails

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Delete lock file
rm package-lock.json

# Reinstall
npm install
```

### Issue: "Port 5173 already in use"

**Solution:**
```powershell
# PowerShell (Windows)
lsof -i :5173        # macOS/Linux
netstat -ano | findstr :5173  # Windows

# Kill process
taskkill /PID [PID] /F

# Or use different port
npm run dev -- --port 5174
```

---

## Performance Checks

### Bundle Size

```bash
npm run build
```

Then check `dist/assets/` folder sizes:
- index JS should be < 500KB
- index CSS should be < 100KB

If larger, may need code splitting.

### Dev Server Speed

- `npm run dev`: Should start in < 5 seconds
- Page load: Should load in < 2 seconds
- Hot reload (save file): Should update in < 1 second

### Memory Usage

- Node process should use < 300MB RAM
- If higher, check for memory leaks

---

## What's Working

✅ **Login Page**
- Form with async submission
- Email/password validation
- Error message display
- Loading state (button disabled)
- Redirect on success

✅ **Dashboard Page**
- Protected route (requires auth)
- User information display
- Sidebar with navigation
- Responsive layout

✅ **API Integration**
- Axios client configured
- JWT interceptor working
- Token storage in localStorage
- Token refresh on 401

✅ **State Management**
- Zustand stores initialized
- localStorage persistence
- Clean setters/getters
- Type-safe usage

✅ **Build & Dev Tools**
- Vite dev server fast
- TypeScript strict checking
- Tailwind CSS compiling
- ESLint + Prettier configured

---

## What's Pending

🟡 **Layout Components**
- AppShell (main layout wrapper)
- Sidebar (navigation menu)
- TopBar (user profile + logout)

🟡 **Page Components** (8 pages)
- ProjectsPage
- AccessoriesPage
- ExternalInspectionPage
- SiteInspectionPage
- DecommissionPage
- ReportsPage (semáforo dashboard)
- AuditPage
- UsersPage

🟡 **Reusable UI Components** (10+)
- DataTable
- Form components
- Modal/Dialog
- Cards/Chips
- File upload
- Date picker
- Status badges
- Dropdowns
- Buttons
- Inputs

---

## Success Criteria

After running `npm run dev`:

- [ ] Vite server starts on http://localhost:5173
- [ ] Page loads with LoginPage visible
- [ ] Email and password fields present (pre-filled)
- [ ] Can type in fields
- [ ] Login button is clickable
- [ ] Click login → makes API request to backend
- [ ] Tokens appear in localStorage
- [ ] After login → redirects to /dashboard
- [ ] Dashboard shows welcome message
- [ ] User role displays in top right
- [ ] No red errors in console
- [ ] DevTools shows successful API request to `/api/v1/auth/login`
- [ ] Response includes `access_token` and `refresh_token`

If all ✅ above: **Frontend is working correctly!**

---

## Next Steps After Verification

1. **Build remaining services & routers** in backend (7 services × 3-5 methods each)
2. **Create page components** in frontend (8 pages × 100-300 lines each)
3. **Build reusable UI components** (tables, forms, modals, etc.)
4. **Add tests** (unit + integration + E2E)
5. **Optimize performance** (lazy load, code split, caching)
6. **Deploy** (Docker + CI/CD)

---

**Checklist Version:** 1.0  
**Last Updated:** December 2024  
**Status:** Ready for Testing
