"""
Application configuration using Pydantic Settings.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Historia Clínica Electrónica"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Clinic Information
    CLINIC_NAME: str = "Clínica Médica"
    CLINIC_ADDRESS: str = ""
    CLINIC_PHONE: str = ""
    CLINIC_LOGO_PATH: str = ""  # Path to clinic logo image (optional)

    # Storage
    DOCUMENTS_STORAGE_PATH: str = "./storage/documents"

    # Database
    DATABASE_URL: str = "sqlite:///./galenos.db"
    SQLALCHEMY_ECHO: bool = False

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v


# Global settings instance
settings = Settings()
