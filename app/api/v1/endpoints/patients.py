"""
Patient endpoints for CRUD operations with audit logging.
"""
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_active_user, require_admin
from app.core.db_errors import raise_conflict_for_integrity_error
from app.models.user import User
from app.models.patient import Patient
from app.models.encounter import Encounter
from app.schemas.patient import PatientCreate, PatientUpdate, Patient as PatientSchema, PatientWithAge
from app.schemas.encounter import Encounter as EncounterSchema
from app.services.pdf_service import pdf_service
from app.services.audit_service import audit_service

router = APIRouter()


@router.post("/", response_model=PatientSchema, status_code=status.HTTP_201_CREATED)
def create_patient(
    patient_in: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new patient with audit logging."""
    # Check if patient with same CI already exists
    existing_patient = db.query(Patient).filter(Patient.ci == patient_in.ci).first()
    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Patient with CI {patient_in.ci} already exists"
        )

    if patient_in.email and Patient.__table__.columns["email"].unique:
        existing_email = db.query(Patient).filter(Patient.email == patient_in.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Patient with email {patient_in.email} already exists"
            )

    # Create new patient
    db_patient = Patient(**patient_in.model_dump())
    db.add(db_patient)
    conflict_detail_map = {
        "patients.ci": f"Patient with CI {patient_in.ci} already exists",
        "(ci)": f"Patient with CI {patient_in.ci} already exists",
    }
    if patient_in.email:
        conflict_detail_map.update({
            "patients.email": f"Patient with email {patient_in.email} already exists",
            "(email)": f"Patient with email {patient_in.email} already exists",
        })

    try:
        db.commit()
        db.refresh(db_patient)
    except IntegrityError as exc:
        db.rollback()
        raise_conflict_for_integrity_error(
            exc,
            detail_map=conflict_detail_map,
        )

    # Audit log
    audit_service.log_patient_create(db, current_user, db_patient.id, db_patient.ci)

    return db_patient


@router.get("/", response_model=List[PatientSchema])
def list_patients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of all patients with pagination."""
    patients = db.query(Patient).filter(Patient.deleted_at.is_(None)).offset(skip).limit(limit).all()
    return patients


@router.get("/{patient_id}", response_model=PatientWithAge)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific patient by ID."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient or patient.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )

    # Convert to PatientWithAge schema
    patient_dict = {
        "id": patient.id,
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "ci": patient.ci,
        "date_of_birth": patient.date_of_birth,
        "phone": patient.phone,
        "email": patient.email,
        "address": patient.address,
        "emergency_contact_name": patient.emergency_contact_name,
        "emergency_contact_phone": patient.emergency_contact_phone,
        "emergency_contact_relationship": patient.emergency_contact_relationship,
        "allergies": patient.allergies,
        "medical_history": patient.medical_history,
        "created_at": patient.created_at,
        "updated_at": patient.updated_at,
        "age": patient.age
    }

    return patient_dict


@router.get("/{patient_id}/encounters", response_model=List[EncounterSchema])
def get_patient_encounters(
    patient_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all encounters for a specific patient.
    Returns encounters ordered by most recent first.
    """
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient or patient.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )

    # Get patient's encounters
    encounters = db.query(Encounter).filter(
        Encounter.patient_id == patient_id
    ).order_by(Encounter.created_at.desc()).offset(skip).limit(limit).all()

    return encounters


@router.put("/{patient_id}", response_model=PatientSchema)
def update_patient(
    patient_id: int,
    patient_in: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a patient's information with audit logging."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient or patient.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )

    # Check if new CI already exists (if CI is being updated)
    if patient_in.ci and patient_in.ci != patient.ci:
        existing_patient = db.query(Patient).filter(Patient.ci == patient_in.ci).first()
        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Patient with CI {patient_in.ci} already exists"
            )

    if patient_in.email and patient_in.email != patient.email and Patient.__table__.columns["email"].unique:
        existing_email = db.query(Patient).filter(Patient.email == patient_in.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Patient with email {patient_in.email} already exists"
            )

    # Track changed fields for audit
    update_data = patient_in.model_dump(exclude_unset=True)
    changed_fields = {k: v for k, v in update_data.items() if getattr(patient, k) != v}

    # Update patient fields
    for field, value in update_data.items():
        setattr(patient, field, value)

    conflict_ci = patient_in.ci or patient.ci
    conflict_detail_map = {
        "patients.ci": f"Patient with CI {conflict_ci} already exists",
        "(ci)": f"Patient with CI {conflict_ci} already exists",
    }
    conflict_email = patient_in.email or patient.email
    if conflict_email:
        conflict_detail_map.update({
            "patients.email": f"Patient with email {conflict_email} already exists",
            "(email)": f"Patient with email {conflict_email} already exists",
        })

    try:
        db.commit()
        db.refresh(patient)
    except IntegrityError as exc:
        db.rollback()
        raise_conflict_for_integrity_error(
            exc,
            detail_map=conflict_detail_map,
        )

    # Audit log
    if changed_fields:
        audit_service.log_patient_update(db, current_user, patient.id, patient.ci, changed_fields)

    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a patient with audit logging."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient or patient.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )

    patient_ci = patient.ci

    patient.deleted_at = datetime.now(timezone.utc)
    db.commit()

    # Audit log
    audit_service.log_patient_delete(db, current_user, patient_id, patient_ci)

    return None


@router.get("/search/ci/{ci}", response_model=PatientSchema)
def search_patient_by_ci(
    ci: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Search for a patient by CI."""
    patient = db.query(Patient).filter(
        Patient.ci == ci,
        Patient.deleted_at.is_(None)
    ).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with CI {ci} not found"
        )

    return patient


@router.post("/{patient_id}/generate-card")
def generate_patient_card_pdf(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate and save a new PDF patient card.
    Returns the document ID and download URL.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient or patient.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )

    # Generate PDF and save to database
    pdf_bytes, document = pdf_service.generate_patient_card(
        db=db,
        patient=patient,
        user=current_user,
        save_to_db=True
    )

    # Audit log
    audit_service.log_document_generate(
        db,
        current_user,
        document.id,
        patient.id,
        document.document_type
    )

    return {
        "document_id": document.id,
        "filename": document.filename,
        "created_at": document.created_at,
        "download_url": f"/api/v1/documents/{document.id}/download"
    }


@router.get("/{patient_id}/card-pdf")
def get_patient_card_pdf_quick(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate PDF on-the-fly without saving to database.
    Quick preview mode.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient or patient.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )

    # Generate PDF without saving
    pdf_bytes, _ = pdf_service.generate_patient_card(
        db=db,
        patient=patient,
        user=current_user,
        save_to_db=False
    )

    # Return PDF as response
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename=ficha_paciente_{patient.ci}_preview.pdf"
        }
    )
