"""
Tests for refresh token rotation and revocation.
"""
from datetime import datetime

from tests.conftest import client, TestingSessionLocal
from app.core.security import decode_token
from app.models.revoked_token import RevokedToken


def _login_and_get_refresh_token() -> str:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "doctor_test", "password": "password123"}
    )
    assert response.status_code == 200
    return response.json()["refresh_token"]


def test_refresh_rotation_happy_path(test_doctor):
    refresh_token = _login_and_get_refresh_token()

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["refresh_token"] != refresh_token
    assert data["token_type"] == "bearer"


def test_refresh_reuse_fails(test_doctor):
    refresh_token = _login_and_get_refresh_token()

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200

    reuse_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert reuse_response.status_code == 401


def test_refresh_revoked_fails(test_doctor):
    refresh_token = _login_and_get_refresh_token()
    payload = decode_token(refresh_token)
    assert payload is not None
    jti = payload.get("jti")
    assert jti is not None

    db = TestingSessionLocal()
    db.add(RevokedToken(
        jti=jti,
        token_type="refresh",
        revoked_at=datetime.utcnow(),
        expires_at=None,
        user_id=None
    ))
    db.commit()
    db.close()

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 401
