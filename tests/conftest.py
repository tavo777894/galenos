"""
Shared pytest fixtures for Galenos backend tests.
Centralizes database setup, user fixtures, and authentication helpers.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import date

from app.main import app
from app.db.session import Base, get_db
from app.core.security import get_password_hash
from app.core.limiter import limiter

# Import ALL models to register them with Base.metadata
# This ensures create_all() creates all tables
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.document import Document
from app.models.encounter import Encounter
from app.models.template import Template
from app.models.snippet import Snippet
from app.models.attachment import Attachment
from app.models.audit_log import AuditLog
from app.models.revoked_token import RevokedToken

# Test database setup - in-memory SQLite with StaticPool for thread safety
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Dependency override for database session."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Apply dependency override
app.dependency_overrides[get_db] = override_get_db


# =============================================================================
# RATE LIMITER CONTROL
# =============================================================================

@pytest.fixture(autouse=True)
def disable_rate_limiter(request):
    """
    Automatically disable rate limiter for all tests EXCEPT those in
    test_auth_rate_limit.py (which need the limiter enabled).

    This prevents 429 errors during normal test runs while still allowing
    rate limit tests to function correctly.
    """
    # Check if this test is in a rate limit test module
    test_module = request.node.fspath.basename
    if test_module in {"test_auth_rate_limit.py", "test_auth_register_security.py"}:
        # Keep limiter enabled for rate limit tests, but reset storage
        limiter.reset()
        yield
    else:
        # Disable limiter for all other tests
        original_enabled = limiter.enabled
        limiter.enabled = False
        yield
        limiter.enabled = original_enabled


@pytest.fixture
def reset_limiter():
    """
    Fixture to reset limiter storage before a rate limit test.
    Use this in rate limit tests to ensure clean state.
    """
    limiter.reset()
    yield
    limiter.reset()


# =============================================================================
# DATABASE FIXTURES
# =============================================================================

@pytest.fixture(scope="function")
def test_db():
    """Create and drop test database tables for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """Provide a database session for direct DB operations in tests."""
    db = TestingSessionLocal()
    yield db
    db.close()


# =============================================================================
# TEST CLIENT
# =============================================================================

# Shared test client - rate limiting controlled by disable_rate_limiter fixture
client = TestClient(app)


# =============================================================================
# USER FIXTURES
# =============================================================================

@pytest.fixture
def test_doctor(test_db):
    """Create a test doctor user."""
    db = TestingSessionLocal()
    doctor = User(
        email="doctor@test.com",
        username="doctor_test",
        full_name="Dr. Test",
        hashed_password=get_password_hash("password123"),
        role=UserRole.DOCTOR,
        is_active=True
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    db.close()
    return doctor


@pytest.fixture
def test_admin(test_db):
    """Create a test admin user."""
    db = TestingSessionLocal()
    admin = User(
        email="admin@test.com",
        username="admin_test",
        full_name="Admin Test",
        hashed_password=get_password_hash("password123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    db.close()
    return admin


@pytest.fixture
def test_secretaria(test_db):
    """Create a test secretaria user."""
    db = TestingSessionLocal()
    secretaria = User(
        email="secretaria@test.com",
        username="secretaria_test",
        full_name="Secretaria Test",
        hashed_password=get_password_hash("password123"),
        role=UserRole.SECRETARIA,
        is_active=True
    )
    db.add(secretaria)
    db.commit()
    db.refresh(secretaria)
    db.close()
    return secretaria


# =============================================================================
# PATIENT FIXTURES
# =============================================================================

@pytest.fixture
def test_patient(test_db):
    """Create a test patient."""
    db = TestingSessionLocal()
    patient = Patient(
        first_name="John",
        last_name="Doe",
        ci="12345678",
        date_of_birth=date(1990, 1, 1),
        phone="+59170123456",
        email="john@test.com"
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    db.close()
    return patient


# =============================================================================
# TOKEN FIXTURES
# =============================================================================

@pytest.fixture
def auth_token(test_doctor):
    """Get authentication token for test doctor."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "doctor_test", "password": "password123"}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture
def admin_token(test_admin):
    """Get authentication token for test admin."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin_test", "password": "password123"}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture
def secretaria_token(test_secretaria):
    """Get authentication token for test secretaria."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "secretaria_test", "password": "password123"}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]
