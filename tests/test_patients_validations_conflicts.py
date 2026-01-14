"""
Patient validation and conflict tests.
Tests field validation (date_of_birth) and unique constraint conflicts (CI).
"""
import pytest
from datetime import date, timedelta
from tests.conftest import client


class TestPatientCreate:
    """Tests for POST /api/v1/patients/ endpoint."""

    def test_create_patient_success(self, auth_token):
        """
        Test: Create patient with valid data returns 201.
        Verifies: Patient is created and returned with correct fields.
        """
        patient_data = {
            "first_name": "Maria",
            "last_name": "Garcia",
            "ci": "87654321",
            "date_of_birth": "1985-06-15",
            "phone": "+59171234567",
            "email": "maria@test.com"
        }

        response = client.post(
            "/api/v1/patients/",
            json=patient_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "Maria"
        assert data["last_name"] == "Garcia"
        assert data["ci"] == "87654321"
        assert "id" in data
        assert "created_at" in data

    def test_create_patient_future_dob_returns_422(self, auth_token):
        """
        Test: Create patient with future date_of_birth returns 422.
        Verifies: Pydantic validator rejects future dates.
        """
        future_date = (date.today() + timedelta(days=30)).isoformat()

        patient_data = {
            "first_name": "Future",
            "last_name": "Baby",
            "ci": "99999999",
            "date_of_birth": future_date,
            "phone": "+59170000000"
        }

        response = client.post(
            "/api/v1/patients/",
            json=patient_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 422
        detail = response.json()["detail"]
        # Pydantic v2 returns list of errors
        assert any("date_of_birth" in str(err) for err in detail)

    def test_create_patient_duplicate_ci_returns_409(self, test_patient, auth_token):
        """
        Test: Create patient with duplicate CI returns 409 Conflict.
        Verifies: Unique constraint on CI is enforced.
        """
        # test_patient fixture creates patient with ci="12345678"
        patient_data = {
            "first_name": "Another",
            "last_name": "Person",
            "ci": "12345678",  # Same CI as test_patient
            "date_of_birth": "1995-03-20",
            "phone": "+59172222222"
        }

        response = client.post(
            "/api/v1/patients/",
            json=patient_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 409
        assert "12345678" in response.json()["detail"]

    def test_create_patient_missing_required_fields_returns_422(self, auth_token):
        """
        Test: Create patient with missing required fields returns 422.
        Verifies: first_name, last_name, ci, date_of_birth are required.
        """
        # Missing ci and date_of_birth
        patient_data = {
            "first_name": "Incomplete",
            "last_name": "Patient"
        }

        response = client.post(
            "/api/v1/patients/",
            json=patient_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 422

    def test_create_patient_requires_authentication(self, test_db):
        """
        Test: Create patient without auth token returns 401.
        Verifies: Endpoint requires authentication.
        """
        patient_data = {
            "first_name": "No",
            "last_name": "Auth",
            "ci": "11111111",
            "date_of_birth": "2000-01-01"
        }

        response = client.post(
            "/api/v1/patients/",
            json=patient_data
        )

        assert response.status_code == 401


class TestPatientGet:
    """Tests for GET /api/v1/patients/ and GET /api/v1/patients/{id} endpoints."""

    def test_list_patients_returns_200(self, test_patient, auth_token):
        """
        Test: List patients returns 200 with array.
        Verifies: GET /api/v1/patients/ works.
        """
        response = client.get(
            "/api/v1/patients/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_patient_by_id_returns_200(self, test_patient, auth_token):
        """
        Test: Get patient by ID returns 200 with patient data.
        Verifies: GET /api/v1/patients/{id} works and includes age.
        """
        response = client.get(
            f"/api/v1/patients/{test_patient.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_patient.id
        assert data["ci"] == "12345678"
        assert "age" in data  # PatientWithAge schema

    def test_get_nonexistent_patient_returns_404(self, test_db, auth_token):
        """
        Test: Get non-existent patient returns 404.
        Verifies: Proper error for missing patient.
        """
        response = client.get(
            "/api/v1/patients/99999",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 404
