"""
Custom Exceptions for IAU Portal

Provides standardized error handling with specific error codes
for better frontend error handling and user experience.
"""

from fastapi import HTTPException, status
from typing import Optional, Dict, Any


class IAUPortalException(HTTPException):
    """
    Base exception for IAU Portal.

    All custom exceptions inherit from this class.
    """

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}

        super().__init__(
            status_code=status_code,
            detail={
                "error_code": error_code,
                "message": message,
                "details": details
            }
        )


# ==========================================
# Authentication & Authorization Exceptions
# ==========================================

class InvalidCredentialsError(IAUPortalException):
    """Invalid email or password"""

    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_CREDENTIALS",
            message=message
        )


class InactiveUserError(IAUPortalException):
    """User account is inactive"""

    def __init__(self, message: str = "User account is inactive"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="INACTIVE_USER",
            message=message
        )


class UnauthorizedError(IAUPortalException):
    """User not authorized for this action"""

    def __init__(self, message: str = "You are not authorized to perform this action"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="UNAUTHORIZED",
            message=message
        )


class InvalidTokenError(IAUPortalException):
    """JWT token is invalid or expired"""

    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_TOKEN",
            message=message
        )


# ==========================================
# Resource Not Found Exceptions
# ==========================================

class ResourceNotFoundError(IAUPortalException):
    """Generic resource not found"""

    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            message=f"{resource} not found",
            details={"resource": resource, "id": resource_id}
        )


class EmployeeNotFoundError(ResourceNotFoundError):
    """Employee not found"""

    def __init__(self, employee_id: str):
        super().__init__("Employee", employee_id)
        self.error_code = "EMPLOYEE_NOT_FOUND"


class LeaveRequestNotFoundError(ResourceNotFoundError):
    """Leave request not found"""

    def __init__(self, request_id: str):
        super().__init__("Leave request", request_id)
        self.error_code = "LEAVE_REQUEST_NOT_FOUND"


class UserNotFoundError(ResourceNotFoundError):
    """User not found"""

    def __init__(self, user_id: str):
        super().__init__("User", user_id)
        self.error_code = "USER_NOT_FOUND"


class UnitNotFoundError(ResourceNotFoundError):
    """Organizational unit not found"""

    def __init__(self, unit_id: str):
        super().__init__("Unit", unit_id)
        self.error_code = "UNIT_NOT_FOUND"


# ==========================================
# Validation Exceptions
# ==========================================

class ValidationError(IAUPortalException):
    """Generic validation error"""

    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            message=message,
            details=details
        )


class InsufficientBalanceError(IAUPortalException):
    """
    Employee vacation balance insufficient for request.

    Note: This is intentionally not enforced in the current implementation,
    but the exception exists for future use if business rules change.
    """

    def __init__(self, available: float, requested: float):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INSUFFICIENT_BALANCE",
            message="Insufficient vacation balance for this request",
            details={
                "available_balance": available,
                "requested_days": requested,
                "shortfall": requested - available
            }
        )


class InvalidDateRangeError(ValidationError):
    """Start date is after end date or other date range issues"""

    def __init__(self, message: str = "Invalid date range: start date must be before end date"):
        super().__init__(message, field="date_range")
        self.error_code = "INVALID_DATE_RANGE"


class DuplicateResourceError(IAUPortalException):
    """Resource already exists"""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="DUPLICATE_RESOURCE",
            message=f"{resource} already exists",
            details={"resource": resource, "identifier": identifier}
        )


class InvalidFileError(ValidationError):
    """File upload validation failed"""

    def __init__(self, message: str):
        super().__init__(message, field="file")
        self.error_code = "INVALID_FILE"


# ==========================================
# Business Logic Exceptions
# ==========================================

class PasswordMismatchError(IAUPortalException):
    """Current password does not match"""

    def __init__(self, message: str = "Current password is incorrect"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="PASSWORD_MISMATCH",
            message=message
        )


class WeakPasswordError(ValidationError):
    """Password does not meet security requirements"""

    def __init__(self, message: str = "Password does not meet security requirements"):
        super().__init__(message, field="password")
        self.error_code = "WEAK_PASSWORD"


class InvalidStatusTransitionError(IAUPortalException):
    """Cannot transition from current status to requested status"""

    def __init__(self, from_status: str, to_status: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_STATUS_TRANSITION",
            message=f"Cannot transition from '{from_status}' to '{to_status}'",
            details={"from_status": from_status, "to_status": to_status}
        )


class AlreadySetupError(IAUPortalException):
    """System has already been initialized"""

    def __init__(self, message: str = "Application is already set up"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="ALREADY_SETUP",
            message=message
        )


# ==========================================
# Helper Functions
# ==========================================

def raise_not_found(resource: str, resource_id: str):
    """
    Raise appropriate not found exception based on resource type.

    Args:
        resource: Type of resource (employee, user, leave_request, unit)
        resource_id: ID of the resource

    Raises:
        Specific ResourceNotFoundError subclass
    """
    resource_lower = resource.lower()

    if resource_lower == "employee":
        raise EmployeeNotFoundError(resource_id)
    elif resource_lower == "user":
        raise UserNotFoundError(resource_id)
    elif resource_lower in ["leave_request", "leaverequest", "request"]:
        raise LeaveRequestNotFoundError(resource_id)
    elif resource_lower == "unit":
        raise UnitNotFoundError(resource_id)
    else:
        raise ResourceNotFoundError(resource, resource_id)
