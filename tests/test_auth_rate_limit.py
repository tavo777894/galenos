"""
Authentication and rate limiting tests.
Tests login behavior and rate limit enforcement.

NOTE: Rate limit tests require the limiter to be ENABLED.
The conftest.py autouse fixture keeps it enabled for this module only.
"""
import pytest
from tests.conftest import client, limiter


class TestAuthLogin:
    """Tests for /api/v1/auth/login endpoint (non-rate-limit behavior)."""

    def test_login_wrong_password_returns_401(self, test_doctor):
        """
        Test: Login with wrong password returns 401 Unauthorized.
        Verifies: POST /api/v1/auth/login with invalid credentials.
        """
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "doctor_test", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user_returns_401(self, test_db):
        """
        Test: Login with non-existent user returns 401.
        Verifies: Consistent error for missing user (no user enumeration).
        """
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "nobody", "password": "anypassword"}
        )
        assert response.status_code == 401

    def test_login_success_returns_tokens(self, test_doctor):
        """
        Test: Successful login returns access and refresh tokens.
        Verifies: Token structure is correct.
        """
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "doctor_test", "password": "password123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"


class TestAuthRateLimit:
    """
    Tests for login rate limiting.

    These tests verify that slowapi rate limiting is enforced.
    The limiter is reset before each test via the autouse fixture in conftest.py.

    Current config: 5 requests per 15 minutes per IP.
    """

    def test_rate_limit_triggers_after_5_attempts(self, test_db, reset_limiter):
        """
        Test: Rate limit returns 429 after 5 login attempts in 15 minutes.
        Verifies: 6th request returns HTTP 429 Too Many Requests.
        """
        # Ensure limiter is enabled for this test
        assert limiter.enabled, "Limiter should be enabled for rate limit tests"

        responses = []

        # Send 6 rapid login attempts (limit is 5/15min)
        for i in range(6):
            response = client.post(
                "/api/v1/auth/login",
                data={"username": f"user_{i}", "password": "wrongpass"}
            )
            responses.append(response.status_code)

        # First 5 should be 401 (wrong password), 6th should be 429
        assert responses[:5] == [401, 401, 401, 401, 401], (
            f"First 5 requests should be 401, got: {responses[:5]}"
        )
        assert responses[5] == 429, (
            f"6th request should be 429, got {responses[5]}. "
            f"All responses: {responses}"
        )

    def test_rate_limit_response_format(self, test_db, reset_limiter):
        """
        Test: Rate limit response has proper format.
        Verifies: 429 response contains error information.
        """
        # Exhaust rate limit (5 requests allowed, 6th triggers 429)
        for i in range(6):
            response = client.post(
                "/api/v1/auth/login",
                data={"username": f"ratelimituser_{i}", "password": "wrong"}
            )

        # Last response should be 429 with proper body
        assert response.status_code == 429, f"Expected 429, got {response.status_code}"

        # slowapi returns error detail in response body
        body = response.json()
        assert "error" in body or "detail" in body, (
            f"Expected error info in 429 response body, got: {body}"
        )

    def test_rate_limit_allows_5_requests(self, test_db, reset_limiter):
        """
        Test: Exactly 5 requests are allowed before rate limiting.
        Verifies: Requests 1-5 succeed, request 6 fails.
        """
        responses = []

        # Send exactly 5 requests - all should succeed (get 401 for wrong creds)
        for i in range(5):
            response = client.post(
                "/api/v1/auth/login",
                data={"username": f"testuser_{i}", "password": "wrongpass"}
            )
            responses.append(response.status_code)

        # All 5 should be 401 (not 429)
        assert all(code == 401 for code in responses), (
            f"First 5 requests should all be 401, got: {responses}"
        )

        # 6th request should be rate limited
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser_6", "password": "wrongpass"}
        )
        assert response.status_code == 429
