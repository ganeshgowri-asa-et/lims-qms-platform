"""
Base model with common fields for all tables
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.orm import declared_attr


class BaseModel:
    """Base model with common audit fields"""

    @declared_attr
    def id(cls):
        return Column(Integer, primary_key=True, index=True, autoincrement=True)

    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.utcnow, nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @declared_attr
    def created_by(cls):
        return Column(String(255), nullable=False, default="system")

    @declared_attr
    def updated_by(cls):
        return Column(String(255), nullable=True)
