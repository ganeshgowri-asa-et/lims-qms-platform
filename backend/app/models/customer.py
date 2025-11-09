"""
Customer model for LIMS/QMS platform
"""
from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import BaseModel


class Customer(Base, BaseModel):
    """Customer master table"""
    __tablename__ = "customers"

    customer_code = Column(String(50), unique=True, nullable=False, index=True)
    customer_name = Column(String(255), nullable=False)
    customer_type = Column(String(50), nullable=False)  # internal, external, government, academic

    # Contact Information
    contact_person = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    mobile = Column(String(50), nullable=True)

    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True, default="India")

    # Additional Info
    gst_number = Column(String(50), nullable=True)
    pan_number = Column(String(20), nullable=True)
    remarks = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    test_requests = relationship("TestRequest", back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Customer {self.customer_code}: {self.customer_name}>"
