"""
Template Pydantic schemas for SOAP consultation templates.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.encounter import MedicalSpecialty


class TemplateBase(BaseModel):
    """Base template schema with common attributes."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    specialty: MedicalSpecialty
    default_subjective: Optional[str] = Field(None, description="Contenido por defecto para S (Subjetivo)")
    default_objective: Optional[str] = Field(None, description="Contenido por defecto para O (Objetivo)")
    default_assessment: Optional[str] = Field(None, description="Contenido por defecto para A (Evaluación)")
    default_plan: Optional[str] = Field(None, description="Contenido por defecto para P (Plan)")
    requires_photo: int = Field(default=0, ge=0, le=1, description="1 si requiere foto adjunta, 0 si no")


class TemplateCreate(TemplateBase):
    """Schema for creating a new template."""
    is_active: int = Field(default=1, ge=0, le=1, description="1=activo, 0=inactivo")


class TemplateUpdate(BaseModel):
    """Schema for updating a template."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    specialty: Optional[MedicalSpecialty] = None
    default_subjective: Optional[str] = None
    default_objective: Optional[str] = None
    default_assessment: Optional[str] = None
    default_plan: Optional[str] = None
    is_active: Optional[int] = Field(None, ge=0, le=1)


class TemplateInDB(TemplateBase):
    """Schema for template as stored in database."""
    id: int
    is_active: int
    requires_photo: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Template(TemplateInDB):
    """Schema for template response (public)."""
    pass


class TemplateWithFavorite(Template):
    """Schema for template response with favorite status."""
    is_favorite: bool = False
    specialty_display_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
