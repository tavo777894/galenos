"""
Snippet model for reusable text fragments in clinical notes.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Table, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.encounter import MedicalSpecialty


# Association table for user favorite snippets
user_favorite_snippets = Table(
    'user_favorite_snippets',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('snippet_id', Integer, ForeignKey('snippets.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)


class SnippetCategory(str):
    """Snippet category constants."""
    MOTIVO = "MOTIVO"
    ANTECEDENTES = "ANTECEDENTES"
    EXAMEN = "EXAMEN"
    DX = "DX"
    PLAN = "PLAN"
    INDICACIONES = "INDICACIONES"


class Snippet(Base):
    """
    Reusable text snippets for clinical documentation.
    Allows doctors to quickly insert common phrases and instructions.
    """
    __tablename__ = "snippets"

    id = Column(Integer, primary_key=True, index=True)

    # Snippet info
    specialty = Column(Enum(MedicalSpecialty), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    content = Column(Text, nullable=False)

    # Metadata
    is_active = Column(Integer, default=1)  # SQLite compatible boolean
    usage_count = Column(Integer, default=0)  # Track how often it's used
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    favorited_by = relationship(
        "User",
        secondary=user_favorite_snippets,
        backref="favorite_snippets"
    )

    def __repr__(self):
        return f"<Snippet {self.title} - {self.category}>"
