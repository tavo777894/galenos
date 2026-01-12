"""
Attachment model for file uploads (photos, PDFs, documents).
"""
from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.session import Base


class AttachmentType(str, enum.Enum):
    """Attachment type enum."""
    PHOTO = "PHOTO"
    PDF = "PDF"
    OTHER = "OTHER"


class Attachment(Base):
    """
    File attachments linked to patients and optionally to encounters.
    Used for photos, medical documents, imaging results, etc.
    """
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)

    # References
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # File info
    file_path = Column(String(500), nullable=False)  # Path to stored file
    mime_type = Column(String(100), nullable=True)   # e.g., image/jpeg, application/pdf
    attachment_type = Column(Enum(AttachmentType), nullable=False, default=AttachmentType.OTHER)

    # Metadata
    original_filename = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    patient = relationship("Patient", backref="attachments")
    encounter = relationship("Encounter", backref="attachments")
    uploader = relationship("User", backref="uploaded_attachments")

    def __repr__(self):
        return f"<Attachment {self.id} - {self.attachment_type} for Patient:{self.patient_id}>"
