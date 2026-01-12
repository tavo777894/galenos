"""
Smoke tests for Sprint 3: Encounters, Templates, Snippets.
Basic tests to verify core functionality works.
Includes comprehensive photo validation tests for dermatology encounters.
"""
import pytest
import io
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base, get_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.encounter import Encounter, EncounterStatus, MedicalSpecialty
from app.models.template import Template
from app.models.snippet import Snippet, SnippetCategory
from app.models.attachment import Attachment, AttachmentType
from datetime import date

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    """Create and drop test database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


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
def test_patient(test_db):
    """Create a test patient."""
    db = TestingSessionLocal()
    patient = Patient(
        first_name="John",
        last_name="Doe",
        ci="12345678",
        date_of_birth=date(1990, 1, 1),
        phone="+591 70123456",
        email="john@test.com"
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    db.close()
    return patient


@pytest.fixture
def test_template(test_db):
    """Create a test template."""
    db = TestingSessionLocal()
    template = Template(
        title="Test Cardiology Template",
        description="Test template",
        specialty=MedicalSpecialty.CARDIOLOGIA,
        default_subjective="Test subjective",
        default_objective="Test objective",
        default_assessment="Test assessment",
        default_plan="Test plan",
        is_active=1
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    db.close()
    return template


@pytest.fixture
def test_snippet(test_db):
    """Create a test snippet."""
    db = TestingSessionLocal()
    snippet = Snippet(
        specialty=MedicalSpecialty.CARDIOLOGIA,
        title="Test Snippet",
        category=SnippetCategory.DX,
        content="Test content",
        is_active=1
    )
    db.add(snippet)
    db.commit()
    db.refresh(snippet)
    db.close()
    return snippet


@pytest.fixture
def test_derma_template_requires_photo(test_db):
    """Create a dermatology template that requires photo."""
    db = TestingSessionLocal()
    template = Template(
        title="Dermatología - Lesión cutánea",
        description="Template requiring photo",
        specialty=MedicalSpecialty.DERMATOLOGIA,
        default_subjective="Lesión cutánea sospechosa",
        default_objective="Examen dermatológico",
        default_assessment="Diagnóstico presuntivo",
        default_plan="Plan de manejo",
        is_active=1,
        requires_photo=1  # REQUIRES PHOTO
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    db.close()
    return template


@pytest.fixture
def test_derma_template_no_photo(test_db):
    """Create a dermatology template that does NOT require photo."""
    db = TestingSessionLocal()
    template = Template(
        title="Dermatología - Control",
        description="Template without photo requirement",
        specialty=MedicalSpecialty.DERMATOLOGIA,
        default_subjective="Control de seguimiento",
        default_objective="Estado actual",
        default_assessment="Evaluación de respuesta",
        default_plan="Plan de seguimiento",
        is_active=1,
        requires_photo=0  # NO PHOTO REQUIRED
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    db.close()
    return template


@pytest.fixture
def auth_token(test_doctor):
    """Get authentication token for test doctor."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "doctor_test", "password": "password123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_create_encounter(test_db, test_patient, auth_token):
    """
    Smoke test: Create an encounter.
    Verifies: POST /api/v1/encounters works.
    """
    response = client.post(
        "/api/v1/encounters/",
        json={
            "patient_id": test_patient.id,
            "specialty": "CARDIOLOGIA",
            "subjective": "Chest pain",
            "objective": "BP: 120/80",
            "assessment": "Stable angina",
            "plan": "Aspirin 100mg",
            "status": "DRAFT"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["patient_id"] == test_patient.id
    assert data["specialty"] == "CARDIOLOGIA"
    assert data["status"] == "DRAFT"
    assert "id" in data


def test_list_patient_encounters(test_db, test_patient, auth_token):
    """
    Smoke test: List encounters for a patient.
    Verifies: GET /api/v1/patients/{id}/encounters works.
    """
    # Create an encounter first
    db = TestingSessionLocal()
    doctor_id = db.query(User).filter(User.username == "doctor_test").first().id
    encounter = Encounter(
        patient_id=test_patient.id,
        doctor_id=doctor_id,
        specialty=MedicalSpecialty.CARDIOLOGIA,
        subjective="Test",
        status=EncounterStatus.DRAFT
    )
    db.add(encounter)
    db.commit()
    db.close()

    # List encounters
    response = client.get(
        f"/api/v1/patients/{test_patient.id}/encounters",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["patient_id"] == test_patient.id


def test_list_templates(test_db, test_template, auth_token):
    """
    Smoke test: List templates.
    Verifies: GET /api/v1/templates works.
    """
    response = client.get(
        "/api/v1/templates/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["specialty"] == "CARDIOLOGIA"


def test_list_templates_by_specialty(test_db, test_template, auth_token):
    """
    Smoke test: List templates filtered by specialty.
    Verifies: GET /api/v1/templates?specialty= works.
    """
    response = client.get(
        "/api/v1/templates/?specialty=CARDIOLOGIA",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(t["specialty"] == "CARDIOLOGIA" for t in data)


def test_list_snippets(test_db, test_snippet, auth_token):
    """
    Smoke test: List snippets.
    Verifies: GET /api/v1/snippets works.
    """
    response = client.get(
        "/api/v1/snippets/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["specialty"] == "CARDIOLOGIA"


def test_list_snippets_by_specialty_and_category(test_db, test_snippet, auth_token):
    """
    Smoke test: List snippets filtered by specialty and category.
    Verifies: GET /api/v1/snippets?specialty=&category= works.
    """
    response = client.get(
        "/api/v1/snippets/?specialty=CARDIOLOGIA&category=DX",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # All snippets should match filters
    for snippet in data:
        assert snippet["specialty"] == "CARDIOLOGIA"
        assert snippet["category"] == "DX"


def test_apply_template_to_encounter(test_db, test_patient, test_template, auth_token):
    """
    Smoke test: Apply template to encounter.
    Verifies: POST /api/v1/encounters/{id}/apply-template/{template_id} works.
    Verifies: Audit log is created with action=APPLY_TEMPLATE.
    """
    # Create encounter
    db = TestingSessionLocal()
    doctor_id = db.query(User).filter(User.username == "doctor_test").first().id
    encounter = Encounter(
        patient_id=test_patient.id,
        doctor_id=doctor_id,
        specialty=MedicalSpecialty.CARDIOLOGIA,
        status=EncounterStatus.DRAFT
    )
    db.add(encounter)
    db.commit()
    db.refresh(encounter)
    encounter_id = encounter.id
    db.close()

    # Apply template
    response = client.post(
        f"/api/v1/encounters/{encounter_id}/apply-template/{test_template.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["subjective"] == "Test subjective"
    assert data["objective"] == "Test objective"
    assert data["assessment"] == "Test assessment"
    assert data["plan"] == "Test plan"

    # Verify audit log was created
    from app.models.audit_log import AuditLog
    db = TestingSessionLocal()
    audit_log = db.query(AuditLog).filter(
        AuditLog.action == "APPLY_TEMPLATE",
        AuditLog.entity == "encounter",
        AuditLog.entity_id == encounter_id
    ).first()
    assert audit_log is not None
    assert audit_log.metadata["template_id"] == test_template.id
    db.close()


def test_favorites_endpoints(test_db, test_template, test_snippet, auth_token):
    """
    Smoke test: Favorites endpoints.
    Verifies: POST/DELETE /api/v1/favorites/templates/{id} works.
    Verifies: POST/DELETE /api/v1/favorites/snippets/{id} works.
    """
    # Add template to favorites
    response = client.post(
        f"/api/v1/favorites/templates/{test_template.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 204

    # Remove template from favorites
    response = client.delete(
        f"/api/v1/favorites/templates/{test_template.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 204

    # Add snippet to favorites
    response = client.post(
        f"/api/v1/favorites/snippets/{test_snippet.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 204

    # Remove snippet from favorites
    response = client.delete(
        f"/api/v1/favorites/snippets/{test_snippet.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 204


# ========== PHOTO VALIDATION TESTS (Sprint 3 Enhancement) ==========


def test_upload_photo_attachment(test_db, test_patient, auth_token):
    """
    Test: Upload a photo attachment to an encounter.
    Verifies: POST /api/v1/attachments works with file upload.
    """
    # Create dermatology encounter
    db = TestingSessionLocal()
    doctor_id = db.query(User).filter(User.username == "doctor_test").first().id
    encounter = Encounter(
        patient_id=test_patient.id,
        doctor_id=doctor_id,
        specialty=MedicalSpecialty.DERMATOLOGIA,
        status=EncounterStatus.DRAFT
    )
    db.add(encounter)
    db.commit()
    db.refresh(encounter)
    encounter_id = encounter.id
    db.close()

    # Create a fake image file
    fake_image = io.BytesIO(b"fake image content")
    fake_image.name = "test_lesion.jpg"

    # Upload photo attachment
    response = client.post(
        "/api/v1/attachments/",
        data={
            "patient_id": test_patient.id,
            "encounter_id": encounter_id,
            "attachment_type": "PHOTO"
        },
        files={"file": ("test_lesion.jpg", fake_image, "image/jpeg")},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["patient_id"] == test_patient.id
    assert data["encounter_id"] == encounter_id
    assert data["attachment_type"] == "PHOTO"
    assert data["original_filename"] == "test_lesion.jpg"
    assert "id" in data


def test_sign_derma_encounter_with_photo_success(test_db, test_patient, test_derma_template_requires_photo, auth_token):
    """
    Test: Sign dermatology encounter WITH photo when template requires it - SUCCESS.
    Verifies: Signing succeeds when photo is present and template.requires_photo=1.
    Verifies: Audit log SIGN_ENCOUNTER is created.
    """
    # Create dermatology encounter
    db = TestingSessionLocal()
    doctor_id = db.query(User).filter(User.username == "doctor_test").first().id
    encounter = Encounter(
        patient_id=test_patient.id,
        doctor_id=doctor_id,
        specialty=MedicalSpecialty.DERMATOLOGIA,
        status=EncounterStatus.DRAFT,
        subjective="Lesión cutánea",
        objective="Examen",
        assessment="Diagnóstico",
        plan="Plan"
    )
    db.add(encounter)
    db.commit()
    db.refresh(encounter)
    encounter_id = encounter.id
    db.close()

    # Apply template that requires photo
    response = client.post(
        f"/api/v1/encounters/{encounter_id}/apply-template/{test_derma_template_requires_photo.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200

    # Upload photo attachment
    fake_image = io.BytesIO(b"fake image content")
    response = client.post(
        "/api/v1/attachments/",
        data={
            "patient_id": test_patient.id,
            "encounter_id": encounter_id,
            "attachment_type": "PHOTO"
        },
        files={"file": ("lesion.jpg", fake_image, "image/jpeg")},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201

    # Sign encounter - should SUCCEED because photo is present
    response = client.post(
        f"/api/v1/encounters/{encounter_id}/sign",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SIGNED"

    # Verify audit log
    from app.models.audit_log import AuditLog
    db = TestingSessionLocal()
    audit_log = db.query(AuditLog).filter(
        AuditLog.action == "SIGN_ENCOUNTER",
        AuditLog.entity_id == encounter_id
    ).first()
    assert audit_log is not None
    assert audit_log.metadata["new_status"] == "SIGNED"
    db.close()


def test_sign_derma_encounter_without_photo_fails(test_db, test_patient, test_derma_template_requires_photo, auth_token):
    """
    Test: Sign dermatology encounter WITHOUT photo when template requires it - FAILS.
    Verifies: Signing fails with HTTP 400 when photo is missing and template.requires_photo=1.
    Verifies: Error message is clear and helpful.
    """
    # Create dermatology encounter
    db = TestingSessionLocal()
    doctor_id = db.query(User).filter(User.username == "doctor_test").first().id
    encounter = Encounter(
        patient_id=test_patient.id,
        doctor_id=doctor_id,
        specialty=MedicalSpecialty.DERMATOLOGIA,
        status=EncounterStatus.DRAFT,
        subjective="Lesión cutánea",
        objective="Examen",
        assessment="Diagnóstico",
        plan="Plan"
    )
    db.add(encounter)
    db.commit()
    db.refresh(encounter)
    encounter_id = encounter.id
    db.close()

    # Apply template that requires photo
    response = client.post(
        f"/api/v1/encounters/{encounter_id}/apply-template/{test_derma_template_requires_photo.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200

    # Try to sign without uploading photo - should FAIL
    response = client.post(
        f"/api/v1/encounters/{encounter_id}/sign",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 400
    assert "requires at least one PHOTO attachment" in response.json()["detail"]
    assert "Dermatología - Lesión cutánea" in response.json()["detail"]


def test_sign_derma_encounter_no_photo_requirement(test_db, test_patient, test_derma_template_no_photo, auth_token):
    """
    Test: Sign dermatology encounter with template that does NOT require photo - SUCCESS.
    Verifies: Signing succeeds even without photo when template.requires_photo=0.
    """
    # Create dermatology encounter
    db = TestingSessionLocal()
    doctor_id = db.query(User).filter(User.username == "doctor_test").first().id
    encounter = Encounter(
        patient_id=test_patient.id,
        doctor_id=doctor_id,
        specialty=MedicalSpecialty.DERMATOLOGIA,
        status=EncounterStatus.DRAFT,
        subjective="Control",
        objective="Estado",
        assessment="Evaluación",
        plan="Seguimiento"
    )
    db.add(encounter)
    db.commit()
    db.refresh(encounter)
    encounter_id = encounter.id
    db.close()

    # Apply dermatology template that does NOT require photo
    response = client.post(
        f"/api/v1/encounters/{encounter_id}/apply-template/{test_derma_template_no_photo.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200

    # Sign encounter without photo - should SUCCEED
    response = client.post(
        f"/api/v1/encounters/{encounter_id}/sign",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SIGNED"


def test_sign_non_derma_encounter_no_photo_required(test_db, test_patient, test_template, auth_token):
    """
    Test: Sign non-dermatology encounter (cardiology) without photo - SUCCESS.
    Verifies: Photo validation only applies to DERMATOLOGIA specialty.
    """
    # Create cardiology encounter
    db = TestingSessionLocal()
    doctor_id = db.query(User).filter(User.username == "doctor_test").first().id
    encounter = Encounter(
        patient_id=test_patient.id,
        doctor_id=doctor_id,
        specialty=MedicalSpecialty.CARDIOLOGIA,
        status=EncounterStatus.DRAFT,
        subjective="Chest pain",
        objective="BP 120/80",
        assessment="Stable",
        plan="Aspirin"
    )
    db.add(encounter)
    db.commit()
    db.refresh(encounter)
    encounter_id = encounter.id
    db.close()

    # Apply cardiology template
    response = client.post(
        f"/api/v1/encounters/{encounter_id}/apply-template/{test_template.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200

    # Sign encounter without photo - should SUCCEED (not dermatology)
    response = client.post(
        f"/api/v1/encounters/{encounter_id}/sign",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SIGNED"


def test_sign_encounter_already_signed_fails(test_db, test_patient, auth_token):
    """
    Test: Signing an already-signed encounter fails.
    Verifies: Cannot sign an encounter twice.
    """
    # Create encounter
    db = TestingSessionLocal()
    doctor_id = db.query(User).filter(User.username == "doctor_test").first().id
    encounter = Encounter(
        patient_id=test_patient.id,
        doctor_id=doctor_id,
        specialty=MedicalSpecialty.CARDIOLOGIA,
        status=EncounterStatus.SIGNED,  # Already signed
        subjective="Test",
        objective="Test",
        assessment="Test",
        plan="Test"
    )
    db.add(encounter)
    db.commit()
    db.refresh(encounter)
    encounter_id = encounter.id
    db.close()

    # Try to sign again - should FAIL
    response = client.post(
        f"/api/v1/encounters/{encounter_id}/sign",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 400
    assert "already signed" in response.json()["detail"].lower()


def test_list_encounter_attachments(test_db, test_patient, auth_token):
    """
    Test: List attachments for an encounter.
    Verifies: GET /api/v1/attachments/encounters/{id}/attachments works.
    """
    # Create encounter
    db = TestingSessionLocal()
    doctor_id = db.query(User).filter(User.username == "doctor_test").first().id
    encounter = Encounter(
        patient_id=test_patient.id,
        doctor_id=doctor_id,
        specialty=MedicalSpecialty.DERMATOLOGIA,
        status=EncounterStatus.DRAFT
    )
    db.add(encounter)
    db.commit()
    db.refresh(encounter)
    encounter_id = encounter.id
    db.close()

    # Upload multiple attachments
    for i in range(3):
        fake_file = io.BytesIO(f"file content {i}".encode())
        client.post(
            "/api/v1/attachments/",
            data={
                "patient_id": test_patient.id,
                "encounter_id": encounter_id,
                "attachment_type": "PHOTO"
            },
            files={"file": (f"photo{i}.jpg", fake_file, "image/jpeg")},
            headers={"Authorization": f"Bearer {auth_token}"}
        )

    # List attachments
    response = client.get(
        f"/api/v1/attachments/encounters/{encounter_id}/attachments",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert all(att["encounter_id"] == encounter_id for att in data)
    assert all(att["attachment_type"] == "PHOTO" for att in data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
