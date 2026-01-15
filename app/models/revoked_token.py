"""
Model for storing revoked refresh tokens.
"""
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from app.db.session import Base


class RevokedToken(Base):
    """Revoked token model for refresh token blacklist."""
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(36), unique=True, index=True, nullable=False)
    token_type = Column(String(20), nullable=False)
    revoked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
