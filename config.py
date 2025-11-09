"""Configuration management for LIMS QMS Platform."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/lims_qms_db"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    SECRET_KEY: str = "development-secret-key-change-in-production"

    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Application
    APP_NAME: str = "LIMS QMS Platform"
    ORGANIZATION_NAME: str = "Your Organization"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
