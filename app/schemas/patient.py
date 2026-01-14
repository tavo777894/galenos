"""
Patient Pydantic schemas for request/response validation.
"""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class PatientBase(BaseModel):
    """Base patient schema with common attributes."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    ci: str = Field(..., min_length=1, max_length=20, description="Cédula de Identidad")
    date_of_birth: date
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)
    emergency_contact_name: Optional[str] = Field(None, max_length=255)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=100)
    allergies: Optional[str] = None
    medical_history: Optional[str] = None

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return value

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if isinstance(value, str):
            return value.replace(" ", "")
        return value


class PatientCreate(PatientBase):
    """Schema for creating a new patient."""
    pass


class PatientUpdate(BaseModel):
    """Schema for updating a patient."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    ci: Optional[str] = Field(None, min_length=1, max_length=20)
    date_of_birth: Optional[date] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)
    emergency_contact_name: Optional[str] = Field(None, max_length=255)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=100)
    allergies: Optional[str] = None
    medical_history: Optional[str] = None

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: Optional[date]) -> Optional[date]:
        if value is None:
            return value
        if value > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return value

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if isinstance(value, str):
            return value.replace(" ", "")
        return value


class PatientInDB(PatientBase):
    """Schema for patient as stored in database."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Patient(PatientInDB):
    """Schema for patient response (public)."""
    pass


class PatientWithAge(Patient):
    """Schema for patient response with calculated age."""
    age: int

    model_config = ConfigDict(from_attributes=True)
