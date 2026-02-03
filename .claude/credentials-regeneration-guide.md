# Credentials Regeneration Guide

**Created:** 2026-01-05
**Purpose:** Guide to regenerate exposed credentials for security hardening
**Status:** Action Required by User

---

## Overview

During the security review, we identified that some credentials were visible in the `.env` file. While the `.env` file was **never committed to Git** (verified by checking Git history), it's still best practice to regenerate these credentials to ensure maximum security.

---

## ✅ Good News: .env Not in Git History

We verified that:
- `.env` is properly in `.gitignore` (line 10)
- `.env` has never been committed to Git (verified with `git log --all --full-history -- .env`)
- No credential cleanup needed in Git history

---

## 🔐 Credentials That Should Be Regenerated

### 1. Mailtrap SMTP Credentials (HIGH PRIORITY)

**Current Values (EXPOSED in .env):**
```
SMTP_USERNAME=8b19e416e471ec
SMTP_PASSWORD=6b2fbb4e7b9fec
```

**Action Required:**
1. Log in to Mailtrap: https://mailtrap.io
2. Navigate to **Email Testing** → **Inboxes** → [Your Inbox]
3. Click on **SMTP Settings**
4. Click **Reset Credentials** or create a new inbox
5. Copy the new credentials
6. Update `.env` file with new values:
   ```bash
   SMTP_USERNAME=<new-username-from-mailtrap>
   SMTP_PASSWORD=<new-password-from-mailtrap>
   ```
7. Restart the backend: `docker-compose restart backend`

**Why:** Anyone with these credentials can send emails from your Mailtrap account.

---

### 2. PostgreSQL Database Password (MEDIUM PRIORITY)

**Current Value (in .env):**
```
POSTGRES_PASSWORD=iau_secure_password_2024
```

**Action Required:**

#### If using Docker (recommended):
```bash
# 1. Stop containers
docker-compose down

# 2. Generate new secure password
python -c "import secrets; print(secrets.token_urlsafe(24))"

# 3. Update .env file with new password
# Replace POSTGRES_PASSWORD value

# 4. Update DATABASE_URL with same password
# DATABASE_URL=postgresql://iau_admin:NEW_PASSWORD_HERE@postgres:5432/iau_portal

# 5. Remove old database volume (data will be recreated)
docker volume rm iau-portal_postgres_data

# 6. Start fresh with new password
docker-compose up -d
```

#### If database already has data:
```bash
# 1. Backup database first!
docker exec -t iau-portal-postgres pg_dump -U iau_admin iau_portal > backup.sql

# 2. Connect to PostgreSQL container
docker exec -it iau-portal-postgres psql -U iau_admin -d iau_portal

# 3. Change password
ALTER USER iau_admin WITH PASSWORD 'your_new_secure_password';
\q

# 4. Update .env with new password

# 5. Restart backend
docker-compose restart backend
```

**Why:** Exposed database password could allow unauthorized access to employee data.

---

### 3. JWT SECRET_KEY (COMPLETED ✅)

**Status:** Already fixed!
- Generated new secure key: `pbwLUrSzURc8wQe6hhha7PkO_aePiHM8v4gPIJJMies`
- Updated `backend/auth.py` to load from environment variable
- Added to `.env` file

**For production deployment:** Generate a different SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 📋 Verification Checklist

After regenerating credentials:

### Mailtrap
- [ ] Old credentials no longer work in Mailtrap dashboard
- [ ] New credentials copied to `.env`
- [ ] Backend restarted
- [ ] Test email sent successfully (try creating a leave request)

### PostgreSQL
- [ ] Database backup created (if data exists)
- [ ] New password set in PostgreSQL
- [ ] New password updated in `.env`
- [ ] Backend can connect to database
- [ ] Can login to IAU Portal

### JWT Secret
- [ ] New SECRET_KEY in `.env`
- [ ] Backend starts without errors
- [ ] Can login successfully
- [ ] Token validation works

---

## 🚨 Important Security Notes

1. **Never commit `.env` to Git**
   - It's already in `.gitignore` ✅
   - Always use `.env.example` as template

2. **Use different credentials for each environment**
   - Development: Current `.env` (after regeneration)
   - Staging: Separate credentials
   - Production: Completely different credentials

3. **Store production secrets securely**
   - Use environment variables in deployment platform
   - OR use secrets management (Azure Key Vault, AWS Secrets Manager, etc.)
   - Never store in code or commit to Git

4. **Rotate credentials periodically**
   - Database passwords: Every 90 days
   - JWT secrets: Every 6 months or after security incident
   - SMTP credentials: When leaving free tier or annually

---

## 🎯 Quick Reference: Credential Locations

| Credential | File | Line | Status |
|------------|------|------|--------|
| SECRET_KEY | `.env` | 51 | ✅ New secure key generated |
| POSTGRES_PASSWORD | `.env` | 39 | ⚠️ Needs regeneration |
| DATABASE_URL | `.env` | 44 | ⚠️ Update after password change |
| SMTP_USERNAME | `.env` | 23 | ⚠️ Needs regeneration |
| SMTP_PASSWORD | `.env` | 24 | ⚠️ Needs regeneration |
| ALLOWED_ORIGINS | `.env` | 59 | ✅ Set to localhost (secure for dev) |

---

## ✅ What's Already Done

1. **SECRET_KEY** - Generated new secure random key
2. **Git Security** - Verified .env never committed to Git
3. **.env.example** - Created template with placeholder values
4. **CORS Configuration** - Restricted to specific origins
5. **Code Security** - Updated auth.py to load from environment

---

## 🔜 Next Steps

1. **Regenerate Mailtrap credentials** (5 minutes)
2. **Regenerate database password** (10 minutes if Docker, 15 if manual)
3. **Test application** (5 minutes)
4. **Document credentials** in password manager (recommended)

**Total Time:** ~20-30 minutes

---

**Questions?** See `.claude/security-fixes-plan.md` for detailed implementation notes.
