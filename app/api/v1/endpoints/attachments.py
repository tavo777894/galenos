"""
Attachment endpoints for file uploads (photos, documents).
"""
import os
import shutil
from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.patient import Patient
from app.models.encounter import Encounter
from app.models.attachment import Attachment, AttachmentType
from app.schemas.attachment import (
    Attachment as AttachmentSchema,
    AttachmentWithUploader
)
from app.services.audit_service import audit_service

router = APIRouter()

# Directory to store uploaded files
UPLOAD_DIR = Path("uploads/attachments")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/", response_model=AttachmentSchema, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    file: UploadFile = File(...),
    patient_id: int = Form(...),
    encounter_id: Optional[int] = Form(None),
    attachment_type: AttachmentType = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a file attachment (photo, PDF, document).
    File is associated with a patient and optionally with an encounter.
    """
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )

    # Verify encounter exists if provided
    if encounter_id:
        encounter = db.query(Encounter).filter(Encounter.id == encounter_id).first()
        if not encounter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Encounter with ID {encounter_id} not found"
            )
        # Verify encounter belongs to the patient
        if encounter.patient_id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Encounter does not belong to the specified patient"
            )

    # Generate unique filename
    import uuid
    file_extension = Path(file.filename).suffix if file.filename else ""
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    # Save file to disk
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    finally:
        file.file.close()

    # Get file size
    file_size = file_path.stat().st_size

    # Create attachment record
    attachment = Attachment(
        patient_id=patient_id,
        encounter_id=encounter_id,
        created_by=current_user.id,
        file_path=str(file_path),
        mime_type=file.content_type,
        attachment_type=attachment_type,
        original_filename=file.filename,
        file_size=file_size
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    # Audit log
    audit_service.log(
        db=db,
        user=current_user,
        entity="attachment",
        action="upload",
        entity_id=attachment.id,
        metadata={
            "patient_id": patient_id,
            "encounter_id": encounter_id,
            "attachment_type": attachment_type.value,
            "file_size": file_size,
            "original_filename": file.filename
        }
    )

    return attachment


@router.get("/encounters/{encounter_id}/attachments", response_model=List[AttachmentWithUploader])
def list_encounter_attachments(
    encounter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all attachments associated with an encounter.
    Returns attachments with uploader information.
    """
    # Verify encounter exists
    encounter = db.query(Encounter).filter(Encounter.id == encounter_id).first()
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Encounter with ID {encounter_id} not found"
        )

    # Get attachments
    attachments = db.query(Attachment).filter(
        Attachment.encounter_id == encounter_id
    ).all()

    # Add uploader name
    result = []
    for attachment in attachments:
        attachment_dict = {
            "id": attachment.id,
            "patient_id": attachment.patient_id,
            "encounter_id": attachment.encounter_id,
            "file_path": attachment.file_path,
            "mime_type": attachment.mime_type,
            "attachment_type": attachment.attachment_type,
            "original_filename": attachment.original_filename,
            "file_size": attachment.file_size,
            "created_by": attachment.created_by,
            "created_at": attachment.created_at,
            "uploader_name": attachment.uploader.full_name if attachment.uploader else None
        }
        result.append(attachment_dict)

    return result


@router.get("/{attachment_id}", response_model=AttachmentWithUploader)
def get_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get attachment details by ID."""
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attachment with ID {attachment_id} not found"
        )

    attachment_dict = {
        "id": attachment.id,
        "patient_id": attachment.patient_id,
        "encounter_id": attachment.encounter_id,
        "file_path": attachment.file_path,
        "mime_type": attachment.mime_type,
        "attachment_type": attachment.attachment_type,
        "original_filename": attachment.original_filename,
        "file_size": attachment.file_size,
        "created_by": attachment.created_by,
        "created_at": attachment.created_at,
        "uploader_name": attachment.uploader.full_name if attachment.uploader else None
    }

    return attachment_dict
