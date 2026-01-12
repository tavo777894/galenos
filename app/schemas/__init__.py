"""
Schemas package.
"""
from app.schemas.user import User, UserCreate, UserUpdate, UserInDB, Token, TokenData, RefreshTokenRequest
from app.schemas.patient import Patient, PatientCreate, PatientUpdate, PatientInDB, PatientWithAge
from app.schemas.document import Document, DocumentCreate, DocumentInDB, DocumentWithCreator
from app.schemas.audit_log import AuditLog, AuditLogCreate, AuditLogInDB, AuditLogWithUser
from app.schemas.encounter import Encounter, EncounterCreate, EncounterUpdate, EncounterInDB, EncounterWithDetails
from app.schemas.template import Template, TemplateCreate, TemplateUpdate, TemplateInDB, TemplateWithFavorite
from app.schemas.snippet import Snippet, SnippetCreate, SnippetUpdate, SnippetInDB, SnippetWithFavorite
from app.schemas.attachment import Attachment, AttachmentCreate, AttachmentInDB, AttachmentWithUploader

__all__ = [
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "Token",
    "TokenData",
    "RefreshTokenRequest",
    "Patient",
    "PatientCreate",
    "PatientUpdate",
    "PatientInDB",
    "PatientWithAge",
    "Document",
    "DocumentCreate",
    "DocumentInDB",
    "DocumentWithCreator",
    "AuditLog",
    "AuditLogCreate",
    "AuditLogInDB",
    "AuditLogWithUser",
    "Encounter",
    "EncounterCreate",
    "EncounterUpdate",
    "EncounterInDB",
    "EncounterWithDetails",
    "Template",
    "TemplateCreate",
    "TemplateUpdate",
    "TemplateInDB",
    "TemplateWithFavorite",
    "Snippet",
    "SnippetCreate",
    "SnippetUpdate",
    "SnippetInDB",
    "SnippetWithFavorite",
    "Attachment",
    "AttachmentCreate",
    "AttachmentInDB",
    "AttachmentWithUploader",
]
