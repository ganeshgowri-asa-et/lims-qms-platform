"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Database
    DATABASE_URL: str = Field(default="postgresql://postgres:password@localhost:5432/lims_qms")
    DATABASE_ECHO: bool = Field(default=False)

    # Application
    APP_NAME: str = Field(default="LIMS-QMS Platform")
    APP_VERSION: str = Field(default="1.0.0")
    ENVIRONMENT: str = Field(default="development")
    SECRET_KEY: str = Field(default="change-me-in-production")

    # API
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    API_RELOAD: bool = Field(default=True)

    # Lab Configuration
    LAB_NAME: str = Field(default="Solar PV Testing Laboratory")
    LAB_ADDRESS: str = Field(default="Your Lab Address")
    LAB_ACCREDITATION: str = Field(default="ISO/IEC 17025:2017")
    LAB_LICENSE: str = Field(default="Your License Number")

    # Digital Certificate
    CERT_SIGNING_KEY: Optional[str] = Field(default=None)
    CERT_PUBLIC_KEY: Optional[str] = Field(default=None)
    CERT_VALIDITY_DAYS: int = Field(default=3650)

    # Report Settings
    REPORT_OUTPUT_DIR: str = Field(default="reports")
    TEMP_DATA_DIR: str = Field(default="temp_data")
    GRAPH_DPI: int = Field(default=300)

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
