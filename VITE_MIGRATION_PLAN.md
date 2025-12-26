# Vite Migration Plan - IAU Portal

> **Purpose:** Step-by-step guide to migrate from Create React App (CRA) to Vite
> **Estimated Time:** 2-3 hours
> **Risk Level:** Low (reversible via Git)
> **Target Date:** Phase 2, Week 3

---

## Table of Contents

1. [Why Migrate to Vite?](#1-why-migrate-to-vite)
2. [Pre-Migration Checklist](#2-pre-migration-checklist)
3. [Migration Steps](#3-migration-steps)
4. [Post-Migration Verification](#4-post-migration-verification)
5. [Rollback Plan](#5-rollback-plan)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Why Migrate to Vite?

### Current Situation (CRA)
- **Create React App is DEPRECATED** (last update: April 2023)
- **Build time:** 30-60 seconds (slow)
- **Dev server start:** 10-15 seconds
- **No security updates** from Meta
- **Webpack-based** (complex, legacy)

### Future State (Vite)
- **Build time:** 2-5 seconds (10-20x faster)
- **Dev server start:** <1 second (instant hot reload)
- **Active development** (regular updates)
- **esbuild + Rollup** (modern, fast)
- **Better production builds**

### Business Impact
- ✅ Faster development (less waiting for builds)
- ✅ Easier university IT handover (modern, well-documented)
- ✅ Future-proof (actively maintained)
- ✅ Better developer experience
- ✅ Smaller production bundle sizes

---

## 2. Pre-Migration Checklist

### ✅ Before You Start

**CRITICAL: Create a Git branch for migration**

```bash
# 1. Ensure you're on main with no uncommitted changes
git status

# 2. Create a new branch for migration
git checkout -b migration/vite

# 3. If anything goes wrong, you can always:
git checkout main  # Go back to working CRA version
```

**Backup Checklist:**
- [x] Git repository initialized (✅ done)
- [x] Code pushed to GitHub (✅ done)
- [ ] CSV data backed up externally
- [ ] Current app running and tested

**Environment Verification:**
```bash
# Check Node.js version (need 18+)
node --version   # Should be v18.0.0 or higher

# Check npm version
npm --version

# Ensure backend is NOT running (avoid port conflicts)
# Stop: python -m uvicorn backend.main:app --reload
```

---

## 3. Migration Steps

### Step 1: Install Vite (15 minutes)

#### 1A. Install Vite and plugins

```bash
# Install Vite and React plugin
npm install --save-dev vite @vitejs/plugin-react

# Install additional Vite-specific tools
npm install --save-dev vite-plugin-svgr  # For SVG imports (if needed)
```

**Expected output:**
```
added 50 packages in 30s
```

#### 1B. Create Vite configuration file

**Create:** `vite.config.js` in project root

```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true,
  },
  build: {
    outDir: 'build',
    sourcemap: false,
  },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
});
```

---

### Step 2: Move and Update index.html (10 minutes)

#### 2A. Move index.html from public/ to root

```bash
# Move index.html from public/ to root directory
# Windows:
move public\index.html index.html

# OR manually drag & drop in file explorer
```

#### 2B. Update index.html

**Replace** the contents of `index.html` (now in root) with:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="IAU Portal - Employee Leave Management System" />
    <link rel="apple-touch-icon" href="/logo192.png" />
    <link rel="manifest" href="/manifest.json" />
    <title>IAU Portal</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
    <script type="module" src="/src/index.js"></script>
  </body>
</html>
```

**Key Changes:**
1. ❌ Removed `%PUBLIC_URL%` (Vite uses `/` for public assets)
2. ✅ Added `<script type="module" src="/src/index.js"></script>`
3. ✅ Changed `<html lang="en">` for accessibility
4. ✅ Updated title to "IAU Portal"

---

### Step 3: Update Environment Variables (5 minutes)

**CRA uses:** `REACT_APP_*` prefix
**Vite uses:** `VITE_*` prefix

#### 3A. Check if you have a .env file

```bash
# List .env files
dir .env* /s  # Windows
# OR
ls -la | grep .env  # If using Git Bash
```

#### 3B. If .env exists, rename variables

**OLD (CRA):**
```
REACT_APP_API_URL=http://localhost:8000
```

**NEW (Vite):**
```
VITE_API_URL=http://localhost:8000
```

#### 3C. Update code that references environment variables

**Search and replace in all files:**

**OLD:**
```javascript
const apiUrl = process.env.REACT_APP_API_URL;
```

**NEW:**
```javascript
const apiUrl = import.meta.env.VITE_API_URL;
```

**For your project:** You're using dynamic API URL based on `window.location.hostname`, so this may not apply. Check `src/api.js`:

```javascript
// Current code (src/api.js) - likely fine as-is
const API_BASE_URL = `http://${window.location.hostname}:8000/api`;
```

✅ **No changes needed if using window.location**

---

### Step 4: Update package.json Scripts (5 minutes)

**Edit:** `package.json`

**OLD (CRA) scripts:**
```json
"scripts": {
  "start": "react-scripts start",
  "build": "react-scripts build",
  "test": "react-scripts test",
  "eject": "react-scripts eject"
}
```

**NEW (Vite) scripts:**
```json
"scripts": {
  "dev": "vite",
  "start": "vite",
  "build": "vite build",
  "preview": "vite preview",
  "test": "vitest"
}
```

**Note:**
- `npm start` will still work (maps to `vite`)
- `npm run dev` is Vite's standard command
- `npm run preview` lets you test production build locally

---

### Step 5: Remove CRA Dependencies (10 minutes)

#### 5A. Uninstall react-scripts

```bash
npm uninstall react-scripts
```

**Expected:** This will remove ~1,200 packages (saves 500+ MB in node_modules)

#### 5B. Remove CRA-specific config from package.json

**Remove these sections from package.json:**

```json
// DELETE THIS:
"eslintConfig": {
  "extends": [
    "react-app",
    "react-app/jest"
  ]
},
```

**Keep:**
```json
"browserslist": {
  "production": [
    ">0.2%",
    "not dead",
    "not op_mini all"
  ],
  "development": [
    "last 1 chrome version",
    "last 1 firefox version",
    "last 1 safari version"
  ]
}
```

---

### Step 6: Update Tailwind Configuration (5 minutes)

**Your current `tailwind.config.js` should work as-is.**

Verify it includes:

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",  // ✅ Correct
    "./public/index.html"           // ❌ Remove this line (index.html moved)
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**Update to:**

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",                 // ✅ New location
    "./src/**/*.{js,jsx,ts,tsx}",  // ✅ Keep this
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

---

### Step 7: First Run - Test Vite (10 minutes)

#### 7A. Clean install dependencies

```bash
# Delete node_modules and package-lock.json
rmdir /s /q node_modules  # Windows
del package-lock.json

# Fresh install
npm install
```

#### 7B. Start Vite dev server

```bash
npm start

# OR
npm run dev
```

**Expected output:**
```
VITE v5.x.x  ready in 500 ms

➜  Local:   http://localhost:3000/
➜  Network: http://192.168.x.x:3000/
➜  press h + enter to show help
```

#### 7C. Open browser and test

Visit: http://localhost:3000

**Check:**
- [ ] Login page loads
- [ ] Tailwind CSS styles apply
- [ ] Can navigate between pages
- [ ] Dashboard renders correctly
- [ ] No console errors

---

### Step 8: Test Production Build (15 minutes)

#### 8A. Build for production

```bash
npm run build
```

**Expected output:**
```
vite v5.x.x building for production...
✓ 150 modules transformed.
build/index.html                   0.45 kB │ gzip:  0.30 kB
build/assets/index-abc123.css     12.34 kB │ gzip:  3.45 kB
build/assets/index-xyz789.js     145.67 kB │ gzip: 45.67 kB
✓ built in 2.5s
```

**Comparison:**
- CRA build: ~30-60 seconds
- Vite build: ~2-5 seconds (10x faster!)

#### 8B. Preview production build

```bash
npm run preview
```

Visit: http://localhost:4173

**Test all features:**
- [ ] Login works
- [ ] Dashboard loads
- [ ] Leave requests work
- [ ] Document download works
- [ ] Bilingual switching (AR/EN)
- [ ] All pages accessible

---

### Step 9: Update .gitignore (2 minutes)

**Add Vite-specific entries to `.gitignore`:**

```
# Vite
dist/
.vite/
dist-ssr/
*.local
```

**Note:** Your `.gitignore` already has these from our Git setup! ✅

---

### Step 10: Commit Migration (5 minutes)

```bash
# Check status
git status

# Stage all changes
git add .

# Commit
git commit -m "Migrate from Create React App to Vite

- Install Vite and @vitejs/plugin-react
- Move index.html from public/ to root
- Update index.html to use Vite's module script
- Update package.json scripts (start -> vite)
- Remove react-scripts dependency
- Update Tailwind config for new index.html location
- Create vite.config.js
- Build time reduced from 30s to ~3s (10x improvement)
- Dev server startup: <1s (instant hot reload)

Tested:
✅ Dev server runs on port 3000
✅ All pages load correctly
✅ Tailwind CSS working
✅ Production build successful
✅ Bilingual support intact"

# Push to GitHub
git push -u origin migration/vite
```

---

### Step 11: Merge to Main (5 minutes)

**After thorough testing:**

```bash
# Switch to main branch
git checkout main

# Merge migration branch
git merge migration/vite

# Push to GitHub
git push

# Delete migration branch (optional)
git branch -d migration/vite
git push origin --delete migration/vite
```

---

## 4. Post-Migration Verification

### Comprehensive Testing Checklist

**Frontend (Dev Mode):**
- [ ] `npm start` works on port 3000
- [ ] Login page loads with correct styling
- [ ] Can log in with valid credentials
- [ ] Dashboard displays correctly
- [ ] RTL (Arabic) layout works
- [ ] Sidebar navigation functional
- [ ] All icons (lucide-react) render

**Pages:**
- [ ] Dashboard - team members, charts render
- [ ] My Requests - table displays, can create request
- [ ] Approvals - manager can see pending requests
- [ ] User Management - table loads, can add user
- [ ] Unit Management - units display
- [ ] Profile - can upload signature, change password
- [ ] Site Settings - SMTP configuration loads

**Features:**
- [ ] Leave request creation modal works
- [ ] Document download (DOCX) works
- [ ] File attachments upload
- [ ] Date picker functions
- [ ] Form validation shows errors

**Backend Integration:**
- [ ] FastAPI backend connects (http://localhost:8000)
- [ ] JWT authentication works
- [ ] API calls succeed
- [ ] No CORS errors

**Production Build:**
- [ ] `npm run build` completes in <10 seconds
- [ ] `npm run preview` serves correctly
- [ ] All assets load from /build/
- [ ] Console has no errors

**Performance:**
- [ ] Dev server starts in <2 seconds
- [ ] Hot reload is instant (<1s)
- [ ] Build time <5 seconds
- [ ] Production bundle size reasonable (<500 KB)

---

## 5. Rollback Plan

**If migration fails, rollback is EASY:**

```bash
# Discard all changes and go back to CRA
git checkout main

# Verify you're back to working state
npm install
npm start  # Should use react-scripts again
```

**Your data is safe:**
- ✅ CSV files not affected (in backend/data/)
- ✅ Git history preserved
- ✅ Can retry migration anytime

---

## 6. Troubleshooting

### Issue 1: "Cannot find module '@vitejs/plugin-react'"

**Cause:** Vite plugin not installed

**Solution:**
```bash
npm install --save-dev @vitejs/plugin-react
```

---

### Issue 2: "Failed to resolve import './index.css'"

**Cause:** Path resolution issue

**Solution:** Check `src/index.js` imports:
```javascript
import './index.css';  // ✅ Correct (relative path)
```

---

### Issue 3: Tailwind CSS not working

**Cause:** `tailwind.config.js` not updated

**Solution:** Ensure `content` includes `./index.html`:
```javascript
content: [
  "./index.html",                // ✅ Required
  "./src/**/*.{js,jsx,ts,tsx}",
],
```

---

### Issue 4: "Port 3000 is already in use"

**Cause:** Old CRA dev server still running

**Solution:**
```bash
# Kill the process on port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Then restart
npm start
```

---

### Issue 5: Public assets (images, manifest.json) not loading

**Cause:** Assets still using `%PUBLIC_URL%`

**Solution:**

**In HTML files:**
```html
<!-- OLD (CRA) -->
<link rel="icon" href="%PUBLIC_URL%/favicon.ico" />

<!-- NEW (Vite) -->
<link rel="icon" href="/favicon.ico" />
```

**In JavaScript:**
```javascript
// OLD (CRA)
<img src={process.env.PUBLIC_URL + '/logo.png'} />

// NEW (Vite)
<img src="/logo.png" />
```

---

### Issue 6: Environment variables not working

**Cause:** Still using `REACT_APP_*` prefix

**Solution:**

1. Rename in `.env`:
   ```
   VITE_API_URL=http://localhost:8000
   ```

2. Update code:
   ```javascript
   // OLD
   process.env.REACT_APP_API_URL

   // NEW
   import.meta.env.VITE_API_URL
   ```

---

### Issue 7: "Unexpected token '<'" in console

**Cause:** index.html script tag missing `type="module"`

**Solution:** Update `index.html`:
```html
<script type="module" src="/src/index.js"></script>
```

---

## 7. Performance Comparison

### Before (CRA)

| Metric | Time |
|--------|------|
| Dev server start | 10-15s |
| Hot reload | 2-5s |
| Production build | 30-60s |
| Bundle size | ~500 KB |

### After (Vite)

| Metric | Time | Improvement |
|--------|------|-------------|
| Dev server start | <1s | **15x faster** |
| Hot reload | <0.5s | **10x faster** |
| Production build | 2-5s | **10-15x faster** |
| Bundle size | ~300 KB | **40% smaller** |

---

## 8. Additional Resources

**Official Documentation:**
- Vite Guide: https://vitejs.dev/guide/
- Vite Config: https://vitejs.dev/config/
- Migration from CRA: https://vitejs.dev/guide/migration.html

**Troubleshooting:**
- Vite Troubleshooting: https://vitejs.dev/guide/troubleshooting.html
- GitHub Issues: https://github.com/vitejs/vite/issues

---

## 9. Success Criteria

✅ **Migration is successful when:**

1. `npm start` launches Vite dev server in <2 seconds
2. All 16 pages load without errors
3. Tailwind CSS styles apply correctly
4. Backend API integration works
5. Production build completes in <10 seconds
6. All features tested and working:
   - Login/logout
   - Leave request creation
   - Document generation
   - User management
   - Bilingual switching (AR/EN)
7. No console errors in browser
8. Git commit created and pushed to GitHub

---

## 10. Next Steps After Migration

Once Vite migration is complete:

1. **Update CLAUDE.md** - Mark "Migrate CRA → Vite" as ✅ Complete
2. **Update run_frontend.bat** - Change to `npm run dev` (optional)
3. **Phase 2, Week 4-5:** Start CSV → SQLite migration
4. **Phase 2, Week 6:** Add critical path tests

---

**Status:** Ready to execute
**Branch:** migration/vite
**Estimated Time:** 2-3 hours
**Risk:** Low (reversible via Git)
**Reward:** 10x faster builds, future-proof stack

**Good luck! I'll be here to help if you encounter any issues.**
