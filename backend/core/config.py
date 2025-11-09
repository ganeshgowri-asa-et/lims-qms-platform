"""
Configuration Management
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # Environment
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql://lims_user:lims_password@localhost:5432/lims_qms_db"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # API Gateway
    API_GATEWAY_HOST: str = "0.0.0.0"
    API_GATEWAY_PORT: int = 8000

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI Models
    ML_MODEL_PATH: str = "./ml_models"
    ENABLE_AI_FEATURES: bool = True

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # Storage
    UPLOAD_DIR: str = "./uploads"
    REPORTS_DIR: str = "./reports"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8501"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
