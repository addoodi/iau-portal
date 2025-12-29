# Portainer Deployment Guide - IAU Portal

## Prerequisites
- Docker installed on your server
- Portainer CE/BE installed
- GitHub repository access

## Deployment Steps

### 1. Prepare Environment Variables

In Portainer, when creating a stack, add these **environment variables** in the "Environment variables" section or in your docker-compose.yml:

```env
# Backend Host
HOST=0.0.0.0
FRONTEND_PORT=8098

# SMTP Email Configuration (Mailtrap for Testing)
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=587
SMTP_USERNAME=8b19e416e471ec
SMTP_PASSWORD=6b2fbb4e7b9fec
SMTP_SENDER_EMAIL=noreply@iau-portal.com
SMTP_ENABLED=true
```

⚠️ **For Production:** Replace Mailtrap credentials with your production SMTP server (Gmail, Office365, SendGrid, etc.)

### 2. Deploy Using Portainer Stack

#### Option A: Git Repository Method (Recommended)

1. **In Portainer:**
   - Go to **Stacks** → **Add Stack**
   - Select **"Repository"**
   - Enter your GitHub repository URL
   - Specify branch (e.g., `main`)
   - Set Compose path: `docker-compose.yml`

2. **Add Environment Variables:**
   - Scroll to "Environment variables"
   - Add each variable from above (one per line)
   - Format: `KEY=value`

3. **Deploy:**
   - Click **"Deploy the stack"**
   - Wait for containers to start

#### Option B: Web Editor Method

1. **In Portainer:**
   - Go to **Stacks** → **Add Stack**
   - Select **"Web editor"**
   - Paste your `docker-compose.yml` content

2. **Add Environment Variables** (same as Option A)

3. **Deploy the stack**

### 3. Docker Compose Configuration

Ensure your `docker-compose.yml` uses environment variables:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - HOST=${HOST:-0.0.0.0}
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USERNAME=${SMTP_USERNAME}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - SMTP_SENDER_EMAIL=${SMTP_SENDER_EMAIL}
      - SMTP_ENABLED=${SMTP_ENABLED:-false}
    volumes:
      - ./backend/data:/app/backend/data
      - ./backend/templates:/app/backend/templates
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
      args:
        - VITE_API_URL=${VITE_API_URL:-}
    ports:
      - "${FRONTEND_PORT:-8098}:80"
    depends_on:
      - backend
    restart: unless-stopped
```

### 4. Verify Deployment

After deployment:

1. **Check Container Logs:**
   - Click on the stack
   - View logs for `backend` and `frontend` containers
   - Look for "Application startup complete" message

2. **Test Backend:**
   - Visit: `http://your-server-ip:8000/docs`
   - Should see FastAPI Swagger documentation

3. **Test Frontend:**
   - Visit: `http://your-server-ip:8098`
   - Should see login page

4. **Test Email:**
   - Create a leave request in the application
   - Check Mailtrap inbox for notification email

### 5. Persistent Data Volumes

Make sure these directories are mapped as volumes in Portainer:

| Container Path | Host Path | Purpose |
|----------------|-----------|---------|
| `/app/backend/data` | `./backend/data` | CSV database files |
| `/app/backend/templates` | `./backend/templates` | Document templates |

This ensures data persists between container restarts.

### 6. Security Considerations

⚠️ **Production Checklist:**

- [ ] Change default admin password immediately after first login
- [ ] Use production SMTP server (not Mailtrap)
- [ ] Set up HTTPS/SSL (use Traefik or Nginx proxy)
- [ ] Restrict network access to necessary ports
- [ ] Regular backups of `backend/data` directory
- [ ] Keep environment variables secure (don't commit to Git)
- [ ] Use Docker secrets for sensitive data in production

### 7. Updating the Application

To update after pushing changes to GitHub:

1. **In Portainer:**
   - Go to **Stacks** → Select your stack
   - Click **"Pull and redeploy"** (if using Git repository)
   - Or click **"Stop"** then **"Start"** to rebuild

2. **Manual update:**
   ```bash
   docker-compose down
   docker-compose pull
   docker-compose up -d --build
   ```

### 8. Troubleshooting

#### Backend not starting:
```bash
# View backend logs
docker logs iau-portal-backend

# Check environment variables
docker exec iau-portal-backend env | grep SMTP
```

#### Email not sending:
```bash
# Check email.log
docker exec iau-portal-backend cat /app/backend/email.log

# Verify SMTP_ENABLED=true
docker exec iau-portal-backend env | grep SMTP_ENABLED
```

#### Frontend can't connect to backend:
- Check `VITE_API_URL` is set correctly
- Ensure backend is accessible from frontend container
- Verify CORS settings in backend

### 9. Backup Strategy

Create regular backups of the data directory:

```bash
# Backup script
tar -czf iau-portal-backup-$(date +%Y%m%d).tar.gz backend/data/

# Restore
tar -xzf iau-portal-backup-20250129.tar.gz
```

### 10. Production SMTP Setup

For production, replace Mailtrap with:

**Gmail:**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_ENABLED=true
```

**Office 365:**
```env
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your-email@company.com
SMTP_PASSWORD=your-password
SMTP_ENABLED=true
```

**SendGrid:**
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_ENABLED=true
```

---

## Quick Reference

| Service | Port | URL |
|---------|------|-----|
| Backend API | 8000 | http://server-ip:8000 |
| Frontend | 8098 | http://server-ip:8098 |
| API Docs | 8000 | http://server-ip:8000/docs |

## Support

- Check logs in Portainer for error messages
- Verify environment variables are set correctly
- Ensure all volumes are mounted properly
- Test SMTP connection: `python backend/test_email.py`

---

**Last Updated:** 2025-12-29
