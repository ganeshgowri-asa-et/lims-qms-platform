"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/lims_qms"

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application
    APP_NAME: str = "LIMS-QMS Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Document Storage
    DOCUMENT_STORAGE_PATH: str = "./storage/documents"
    SIGNATURE_STORAGE_PATH: str = "./storage/signatures"

    # PDF Watermark
    WATERMARK_TEXT: str = "CONTROLLED COPY"
    WATERMARK_OPACITY: float = 0.3

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
