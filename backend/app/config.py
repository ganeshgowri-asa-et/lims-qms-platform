"""
Configuration settings for LIMS/QMS Platform
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # Database
    DB_USER: str = os.getenv("DB_USER", "lims_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "lims_password")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "lims_qms")

    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_VERSION: str = "v1"

    # Auto-numbering
    SEQUENCE_PADDING: int = 5

    # Application
    APP_NAME: str = "LIMS/QMS Platform"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
