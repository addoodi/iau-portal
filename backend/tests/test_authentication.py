"""
Critical Path Tests - Authentication Flow

Tests the most critical authentication functionality:
- Admin initialization (duplicate prevention)
- User login (success and failure)
- Token validation
- Protected endpoint access
- Audit logging for login events
"""

import pytest
from .conftest import ADMIN_EMAIL, ADMIN_PASSWORD


# ==========================================
# Test Cases - Admin Initialization
# ==========================================

def test_admin_initialization_duplicate(test_client, admin_setup):
    """Test that second admin initialization fails"""
    response = test_client.post(
        "/api/setup/initialize",
        json={
            "email": "admin2@test.com",
            "password": "Test123!@#",
            "first_name_ar": "مدير",
            "last_name_ar": "ثاني",
            "first_name_en": "Second",
            "last_name_en": "Admin",
        }
    )

    assert response.status_code == 400
    data = response.json()
    assert "error_code" in data["detail"]
    assert data["detail"]["error_code"] == "ALREADY_SETUP"


def test_setup_status_check(test_client, admin_setup):
    """Test setup status endpoint"""
    response = test_client.get("/api/setup/status")

    assert response.status_code == 200
    data = response.json()
    assert data["is_setup"] == True


# ==========================================
# Test Cases - User Login
# ==========================================

def test_login_success(test_client, admin_setup):
    """Test successful login with valid credentials"""
    response = test_client.post(
        "/api/token",
        data={
            "username": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user_role"] == "admin"
    assert len(data["access_token"]) > 0


def test_login_invalid_email(test_client, admin_setup):
    """Test login with non-existent email"""
    response = test_client.post(
        "/api/token",
        data={
            "username": "nonexistent@test.com",
            "password": "Test123!@#"
        }
    )

    assert response.status_code == 401
    data = response.json()
    assert "error_code" in data["detail"]
    assert data["detail"]["error_code"] == "INVALID_CREDENTIALS"


def test_login_invalid_password(test_client, admin_setup):
    """Test login with wrong password"""
    response = test_client.post(
        "/api/token",
        data={
            "username": ADMIN_EMAIL,
            "password": "WrongPassword123"
        }
    )

    assert response.status_code == 401
    data = response.json()
    assert "error_code" in data["detail"]
    assert data["detail"]["error_code"] == "INVALID_CREDENTIALS"


def test_login_empty_credentials(test_client):
    """Test login with empty credentials"""
    response = test_client.post(
        "/api/token",
        data={
            "username": "",
            "password": ""
        }
    )

    assert response.status_code in [401, 422]


# ==========================================
# Test Cases - Token Validation
# ==========================================

def test_protected_endpoint_with_valid_token(test_client, admin_token):
    """Test accessing protected endpoint with valid token"""
    response = test_client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == ADMIN_EMAIL


def test_protected_endpoint_without_token(test_client, admin_setup):
    """Test accessing protected endpoint without token"""
    response = test_client.get("/api/users/me")

    assert response.status_code == 401


def test_protected_endpoint_with_invalid_token(test_client, admin_setup):
    """Test accessing protected endpoint with invalid token"""
    response = test_client.get(
        "/api/users/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )

    assert response.status_code == 401


def test_protected_endpoint_with_malformed_token(test_client, admin_setup):
    """Test accessing protected endpoint with malformed authorization header"""
    response = test_client.get(
        "/api/users/me",
        headers={"Authorization": "InvalidFormat token"}
    )

    assert response.status_code == 401


# ==========================================
# Test Cases - Audit Logging
# ==========================================

def test_successful_login_creates_audit_log(test_client, admin_token):
    """Test that successful login creates audit log entry"""
    response = test_client.get(
        "/api/admin/audit-logs?action=user_login&limit=1",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["logs"]) >= 1
    assert data["logs"][0]["action"] == "user_login"


def test_failed_login_creates_audit_log(test_client, admin_token):
    """Test that failed login creates audit log entry"""
    # Trigger a failed login
    test_client.post(
        "/api/token",
        data={
            "username": "audit_fail_test@example.com",
            "password": "WrongPassword"
        }
    )

    # Check audit logs
    response = test_client.get(
        "/api/admin/audit-logs?action=user_login_failed&limit=1",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["logs"][0]["action"] == "user_login_failed"


# ==========================================
# Run Tests
# ==========================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
