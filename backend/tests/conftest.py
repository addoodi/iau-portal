"""
Test configuration - uses SQLite for testing instead of PostgreSQL.

Sets DATABASE_URL before any backend module import to ensure the test database is used.
"""

import os

# MUST be set before any backend module import
os.environ["DATABASE_URL"] = "sqlite:///./test_iau_portal.db"
os.environ["ENVIRONMENT"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000"

import pytest
from fastapi.testclient import TestClient

# Shared admin credentials for all tests
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "Test123!@#"


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create all tables at the start of the test session, drop at the end."""
    from backend.database import Base, engine
    Base.metadata.create_all(bind=engine)

    # Disable rate limiting for tests
    from backend.main import app
    app.state.limiter.enabled = False

    yield
    Base.metadata.drop_all(bind=engine)
    # Clean up the test database file
    db_path = "./test_iau_portal.db"
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except PermissionError:
        pass  # File may be locked on Windows; will be cleaned next run


@pytest.fixture(scope="session")
def test_client():
    """Shared test client for all tests."""
    from backend.main import app
    return TestClient(app)


@pytest.fixture(scope="session")
def admin_setup(test_client, setup_test_database):
    """Initialize admin user once for the entire test session."""
    response = test_client.post(
        "/api/setup/initialize",
        json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "first_name_ar": "مدير",
            "last_name_ar": "النظام",
            "first_name_en": "System",
            "last_name_en": "Admin",
        }
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture(scope="session")
def admin_token(test_client, admin_setup):
    """Get admin auth token, reusable across the session."""
    response = test_client.post(
        "/api/token",
        data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200
    return response.json()["access_token"]
