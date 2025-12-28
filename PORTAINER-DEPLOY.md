# IAU Portal - Portainer Deployment Guide

Complete guide for deploying IAU Portal using Docker and Portainer on your local server.

## 📋 Prerequisites

- Local server with Docker installed (Linux/Windows Server)
- Portainer installed and running
- Access to Portainer web interface
- Git installed on the server (optional, for direct cloning)

---

## 🚀 Quick Deploy (3 Methods)

### Method 1: Deploy via Portainer Git Repository (Recommended)

**Easiest method - Portainer builds from your GitHub repo**

1. **Open Portainer** → Navigate to your Portainer instance (e.g., `http://your-server:9000`)

2. **Go to Stacks**
   - Left menu → **Stacks**
   - Click **"+ Add stack"**

3. **Configure Stack**
   - **Name:** `iau-portal`
   - **Build method:** Select **"Repository"**
   - **Repository URL:** `https://github.com/addoodi/iau-portal`
   - **Repository reference:** `refs/heads/main`
   - **Compose path:** `docker-compose.yml`

4. **Environment Variables** (Optional)
   Click "+ Add an environment variable" if needed:
   ```
   VITE_API_URL=http://your-server-ip:8000
   ```

5. **Deploy**
   - Click **"Deploy the stack"**
   - Portainer will clone the repo and build both containers
   - Wait for build to complete (~2-5 minutes)

6. **Access Application**
   - Frontend: `http://your-server-ip:3000`
   - Backend: `http://your-server-ip:8000`

---

### Method 2: Deploy via Portainer Web Editor

**Good if you want to customize the compose file**

1. **Open Portainer** → **Stacks** → **"+ Add stack"**

2. **Name:** `iau-portal`

3. **Build method:** Select **"Web editor"**

4. **Paste this docker-compose configuration:**

```yaml
version: '3.8'

services:
  # Backend - FastAPI
  backend:
    image: ghcr.io/addoodi/iau-portal-backend:latest
    container_name: iau-portal-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - iau-data:/app/backend/data
      - iau-templates:/app/backend/templates
    environment:
      - PYTHONUNBUFFERED=1
    networks:
      - iau-network
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/api/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s

  # Frontend - React + Vite
  frontend:
    image: ghcr.io/addoodi/iau-portal-frontend:latest
    container_name: iau-portal-frontend
    restart: unless-stopped
    ports:
      - "3000:80"
    depends_on:
      - backend
    networks:
      - iau-network
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s

networks:
  iau-network:
    driver: bridge

volumes:
  iau-data:
    driver: local
  iau-templates:
    driver: local
```

5. **Deploy the stack**

---

### Method 3: SSH + Docker Compose (Advanced)

**Direct deployment on server via command line**

1. **SSH into your server:**
   ```bash
   ssh user@your-server-ip
   ```

2. **Clone the repository:**
   ```bash
   cd /opt
   git clone https://github.com/addoodi/iau-portal.git
   cd iau-portal
   ```

3. **Build and start containers:**
   ```bash
   docker-compose up -d --build
   ```

4. **Check status:**
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

5. **Manage via Portainer:**
   - The stack will appear automatically in Portainer
   - Navigate to **Stacks** to see `iau-portal`

---

## 🔧 Configuration

### Custom Ports

If ports 3000 or 8000 are already in use, edit the ports in docker-compose.yml:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Change 8001 to your preferred port
  frontend:
    ports:
      - "3001:80"    # Change 3001 to your preferred port
```

### Custom Backend URL

If your backend is on a different server or port:

1. **In Portainer Stack:**
   - Add environment variable to frontend service:
   ```yaml
   frontend:
     environment:
       - VITE_API_URL=http://192.168.1.100:8001
   ```

2. **Or via .env file** (if using Method 3):
   ```bash
   echo "VITE_API_URL=http://your-backend-url" > .env.production
   docker-compose up -d --build frontend
   ```

### Persistent Data Location

By default, CSV data is stored in Docker volumes. To use a specific directory:

```yaml
backend:
  volumes:
    - /opt/iau-portal-data:/app/backend/data  # Your custom path
```

---

## 📊 Managing via Portainer

### View Logs

1. **Portainer** → **Stacks** → **iau-portal**
2. Click on a container name (backend or frontend)
3. Click **"Logs"** tab
4. Enable **"Auto-refresh"** to see live logs

### Restart Services

1. **Portainer** → **Stacks** → **iau-portal**
2. Click **"Stop"** then **"Start"**
3. Or restart individual containers

### Update to Latest Code

**Method 1: Via Portainer (if using Git repository)**
1. **Stacks** → **iau-portal**
2. Click **"Pull and redeploy"**
3. Portainer will pull latest code and rebuild

**Method 2: Via SSH**
```bash
cd /opt/iau-portal
git pull origin main
docker-compose up -d --build
```

### View Container Stats

1. **Portainer** → **Containers**
2. Click on container name
3. View CPU, Memory, Network usage in real-time

### Access Container Shell

1. **Portainer** → **Containers** → **iau-portal-backend**
2. Click **"Console"**
3. Click **"Connect"**
4. You can now run commands inside the container:
   ```bash
   # Check Python version
   python --version

   # List data files
   ls -la /app/backend/data/

   # Check running processes
   ps aux
   ```

---

## 🔒 Security Best Practices

### 1. Use Reverse Proxy (Recommended)

Instead of exposing ports directly, use nginx or Traefik:

**Example with nginx on host:**

```nginx
# /etc/nginx/sites-available/iau-portal
server {
    listen 80;
    server_name portal.iau.edu.sa;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. Enable SSL/TLS

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d portal.iau.edu.sa
```

### 3. Restrict CORS (Production)

Edit `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://portal.iau.edu.sa",
        "https://portal.iau.edu.sa",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Change Default Ports

Don't expose on standard ports if accessible from internet:

```yaml
ports:
  - "8443:8000"  # Backend on 8443
  - "8080:80"    # Frontend on 8080
```

---

## 📈 Monitoring & Health Checks

### Health Check Endpoints

**Backend:** `http://your-server:8000/api/health`
```json
{"status": "healthy", "service": "iau-portal-api"}
```

**Frontend:** `http://your-server:3000/health`
```
healthy
```

### Portainer Notifications

1. **Portainer** → **Settings** → **Notifications**
2. Add webhook URL (Slack, Discord, email)
3. Get alerts when containers stop/restart

### Resource Limits (Recommended for production)

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          memory: 512M

  frontend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          memory: 256M
```

---

## 🧪 Testing After Deployment

1. **Check containers are running:**
   - Portainer → Containers
   - Both should show green "running" status

2. **Test Backend:**
   ```bash
   curl http://your-server:8000/api/health
   # Should return: {"status":"healthy","service":"iau-portal-api"}
   ```

3. **Test Frontend:**
   - Open browser: `http://your-server:3000`
   - Should see login page
   - Check browser console for errors

4. **Test End-to-End:**
   - Login with admin credentials
   - Create a leave request
   - Check if data persists after container restart

---

## 🐛 Troubleshooting

### Container won't start

**Check logs in Portainer:**
```
Stacks → iau-portal → backend → Logs
```

**Common issues:**

1. **Port already in use:**
   ```
   Error: bind: address already in use
   ```
   **Solution:** Change ports in docker-compose.yml

2. **Permission denied:**
   ```
   Error: permission denied while trying to connect to Docker daemon
   ```
   **Solution:** Add user to docker group:
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Build fails:**
   ```
   Error: failed to solve with frontend
   ```
   **Solution:** Check .dockerignore and ensure all files exist

### Frontend shows "Network Error"

1. **Check backend is running:**
   ```bash
   docker ps | grep backend
   ```

2. **Check backend URL in browser console:**
   - Open browser DevTools → Network tab
   - Look for failed API calls
   - Verify URL is correct

3. **Fix VITE_API_URL if needed:**
   ```bash
   # Redeploy frontend with correct URL
   docker-compose up -d --build frontend
   ```

### Data not persisting

1. **Check volume mount:**
   ```bash
   docker volume inspect iau-portal_iau-data
   ```

2. **Verify data location:**
   ```bash
   docker exec -it iau-portal-backend ls -la /app/backend/data/
   ```

3. **Backup data:**
   ```bash
   docker cp iau-portal-backend:/app/backend/data ./backup-data
   ```

---

## 📦 Backup & Restore

### Backup Data

**Method 1: Copy from container**
```bash
docker cp iau-portal-backend:/app/backend/data ./backup-$(date +%Y%m%d)
```

**Method 2: Volume backup**
```bash
docker run --rm \
  -v iau-portal_iau-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/iau-data-backup.tar.gz -C /data .
```

### Restore Data

```bash
docker run --rm \
  -v iau-portal_iau-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/iau-data-backup.tar.gz -C /data
```

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups/iau-portal"

mkdir -p $BACKUP_DIR

docker cp iau-portal-backend:/app/backend/data $BACKUP_DIR/data-$DATE

# Keep only last 7 backups
ls -t $BACKUP_DIR | tail -n +8 | xargs -I {} rm -rf $BACKUP_DIR/{}

echo "Backup completed: $BACKUP_DIR/data-$DATE"
```

Add to crontab for daily backups:
```bash
0 2 * * * /opt/scripts/backup.sh
```

---

## 🔄 CI/CD Integration (Optional)

### Auto-deploy on Git Push

**Using Portainer Webhooks:**

1. **Portainer** → **Stacks** → **iau-portal** → **Webhooks**
2. Copy webhook URL
3. **GitHub** → Your Repo → **Settings** → **Webhooks**
4. Add webhook URL
5. Select "Just the push event"

Now, every push to `main` triggers auto-deployment!

---

## 📝 Quick Command Reference

```bash
# Start stack
docker-compose up -d

# Stop stack
docker-compose down

# View logs
docker-compose logs -f

# Rebuild and restart
docker-compose up -d --build

# Check status
docker-compose ps

# Execute command in backend
docker exec -it iau-portal-backend bash

# Check backend health
curl http://localhost:8000/api/health

# View resource usage
docker stats

# Remove everything (including volumes)
docker-compose down -v
```

---

## 🎯 Recommended Production Setup

1. ✅ Use reverse proxy (nginx/Traefik)
2. ✅ Enable SSL/TLS with Let's Encrypt
3. ✅ Set up automated backups
4. ✅ Configure resource limits
5. ✅ Enable health check monitoring
6. ✅ Restrict CORS to your domain
7. ✅ Use named volumes for data persistence
8. ✅ Set up log rotation
9. ✅ Enable Portainer authentication
10. ✅ Regular security updates

---

## 📞 Support

For deployment issues:
- Check logs in Portainer
- Review this guide
- Create GitHub issue: https://github.com/addoodi/iau-portal/issues

---

**Last Updated:** 2025-12-28
**Docker Version:** 24.0+
**Portainer Version:** 2.19+
