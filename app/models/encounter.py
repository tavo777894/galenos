"""
Encounter (Clinical Consultation) model using SOAP format.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from app.db.session import Base


class EncounterStatus(str, enum.Enum):
    """Encounter status enum."""
    DRAFT = "DRAFT"
    SIGNED = "SIGNED"


class MedicalSpecialty(str, enum.Enum):
    """Medical specialty enum with display names."""
    CARDIOLOGIA = "CARDIOLOGIA"
    NEUROLOGIA = "NEUROLOGIA"
    DERMATOLOGIA = "DERMATOLOGIA"
    CIRUGIA_CARDIOVASCULAR = "CIRUGIA_CARDIOVASCULAR"

    @property
    def display_name(self) -> str:
        """Get the full display name of the specialty."""
        names = {
            "CARDIOLOGIA": "Cardiología",
            "NEUROLOGIA": "Neurología",
            "DERMATOLOGIA": "Dermatología",
            "CIRUGIA_CARDIOVASCULAR": "Cirugía Cardiovascular"
        }
        return names.get(self.value, self.value)


class Encounter(Base):
    """
    Clinical encounter/consultation using SOAP format.

    SOAP:
    - S (Subjective): Patient's description of symptoms
    - O (Objective): Observable/measurable findings
    - A (Assessment): Diagnosis or clinical impression
    - P (Plan): Treatment plan and next steps
    """
    __tablename__ = "encounters"

    id = Column(Integer, primary_key=True, index=True)

    # References
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # SOAP Format
    subjective = Column(Text, nullable=True)  # S: Motivo de consulta, síntomas
    objective = Column(Text, nullable=True)   # O: Signos vitales, examen físico
    assessment = Column(Text, nullable=True)  # A: Diagnóstico, impresión clínica
    plan = Column(Text, nullable=True)        # P: Plan de tratamiento

    # Metadata
    specialty = Column(Enum(MedicalSpecialty), nullable=False, default=MedicalSpecialty.CARDIOLOGIA)
    status = Column(Enum(EncounterStatus), nullable=False, default=EncounterStatus.DRAFT)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)  # Track applied template

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    patient = relationship("Patient", backref="encounters")
    doctor = relationship("User", backref="encounters_as_doctor")

    def __repr__(self):
        return f"<Encounter {self.id} - Patient:{self.patient_id} - {self.status}>"
