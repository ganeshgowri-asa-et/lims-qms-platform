"""
Test Parameter model for LIMS/QMS platform
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Numeric, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import BaseModel


class TestParameter(Base, BaseModel):
    """Test Parameters for each test request"""
    __tablename__ = "test_parameters"

    # Test Request Reference
    test_request_id = Column(Integer, ForeignKey("test_requests.id"), nullable=False)

    # Parameter Details
    parameter_name = Column(String(255), nullable=False)
    parameter_code = Column(String(50), nullable=True)
    test_method = Column(String(255), nullable=True)
    specification = Column(String(255), nullable=True)

    # Testing Details
    unit_of_measurement = Column(String(50), nullable=True)
    acceptance_criteria = Column(Text, nullable=True)

    # Results
    result = Column(String(255), nullable=True)
    numeric_result = Column(Numeric(10, 4), nullable=True)
    pass_fail = Column(String(20), nullable=True)  # Pass, Fail, NA

    # Analysis Details
    analyzed_by = Column(String(255), nullable=True)
    analyzed_date = Column(String(50), nullable=True)
    verified_by = Column(String(255), nullable=True)
    verified_date = Column(String(50), nullable=True)

    # Pricing
    unit_price = Column(Numeric(10, 2), nullable=True)
    quantity = Column(Integer, default=1, nullable=False)
    total_price = Column(Numeric(10, 2), nullable=True)

    # Status
    is_completed = Column(Boolean, default=False, nullable=False)

    # Remarks
    remarks = Column(Text, nullable=True)

    # Relationships
    test_request = relationship("TestRequest", back_populates="test_parameters")

    def __repr__(self):
        return f"<TestParameter {self.parameter_name}>"
