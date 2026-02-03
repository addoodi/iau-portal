"""
Critical Path Tests - Authentication Flow

Tests the most critical authentication functionality:
- Admin initialization
- User login (success and failure)
- Token validation
- Protected endpoint access
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal, Base, engine
from backend.models import User
import os

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000"

client = TestClient(app)


# ==========================================
# Fixtures
# ==========================================

@pytest.fixture(scope="module")
def test_db():
    """Create test database tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def admin_user(test_db):
    """Create an admin user for testing"""
    # Initialize admin via API
    response = client.post(
        "/api/setup/initialize",
        json={
            "email": "admin@test.com",
            "password": "Test123!@#",
            "first_name_ar": "مدير",
            "last_name_ar": "النظام",
            "first_name_en": "System",
            "last_name_en": "Admin",
        }
    )
    assert response.status_code == 201
    return response.json()


# ==========================================
# Test Cases - Admin Initialization
# ==========================================

def test_admin_initialization_success(test_db):
    """Test successful admin initialization"""
    response = client.post(
        "/api/setup/initialize",
        json={
            "email": "admin@test.com",
            "password": "Test123!@#",
            "first_name_ar": "مدير",
            "last_name_ar": "النظام",
            "first_name_en": "System",
            "last_name_en": "Admin",
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "admin@test.com"
    assert data["role"] == "admin"
    assert data["is_active"] == True


def test_admin_initialization_duplicate(admin_user):
    """Test that second admin initialization fails"""
    response = client.post(
        "/api/setup/initialize",
        json={
            "email": "admin2@test.com",
            "password": "Test123!@#",
            "first_name_ar": "مدير",
            "last_name_ar": "ثاني",
            "first_name_en": "Second",
            "last_name_en": "Admin",
            "position_ar": "مدير",
            "position_en": "Administrator"
        }
    )

    assert response.status_code == 400
    data = response.json()
    assert "error_code" in data["detail"]
    assert data["detail"]["error_code"] == "ALREADY_SETUP"


def test_setup_status_check(admin_user):
    """Test setup status endpoint"""
    response = client.get("/api/setup/status")

    assert response.status_code == 200
    data = response.json()
    assert data["is_setup"] == True


# ==========================================
# Test Cases - User Login
# ==========================================

def test_login_success(admin_user):
    """Test successful login with valid credentials"""
    response = client.post(
        "/api/token",
        data={
            "username": "admin@test.com",
            "password": "Test123!@#"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user_role"] == "admin"
    assert len(data["access_token"]) > 0


def test_login_invalid_email(admin_user):
    """Test login with non-existent email"""
    response = client.post(
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


def test_login_invalid_password(admin_user):
    """Test login with wrong password"""
    response = client.post(
        "/api/token",
        data={
            "username": "admin@test.com",
            "password": "WrongPassword123"
        }
    )

    assert response.status_code == 401
    data = response.json()
    assert "error_code" in data["detail"]
    assert data["detail"]["error_code"] == "INVALID_CREDENTIALS"


def test_login_empty_credentials():
    """Test login with empty credentials"""
    response = client.post(
        "/api/token",
        data={
            "username": "",
            "password": ""
        }
    )

    assert response.status_code in [401, 422]  # 422 for validation error


# ==========================================
# Test Cases - Token Validation
# ==========================================

def test_protected_endpoint_with_valid_token(admin_user):
    """Test accessing protected endpoint with valid token"""
    # Login first
    login_response = client.post(
        "/api/token",
        data={
            "username": "admin@test.com",
            "password": "Test123!@#"
        }
    )
    token = login_response.json()["access_token"]

    # Access protected endpoint
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@test.com"


def test_protected_endpoint_without_token(admin_user):
    """Test accessing protected endpoint without token"""
    response = client.get("/api/users/me")

    assert response.status_code == 401


def test_protected_endpoint_with_invalid_token(admin_user):
    """Test accessing protected endpoint with invalid token"""
    response = client.get(
        "/api/users/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )

    assert response.status_code == 401


def test_protected_endpoint_with_malformed_token(admin_user):
    """Test accessing protected endpoint with malformed authorization header"""
    response = client.get(
        "/api/users/me",
        headers={"Authorization": "InvalidFormat token"}
    )

    assert response.status_code == 401


# ==========================================
# Test Cases - Rate Limiting
# ==========================================

def test_login_rate_limiting(admin_user):
    """Test that login is rate limited (max 5 per minute)"""
    # Try to login 6 times quickly
    responses = []
    for i in range(6):
        response = client.post(
            "/api/token",
            data={
                "username": "admin@test.com",
                "password": "WrongPassword"
            }
        )
        responses.append(response)

    # First 5 should get 401 (invalid credentials)
    # 6th should get 429 (rate limit exceeded)
    assert responses[4].status_code == 401  # 5th attempt
    assert responses[5].status_code == 429  # 6th attempt - rate limited


# ==========================================
# Test Cases - Audit Logging
# ==========================================

def test_successful_login_creates_audit_log(admin_user):
    """Test that successful login creates audit log entry"""
    # Login
    login_response = client.post(
        "/api/token",
        data={
            "username": "admin@test.com",
            "password": "Test123!@#"
        }
    )
    token = login_response.json()["access_token"]

    # Check audit logs (admin only)
    response = client.get(
        "/api/admin/audit-logs?action=user_login&limit=1",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["logs"]) >= 1
    assert data["logs"][0]["action"] == "user_login"
    assert data["logs"][0]["user_email"] == "admin@test.com"


def test_failed_login_creates_audit_log(admin_user):
    """Test that failed login creates audit log entry"""
    # Failed login
    client.post(
        "/api/token",
        data={
            "username": "admin@test.com",
            "password": "WrongPassword"
        }
    )

    # Get admin token
    login_response = client.post(
        "/api/token",
        data={
            "username": "admin@test.com",
            "password": "Test123!@#"
        }
    )
    token = login_response.json()["access_token"]

    # Check audit logs
    response = client.get(
        "/api/admin/audit-logs?action=user_login_failed&limit=1",
        headers={"Authorization": f"Bearer {token}"}
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
