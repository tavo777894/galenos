"""
Patient soft delete and RBAC tests.
Tests role-based access control for delete operations and soft delete behavior.
"""
import pytest
from tests.conftest import client, TestingSessionLocal
from app.models.patient import Patient
from datetime import date


class TestPatientDeleteRBAC:
    """
    Tests for DELETE /api/v1/patients/{id} role-based access control.
    Only ADMIN role can delete patients.
    """

    def test_secretaria_delete_patient_returns_403(self, test_patient, secretaria_token):
        """
        Test: Secretaria cannot delete patient - returns 403 Forbidden.
        Verifies: RBAC rejects non-admin roles.
        """
        response = client.delete(
            f"/api/v1/patients/{test_patient.id}",
            headers={"Authorization": f"Bearer {secretaria_token}"}
        )

        assert response.status_code == 403
        detail = response.json()["detail"]
        assert "admin" in detail.lower()

    def test_doctor_delete_patient_returns_403(self, test_patient, auth_token):
        """
        Test: Doctor cannot delete patient - returns 403 Forbidden.
        Verifies: RBAC rejects doctor role for delete.
        """
        response = client.delete(
            f"/api/v1/patients/{test_patient.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 403
        detail = response.json()["detail"]
        assert "admin" in detail.lower()

    def test_admin_delete_patient_returns_204(self, test_patient, admin_token):
        """
        Test: Admin can delete patient - returns 204 No Content.
        Verifies: RBAC allows admin role for delete.
        """
        response = client.delete(
            f"/api/v1/patients/{test_patient.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 204

    def test_delete_nonexistent_patient_returns_404(self, test_db, admin_token):
        """
        Test: Delete non-existent patient returns 404.
        Verifies: Proper error when patient doesn't exist.
        """
        response = client.delete(
            "/api/v1/patients/99999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 404


class TestPatientSoftDelete:
    """
    Tests for soft delete behavior.
    Deleted patients should have deleted_at set and be excluded from queries.
    """

    def test_get_deleted_patient_returns_404(self, test_patient, admin_token):
        """
        Test: Get soft-deleted patient returns 404.
        Verifies: Soft-deleted patients are not accessible via GET.
        """
        # Delete the patient
        delete_response = client.delete(
            f"/api/v1/patients/{test_patient.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert delete_response.status_code == 204

        # Try to get the deleted patient
        get_response = client.get(
            f"/api/v1/patients/{test_patient.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert get_response.status_code == 404

    def test_list_patients_excludes_deleted(self, test_db, admin_token):
        """
        Test: List patients does NOT include soft-deleted patients.
        Verifies: Deleted patients are filtered from list queries.
        """
        # Create two patients
        db = TestingSessionLocal()
        patient1 = Patient(
            first_name="Active",
            last_name="Patient",
            ci="11111111",
            date_of_birth=date(1990, 1, 1)
        )
        patient2 = Patient(
            first_name="ToDelete",
            last_name="Patient",
            ci="22222222",
            date_of_birth=date(1990, 1, 1)
        )
        db.add(patient1)
        db.add(patient2)
        db.commit()
        patient1_id = patient1.id
        patient2_id = patient2.id
        db.close()

        # Verify both appear in list initially
        list_response = client.get(
            "/api/v1/patients/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert list_response.status_code == 200
        patient_ids = [p["id"] for p in list_response.json()]
        assert patient1_id in patient_ids
        assert patient2_id in patient_ids

        # Delete patient2
        delete_response = client.delete(
            f"/api/v1/patients/{patient2_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert delete_response.status_code == 204

        # Verify deleted patient is excluded from list
        list_response = client.get(
            "/api/v1/patients/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert list_response.status_code == 200
        patient_ids = [p["id"] for p in list_response.json()]
        assert patient1_id in patient_ids
        assert patient2_id not in patient_ids

    def test_soft_delete_sets_deleted_at_timestamp(self, test_patient, admin_token):
        """
        Test: Soft delete sets deleted_at timestamp in database.
        Verifies: Database record is updated, not removed.
        """
        patient_id = test_patient.id

        # Delete the patient
        delete_response = client.delete(
            f"/api/v1/patients/{patient_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert delete_response.status_code == 204

        # Verify in database that deleted_at is set
        db = TestingSessionLocal()
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        assert patient is not None, "Patient record should still exist in DB"
        assert patient.deleted_at is not None, "deleted_at should be set"
        db.close()

    def test_delete_already_deleted_patient_returns_404(self, test_patient, admin_token):
        """
        Test: Delete an already-deleted patient returns 404.
        Verifies: Cannot delete a patient twice.
        """
        # Delete once
        response = client.delete(
            f"/api/v1/patients/{test_patient.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 204

        # Try to delete again
        response = client.delete(
            f"/api/v1/patients/{test_patient.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404
