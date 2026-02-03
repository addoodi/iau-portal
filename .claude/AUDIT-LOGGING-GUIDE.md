# Audit Logging System - Developer & Admin Guide

**Version:** 0.3.0
**Last Updated:** 2026-01-05

---

## Overview

The IAU Portal includes a comprehensive audit logging system that tracks all critical user actions for security, compliance, and debugging purposes.

**What Gets Logged:**
- User login attempts (success and failure)
- Leave request creation
- Leave request approvals/rejections
- Employee creation/updates
- Document downloads
- Password changes
- And more...

**Why Audit Logging:**
- **Security:** Track unauthorized access attempts
- **Compliance:** HR requirements for leave approval records
- **Debugging:** Trace user actions leading to issues
- **Analytics:** Understand user behavior patterns
- **Accountability:** Know who did what and when

---

## For Administrators

### Viewing Audit Logs

**Endpoint:** `GET /api/admin/audit-logs`

**Requirements:** Admin role only

**Basic Query:**
```bash
curl -H "Authorization: Bearer <your-admin-token>" \
  http://localhost:8000/api/admin/audit-logs
```

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `limit` | int | Max logs to return (default: 100, max: 1000) | `?limit=50` |
| `offset` | int | Skip N logs (pagination) | `?offset=100` |
| `action` | string | Filter by action type | `?action=leave_request_approved` |
| `entity_type` | string | Filter by entity type | `?entity_type=leave_request` |
| `user_id` | UUID | Filter by user | `?user_id=<uuid>` |
| `start_date` | string | Filter after date (YYYY-MM-DD) | `?start_date=2026-01-01` |
| `end_date` | string | Filter before date (YYYY-MM-DD) | `?end_date=2026-01-31` |

**Example Queries:**

```bash
# Get last 50 login attempts
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/admin/audit-logs?action=user_login&limit=50"

# Get all failed logins today
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/admin/audit-logs?action=user_login_failed&start_date=2026-01-05"

# Get all leave approvals this month
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/admin/audit-logs?action=leave_request_approved&start_date=2026-01-01&end_date=2026-01-31"

# Get all actions by specific user
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/admin/audit-logs?user_id=<user-uuid>&limit=100"

# Pagination: Get logs 100-200
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/admin/audit-logs?offset=100&limit=100"
```

### Response Format

```json
{
  "total": 1523,
  "limit": 100,
  "offset": 0,
  "logs": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "timestamp": "2026-01-05T10:30:45.123456",
      "user_id": "12345678-1234-1234-1234-123456789012",
      "user_email": "manager@iau.edu.sa",
      "action": "leave_request_approved",
      "entity_type": "leave_request",
      "entity_id": "123",
      "details": {
        "employee_id": "IAU-001",
        "previous_status": "Pending",
        "new_status": "Approved",
        "vacation_type": "Annual",
        "duration": 5
      },
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0..."
    }
  ]
}
```

### Common Use Cases

#### 1. Security Investigation
**Scenario:** Suspicious activity reported

```bash
# Check failed login attempts
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/admin/audit-logs?action=user_login_failed&start_date=2026-01-04"

# Check all actions from suspicious IP
# (Query by IP requires database query - not exposed in API for security)
```

#### 2. Compliance Audit
**Scenario:** HR needs leave approval records

```bash
# Get all leave approvals for the year
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/admin/audit-logs?action=leave_request_approved&start_date=2026-01-01&end_date=2026-12-31&limit=1000"
```

#### 3. User Activity Report
**Scenario:** Need to see what a specific user has been doing

```bash
# Get all actions by user
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/admin/audit-logs?user_id=<uuid>&limit=500"
```

#### 4. Debugging
**Scenario:** User reports issue with leave request

```bash
# Find all actions related to specific leave request
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/admin/audit-logs?entity_type=leave_request&entity_id=123"
```

### Database Access (Direct)

For advanced queries, you can access the `audit_logs` table directly:

```sql
-- Most recent 100 logs
SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 100;

-- Failed logins by IP address
SELECT ip_address, COUNT(*) as attempts
FROM audit_logs
WHERE action = 'user_login_failed'
  AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY ip_address
ORDER BY attempts DESC;

-- Approvals by manager
SELECT user_email, COUNT(*) as approvals
FROM audit_logs
WHERE action = 'leave_request_approved'
  AND timestamp > NOW() - INTERVAL '30 days'
GROUP BY user_email
ORDER BY approvals DESC;

-- Activity timeline for specific employee
SELECT timestamp, action, user_email, details
FROM audit_logs
WHERE entity_type = 'employee'
  AND entity_id = 'IAU-001'
ORDER BY timestamp DESC;
```

---

## For Developers

### Adding Audit Logging to New Features

**Step 1: Import the audit module**

```python
from .audit import (
    log_audit,
    ACTION_*,  # Use predefined constants
    ENTITY_TYPE_*
)
from .database import get_db
from fastapi import Request
from sqlalchemy.orm import Session
```

**Step 2: Add Request and Session to endpoint**

```python
@app.post("/api/your-endpoint")
def your_endpoint(
    request: Request,  # Add this for IP/user-agent
    db: Session = Depends(get_db),  # Add this for database
    current_user: User = Depends(get_current_user)
):
    # Your code here
```

**Step 3: Call log_audit after action**

```python
# After successful action
log_audit(
    db=db,
    action="your_action_name",  # Use ACTION_* constants
    entity_type="your_entity_type",  # Use ENTITY_TYPE_* constants
    entity_id=str(entity.id),
    user=current_user,
    details={  # Optional additional context
        "key1": "value1",
        "key2": "value2"
    },
    request=request
)
```

### Example: Adding Audit Logging

```python
@app.post("/api/employees", status_code=status.HTTP_201_CREATED)
def create_employee(
    request: Request,
    employee_in: EmployeeCreate,
    employee_service: EmployeeService = Depends(get_employee_service),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Create employee
    created_employee = employee_service.create_employee(employee_in, current_user.id)

    # Audit log
    log_audit(
        db=db,
        action=ACTION_EMPLOYEE_CREATED,
        entity_type=ENTITY_TYPE_EMPLOYEE,
        entity_id=created_employee.id,
        user=current_user,
        details={
            "employee_name": f"{created_employee.first_name_en} {created_employee.last_name_en}",
            "unit_id": created_employee.unit_id,
            "position": created_employee.position_en
        },
        request=request
    )

    return created_employee
```

### Available Action Constants

**Authentication:**
- `ACTION_USER_LOGIN` - Successful login
- `ACTION_USER_LOGIN_FAILED` - Failed login attempt
- `ACTION_USER_CREATED` - New user account created
- `ACTION_PASSWORD_CHANGED` - Password changed

**Leave Requests:**
- `ACTION_LEAVE_REQUEST_CREATED` - New leave request
- `ACTION_LEAVE_REQUEST_APPROVED` - Request approved
- `ACTION_LEAVE_REQUEST_REJECTED` - Request rejected
- `ACTION_LEAVE_REQUEST_UPDATED` - Request modified
- `ACTION_LEAVE_REQUEST_DELETED` - Request deleted
- `ACTION_LEAVE_DOCUMENT_GENERATED` - Document created
- `ACTION_LEAVE_DOCUMENT_DOWNLOADED` - Document downloaded

**Employees:**
- `ACTION_EMPLOYEE_CREATED` - New employee added
- `ACTION_EMPLOYEE_UPDATED` - Employee info updated
- `ACTION_EMPLOYEE_DELETED` - Employee removed
- `ACTION_SIGNATURE_UPLOADED` - Signature uploaded

**Admin:**
- `ACTION_ADMIN_INIT` - Admin account initialized
- `ACTION_UNIT_CREATED` - Organizational unit created
- `ACTION_UNIT_UPDATED` - Unit updated
- `ACTION_UNIT_DELETED` - Unit deleted

**System:**
- `ACTION_SYSTEM_BACKUP` - System backup created
- `ACTION_SYSTEM_RESTORE` - System restored from backup
- `ACTION_CONTRACT_AUTO_RENEWED` - Contract automatically renewed

### Available Entity Type Constants

- `ENTITY_TYPE_LEAVE_REQUEST` - "leave_request"
- `ENTITY_TYPE_EMPLOYEE` - "employee"
- `ENTITY_TYPE_USER` - "user"
- `ENTITY_TYPE_UNIT` - "unit"
- `ENTITY_TYPE_SYSTEM` - "system"

### Adding Custom Actions

**In backend/audit.py:**

```python
# Add new action constant
ACTION_YOUR_NEW_ACTION = "your_new_action_name"

# Use lowercase with underscores
# Be descriptive but concise
# Examples:
ACTION_REPORT_GENERATED = "report_generated"
ACTION_SETTINGS_UPDATED = "settings_updated"
ACTION_NOTIFICATION_SENT = "notification_sent"
```

### Best Practices

1. **Always log critical actions:**
   - Authentication (login/logout)
   - Data creation/modification/deletion
   - Permission changes
   - Document access
   - Administrative actions

2. **Include useful details:**
   ```python
   details={
       "old_value": previous_state,
       "new_value": new_state,
       "reason": user_provided_reason,
       "affected_users": [user1, user2]
   }
   ```

3. **Don't log sensitive data:**
   - ❌ Passwords (even hashed)
   - ❌ Full credit card numbers
   - ❌ Social security numbers
   - ✅ IDs, names, statuses are OK
   - ✅ Metadata and context are OK

4. **Keep actions atomic:**
   - One action = one log entry
   - Don't combine multiple actions
   - Example: Separate "created" and "approved" into two logs

5. **Use consistent naming:**
   - All lowercase
   - Underscores not hyphens
   - Past tense: "created", "updated", "deleted"
   - Specific: "leave_request_approved" not "request_approved"

---

## Database Schema

### audit_logs Table

| Column | Type | Description | Indexed |
|--------|------|-------------|---------|
| `id` | UUID | Primary key | Yes (PK) |
| `timestamp` | DateTime | When action occurred | Yes |
| `user_id` | UUID | Who performed action (NULL for system) | No |
| `user_email` | String | User's email | No |
| `action` | String(100) | Action type | Yes |
| `entity_type` | String(50) | Entity affected | Yes |
| `entity_id` | String(100) | ID of entity | Yes |
| `details` | Text (JSON) | Additional context | No |
| `ip_address` | String(50) | Client IP | No |
| `user_agent` | Text | Browser info | No |

### Indexes

- Primary key on `id`
- Index on `timestamp` (for date range queries)
- Index on `action` (for filtering by action type)
- Index on `entity_type` (for filtering by entity)
- Index on `entity_id` (for finding all actions on specific entity)

### Storage Estimates

**Average log entry:** ~500 bytes
**Expected logs per day:** ~500-1000 (depends on activity)
**Monthly storage:** ~15-30 MB
**Yearly storage:** ~180-360 MB

**Retention Policy Recommendation:**
- Keep 1 year online (immediate access)
- Archive 1-7 years to cold storage (HR compliance)
- Delete after 7 years (unless legal hold)

---

## Monitoring & Alerts

### Recommended Alerts

**Security Alerts (High Priority):**
- More than 10 failed login attempts in 10 minutes
- Login from new IP address for admin accounts
- Unauthorized access attempts (403 errors)
- Audit log deletion attempts

**Operational Alerts (Medium Priority):**
- No audit logs written in last hour (system issue)
- Audit log table size > 80% of allocated space
- Slow audit log queries (> 5 seconds)

### Monitoring Queries

```sql
-- Failed login attempts in last hour
SELECT COUNT(*) FROM audit_logs
WHERE action = 'user_login_failed'
  AND timestamp > NOW() - INTERVAL '1 hour';

-- Most active users today
SELECT user_email, COUNT(*) as actions
FROM audit_logs
WHERE timestamp > CURRENT_DATE
GROUP BY user_email
ORDER BY actions DESC
LIMIT 10;

-- Audit log growth rate (MB per day)
SELECT
  DATE(timestamp) as date,
  COUNT(*) as entries,
  pg_size_pretty(SUM(LENGTH(details::text))::bigint) as size
FROM audit_logs
GROUP BY DATE(timestamp)
ORDER BY date DESC
LIMIT 30;
```

---

## Troubleshooting

### Issue: No audit logs appearing

**Check 1: Is audit logging enabled?**
```python
# In backend/main.py, verify log_audit() calls exist
```

**Check 2: Does audit_logs table exist?**
```sql
SELECT * FROM audit_logs LIMIT 1;
```

**Check 3: Are there database errors?**
```bash
# Check backend logs for errors
docker-compose logs backend | grep audit
```

### Issue: Can't access audit logs endpoint (403)

**Solution:** Ensure user has admin role
```sql
UPDATE users SET role = 'admin' WHERE email = 'your@email.com';
```

### Issue: Audit logs table too large

**Solution:** Archive old logs
```sql
-- Export logs older than 1 year
COPY (
  SELECT * FROM audit_logs
  WHERE timestamp < NOW() - INTERVAL '1 year'
) TO '/tmp/audit_logs_archive.csv' CSV HEADER;

-- Delete archived logs
DELETE FROM audit_logs
WHERE timestamp < NOW() - INTERVAL '1 year';

-- Vacuum to reclaim space
VACUUM FULL audit_logs;
```

---

## FAQ

**Q: How long are audit logs retained?**
A: By default, forever. Set up archival/deletion policy based on compliance requirements.

**Q: Can audit logs be modified?**
A: No write-once design. Only admins can view, logs cannot be modified or deleted through API.

**Q: What if audit logging fails?**
A: The action still succeeds - audit logging failure doesn't block operations (fail-open design).

**Q: Are audit logs encrypted?**
A: They're stored in the database, so they inherit database encryption (if enabled).

**Q: Can I export audit logs?**
A: Yes, use the API or direct database export to CSV/JSON.

---

**For More Information:**
- Implementation: `backend/audit.py`
- Database model: `backend/database.py` (AuditLogModel)
- API endpoint: `backend/main.py` (get_audit_logs)
- Security plan: `.claude/security-fixes-plan.md`

---

**END OF GUIDE**
