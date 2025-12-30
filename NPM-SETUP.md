# Nginx Proxy Manager (NPM) Setup Guide

## Problem: "Insecure Site" Warning

When accessing your site via HTTPS through NPM, you see an "insecure" warning. This is caused by mixed content (HTTPS page trying to load HTTP resources).

## Solution: Proper NPM Configuration

### Step 1: NPM Proxy Host Settings

1. **Go to NPM Dashboard** → Proxy Hosts → Edit your IAU Portal proxy

2. **Details Tab:**
   ```
   Domain Names: portal.iau.edu.sa (or your domain)
   Scheme: http
   Forward Hostname/IP: 192.168.100.56
   Forward Port: 8098
   ✅ Cache Assets
   ✅ Block Common Exploits
   ✅ Websockets Support (if needed)
   ```

3. **SSL Tab:**
   ```
   SSL Certificate: [Select your certificate]
   ✅ Force SSL
   ✅ HTTP/2 Support
   ✅ HSTS Enabled
   ✅ HSTS Subdomains (optional)
   ```

4. **Advanced Tab:**
   Add this custom configuration:
   ```nginx
   # Forward original protocol to backend
   proxy_set_header X-Forwarded-Proto $scheme;
   proxy_set_header X-Forwarded-Host $host;
   proxy_set_header X-Forwarded-Port $server_port;
   proxy_set_header X-Real-IP $remote_addr;
   proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

   # Security headers
   add_header X-Frame-Options "SAMEORIGIN" always;
   add_header X-Content-Type-Options "nosniff" always;
   add_header X-XSS-Protection "1; mode=block" always;
   ```

5. Click **Save**

### Step 2: Verify SSL Certificate

Ensure your SSL certificate is:
- ✅ Valid and not expired
- ✅ Matches your domain name
- ✅ Issued by a trusted CA (Let's Encrypt, etc.)

For Let's Encrypt in NPM:
1. SSL Tab → Request a new SSL Certificate
2. Enter your domain: `portal.iau.edu.sa`
3. Enter your email
4. ✅ Use a DNS Challenge (if needed)
5. ✅ I Agree to Let's Encrypt Terms
6. Click **Save**

### Step 3: Rebuild Docker Stack

After updating nginx.conf:

1. In Portainer:
   - Go to your IAU Portal stack
   - Edit environment variables
   - Change `CACHEBUST=1` to `CACHEBUST=2`
   - Enable "Re-pull and redeploy"
   - Click "Update"

2. Or via CLI:
   ```bash
   docker-compose build --no-cache frontend
   docker-compose up -d
   ```

### Step 4: Clear Browser Cache

1. Hard refresh: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
2. Or clear browser cache completely
3. Try in incognito/private mode

## Troubleshooting

### Issue 1: Still seeing "Not Secure"

**Check browser console:**
- Press `F12` → Console tab
- Look for "Mixed Content" warnings
- Should see: `Blocked loading mixed active content "http://..."`

**Fix:**
- Verify NPM has "Force SSL" enabled
- Check that `X-Forwarded-Proto` is in NPM Advanced config
- Rebuild frontend with updated nginx.conf

### Issue 2: 502 Bad Gateway

**Causes:**
- Backend container not running
- Wrong IP/port in NPM
- Firewall blocking port 8098

**Fix:**
```bash
# Check backend is running
docker ps | grep iau-portal

# Check backend logs
docker logs iau-portal-backend

# Test direct access
curl http://192.168.100.56:8098
```

### Issue 3: SSL Certificate Errors

**Check certificate:**
```bash
# Via NPM
# Go to SSL Certificates → View certificate details

# Via browser
# Click padlock icon → Certificate → Verify domain matches
```

**Renew Let's Encrypt:**
- NPM automatically renews 30 days before expiry
- Check NPM logs for renewal status
- Manually renew: SSL Certificates → Click certificate → Force Renew

### Issue 4: Headers Not Working

**Verify headers are passed:**
```bash
# From server
curl -I https://portal.iau.edu.sa

# Should see:
# x-forwarded-proto: https
# strict-transport-security: max-age=31536000
```

**Debug NPM:**
```bash
# View NPM logs
docker logs nginx-proxy-manager

# Check for errors
docker exec -it nginx-proxy-manager nginx -t
```

## Architecture Overview

```
User Browser (HTTPS)
    ↓
Nginx Proxy Manager (NPM)
  - SSL Termination
  - Sets X-Forwarded-Proto: https
    ↓
Docker Container (HTTP) - Port 8098
  - Frontend Nginx
  - Proxies /api/ to backend
    ↓
Backend Container (HTTP) - Port 8000
  - FastAPI
  - Responds to API requests
```

## Security Checklist

- ✅ NPM has valid SSL certificate
- ✅ "Force SSL" enabled in NPM
- ✅ HSTS enabled
- ✅ X-Forwarded-Proto header configured
- ✅ Browser shows padlock icon (🔒)
- ✅ No mixed content warnings in console
- ✅ Security headers present (check with https://securityheaders.com)

## Production Best Practices

1. **Use Let's Encrypt Auto-Renewal**
   - NPM handles this automatically
   - Certificates renew every 90 days

2. **Enable HTTP/2**
   - Already enabled in NPM SSL tab
   - Improves performance

3. **Configure HSTS**
   - Already added in nginx.conf
   - Forces HTTPS for 1 year

4. **Monitor SSL Expiry**
   - NPM dashboard shows expiry dates
   - Set calendar reminder 2 weeks before expiry

5. **Regular Updates**
   - Keep NPM updated
   - Update Docker images regularly
   - Monitor security advisories

## Testing After Setup

1. **Visit your site:**
   ```
   https://portal.iau.edu.sa
   ```

2. **Check SSL:**
   - Should see 🔒 padlock icon
   - No warnings or errors

3. **Test API:**
   - Log in to portal
   - Create/view leave requests
   - Check browser console for errors

4. **Verify Headers:**
   ```bash
   curl -I https://portal.iau.edu.sa
   # Look for: strict-transport-security, x-frame-options, etc.
   ```

5. **SSL Report:**
   - Visit: https://www.ssllabs.com/ssltest/
   - Enter your domain
   - Should get A or A+ rating

## Common NPM Mistakes

❌ **Wrong:** Scheme = https in NPM
✅ **Correct:** Scheme = http (SSL terminates at NPM)

❌ **Wrong:** Forward Port = 80
✅ **Correct:** Forward Port = 8098 (your actual container port)

❌ **Wrong:** No X-Forwarded-Proto header
✅ **Correct:** Add in NPM Advanced config

❌ **Wrong:** Certificate doesn't match domain
✅ **Correct:** Certificate must match portal.iau.edu.sa exactly

## Need Help?

If issues persist:

1. **Check NPM logs:**
   ```bash
   docker logs -f nginx-proxy-manager
   ```

2. **Check frontend logs:**
   ```bash
   docker logs -f iau-portal-frontend
   ```

3. **Check backend logs:**
   ```bash
   docker logs -f iau-portal-backend
   ```

4. **Test without NPM:**
   ```bash
   # Access directly via IP:port
   http://192.168.100.56:8098
   ```

5. **Browser DevTools:**
   - F12 → Network tab
   - Check for failed requests
   - Look at response headers
