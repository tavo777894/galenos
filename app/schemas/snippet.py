"""
Snippet Pydantic schemas for reusable text fragments.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.snippet import SnippetCategory
from app.models.encounter import MedicalSpecialty


class SnippetBase(BaseModel):
    """Base snippet schema with common attributes."""
    specialty: MedicalSpecialty = Field(..., description="Especialidad médica")
    title: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1, description="Contenido del snippet")


class SnippetCreate(SnippetBase):
    """Schema for creating a new snippet."""
    is_active: int = Field(default=1, ge=0, le=1, description="1=activo, 0=inactivo")


class SnippetUpdate(BaseModel):
    """Schema for updating a snippet."""
    specialty: Optional[MedicalSpecialty] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    content: Optional[str] = Field(None, min_length=1)
    is_active: Optional[int] = Field(None, ge=0, le=1)


class SnippetInDB(SnippetBase):
    """Schema for snippet as stored in database."""
    id: int
    is_active: int
    usage_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Snippet(SnippetInDB):
    """Schema for snippet response (public)."""
    pass


class SnippetWithFavorite(Snippet):
    """Schema for snippet response with favorite status."""
    is_favorite: bool = False

    model_config = ConfigDict(from_attributes=True)
