"""
Audit Logging Module

Provides functions to log critical user actions for security,
compliance, and debugging purposes.
"""

import json
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Request

from .database import AuditLogModel
from .models import User


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request headers.

    Checks for proxy headers (X-Forwarded-For, X-Real-IP) first,
    then falls back to direct client IP.

    Args:
        request: FastAPI Request object

    Returns:
        str: Client IP address
    """
    # Check for X-Forwarded-For header (from proxies/load balancers)
    if "X-Forwarded-For" in request.headers:
        # X-Forwarded-For can contain multiple IPs (client, proxy1, proxy2...)
        # The first IP is the original client
        return request.headers["X-Forwarded-For"].split(",")[0].strip()

    # Check for X-Real-IP header (from Nginx)
    if "X-Real-IP" in request.headers:
        return request.headers["X-Real-IP"]

    # Fallback to direct client IP
    if request.client:
        return request.client.host

    return "unknown"


def log_audit(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: str,
    user: Optional[User] = None,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
) -> None:
    """
    Log an audit entry to the database.

    Args:
        db: SQLAlchemy database session
        action: Action performed (e.g., "leave_request_created", "leave_request_approved")
        entity_type: Type of entity affected (e.g., "leave_request", "employee", "user")
        entity_id: ID of the affected entity
        user: User who performed the action (None for system actions)
        details: Additional context as dictionary (will be JSON serialized)
        request: FastAPI Request object (for extracting IP and user agent)

    Example:
        ```python
        log_audit(
            db=db,
            action="leave_request_approved",
            entity_type="leave_request",
            entity_id="123",
            user=current_user,
            details={
                "employee_id": "IAU-001",
                "previous_status": "Pending",
                "new_status": "Approved"
            },
            request=request
        )
        ```
    """
    # Extract request metadata
    ip_address = None
    user_agent = None
    if request:
        ip_address = get_client_ip(request)
        user_agent = request.headers.get("User-Agent")

    # Create audit log entry
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


# ==========================================
# Predefined Action Constants
# ==========================================
# Use these constants for consistency

# Leave Request Actions
ACTION_LEAVE_REQUEST_CREATED = "leave_request_created"
ACTION_LEAVE_REQUEST_APPROVED = "leave_request_approved"
ACTION_LEAVE_REQUEST_REJECTED = "leave_request_rejected"
ACTION_LEAVE_REQUEST_UPDATED = "leave_request_updated"
ACTION_LEAVE_REQUEST_DELETED = "leave_request_deleted"
ACTION_LEAVE_DOCUMENT_GENERATED = "leave_document_generated"
ACTION_LEAVE_DOCUMENT_DOWNLOADED = "leave_document_downloaded"

# Employee Actions
ACTION_EMPLOYEE_CREATED = "employee_created"
ACTION_EMPLOYEE_UPDATED = "employee_updated"
ACTION_EMPLOYEE_DELETED = "employee_deleted"
ACTION_SIGNATURE_UPLOADED = "signature_uploaded"

# User Actions
ACTION_USER_LOGIN = "user_login"
ACTION_USER_LOGIN_FAILED = "user_login_failed"
ACTION_USER_CREATED = "user_created"
ACTION_USER_UPDATED = "user_updated"
ACTION_USER_DELETED = "user_deleted"
ACTION_PASSWORD_CHANGED = "password_changed"

# Admin Actions
ACTION_ADMIN_INIT = "admin_initialized"
ACTION_UNIT_CREATED = "unit_created"
ACTION_UNIT_UPDATED = "unit_updated"
ACTION_UNIT_DELETED = "unit_deleted"

# System Actions
ACTION_SYSTEM_BACKUP = "system_backup"
ACTION_SYSTEM_RESTORE = "system_restore"
ACTION_CONTRACT_AUTO_RENEWED = "contract_auto_renewed"

# Entity Types
ENTITY_TYPE_LEAVE_REQUEST = "leave_request"
ENTITY_TYPE_EMPLOYEE = "employee"
ENTITY_TYPE_USER = "user"
ENTITY_TYPE_UNIT = "unit"
ENTITY_TYPE_SYSTEM = "system"
