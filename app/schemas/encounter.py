"""
Encounter Pydantic schemas for SOAP clinical consultations.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.encounter import EncounterStatus, MedicalSpecialty


class EncounterBase(BaseModel):
    """Base encounter schema with common attributes."""
    patient_id: int = Field(..., gt=0, description="ID del paciente")
    specialty: MedicalSpecialty = Field(..., description="Especialidad médica")
    subjective: Optional[str] = Field(None, description="S: Motivo de consulta, síntomas del paciente")
    objective: Optional[str] = Field(None, description="O: Signos vitales, examen físico")
    assessment: Optional[str] = Field(None, description="A: Diagnóstico, impresión clínica")
    plan: Optional[str] = Field(None, description="P: Plan de tratamiento")


class EncounterCreate(EncounterBase):
    """Schema for creating a new encounter."""
    status: EncounterStatus = Field(default=EncounterStatus.DRAFT)


class EncounterUpdate(BaseModel):
    """Schema for updating an encounter."""
    specialty: Optional[MedicalSpecialty] = None
    subjective: Optional[str] = None
    objective: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None
    status: Optional[EncounterStatus] = None


class EncounterInDB(EncounterBase):
    """Schema for encounter as stored in database."""
    id: int
    doctor_id: int
    status: EncounterStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Encounter(EncounterInDB):
    """Schema for encounter response (public)."""
    pass


class EncounterWithDetails(Encounter):
    """Schema for encounter response with patient and doctor details."""
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
