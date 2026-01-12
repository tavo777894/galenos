"""
Patient model for medical records.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from app.db.session import Base


class Patient(Base):
    """Patient model for storing patient information."""
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)

    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    ci = Column(String(20), unique=True, index=True, nullable=False)  # Cédula de Identidad
    date_of_birth = Column(Date, nullable=False)

    # Contact Information
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)

    # Emergency Contact
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relationship = Column(String(100), nullable=True)

    # Medical Information
    allergies = Column(Text, nullable=True)  # Lista de alergias
    medical_history = Column(Text, nullable=True)  # Antecedentes médicos

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def full_name(self) -> str:
        """Return patient's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> int:
        """Calculate patient's age."""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def __repr__(self):
        return f"<Patient {self.full_name} (CI: {self.ci})>"
