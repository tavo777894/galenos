"""
Models package.
"""
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.audit_log import AuditLog
from app.models.document import Document, DocumentType
from app.models.encounter import Encounter, EncounterStatus, MedicalSpecialty
from app.models.template import Template, user_favorite_templates
from app.models.snippet import Snippet, SnippetCategory, user_favorite_snippets
from app.models.attachment import Attachment, AttachmentType

__all__ = [
    "User", "UserRole",
    "Patient",
    "AuditLog",
    "Document", "DocumentType",
    "Encounter", "EncounterStatus", "MedicalSpecialty",
    "Template", "user_favorite_templates",
    "Snippet", "SnippetCategory", "user_favorite_snippets",
    "Attachment", "AttachmentType"
]
