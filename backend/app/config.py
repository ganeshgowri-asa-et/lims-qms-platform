"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/lims_qms_db"

    # Application
    APP_NAME: str = "LIMS-QMS Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "development-secret-key-change-in-production"

    # JWT
    JWT_SECRET_KEY: str = "jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB

    # Calibration Alerts
    CALIBRATION_ALERT_DAYS: str = "30,15,7"

    # Organization
    ORG_NAME: str = "Solar PV Testing Laboratory"
    ORG_ADDRESS: str = ""
    ORG_LOGO_PATH: str = "./assets/logo.png"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
