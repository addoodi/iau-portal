# Docker Diagnostic Test Guide

This guide shows you how to run the **diagnostic version** of the Docker build that **skips the failing `npm run build`** step but checks everything else.

## 🎯 Purpose

The test Dockerfile will:
- ✅ Install all dependencies
- ✅ Copy all files
- ✅ Run 11 diagnostic checks
- ✅ Show you what's available for the build
- ❌ **NOT** run `npm run build` (skip the failing step)

This helps us identify if the problem is:
- Missing dependencies
- Missing files
- Configuration errors
- Or the actual Vite build process itself

---

## 🚀 Deploy Test Version in Portainer

### Method 1: Use Test Docker Compose

1. **Portainer** → **Stacks** → **"+ Add stack"**

2. **Name:** `iau-portal-test`

3. **Build method:** Repository

4. **Repository settings:**
   ```
   Repository URL: https://github.com/addoodi/iau-portal
   Reference: refs/heads/main
   Compose path: docker-compose.test.yml  ← Use TEST compose file

   Authentication: ON
   Username: addoodi
   Token: [your-token]
   ```

5. **Deploy**

---

### Method 2: Use Web Editor

1. **Portainer** → **Stacks** → **"+ Add stack"**

2. **Name:** `iau-portal-test`

3. **Build method:** Web editor

4. **Paste the contents of `docker-compose.test.yml`** or modify the regular one:
   ```yaml
   frontend:
     build:
       dockerfile: Dockerfile.frontend.test  # ← Change this line
   ```

5. **Deploy**

---

## 📊 What to Look For

### In Portainer Logs

1. After deployment, go to:
   ```
   Portainer → Containers → iau-portal-frontend-test → Logs
   ```

2. You'll see 11 diagnostic checks:

   ```
   ========================================
   CHECK 1: Node.js and NPM versions
   ========================================
   v18.x.x
   9.x.x

   ========================================
   CHECK 2: Required files present?
   ========================================
   ✓ package.json exists
   ✓ vite.config.js exists
   ✓ index.html exists
   ✓ src/ directory exists
   ✓ public/ directory exists

   ========================================
   CHECK 3: Installed dependencies
   ========================================
   [list of packages]

   [... checks 4-11 ...]

   ========================================
   ✓ ALL DIAGNOSTIC CHECKS PASSED!
   ========================================
   ```

3. **If all checks pass**, the problem is specifically in the Vite build command

4. **If a check fails**, you'll see which one and can share that with me

---

## 🔍 What Each Check Does

| Check | What it Verifies | If it Fails |
|-------|-----------------|-------------|
| 1 | Node/NPM versions | Node installation broken |
| 2 | Required files exist | Files not copied correctly |
| 3 | Dependencies installed | npm install failed |
| 4 | Critical deps (vite, react) | Missing key packages |
| 5 | Source files in src/ | Source code not copied |
| 6 | Vite config contents | Config file corrupted |
| 7 | NPM scripts defined | package.json broken |
| 8 | Vite CLI available | Vite not installed |
| 9 | Vite config can load | Syntax error in config |
| 10 | Disk space/memory | Resource constraints |
| 11 | Environment variables | ENV not set |

---

## ✅ If Test Passes

If you see:
```
✓ ALL DIAGNOSTIC CHECKS PASSED!
```

Then we know:
- ✅ Dependencies are installed
- ✅ Files are present
- ✅ Vite is available
- ✅ Configuration is valid

**The problem is in the actual Vite build process.**

To debug further, we can:
1. Add a step to run vite with more verbose logging
2. Try building specific files
3. Check for memory issues during transform phase

---

## ❌ If Test Fails

Share the output of the **specific check that failed**.

For example:
```
CHECK 4: Critical dependencies installed?
npm ERR! missing: vite@^7.3.0
```

Then I'll know exactly what to fix!

---

## 🔧 Run Locally (Alternative)

You can also test locally without Portainer:

```bash
# Navigate to project
cd /path/to/iau-portal

# Build with test Dockerfile
docker build -f Dockerfile.frontend.test -t iau-test .

# Watch the diagnostic output
docker build -f Dockerfile.frontend.test -t iau-test . 2>&1 | grep "CHECK"

# Or run the test compose
docker-compose -f docker-compose.test.yml up --build
```

---

## 📝 Next Steps After Test

**Scenario A: All checks pass**
→ The issue is in Vite's transform/bundle process
→ We'll add memory limits, verbose logging, or try building in dev mode

**Scenario B: Check X fails**
→ Share which check failed
→ I'll fix that specific issue

---

## 🔄 Return to Normal Build

When ready to try the real build again:

1. **Delete test stack:**
   ```
   Portainer → Stacks → iau-portal-test → Delete
   ```

2. **Deploy production stack:**
   ```
   Use docker-compose.yml (not docker-compose.test.yml)
   Use Dockerfile.frontend (not Dockerfile.frontend.test)
   ```

---

**Deploy the test version now and share the diagnostic output!** 🔍
