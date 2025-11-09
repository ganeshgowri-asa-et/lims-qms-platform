"""
IEC Test Report Generation Models (Session 6)
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Date, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.core.database import Base


class IECTestExecution(Base):
    """IEC test execution tracking"""
    __tablename__ = "iec_test_execution"

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=False)
    test_standard = Column(String(50), nullable=False)  # IEC61215, IEC61730, IEC61701
    test_sequence = Column(String(100))  # MST10.1, MST10.2, etc.
    test_description = Column(String(200))
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    status = Column(String(50))  # in_progress, completed
    performed_by_id = Column(Integer, ForeignKey("users.id"))
    reviewed_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    test_data = relationship("IECTestData", back_populates="test_execution")


class IECTestData(Base):
    """IEC test data points"""
    __tablename__ = "iec_test_data"

    id = Column(Integer, primary_key=True, index=True)
    test_execution_id = Column(Integer, ForeignKey("iec_test_execution.id"), nullable=False)
    measurement_time = Column(DateTime(timezone=True), nullable=False)
    parameter_name = Column(String(100), nullable=False)
    measured_value = Column(Float)
    unit = Column(String(50))
    acceptance_min = Column(Float)
    acceptance_max = Column(Float)
    result = Column(String(50))  # Pass/Fail
    remarks = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    test_execution = relationship("IECTestExecution", back_populates="test_data")


class IECReport(Base):
    """Generated IEC test reports"""
    __tablename__ = "iec_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_number = Column(String(100), unique=True, nullable=False, index=True)
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=False)
    test_standard = Column(String(50), nullable=False)
    report_date = Column(Date, nullable=False)
    overall_result = Column(String(50))  # Pass/Fail
    test_summary = Column(JSON)  # JSON summary of all tests
    graphs_generated = Column(JSON)  # List of graph file paths
    report_file_path = Column(String(500))
    certificate_file_path = Column(String(500))
    qr_code_path = Column(String(500))
    digital_signature = Column(Text)
    generated_by_id = Column(Integer, ForeignKey("users.id"))
    approved_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
