"""
Notification model
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, JSON
from .base import BaseModel


class Notification(BaseModel):
    """Notification model for user alerts"""
    __tablename__ = 'notifications'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(100), nullable=True)  # info, warning, error, success
    category = Column(String(100), nullable=True)  # task, approval, calibration, audit, etc.
    is_read = Column(Boolean, default=False)
    read_at = Column(String(255), nullable=True)
    link = Column(String(500), nullable=True)  # Link to related entity
    metadata = Column(JSON, nullable=True)
    priority = Column(String(50), default='normal')  # low, normal, high
