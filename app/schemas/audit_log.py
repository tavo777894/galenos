"""
Audit Log Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class AuditLogBase(BaseModel):
    """Base audit log schema."""
    entity: str
    entity_id: Optional[int] = None
    action: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AuditLogCreate(AuditLogBase):
    """Schema for creating an audit log (internal use)."""
    user_id: int


class AuditLogInDB(AuditLogBase):
    """Schema for audit log as stored in database."""
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLog(AuditLogInDB):
    """Schema for audit log response (public)."""
    pass


class AuditLogWithUser(AuditLog):
    """Schema for audit log with user information."""
    username: Optional[str] = None
    user_full_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
