"""
Tests for register endpoint security controls.
"""
from tests.conftest import client


def _register_payload(username: str, email: str) -> dict:
    return {
        "email": email,
        "username": username,
        "full_name": "New User",
        "password": "password123",
        "role": "doctor"
    }


def test_register_requires_admin(test_db, auth_token, secretaria_token):
    response = client.post(
        "/api/v1/auth/register",
        json=_register_payload("doctor_user", "doctor_user@test.com"),
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 403

    response = client.post(
        "/api/v1/auth/register",
        json=_register_payload("secretaria_user", "secretaria_user@test.com"),
        headers={"Authorization": f"Bearer {secretaria_token}"}
    )
    assert response.status_code == 403


def test_register_rate_limited(test_db, admin_token, reset_limiter):
    responses = []
    for i in range(6):
        response = client.post(
            "/api/v1/auth/register",
            json=_register_payload(f"user_{i}", f"user_{i}@test.com"),
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        responses.append(response.status_code)

    assert responses[:5] == [201, 201, 201, 201, 201]
    assert responses[5] == 429
