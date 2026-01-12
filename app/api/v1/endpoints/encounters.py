"""
Encounter endpoints for SOAP clinical consultations with role-based access.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_active_user, require_doctor_or_admin
from app.models.user import User
from app.models.patient import Patient
from app.models.encounter import Encounter, EncounterStatus, MedicalSpecialty
from app.models.template import Template
from app.models.attachment import Attachment, AttachmentType
from app.schemas.encounter import (
    EncounterCreate,
    EncounterUpdate,
    Encounter as EncounterSchema,
    EncounterWithDetails
)
from app.services.audit_service import audit_service

router = APIRouter()


@router.post("/", response_model=EncounterSchema, status_code=status.HTTP_201_CREATED)
def create_encounter(
    encounter_in: EncounterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin)
):
    """
    Create a new encounter (SOAP consultation).
    Requires DOCTOR or ADMIN role.
    """
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == encounter_in.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {encounter_in.patient_id} not found"
        )

    # Create encounter
    encounter_data = encounter_in.model_dump()
    db_encounter = Encounter(
        **encounter_data,
        doctor_id=current_user.id  # Set current user as the doctor
    )
    db.add(db_encounter)
    db.commit()
    db.refresh(db_encounter)

    # Audit log
    audit_service.log(
        db=db,
        user=current_user,
        entity="encounter",
        action="create",
        entity_id=db_encounter.id,
        metadata={
            "patient_id": encounter_in.patient_id,
            "specialty": encounter_in.specialty.value,
            "status": db_encounter.status.value
        }
    )

    return db_encounter


@router.get("/", response_model=List[EncounterSchema])
def list_encounters(
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List encounters with optional patient filter.
    All authenticated users can list encounters.
    """
    query = db.query(Encounter)

    # Filter by patient if provided
    if patient_id is not None:
        query = query.filter(Encounter.patient_id == patient_id)

    # Order by most recent first
    query = query.order_by(Encounter.created_at.desc())

    encounters = query.offset(skip).limit(limit).all()
    return encounters


@router.get("/{encounter_id}", response_model=EncounterWithDetails)
def get_encounter(
    encounter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific encounter by ID with patient and doctor details.
    All authenticated users can view encounters.
    """
    encounter = db.query(Encounter).filter(Encounter.id == encounter_id).first()
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Encounter with ID {encounter_id} not found"
        )

    # Build response with details
    encounter_dict = {
        "id": encounter.id,
        "patient_id": encounter.patient_id,
        "doctor_id": encounter.doctor_id,
        "subjective": encounter.subjective,
        "objective": encounter.objective,
        "assessment": encounter.assessment,
        "plan": encounter.plan,
        "specialty": encounter.specialty,
        "status": encounter.status,
        "created_at": encounter.created_at,
        "updated_at": encounter.updated_at,
        "patient_name": f"{encounter.patient.first_name} {encounter.patient.last_name}",
        "doctor_name": f"{encounter.doctor.full_name}" if hasattr(encounter.doctor, 'full_name') else encounter.doctor.username
    }

    return encounter_dict


@router.put("/{encounter_id}", response_model=EncounterSchema)
def update_encounter(
    encounter_id: int,
    encounter_in: EncounterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin)
):
    """
    Update an encounter.
    Requires DOCTOR or ADMIN role.
    """
    encounter = db.query(Encounter).filter(Encounter.id == encounter_id).first()
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Encounter with ID {encounter_id} not found"
        )

    # Update only provided fields
    update_data = encounter_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(encounter, field, value)

    db.commit()
    db.refresh(encounter)

    # Audit log
    audit_service.log(
        db=db,
        user=current_user,
        entity="encounter",
        action="update",
        entity_id=encounter.id,
        metadata={
            "updated_fields": list(update_data.keys()),
            "patient_id": encounter.patient_id
        }
    )

    return encounter


@router.patch("/{encounter_id}/status", response_model=EncounterSchema)
def update_encounter_status(
    encounter_id: int,
    new_status: EncounterStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin)
):
    """
    Update encounter status only.
    Requires DOCTOR or ADMIN role.
    """
    encounter = db.query(Encounter).filter(Encounter.id == encounter_id).first()
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Encounter with ID {encounter_id} not found"
        )

    old_status = encounter.status
    encounter.status = new_status
    db.commit()
    db.refresh(encounter)

    # Audit log
    audit_service.log(
        db=db,
        user=current_user,
        entity="encounter",
        action="status_change",
        entity_id=encounter.id,
        metadata={
            "old_status": old_status.value,
            "new_status": new_status.value,
            "patient_id": encounter.patient_id
        }
    )

    return encounter


@router.delete("/{encounter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_encounter(
    encounter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin)
):
    """
    Delete an encounter (soft delete by setting status to cancelled).
    Requires DOCTOR or ADMIN role.
    """
    encounter = db.query(Encounter).filter(Encounter.id == encounter_id).first()
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Encounter with ID {encounter_id} not found"
        )

    # Soft delete: set status to cancelled
    encounter.status = EncounterStatus.CANCELLED
    db.commit()

    # Audit log
    audit_service.log(
        db=db,
        user=current_user,
        entity="encounter",
        action="delete",
        entity_id=encounter.id,
        metadata={
            "patient_id": encounter.patient_id
        }
    )

    return None


@router.post("/{encounter_id}/apply-template/{template_id}", response_model=EncounterSchema)
def apply_template_to_encounter(
    encounter_id: int,
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin)
):
    """
    Apply a template to an encounter, filling in the default SOAP fields.
    Requires DOCTOR or ADMIN role.
    Logs the action as APPLY_TEMPLATE in audit.
    """
    # Get encounter
    encounter = db.query(Encounter).filter(Encounter.id == encounter_id).first()
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Encounter with ID {encounter_id} not found"
        )

    # Get template
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with ID {template_id} not found"
        )

    # Verify template specialty matches encounter specialty
    if template.specialty != encounter.specialty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Template specialty ({template.specialty.value}) does not match encounter specialty ({encounter.specialty.value})"
        )

    # Apply template defaults to encounter (only if fields are empty)
    if not encounter.subjective and template.default_subjective:
        encounter.subjective = template.default_subjective
    if not encounter.objective and template.default_objective:
        encounter.objective = template.default_objective
    if not encounter.assessment and template.default_assessment:
        encounter.assessment = template.default_assessment
    if not encounter.plan and template.default_plan:
        encounter.plan = template.default_plan

    # Save template_id to track which template was applied
    encounter.template_id = template.id

    db.commit()
    db.refresh(encounter)

    # Audit log - APPLY_TEMPLATE action
    audit_service.log_apply_template(
        db=db,
        user=current_user,
        encounter_id=encounter.id,
        template_id=template.id,
        patient_id=encounter.patient_id,
        template_title=template.title
    )

    return encounter


@router.post("/{encounter_id}/sign", response_model=EncounterSchema)
def sign_encounter(
    encounter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin)
):
    """
    Sign (finalize) an encounter, changing status to SIGNED.

    Validation: If encounter is DERMATOLOGIA and the applied template
    has requires_photo=True, then at least one PHOTO attachment must exist.

    Requires DOCTOR or ADMIN role.
    """
    # Get encounter
    encounter = db.query(Encounter).filter(Encounter.id == encounter_id).first()
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Encounter with ID {encounter_id} not found"
        )

    # Check if already signed
    if encounter.status == EncounterStatus.SIGNED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Encounter is already signed"
        )

    # VALIDATION: Dermatología + template requires_photo
    if encounter.specialty == MedicalSpecialty.DERMATOLOGIA and encounter.template_id:
        # Get the template
        template = db.query(Template).filter(Template.id == encounter.template_id).first()

        if template and template.requires_photo == 1:
            # Check if at least one PHOTO attachment exists for this encounter
            photo_count = db.query(Attachment).filter(
                Attachment.encounter_id == encounter_id,
                Attachment.attachment_type == AttachmentType.PHOTO
            ).count()

            if photo_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Cannot sign encounter: Template '{template.title}' requires at least one PHOTO attachment. "
                        f"Please upload a photo before signing this dermatology consultation."
                    )
                )

    # Change status to SIGNED
    old_status = encounter.status
    encounter.status = EncounterStatus.SIGNED
    db.commit()
    db.refresh(encounter)

    # Audit log
    audit_service.log(
        db=db,
        user=current_user,
        entity="encounter",
        action="SIGN_ENCOUNTER",
        entity_id=encounter.id,
        metadata={
            "patient_id": encounter.patient_id,
            "specialty": encounter.specialty.value,
            "template_id": encounter.template_id,
            "old_status": old_status.value,
            "new_status": EncounterStatus.SIGNED.value
        }
    )

    return encounter
