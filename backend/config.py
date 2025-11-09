"""
Configuration settings for LIMS-QMS Platform
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/lims_qms"
    )

    # API
    API_TITLE: str = "LIMS-QMS Platform API"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    # CORS
    CORS_ORIGINS: list = ["*"]

    # JWT Secret (for future authentication)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

    # File storage
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    class Config:
        env_file = ".env"


settings = Settings()
