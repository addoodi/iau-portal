# Security Deployment Checklist

**Version:** 0.3.0 (Security Hardened)
**Last Updated:** 2026-01-05
**Status:** Ready for Production Deployment

---

## Pre-Deployment Checklist

### 1. Environment Configuration

- [ ] **SECRET_KEY** - Generate new production key
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
  - Add to production environment variables (NOT in .env file)
  - Never use the development key in production

- [ ] **ALLOWED_ORIGINS** - Set to production domain(s)
  ```bash
  ALLOWED_ORIGINS=https://portal.iau.edu.sa,https://iau.edu.sa
  ```

- [ ] **ENVIRONMENT** - Set to production
  ```bash
  ENVIRONMENT=production
  ```

- [ ] **Database Credentials** - Use strong passwords
  - Generate: `python -c "import secrets; print(secrets.token_urlsafe(24))"`
  - Never use default passwords in production

- [ ] **SMTP Configuration** - University email server
  - Use production SMTP credentials
  - Test email sending before deployment

### 2. Database Setup

- [ ] Run audit logs migration
  ```bash
  python backend/migrations/add_audit_logs_table.py
  ```

- [ ] Verify all tables exist
  ```sql
  SELECT tablename FROM pg_tables WHERE schemaname = 'public';
  ```

- [ ] Set up automated backups (daily recommended)

### 3. Security Verification

- [ ] All secrets removed from code
  - No hardcoded passwords
  - No hardcoded API keys
  - No hardcoded SECRET_KEY

- [ ] CORS properly configured
  - Only university domains allowed
  - No wildcard origins in production

- [ ] File upload validation working
  - Test with .exe file (should be rejected)
  - Test with valid PDF (should be accepted)
  - Test with 15MB file (should be rejected)

- [ ] Authorization working
  - Employee can't access other employees' documents
  - Manager can access team documents
  - Admin can access all documents

- [ ] Audit logging enabled
  - Login attempts logged
  - Approvals/rejections logged
  - Admin can view audit logs

### 4. Testing

- [ ] Run full manual test suite
  - Authentication (login/logout)
  - Leave request creation
  - Leave request approval
  - Document generation
  - File uploads
  - Audit log viewing

- [ ] Load testing (optional but recommended)
  - 10 concurrent users
  - 100 requests/minute

- [ ] Security scanning (optional)
  - OWASP ZAP scan
  - SQLMap scan
  - Check for common vulnerabilities

### 5. Documentation

- [ ] Update deployment documentation
  - Environment variables required
  - Secrets management process
  - Backup/restore procedures

- [ ] Create admin user guide
  - How to view audit logs
  - How to manage users
  - How to troubleshoot common issues

- [ ] Document credential rotation schedule
  - Database password: Every 90 days
  - SECRET_KEY: Every 6 months
  - SMTP password: Annually

### 6. Monitoring

- [ ] Set up logging
  - Application logs
  - Error logs
  - Access logs

- [ ] Set up alerts (optional)
  - Failed login attempts > 10/minute
  - Server errors
  - Database connection failures

### 7. Backup & Recovery

- [ ] Database backup configured
  - Automated daily backups
  - Backup retention: 30 days minimum
  - Test restore procedure

- [ ] Document backup/restore process
- [ ] Store backups securely (encrypted)

---

## Deployment Steps

### Option 1: Docker Deployment (Recommended)

```bash
# 1. Build containers
docker-compose build

# 2. Start services
docker-compose up -d

# 3. Run migrations
docker-compose exec backend python backend/migrations/add_audit_logs_table.py

# 4. Verify health
curl http://localhost:8000/api/health
```

### Option 2: Manual Deployment

```bash
# 1. Install dependencies
pip install -r requirements.txt
npm install

# 2. Build frontend
npm run build

# 3. Run migrations
python backend/migrations/add_audit_logs_table.py

# 4. Start backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# 5. Serve frontend (nginx/apache)
```

---

## Post-Deployment Verification

### Immediate Checks (5 minutes)

- [ ] Backend health check responds
  ```bash
  curl https://portal.iau.edu.sa/api/health
  ```

- [ ] Frontend loads correctly
  - Open https://portal.iau.edu.sa
  - Check for errors in browser console

- [ ] Can login with admin account
  - Use admin credentials
  - Verify token is issued

- [ ] CORS working correctly
  - Frontend can make API requests
  - No CORS errors in console

### Functional Tests (15 minutes)

- [ ] Create leave request
  - As regular employee
  - Verify request appears in dashboard

- [ ] Approve leave request
  - As manager
  - Verify status updates
  - Check audit log entry created

- [ ] Download document
  - Verify authorization (employee can download own)
  - Verify authorization (employee can't download others')
  - Verify PDF generates correctly

- [ ] Upload attachment
  - Test with valid PDF
  - Test with invalid file type (should fail)

- [ ] View audit logs (admin only)
  ```bash
  curl -H "Authorization: Bearer <token>" \
    https://portal.iau.edu.sa/api/admin/audit-logs?limit=10
  ```

### Security Checks (10 minutes)

- [ ] Failed login is logged
  - Attempt login with wrong password
  - Check audit logs for failed attempt

- [ ] Unauthorized access blocked
  - Try to access admin endpoint as non-admin (should get 403)
  - Try to download other employee's document (should get 403)

- [ ] File upload validation working
  - Upload .exe file (should fail)
  - Upload 15MB file (should fail)
  - Upload valid PDF (should succeed)

---

## Rollback Plan

If deployment fails, follow these steps:

### 1. Immediate Rollback (Database)
```sql
-- If audit logs cause issues, you can drop the table
-- WARNING: This deletes all audit data!
DROP TABLE IF EXISTS audit_logs CASCADE;
```

### 2. Code Rollback
```bash
# Revert to previous version
git checkout v0.2.0

# Rebuild and redeploy
docker-compose down
docker-compose up -d --build
```

### 3. Environment Rollback
- Revert environment variables to previous values
- Clear Redis cache if applicable
- Restart services

---

## Common Issues & Solutions

### Issue: Backend won't start - "SECRET_KEY must be set"
**Solution:** Set SECRET_KEY environment variable in production

### Issue: CORS errors in browser console
**Solution:** Add frontend domain to ALLOWED_ORIGINS

### Issue: Can't view audit logs - "Admin access required"
**Solution:** Ensure logged-in user has role='admin'

### Issue: File upload fails - "File type not allowed"
**Solution:** Check file extension is in whitelist (pdf, doc, docx, jpg, png)

### Issue: Database migration fails - "Table already exists"
**Solution:** This is normal if migration already ran - skip it

---

## Security Incident Response

If a security incident occurs:

1. **Immediate Actions**
   - Take affected systems offline if necessary
   - Preserve audit logs
   - Document the incident

2. **Investigation**
   - Review audit logs: `GET /api/admin/audit-logs?start_date=YYYY-MM-DD`
   - Check for unusual patterns
   - Identify compromised accounts

3. **Remediation**
   - Reset compromised passwords
   - Revoke affected tokens
   - Regenerate SECRET_KEY
   - Review access logs

4. **Prevention**
   - Update security policies
   - Add additional monitoring
   - Conduct security training

---

## Credentials Rotation Schedule

| Credential | Rotation Frequency | Next Rotation | Priority |
|------------|-------------------|---------------|----------|
| Database Password | 90 days | YYYY-MM-DD | HIGH |
| SECRET_KEY | 6 months | YYYY-MM-DD | MEDIUM |
| SMTP Password | Annually | YYYY-MM-DD | LOW |
| User Passwords | On demand | N/A | HIGH |

---

## Compliance & Audit

### Required Logs to Retain

- [ ] Authentication logs (login/logout) - 1 year
- [ ] Leave approval logs - 7 years (HR requirement)
- [ ] Data access logs - 1 year
- [ ] Security incidents - Indefinitely

### Audit Reports to Generate

- Monthly: Failed login attempts by user
- Monthly: Leave approvals by manager
- Quarterly: User access patterns
- Annually: Security compliance report

---

## Support Contacts

**Technical Issues:**
- Developer: [Contact Info]
- University IT: [Contact Info]

**Security Issues:**
- Security Team: [Contact Info]
- Emergency: [Contact Info]

**Documentation:**
- Security Plan: `.claude/security-fixes-plan.md`
- Summary: `.claude/security-fixes-summary.md`
- Credentials Guide: `.claude/credentials-regeneration-guide.md`
- Main Guide: `CLAUDE.md`

---

**Deployment Status:** [ ] NOT READY | [ ] STAGING | [ ] PRODUCTION

**Deployed By:** _______________
**Deployment Date:** _______________
**Verified By:** _______________

---

**END OF CHECKLIST**
