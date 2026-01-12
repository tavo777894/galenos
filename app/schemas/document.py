"""
Document Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class DocumentBase(BaseModel):
    """Base document schema."""
    document_type: str
    patient_id: int
    description: Optional[str] = None


class DocumentCreate(DocumentBase):
    """Schema for creating a document (internal use)."""
    pdf_path: str
    file_hash: str
    file_size: int
    filename: str
    created_by: int


class DocumentInDB(DocumentBase):
    """Schema for document as stored in database."""
    id: int
    pdf_path: str
    file_hash: str
    file_size: int
    filename: str
    created_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Document(DocumentInDB):
    """Schema for document response (public)."""
    pass


class DocumentWithCreator(Document):
    """Schema for document with creator information."""
    creator_name: Optional[str] = None
    patient_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
