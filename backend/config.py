"""Application configuration."""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "LIMS-QMS Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql://lims_user:lims_password@localhost:5432/lims_qms_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8501"]
    CORS_ALLOW_CREDENTIALS: bool = True

    # File Storage
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_FILE_TYPES: List[str] = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".png", ".jpg", ".jpeg"]

    # AI Models
    AI_MODELS_ENABLED: bool = True
    AI_MODELS_PATH: str = "/app/ai_models/saved_models"
    AI_PREDICTION_CONFIDENCE_THRESHOLD: float = 75.0
    AI_RETRAIN_INTERVAL_DAYS: int = 30

    # Alerts
    CALIBRATION_ALERT_DAYS: str = "30,15,7"
    TRAINING_ALERT_DAYS: str = "30,15,7"
    ENABLE_EMAIL_ALERTS: bool = True
    ENABLE_DASHBOARD_ALERTS: bool = True

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@solarlims.com"
    SMTP_FROM_NAME: str = "LIMS-QMS Platform"

    # Backup
    BACKUP_ENABLED: bool = True
    BACKUP_PATH: str = "/app/backups"
    BACKUP_RETENTION_DAYS: int = 90

    # Company Information
    COMPANY_NAME: str = "Solar PV Testing Laboratory"
    ISO17025_ACCREDITATION: str = "NABL-TC-XXXX"
    ISO9001_CERTIFICATION: str = "ISO-9001-XXXX"
    COMPANY_ADDRESS: str = ""
    COMPANY_PHONE: str = ""
    COMPANY_EMAIL: str = "info@solarlims.com"
    COMPANY_WEBSITE: str = "https://www.solarlims.com"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/app/logs/app.log"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
