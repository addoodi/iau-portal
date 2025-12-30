# Portainer Deployment Guide

## Problem: Images Not Rebuilding

When you click "Pull and Redeploy" in Portainer, it may reuse cached images instead of rebuilding with your latest code changes.

## Solution Options

### Option 1: Use CACHEBUST Environment Variable (Easiest)

1. In Portainer, go to your stack
2. Click "Edit"
3. Scroll to "Environment variables"
4. Change the `CACHEBUST` value to any new number:
   ```
   CACHEBUST=2    (was 1)
   CACHEBUST=3    (was 2)
   # Or use timestamp
   CACHEBUST=1704067200
   ```
5. Click "Update the stack"
6. Enable "Re-pull image and redeploy"
7. Click "Update"

**This forces Docker to rebuild both frontend and backend images!**

### Option 2: Use Versioned Image Tags

1. In Portainer environment variables, set:
   ```
   IMAGE_TAG=v1.0.1
   ```
2. Each time you update code, increment the version:
   ```
   IMAGE_TAG=v1.0.2
   IMAGE_TAG=v1.0.3
   ```
3. Update the stack with "Re-pull image and redeploy" enabled

### Option 3: Portainer Stack Webhook (Automated)

1. In your stack settings, enable "Webhooks"
2. Copy the webhook URL
3. Add to your CI/CD or call manually:
   ```bash
   curl -X POST https://portainer.example.com/api/webhooks/xxxxx
   ```

### Option 4: CLI Rebuild (For Development)

```bash
# SSH into your server
ssh user@server

# Navigate to the project
cd /path/to/iau-portal

# Force rebuild
docker-compose build --no-cache
docker-compose up -d
```

## Environment Variables Reference

### Required Variables
- `CACHEBUST` - Change this to force rebuild (default: 1)

### Optional Variables
- `IMAGE_TAG` - Version tag for images (default: latest)
- `FRONTEND_PORT` - External port for frontend (default: 3000)

## Quick Steps for Each Deployment

1. Make code changes
2. Commit to git (optional but recommended)
3. Open Portainer stack
4. Edit environment variables
5. Increment `CACHEBUST` (1 → 2 → 3...)
6. Enable "Re-pull and redeploy"
7. Update stack

## Troubleshooting

### Still seeing old code?
- Verify `CACHEBUST` value actually changed
- Check Portainer logs for build errors
- Try deleting the images manually first

### Build fails?
- Check build logs in Portainer
- Ensure all files are committed (if using git volume)
- Verify Dockerfile syntax

### Port conflicts?
- Change `FRONTEND_PORT` in environment variables
- Ensure no other service uses port 3000

## Best Practices

1. **Use git tags**: Match `IMAGE_TAG` to your git tags
   ```bash
   git tag v1.0.1
   # In Portainer: IMAGE_TAG=v1.0.1
   ```

2. **Document changes**: Add comment in Portainer when updating CACHEBUST

3. **Keep old images**: For rollback capability
   ```bash
   # Don't prune immediately
   docker image ls | grep iau-portal
   ```

4. **Use timestamps for CACHEBUST**:
   ```bash
   # Linux/Mac
   date +%s

   # Windows PowerShell
   Get-Date -UFormat %s
   ```

## Automated Deployment (Advanced)

Create a GitHub Action that triggers Portainer webhook on push:

```yaml
name: Deploy to Portainer
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Portainer Webhook
        run: |
          curl -X POST ${{ secrets.PORTAINER_WEBHOOK_URL }}
```
