"""
PDF generation service using WeasyPrint and Jinja2.
"""
import hashlib
import os
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.patient import Patient
from app.models.user import User
from app.models.document import Document, DocumentType


class PDFService:
    """Service for generating and managing PDF documents."""

    def __init__(self):
        """Initialize PDF service with Jinja2 template environment."""
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))

        # Ensure storage directory exists
        self.storage_path = Path(settings.DOCUMENTS_STORAGE_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _calculate_hash(self, pdf_bytes: bytes) -> str:
        """Calculate SHA256 hash of PDF content."""
        return hashlib.sha256(pdf_bytes).hexdigest()

    def _save_pdf(self, pdf_bytes: bytes, filename: str) -> str:
        """
        Save PDF to storage and return relative path.

        Args:
            pdf_bytes: PDF content as bytes
            filename: Filename to use

        Returns:
            Relative path to saved file
        """
        # Create subdirectory by date for organization
        date_dir = datetime.now().strftime("%Y/%m")
        full_dir = self.storage_path / date_dir
        full_dir.mkdir(parents=True, exist_ok=True)

        # Full path to file
        file_path = full_dir / filename

        # Save file
        with open(file_path, "wb") as f:
            f.write(pdf_bytes)

        # Return relative path
        return os.path.join(date_dir, filename)

    def _render_patient_card_html(self, patient: Patient) -> str:
        """
        Render patient card HTML template.

        Args:
            patient: Patient instance

        Returns:
            Rendered HTML string
        """
        template = self.env.get_template("patient_card.html")

        # Check if logo exists
        logo_path = None
        if settings.CLINIC_LOGO_PATH and os.path.exists(settings.CLINIC_LOGO_PATH):
            logo_path = settings.CLINIC_LOGO_PATH

        return template.render(
            patient=patient,
            clinic_name=settings.CLINIC_NAME,
            clinic_address=settings.CLINIC_ADDRESS,
            clinic_phone=settings.CLINIC_PHONE,
            logo_path=logo_path
        )

    def generate_patient_card(
        self,
        db: Session,
        patient: Patient,
        user: User,
        save_to_db: bool = True
    ) -> tuple[bytes, Optional[Document]]:
        """
        Generate a PDF patient card.

        Args:
            db: Database session
            patient: Patient model instance
            user: User generating the document
            save_to_db: Whether to save document record to database

        Returns:
            Tuple of (PDF bytes, Document instance if saved)
        """
        # Render HTML
        html_content = self._render_patient_card_html(patient)

        # Generate PDF
        pdf_file = BytesIO()
        HTML(string=html_content).write_pdf(pdf_file)
        pdf_bytes = pdf_file.getvalue()

        # If not saving to DB, return just the bytes
        if not save_to_db:
            return pdf_bytes, None

        # Calculate hash
        file_hash = self._calculate_hash(pdf_bytes)

        # Generate filename
        filename = f"ficha_paciente_{patient.ci}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        # Save PDF to storage
        relative_path = self._save_pdf(pdf_bytes, filename)

        # Create document record
        document = Document(
            document_type=DocumentType.PATIENT_CARD,
            patient_id=patient.id,
            created_by=user.id,
            pdf_path=relative_path,
            file_hash=file_hash,
            file_size=len(pdf_bytes),
            filename=filename,
            description=f"Ficha de paciente - {patient.full_name}"
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return pdf_bytes, document

    def get_document_bytes(self, document: Document) -> Optional[bytes]:
        """
        Load document from storage.

        Args:
            document: Document instance

        Returns:
            PDF bytes or None if not found
        """
        file_path = self.storage_path / document.pdf_path

        if not file_path.exists():
            return None

        with open(file_path, "rb") as f:
            return f.read()

    def verify_document_integrity(self, document: Document) -> bool:
        """
        Verify document integrity by comparing hash.

        Args:
            document: Document instance

        Returns:
            True if hash matches, False otherwise
        """
        pdf_bytes = self.get_document_bytes(document)

        if pdf_bytes is None:
            return False

        current_hash = self._calculate_hash(pdf_bytes)
        return current_hash == document.file_hash


# Global instance
pdf_service = PDFService()
