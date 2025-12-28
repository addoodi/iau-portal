# 🐳 Docker Quick Start

Deploy IAU Portal with Docker in 3 minutes.

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

## 🚀 Quick Start

### 1. Clone Repository (if not already)

```bash
git clone https://github.com/addoodi/iau-portal.git
cd iau-portal
```

### 2. Start Application

```bash
docker-compose up -d
```

That's it! The application is now running:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000

### 3. View Logs

```bash
docker-compose logs -f
```

### 4. Stop Application

```bash
docker-compose down
```

---

## 📋 What's Included

- ✅ Backend (FastAPI) - Port 8000
- ✅ Frontend (React + Vite) - Port 3000
- ✅ Persistent CSV data storage
- ✅ Health checks
- ✅ Auto-restart on failure
- ✅ Optimized production builds

---

## 🔧 Configuration

### Change Ports

Edit `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Change 8001 to your preferred port
  frontend:
    ports:
      - "3001:80"    # Change 3001 to your preferred port
```

### Use Different Backend URL

Create `.env.production`:

```env
VITE_API_URL=http://192.168.1.100:8000
```

Then rebuild:

```bash
docker-compose up -d --build frontend
```

---

## 🎛️ Using Portainer

**Have Portainer installed?** See [PORTAINER-DEPLOY.md](./PORTAINER-DEPLOY.md) for:
- ✅ Deploy via Git repository
- ✅ One-click updates
- ✅ Visual management
- ✅ Log viewing
- ✅ Resource monitoring

---

## 📦 Common Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Rebuild after code changes
docker-compose up -d --build

# View status
docker-compose ps

# View logs
docker-compose logs -f backend   # Backend only
docker-compose logs -f frontend  # Frontend only

# Execute command in container
docker exec -it iau-portal-backend bash

# Backup data
docker cp iau-portal-backend:/app/backend/data ./backup

# Restore data
docker cp ./backup/. iau-portal-backend:/app/backend/data/
```

---

## 🐛 Troubleshooting

### Port already in use

```bash
# Find what's using the port
sudo lsof -i :3000
sudo lsof -i :8000

# Kill the process or change ports in docker-compose.yml
```

### Container won't start

```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

### Permission denied (Linux)

```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

---

## 📚 Full Documentation

- [Portainer Deployment](./PORTAINER-DEPLOY.md) - Complete Portainer guide
- [General Deployment](./DEPLOYMENT.md) - All deployment options

---

## 🎯 Production Deployment

For production use:

1. Use reverse proxy (nginx)
2. Enable SSL/TLS
3. Set resource limits
4. Configure monitoring
5. Set up automated backups

See [PORTAINER-DEPLOY.md](./PORTAINER-DEPLOY.md) for production setup.

---

**Need help?** Create an issue: https://github.com/addoodi/iau-portal/issues
