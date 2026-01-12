"""
Audit log model for tracking all important actions.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.db.session import Base


class AuditLog(Base):
    """Audit log model for tracking user actions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # User who performed the action
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # What entity was affected (e.g., "patient", "document", "user")
    entity = Column(String(50), nullable=False, index=True)

    # ID of the affected entity
    entity_id = Column(Integer, nullable=True, index=True)

    # Action performed (e.g., "create", "update", "delete", "print", "download", "view")
    action = Column(String(50), nullable=False, index=True)

    # Additional metadata as JSON (e.g., changed fields, IP address, user agent)
    metadata_ = Column("metadata", JSON, nullable=True)

    # Description of the action
    description = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", backref="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.user_id} {self.action} {self.entity}:{self.entity_id}>"
