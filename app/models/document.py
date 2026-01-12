"""
Document model for tracking generated PDFs.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base


class DocumentType:
    """Document type constants."""
    PATIENT_CARD = "patient_card"
    MEDICAL_RECORD = "medical_record"
    PRESCRIPTION = "prescription"
    CERTIFICATE = "certificate"


class Document(Base):
    """Document model for tracking generated documents."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    # Document type
    document_type = Column(String(50), nullable=False, index=True)

    # Patient this document belongs to
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)

    # User who created the document
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Path to the PDF file (relative to storage directory)
    pdf_path = Column(String(500), nullable=False)

    # SHA256 hash of the PDF file for integrity verification
    file_hash = Column(String(64), nullable=False)

    # File size in bytes
    file_size = Column(Integer, nullable=False)

    # Original filename
    filename = Column(String(255), nullable=False)

    # Optional description or notes
    description = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    patient = relationship("Patient", backref="documents")
    creator = relationship("User", backref="created_documents")

    def __repr__(self):
        return f"<Document {self.document_type} for Patient:{self.patient_id}>"
