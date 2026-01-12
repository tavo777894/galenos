"""
Attachment Pydantic schemas for file uploads.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.attachment import AttachmentType


class AttachmentBase(BaseModel):
    """Base attachment schema."""
    patient_id: int = Field(..., gt=0)
    encounter_id: Optional[int] = Field(None, gt=0)
    attachment_type: AttachmentType
    original_filename: Optional[str] = Field(None, max_length=255)


class AttachmentCreate(AttachmentBase):
    """Schema for creating attachment (internal use)."""
    file_path: str
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    created_by: int


class AttachmentInDB(AttachmentBase):
    """Schema for attachment as stored in database."""
    id: int
    file_path: str
    mime_type: Optional[str]
    file_size: Optional[int]
    created_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Attachment(AttachmentInDB):
    """Schema for attachment response (public)."""
    pass


class AttachmentWithUploader(Attachment):
    """Schema for attachment with uploader name."""
    uploader_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
