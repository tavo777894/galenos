"""
Audit service for logging user actions.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.models.user import User


class AuditService:
    """Service for creating audit logs."""

    @staticmethod
    def log(
        db: Session,
        user: User,
        entity: str,
        action: str,
        entity_id: Optional[int] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Create an audit log entry.

        Args:
            db: Database session
            user: User performing the action
            entity: Entity type (e.g., "patient", "document")
            action: Action performed (e.g., "create", "update", "delete", "print", "download")
            entity_id: ID of the affected entity
            description: Human-readable description
            metadata: Additional metadata as dictionary

        Returns:
            Created AuditLog instance
        """
        audit_log = AuditLog(
            user_id=user.id,
            entity=entity,
            entity_id=entity_id,
            action=action,
            description=description,
            metadata=metadata or {}
        )

        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)

        return audit_log

    @staticmethod
    def log_patient_create(db: Session, user: User, patient_id: int, patient_ci: str) -> AuditLog:
        """Log patient creation."""
        return AuditService.log(
            db=db,
            user=user,
            entity="patient",
            action="create",
            entity_id=patient_id,
            description=f"Created patient with CI: {patient_ci}",
            metadata={"patient_ci": patient_ci}
        )

    @staticmethod
    def log_patient_update(
        db: Session,
        user: User,
        patient_id: int,
        patient_ci: str,
        changed_fields: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log patient update."""
        return AuditService.log(
            db=db,
            user=user,
            entity="patient",
            action="update",
            entity_id=patient_id,
            description=f"Updated patient with CI: {patient_ci}",
            metadata={"patient_ci": patient_ci, "changed_fields": changed_fields or {}}
        )

    @staticmethod
    def log_patient_delete(db: Session, user: User, patient_id: int, patient_ci: str) -> AuditLog:
        """Log patient deletion."""
        return AuditService.log(
            db=db,
            user=user,
            entity="patient",
            action="delete",
            entity_id=patient_id,
            description=f"Deleted patient with CI: {patient_ci}",
            metadata={"patient_ci": patient_ci}
        )

    @staticmethod
    def log_document_generate(
        db: Session,
        user: User,
        document_id: int,
        patient_id: int,
        document_type: str
    ) -> AuditLog:
        """Log document generation."""
        return AuditService.log(
            db=db,
            user=user,
            entity="document",
            action="generate",
            entity_id=document_id,
            description=f"Generated {document_type} document for patient ID: {patient_id}",
            metadata={"patient_id": patient_id, "document_type": document_type}
        )

    @staticmethod
    def log_document_download(
        db: Session,
        user: User,
        document_id: int,
        patient_id: int
    ) -> AuditLog:
        """Log document download."""
        return AuditService.log(
            db=db,
            user=user,
            entity="document",
            action="download",
            entity_id=document_id,
            description=f"Downloaded document for patient ID: {patient_id}",
            metadata={"patient_id": patient_id}
        )

    @staticmethod
    def log_document_print(
        db: Session,
        user: User,
        document_id: int,
        patient_id: int
    ) -> AuditLog:
        """Log document print/reprint."""
        return AuditService.log(
            db=db,
            user=user,
            entity="document",
            action="print",
            entity_id=document_id,
            description=f"Printed document for patient ID: {patient_id}",
            metadata={"patient_id": patient_id}
        )

    @staticmethod
    def log_apply_template(
        db: Session,
        user: User,
        encounter_id: int,
        template_id: int,
        patient_id: int,
        template_title: str
    ) -> AuditLog:
        """Log template application to encounter."""
        return AuditService.log(
            db=db,
            user=user,
            entity="encounter",
            action="APPLY_TEMPLATE",
            entity_id=encounter_id,
            description=f"Applied template '{template_title}' to encounter for patient ID: {patient_id}",
            metadata={
                "template_id": template_id,
                "patient_id": patient_id,
                "template_title": template_title
            }
        )


# Global instance
audit_service = AuditService()
