"""Database configuration and connection management."""

import os
from typing import AsyncGenerator
from databases import Database
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://lims_user:lims_password@localhost:5432/lims_qms_db"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    class Config:
        env_file = ".env"


settings = Settings()

# SQLAlchemy setup
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
metadata = MetaData()

# Async database connection
database = Database(settings.DATABASE_URL)


async def get_database() -> AsyncGenerator:
    """Get database connection."""
    async with database.connection() as connection:
        yield connection


def get_db():
    """Get database session for sync operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def connect_db():
    """Connect to database."""
    await database.connect()
    print("✅ Database connected")


async def disconnect_db():
    """Disconnect from database."""
    await database.disconnect()
    print("❌ Database disconnected")
