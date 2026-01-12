"""
Template model for SOAP consultation templates.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, JSON, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.encounter import MedicalSpecialty


# Association table for user favorite templates
user_favorite_templates = Table(
    'user_favorite_templates',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('template_id', Integer, ForeignKey('templates.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)


class Template(Base):
    """
    Template for SOAP clinical consultations.
    Provides default structure for specific medical specialties.
    """
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)

    # Template info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    specialty = Column(Enum(MedicalSpecialty), nullable=False, index=True)

    # SOAP default content (stored as JSON for flexibility)
    soap_default = Column(JSON, nullable=True)
    # Example: {"subjective": "...", "objective": "...", "assessment": "...", "plan": "..."}

    # Or separate fields (we'll use separate fields for simplicity)
    default_subjective = Column(Text, nullable=True)
    default_objective = Column(Text, nullable=True)
    default_assessment = Column(Text, nullable=True)
    default_plan = Column(Text, nullable=True)

    # Metadata
    is_active = Column(Integer, default=1)  # SQLite compatible boolean
    requires_photo = Column(Integer, default=0)  # 1 if photo attachment is required, 0 otherwise
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    favorited_by = relationship(
        "User",
        secondary=user_favorite_templates,
        backref="favorite_templates"
    )

    def __repr__(self):
        return f"<Template {self.title} - {self.specialty}>"
