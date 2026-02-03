# IAU Portal - Critical Security Fixes Plan

**Created:** 2026-01-04
**Status:** In Progress
**Estimated Total Time:** 3-4 hours
**Priority:** URGENT - Must complete before any production deployment

---

## Overview

This plan addresses 7 critical security vulnerabilities identified in the comprehensive code review. These issues represent severe security risks that could lead to:
- Authentication bypass
- Cross-site request forgery (CSRF)
- Database credential theft
- Malware uploads
- Unauthorized data access
- Email account compromise

**Note:** Item #6 (Balance Check) is intentionally excluded - over-balance requests are a requested feature, not a bug.

---

## Critical Security Issues to Fix

### ✅ Issue #1: Hardcoded JWT Secret Key
**Risk Level:** CRITICAL
**Location:** `backend/auth.py:13`
**Estimated Time:** 10 minutes

**Current Code:**
```python
SECRET_KEY = "a_very_secret_key_that_should_be_in_a_config_file"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

**Vulnerability:**
- Anyone with access to source code can forge JWT tokens
- Complete authentication bypass possible
- All user sessions can be hijacked

**Fix Steps:**
1. Add `SECRET_KEY` to `.env` file with strong random value
2. Update `backend/auth.py` to read from environment variable
3. Add fallback warning for development mode
4. Generate new secret key using cryptographically secure method
5. Test JWT token generation/validation still works

**Implementation:**
```python
# backend/auth.py
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if os.getenv("ENVIRONMENT") == "production":
        raise ValueError("SECRET_KEY must be set in production!")
    else:
        print("⚠️  WARNING: Using default SECRET_KEY for development only!")
        SECRET_KEY = "dev-only-insecure-key-change-in-production"

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
```

**Verification:**
- [ ] Can login with valid credentials
- [ ] Invalid tokens are rejected
- [ ] Backend starts successfully
- [ ] No hardcoded secrets remain in code

---

### ✅ Issue #2: CORS Allows All Origins
**Risk Level:** CRITICAL
**Location:** `backend/main.py:33-41`
**Estimated Time:** 15 minutes

**Current Code:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ DANGEROUS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Vulnerability:**
- Any website can make requests to the API
- Cross-Site Request Forgery (CSRF) attacks possible
- Malicious sites can steal user data

**Fix Steps:**
1. Add `ALLOWED_ORIGINS` to `.env` file
2. Update CORS middleware to read from environment
3. Use comma-separated list for multiple origins
4. Restrict methods to only those needed (GET, POST, PUT, DELETE)
5. Restrict headers to Content-Type and Authorization

**Implementation:**
```python
# backend/main.py
import os

# Get allowed origins from environment
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173"  # Dev defaults
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
```

**.env addition:**
```bash
# Development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000

# Production (university will set this)
# ALLOWED_ORIGINS=https://portal.iau.edu.sa
```

**Verification:**
- [ ] Frontend can still make API calls
- [ ] Unauthorized origins are blocked
- [ ] Preflight OPTIONS requests work
- [ ] Credentials (cookies/auth headers) still work

---

### ✅ Issue #3: Database Credentials Exposed in Git
**Risk Level:** CRITICAL
**Location:** `.env` file in repository
**Estimated Time:** 30 minutes

**Current Exposure:**
```bash
# These credentials are visible in Git history!
DATABASE_URL=postgresql://iau_admin:iau_secure_password_2024@localhost:5432/iau_portal
```

**Vulnerability:**
- Anyone with repository access has database credentials
- Even if removed now, credentials exist in Git history
- Database can be accessed/modified by unauthorized parties

**Fix Steps:**
1. ✅ Verify `.env` is in `.gitignore` (already done)
2. Remove `.env` from Git history using git filter-repo
3. Change database password immediately
4. Update `.env` with new credentials
5. Create `.env.example` template (without actual secrets)
6. Document secrets management in README
7. Add reminder in deployment docs

**Implementation:**
```bash
# Step 1: Remove .env from Git history
# WARNING: This rewrites Git history - coordinate with team if needed
git filter-repo --path .env --invert-paths --force

# Step 2: Change PostgreSQL password
# Connect to PostgreSQL and run:
# ALTER USER iau_admin WITH PASSWORD 'new_secure_password_here';

# Step 3: Update .env with new password

# Step 4: Create .env.example template
```

**.env.example (safe to commit):**
```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database

# JWT Configuration
SECRET_KEY=your-secret-key-here-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration (Mailtrap for testing)
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USERNAME=your-mailtrap-username
SMTP_PASSWORD=your-mailtrap-password
SMTP_FROM_EMAIL=noreply@iau.edu.sa
SMTP_FROM_NAME=IAU Portal

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Environment
ENVIRONMENT=development
```

**Verification:**
- [ ] `.env` not in Git history (`git log --all --full-history -- .env` shows nothing)
- [ ] `.env.example` exists and is committed
- [ ] Database connection still works with new password
- [ ] `.gitignore` includes `.env`

**IMPORTANT NOTE:**
Since `.env` may already be committed, we need to be careful. I'll check Git status first and provide options.

---

### ✅ Issue #4: No File Upload Validation
**Risk Level:** HIGH
**Location:** `backend/services.py` (save_attachment function)
**Estimated Time:** 45 minutes

**Current Code:**
```python
def save_attachment(self, leave_request_id: str, file_content: bytes, filename: str) -> str:
    # No validation - any file type/size accepted! ⚠️
    file_path = self.attachment_dir / f"{leave_request_id}_{filename}"
    with open(file_path, "wb") as f:
        f.write(file_content)
    return str(file_path)
```

**Vulnerability:**
- Users can upload malware, executables, scripts
- No size limits - can fill disk space
- File extension spoofing possible

**Fix Steps:**
1. Define allowed file extensions whitelist
2. Define maximum file size (10MB recommended)
3. Validate file extension
4. Validate actual file content (MIME type)
5. Sanitize filename (remove path traversal attempts)
6. Add comprehensive error messages

**Implementation:**
```python
# backend/config.py (new file for constants)
from pathlib import Path

# File upload security settings
ALLOWED_ATTACHMENT_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif'
}
MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024  # 10MB in bytes

ALLOWED_SIGNATURE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_SIGNATURE_SIZE = 500 * 1024  # 500KB

# backend/services.py
import magic  # python-magic for MIME type detection
from pathlib import Path
from backend.config import (
    ALLOWED_ATTACHMENT_EXTENSIONS,
    MAX_ATTACHMENT_SIZE,
    ALLOWED_SIGNATURE_EXTENSIONS,
    MAX_SIGNATURE_SIZE
)

def validate_attachment(file_content: bytes, filename: str) -> tuple[bool, str]:
    """
    Validate file upload for security.
    Returns (is_valid, error_message)
    """
    # Check file size
    if len(file_content) > MAX_ATTACHMENT_SIZE:
        max_mb = MAX_ATTACHMENT_SIZE / (1024 * 1024)
        return False, f"File exceeds maximum size of {max_mb}MB"

    # Extract and validate extension
    ext = Path(filename).suffix.lower().lstrip('.')
    if not ext:
        return False, "File has no extension"

    if ext not in ALLOWED_ATTACHMENT_EXTENSIONS:
        allowed = ', '.join(ALLOWED_ATTACHMENT_EXTENSIONS)
        return False, f"File type '.{ext}' not allowed. Allowed: {allowed}"

    # Validate MIME type matches extension
    try:
        mime = magic.from_buffer(file_content, mime=True)

        # Map extensions to expected MIME types
        mime_map = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif'
        }

        expected_mime = mime_map.get(ext)
        if expected_mime and mime != expected_mime:
            return False, f"File content doesn't match extension .{ext}"
    except Exception as e:
        return False, f"Could not validate file type: {str(e)}"

    return True, ""

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.
    """
    # Get just the filename, no path components
    safe_name = Path(filename).name

    # Remove any remaining dangerous characters
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in "._- ")

    # Ensure it's not empty
    if not safe_name:
        safe_name = "attachment"

    return safe_name

def save_attachment(self, leave_request_id: str, file_content: bytes, filename: str) -> str:
    """
    Save attachment with security validation.
    """
    # Validate file
    is_valid, error_msg = validate_attachment(file_content, filename)
    if not is_valid:
        raise ValueError(error_msg)

    # Sanitize filename
    safe_filename = sanitize_filename(filename)

    # Create unique filename to prevent overwrites
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = self.attachment_dir / f"{leave_request_id}_{timestamp}_{safe_filename}"

    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)

    return str(file_path)
```

**Dependencies to Add:**
```bash
pip install python-magic-bin  # For Windows
# OR
pip install python-magic  # For Linux/Mac
```

Add to `requirements.txt`:
```
python-magic-bin==0.4.14; sys_platform == 'win32'
python-magic==0.4.27; sys_platform != 'win32'
```

**Verification:**
- [ ] Can upload valid PDF file
- [ ] Can upload valid image (JPG, PNG)
- [ ] Cannot upload .exe file
- [ ] Cannot upload file >10MB
- [ ] Error messages are clear
- [ ] Filename with path traversal (../../etc/passwd) is sanitized

---

### ✅ Issue #5: Missing Authorization on Document Download
**Risk Level:** HIGH
**Location:** `backend/main.py` (document download endpoint)
**Estimated Time:** 20 minutes

**Current Issue:**
```python
# TODO: Add authorization check: is this user allowed to download this form?
```

**Vulnerability:**
- Any authenticated user can download any other employee's vacation documents
- Privacy violation - sensitive personal data exposed

**Fix Steps:**
1. Find document download endpoint
2. Get leave request associated with document
3. Check if current user is:
   - The employee who requested it, OR
   - The manager of that employee, OR
   - An admin/dean, OR
   - In the approval chain
4. Return 403 Forbidden if not authorized

**Implementation:**
```python
# backend/main.py

@app.get("/api/documents/{leave_request_id}/download")
async def download_leave_document(
    leave_request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download vacation document with authorization check.
    """
    # Get leave request
    leave_request = db.query(LeaveRequestModel).filter(
        LeaveRequestModel.id == leave_request_id
    ).first()

    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")

    # Get employee associated with request
    employee = db.query(EmployeeModel).filter(
        EmployeeModel.id == leave_request.employee_id
    ).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Authorization check
    is_authorized = False

    # 1. Is this the employee's own request?
    if employee.user_id == current_user.id:
        is_authorized = True

    # 2. Is user an admin or dean?
    elif current_user.role in ['admin', 'dean']:
        is_authorized = True

    # 3. Is user the direct manager?
    elif employee.manager_id:
        manager_employee = db.query(EmployeeModel).filter(
            EmployeeModel.user_id == current_user.id
        ).first()
        if manager_employee and manager_employee.id == employee.manager_id:
            is_authorized = True

    # 4. Is user in the approval chain? (check approvals table)
    if not is_authorized:
        approval = db.query(ApprovalModel).filter(
            ApprovalModel.leave_request_id == leave_request_id,
            ApprovalModel.user_id == current_user.id
        ).first()
        if approval:
            is_authorized = True

    if not is_authorized:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to download this document"
        )

    # Generate and return document
    # ... existing document generation code ...
```

**Verification:**
- [ ] Employee can download their own documents
- [ ] Manager can download their team's documents
- [ ] Admin can download all documents
- [ ] Regular employee CANNOT download other employees' documents
- [ ] 403 error returned with clear message

---

### ✅ Issue #6: Balance Check Bypassed
**Status:** ⚠️ INTENTIONAL FEATURE - NOT A BUG
**Location:** `backend/services.py:140`
**Action:** SKIP - Document as intentional

**Note from User:**
> "Don't reject over-balance requests, it's a feature I requested"

**What to Do:**
1. Remove the TODO comment
2. Add documentation explaining this is intentional
3. Optionally: Add a warning flag in UI when request exceeds balance

**Implementation:**
```python
# backend/services.py

def create_leave_request(self, data: LeaveRequestCreate, user_id: UUID) -> LeaveRequest:
    """
    Create new leave request.

    Note: This intentionally allows requests that exceed available balance.
    The university requires flexibility for special cases (emergency leave,
    carried over days from previous years, etc.). Balance is informational
    only and does not block request creation.
    """
    # ... existing code without balance validation ...
```

**Frontend Enhancement (Optional):**
```javascript
// src/components/RequestModal.jsx
// Show warning if balance exceeded but still allow submission

{requestDays > availableBalance && (
  <div className="bg-yellow-50 border border-yellow-200 rounded p-3 text-sm">
    ⚠️ {lang === 'ar'
      ? 'تحذير: هذا الطلب يتجاوز الرصيد المتاح'
      : 'Warning: This request exceeds your available balance'}
  </div>
)}
```

---

### ✅ Issue #7: Mailtrap Credentials Exposed
**Risk Level:** HIGH
**Location:** `.env` file
**Estimated Time:** 10 minutes

**Current Exposure:**
```bash
SMTP_USERNAME=8b19e416e471ec
SMTP_PASSWORD=6b2fbb4e7b9fec
```

**Vulnerability:**
- Anyone with repository access can use these credentials
- Can send emails from the Mailtrap account
- Could exhaust email quota or send spam

**Fix Steps:**
1. Login to Mailtrap (sandbox.smtp.mailtrap.io)
2. Regenerate/reset SMTP credentials
3. Update `.env` with new credentials
4. Ensure `.env` is not in Git (handled in Issue #3)
5. Document in `.env.example` without actual values

**Implementation:**
```bash
# 1. Go to https://mailtrap.io
# 2. Navigate to Email Testing > Inboxes > [Your Inbox]
# 3. Click "SMTP Settings"
# 4. Click "Reset Credentials" or create new inbox
# 5. Copy new credentials to .env

# .env (new credentials - keep secret!)
SMTP_USERNAME=<new-username-from-mailtrap>
SMTP_PASSWORD=<new-password-from-mailtrap>
```

**Verification:**
- [ ] Old credentials no longer work
- [ ] New credentials successfully send test email
- [ ] Credentials not in Git history (covered by Issue #3)

---

### ✅ Issue #8: No Audit Logging
**Risk Level:** MEDIUM (but important for compliance)
**Location:** Throughout codebase
**Estimated Time:** 2-3 hours

**Current Issue:**
- No record of who approved/rejected leave requests
- Cannot track malicious actions
- Difficult to debug user-reported issues
- Compliance requirement for HR systems

**Fix Steps:**
1. Create `AuditLog` database model
2. Create migration to add `audit_logs` table
3. Implement `log_audit()` helper function
4. Add audit logging to critical operations:
   - Leave request creation
   - Leave request approval/rejection
   - Employee creation/modification
   - User login attempts (success/failure)
   - Password changes
   - Document generation
5. Create admin endpoint to view audit logs

**Implementation:**

**Step 1: Database Model**
```python
# backend/models.py

class AuditLog(BaseModel):
    """Audit log entry for tracking critical actions."""
    id: UUID
    timestamp: datetime
    user_id: Optional[UUID]  # None for system actions
    user_email: Optional[str]
    action: str  # e.g., "leave_request_approved", "employee_created"
    entity_type: str  # e.g., "leave_request", "employee"
    entity_id: str
    details: Optional[str]  # JSON string with additional details
    ip_address: Optional[str]
    user_agent: Optional[str]

# backend/database.py (SQLAlchemy model)

class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    user_email = Column(String, nullable=True)
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(100), nullable=False, index=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
```

**Step 2: Migration Script**
```python
# migrations/add_audit_logs.py

from backend.database import engine, Base
from backend.database import AuditLogModel

def upgrade():
    """Create audit_logs table."""
    AuditLogModel.__table__.create(engine, checkfirst=True)
    print("✅ Created audit_logs table")

if __name__ == "__main__":
    upgrade()
```

**Step 3: Audit Logging Service**
```python
# backend/audit.py

import json
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from backend.database import AuditLogModel
from backend.models import User

def log_audit(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: str,
    user: Optional[User] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> None:
    """
    Log an audit entry.

    Args:
        action: What happened (e.g., "leave_request_approved")
        entity_type: Type of entity (e.g., "leave_request")
        entity_id: ID of the entity
        user: User who performed the action (None for system actions)
        details: Additional context as dictionary
        ip_address: Client IP address
        user_agent: Client user agent
    """
    audit_log = AuditLogModel(
        timestamp=datetime.utcnow(),
        user_id=user.id if user else None,
        user_email=user.email if user else None,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        details=json.dumps(details) if details else None,
        ip_address=ip_address,
        user_agent=user_agent
    )

    db.add(audit_log)
    db.commit()

# Helper to get client IP from request
def get_client_ip(request) -> str:
    """Extract client IP from request headers."""
    if "X-Forwarded-For" in request.headers:
        return request.headers["X-Forwarded-For"].split(",")[0].strip()
    elif "X-Real-IP" in request.headers:
        return request.headers["X-Real-IP"]
    else:
        return request.client.host if request.client else "unknown"
```

**Step 4: Add to Critical Operations**
```python
# backend/services.py

from backend.audit import log_audit

class LeaveRequestService:
    def create_leave_request(
        self,
        data: LeaveRequestCreate,
        user_id: UUID,
        db: Session,
        request  # FastAPI Request object for IP/user-agent
    ) -> LeaveRequest:
        # ... existing creation code ...

        # Audit log
        log_audit(
            db=db,
            action="leave_request_created",
            entity_type="leave_request",
            entity_id=str(new_request.id),
            user=current_user,
            details={
                "employee_id": employee.id,
                "leave_type": data.leave_type,
                "start_date": str(data.start_date),
                "end_date": str(data.end_date),
                "duration_days": duration
            },
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("User-Agent")
        )

        return new_request

    def approve_leave_request(
        self,
        request_id: str,
        user_id: UUID,
        db: Session,
        request
    ):
        # ... existing approval code ...

        # Audit log
        log_audit(
            db=db,
            action="leave_request_approved",
            entity_type="leave_request",
            entity_id=request_id,
            user=current_user,
            details={
                "employee_id": leave_request.employee_id,
                "approver_role": current_user.role,
                "previous_status": old_status
            },
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("User-Agent")
        )
```

**Step 5: Admin Audit Viewer Endpoint**
```python
# backend/main.py

@app.get("/api/admin/audit-logs")
async def get_audit_logs(
    limit: int = 100,
    offset: int = 0,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit logs (admin only).
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    query = db.query(AuditLogModel)

    if action:
        query = query.filter(AuditLogModel.action == action)
    if entity_type:
        query = query.filter(AuditLogModel.entity_type == entity_type)

    total = query.count()
    logs = query.order_by(
        AuditLogModel.timestamp.desc()
    ).offset(offset).limit(limit).all()

    return {
        "total": total,
        "logs": [
            {
                "id": str(log.id),
                "timestamp": log.timestamp.isoformat(),
                "user_email": log.user_email,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "details": json.loads(log.details) if log.details else None,
                "ip_address": log.ip_address
            }
            for log in logs
        ]
    }
```

**Verification:**
- [ ] Audit logs table created
- [ ] Creating leave request logs audit entry
- [ ] Approving leave request logs audit entry
- [ ] Admin can view audit logs via API
- [ ] Non-admin cannot view audit logs (403)
- [ ] IP address and user agent captured
- [ ] Details field contains useful context

---

## Implementation Order

**Recommended sequence to minimize risk:**

1. **Issue #7: Mailtrap Credentials** (10 min) - Quick win, immediate risk
2. **Issue #3: Git History Cleanup** (30 min) - Prevent further exposure
3. **Issue #1: JWT Secret Key** (10 min) - Critical auth fix
4. **Issue #2: CORS Configuration** (15 min) - Critical security
5. **Issue #5: Document Authorization** (20 min) - Privacy fix
6. **Issue #4: File Upload Validation** (45 min) - Complex but important
7. **Issue #6: Balance Check Documentation** (5 min) - Just documentation
8. **Issue #8: Audit Logging** (2-3 hrs) - Important but can be staged

**Total Time:** 3-4 hours for issues #1-7, +2-3 hours for audit logging

---

## Testing Checklist

After each fix, verify:

- [ ] Backend starts without errors
- [ ] Frontend can connect to backend
- [ ] Can login successfully
- [ ] Can create leave request
- [ ] Can approve leave request
- [ ] Can download documents (authorized)
- [ ] Cannot download documents (unauthorized - should get 403)
- [ ] Cannot upload invalid files (should get error)
- [ ] CORS blocks unauthorized origins
- [ ] No secrets in Git history
- [ ] All tests pass (once implemented)

---

## Deployment Notes

**Before deploying to production:**

1. Generate strong SECRET_KEY:
   ```python
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. Set production environment variables:
   ```bash
   SECRET_KEY=<generated-key>
   ALLOWED_ORIGINS=https://portal.iau.edu.sa
   ENVIRONMENT=production
   DATABASE_URL=<production-database>
   ```

3. Ensure `.env` is NEVER deployed to server
   - Use environment variables set in hosting platform
   - Or use secrets management (AWS Secrets Manager, Azure Key Vault, etc.)

4. Verify HTTPS is enabled (all HTTP redirects to HTTPS)

5. Test all critical paths in staging environment

---

## Success Criteria

✅ **This plan is complete when:**

- [ ] No secrets hardcoded in source code
- [ ] No secrets in Git history
- [ ] CORS restricted to known origins
- [ ] File uploads validated for type and size
- [ ] Document downloads require authorization
- [ ] All actions logged to audit trail
- [ ] All tests pass
- [ ] Code review completed
- [ ] Deployment documentation updated

---

## Next Steps After Security Fixes

Once critical security is addressed, the next priorities from the code review are:

1. **Rate limiting on login** (prevent brute force)
2. **HTTPS configuration** (encrypt data in transit)
3. **Comprehensive error handling** (better user experience)
4. **Test coverage for critical paths** (prevent regressions)

See main code review document for full list.

---

**END OF PLAN**
