"""
Application configuration settings
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
import os


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "LIMS-QMS Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str
    DATABASE_URL_SYNC: str

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Email Configuration
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: str = "noreply@lims-qms.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False

    # SMS Configuration (Twilio)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB

    # OCR Configuration
    TESSERACT_CMD: str = "/usr/bin/tesseract"

    # AI/ML Configuration
    AI_MODEL_PATH: str = "./models"
    ENABLE_AI_FEATURES: bool = True

    # Calibration Alert Days
    CALIBRATION_ALERT_DAYS_1: int = 30
    CALIBRATION_ALERT_DAYS_2: int = 15
    CALIBRATION_ALERT_DAYS_3: int = 7

    # Digital Signature
    SIGNATURE_PRIVATE_KEY_PATH: str = "./keys/private_key.pem"
    SIGNATURE_PUBLIC_KEY_PATH: str = "./keys/public_key.pem"

    # Equipment ID Format
    EQUIPMENT_ID_PREFIX: str = "EQP"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
