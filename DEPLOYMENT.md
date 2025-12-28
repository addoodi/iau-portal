# IAU Portal - Deployment Guide

This guide covers multiple deployment options for the IAU Portal application (React + FastAPI + CSV storage).

## Table of Contents
1. [Quick Deploy - Render.com (Recommended)](#option-1-rendercom-recommended)
2. [Vercel (Frontend) + Railway (Backend)](#option-2-vercel--railway)
3. [University Server (Self-Hosted)](#option-3-university-server-self-hosted)
4. [GitHub Pages (Static Demo Only)](#option-4-github-pages-frontend-only)

---

## Option 1: Render.com (Recommended)

**Best for:** Full-stack deployment with persistent CSV storage
**Cost:** Free tier available
**Difficulty:** ⭐ Easy

### Prerequisites
- GitHub account (already set up)
- Render.com account (free signup)

### Steps

1. **Sign up at [Render.com](https://render.com)**
   - Use "Sign in with GitHub" for easy integration

2. **Create New Web Service for Backend**
   - Dashboard → "New +" → "Web Service"
   - Connect your GitHub repository: `addoodi/iau-portal`
   - Configure:
     ```
     Name: iau-portal-backend
     Environment: Python 3
     Build Command: pip install -r requirements.txt
     Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
     ```
   - Add Environment Variables:
     ```
     PYTHON_VERSION=3.11
     ```
   - Add Disk (for CSV persistence):
     ```
     Name: iau-data
     Mount Path: /opt/render/project/src/backend/data
     Size: 1 GB
     ```

3. **Create Static Site for Frontend**
   - Dashboard → "New +" → "Static Site"
   - Connect same repository
   - Configure:
     ```
     Name: iau-portal-frontend
     Build Command: npm install && npm run build
     Publish Directory: build
     ```
   - Add Environment Variable:
     ```
     VITE_API_URL=https://iau-portal-backend.onrender.com
     ```
     (Replace with your actual backend URL from step 2)

4. **Enable CORS on Backend**
   Add your frontend URL to allowed origins in `backend/main.py`:
   ```python
   origins = [
       "http://localhost:3000",
       "https://iau-portal-frontend.onrender.com",  # Add your Render frontend URL
   ]
   ```

5. **Deploy**
   - Render will automatically deploy on every push to `main`
   - Check deployment logs for any errors
   - Your app will be live at: `https://iau-portal-frontend.onrender.com`

### Notes
- Free tier: Backend sleeps after 15 min inactivity (wakes in ~30s on first request)
- CSV data persists on the attached disk
- SSL/HTTPS enabled automatically

---

## Option 2: Vercel + Railway

**Best for:** Separate frontend/backend with auto-scaling
**Cost:** Free tier available
**Difficulty:** ⭐⭐ Medium

### Frontend on Vercel

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy Frontend**
   ```bash
   cd iau-portal
   vercel
   ```
   - Follow prompts
   - Set build command: `npm run build`
   - Set output directory: `build`

3. **Add Environment Variable**
   - Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add: `VITE_API_URL` = `https://your-railway-backend-url.railway.app`

### Backend on Railway

1. **Sign up at [Railway.app](https://railway.app)**

2. **New Project → Deploy from GitHub**
   - Select `addoodi/iau-portal`
   - Railway auto-detects Python

3. **Configure**
   - Add start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Add volume for data persistence:
     ```
     Mount Path: /app/backend/data
     ```

4. **Add CORS Origins**
   Update `backend/main.py` with your Vercel URL

5. **Deploy**
   - Push to GitHub triggers auto-deployment
   - Get backend URL from Railway dashboard

---

## Option 3: University Server (Self-Hosted)

**Best for:** Full control, on-premises hosting
**Cost:** Uses existing infrastructure
**Difficulty:** ⭐⭐⭐ Advanced

### Requirements
- Ubuntu/CentOS server with SSH access
- Domain name (optional but recommended)
- Root or sudo access

### Installation Steps

1. **SSH into Server**
   ```bash
   ssh user@your-server.iau.edu.sa
   ```

2. **Install Dependencies**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Node.js 18+
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt install -y nodejs

   # Install Python 3.11+
   sudo apt install -y python3.11 python3.11-venv python3-pip

   # Install nginx (web server)
   sudo apt install -y nginx

   # Install git
   sudo apt install -y git
   ```

3. **Clone Repository**
   ```bash
   cd /var/www
   sudo git clone https://github.com/addoodi/iau-portal.git
   cd iau-portal
   ```

4. **Setup Backend**
   ```bash
   # Create virtual environment
   python3.11 -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt

   # Test backend
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

5. **Setup Frontend**
   ```bash
   # Create production .env file
   echo "VITE_API_URL=https://portal.iau.edu.sa" > .env.production

   # Install and build
   npm install
   npm run build
   ```

6. **Configure Nginx**
   Create `/etc/nginx/sites-available/iau-portal`:
   ```nginx
   server {
       listen 80;
       server_name portal.iau.edu.sa;

       # Frontend
       location / {
           root /var/www/iau-portal/build;
           try_files $uri $uri/ /index.html;
       }

       # Backend API
       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

   Enable site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/iau-portal /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

7. **Setup Systemd Service** (Keep backend running)
   Create `/etc/systemd/system/iau-portal.service`:
   ```ini
   [Unit]
   Description=IAU Portal Backend
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/var/www/iau-portal
   Environment="PATH=/var/www/iau-portal/venv/bin"
   ExecStart=/var/www/iau-portal/venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable iau-portal
   sudo systemctl start iau-portal
   sudo systemctl status iau-portal
   ```

8. **Setup SSL (HTTPS)** - Optional but Recommended
   ```bash
   # Install certbot
   sudo apt install -y certbot python3-certbot-nginx

   # Get certificate
   sudo certbot --nginx -d portal.iau.edu.sa

   # Auto-renewal
   sudo systemctl enable certbot.timer
   ```

9. **Setup Auto-Deployment** (Optional)
   Create `/var/www/iau-portal/deploy.sh`:
   ```bash
   #!/bin/bash
   cd /var/www/iau-portal
   git pull origin main

   # Update backend
   source venv/bin/activate
   pip install -r requirements.txt
   sudo systemctl restart iau-portal

   # Update frontend
   npm install
   npm run build
   ```

   Make executable: `chmod +x deploy.sh`

### Monitoring
```bash
# Check backend logs
sudo journalctl -u iau-portal -f

# Check nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Check backend status
sudo systemctl status iau-portal
```

---

## Option 4: GitHub Pages (Frontend Only)

**Best for:** Quick demo/preview (no backend functionality)
**Cost:** Free
**Difficulty:** ⭐ Easy
**Limitation:** ⚠️ Frontend only, no backend API

### Steps

1. **Install gh-pages**
   ```bash
   npm install --save-dev gh-pages
   ```

2. **Update package.json**
   ```json
   {
     "homepage": "https://addoodi.github.io/iau-portal",
     "scripts": {
       "predeploy": "npm run build",
       "deploy": "gh-pages -d build"
     }
   }
   ```

3. **Deploy**
   ```bash
   npm run deploy
   ```

4. **Enable GitHub Pages**
   - GitHub repo → Settings → Pages
   - Source: `gh-pages` branch
   - Your site: `https://addoodi.github.io/iau-portal`

⚠️ **Note:** This only deploys the React frontend. You'll need a separate backend deployment.

---

## Comparison Table

| Platform | Cost | Difficulty | Backend | Persistence | Auto-Deploy | SSL |
|----------|------|------------|---------|-------------|-------------|-----|
| **Render** | Free tier | ⭐ | ✅ | ✅ Disk | ✅ | ✅ |
| **Vercel + Railway** | Free tier | ⭐⭐ | ✅ | ✅ Volume | ✅ | ✅ |
| **University Server** | Infrastructure | ⭐⭐⭐ | ✅ | ✅ Local | Manual | Optional |
| **GitHub Pages** | Free | ⭐ | ❌ | ❌ | ✅ | ✅ |

---

## Recommended Approach

**For Testing:** Render.com (Option 1) - Quickest full-stack deployment

**For Production:** University Server (Option 3) - Full control, meets data residency requirements

**For Demo:** Vercel + Railway (Option 2) - Professional, scalable

---

## Post-Deployment Checklist

- [ ] Test login with admin credentials
- [ ] Verify leave request submission
- [ ] Check Arabic/English language switching
- [ ] Test manager approvals
- [ ] Verify document generation (signatures)
- [ ] Check calendar view in approvals
- [ ] Test on mobile devices
- [ ] Verify CORS is properly configured
- [ ] Check that CSV data persists after restart
- [ ] Test RTL (Arabic) layout rendering

---

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip list

# Check logs
uvicorn backend.main:app --reload --log-level debug
```

### Frontend shows "Network Error"
- Check VITE_API_URL is correct
- Verify CORS origins in backend/main.py
- Check browser console for actual error

### CSV data not persisting
- Ensure disk/volume is mounted correctly
- Check write permissions: `ls -la backend/data/`
- Verify path in deployment configuration

### Arabic text displays incorrectly
- Check HTML has `lang` attribute
- Verify font supports Arabic characters
- Check RTL CSS is loading

---

## Support

For deployment issues specific to IAU infrastructure, contact:
- University IT Department
- Or create an issue: https://github.com/addoodi/iau-portal/issues
