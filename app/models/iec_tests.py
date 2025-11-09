"""
IEC Test Models for Solar PV Module Testing
"""
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Boolean,
    Text, JSON, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class TestStatus(str, enum.Enum):
    """Test execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TestResult(str, enum.Enum):
    """Test pass/fail result"""
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL = "conditional"
    NOT_TESTED = "not_tested"


class IECStandard(str, enum.Enum):
    """IEC test standards"""
    IEC_61215 = "IEC 61215"
    IEC_61730 = "IEC 61730"
    IEC_61701 = "IEC 61701"


class TestReport(Base):
    """Main test report table"""
    __tablename__ = "test_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_number = Column(String(50), unique=True, nullable=False, index=True)

    # Customer & Sample Info
    customer_name = Column(String(200), nullable=False)
    customer_id = Column(String(50))
    sample_id = Column(String(50), nullable=False)
    module_model = Column(String(200), nullable=False)
    module_serial_number = Column(String(100))

    # Test Info
    iec_standard = Column(SQLEnum(IECStandard), nullable=False)
    test_type = Column(String(100), nullable=False)
    test_objective = Column(Text)

    # Status & Results
    status = Column(SQLEnum(TestStatus), default=TestStatus.PENDING)
    overall_result = Column(SQLEnum(TestResult), default=TestResult.NOT_TESTED)

    # Personnel
    tested_by = Column(String(100))
    reviewed_by = Column(String(100))
    approved_by = Column(String(100))

    # Dates
    test_start_date = Column(DateTime)
    test_end_date = Column(DateTime)
    report_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Additional Info
    remarks = Column(Text)
    metadata = Column(JSON)  # Store additional flexible data

    # Relationships
    test_modules = relationship("TestModule", back_populates="report", cascade="all, delete-orphan")
    iec_61215_tests = relationship("IEC61215Test", back_populates="report", cascade="all, delete-orphan")
    iec_61730_tests = relationship("IEC61730Test", back_populates="report", cascade="all, delete-orphan")
    iec_61701_tests = relationship("IEC61701Test", back_populates="report", cascade="all, delete-orphan")
    graphs = relationship("TestGraph", back_populates="report", cascade="all, delete-orphan")
    certificate = relationship("TestCertificate", back_populates="report", uselist=False, cascade="all, delete-orphan")


class TestModule(Base):
    """PV Module specifications and characteristics"""
    __tablename__ = "test_modules"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("test_reports.id"), nullable=False)

    # Module Specifications
    manufacturer = Column(String(200))
    model_number = Column(String(100))
    serial_number = Column(String(100))
    technology_type = Column(String(100))  # Mono-Si, Poly-Si, Thin-Film, etc.

    # Electrical Characteristics (STC)
    rated_power_pmax = Column(Float)  # Watts
    open_circuit_voltage_voc = Column(Float)  # Volts
    short_circuit_current_isc = Column(Float)  # Amperes
    max_power_voltage_vmp = Column(Float)  # Volts
    max_power_current_imp = Column(Float)  # Amperes
    efficiency = Column(Float)  # Percentage

    # Physical Characteristics
    length = Column(Float)  # mm
    width = Column(Float)  # mm
    thickness = Column(Float)  # mm
    weight = Column(Float)  # kg
    cell_count = Column(Integer)

    # Additional Info
    junction_box_type = Column(String(100))
    cable_length = Column(Float)  # meters
    connector_type = Column(String(100))
    frame_material = Column(String(100))

    # Relationships
    report = relationship("TestReport", back_populates="test_modules")


class IEC61215Test(Base):
    """IEC 61215: Design qualification and type approval tests"""
    __tablename__ = "iec_61215_tests"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("test_reports.id"), nullable=False)

    # Test Identification
    test_sequence = Column(String(20))  # e.g., "MST 01", "MST 23"
    test_name = Column(String(200), nullable=False)
    test_clause = Column(String(20))  # IEC clause reference

    # Test Conditions
    temperature = Column(Float)  # Celsius
    humidity = Column(Float)  # Percentage
    irradiance = Column(Float)  # W/m²
    duration = Column(Integer)  # Hours or cycles

    # Test Parameters (JSON for flexibility)
    test_parameters = Column(JSON)

    # Results
    result = Column(SQLEnum(TestResult), default=TestResult.NOT_TESTED)
    measured_values = Column(JSON)
    acceptance_criteria = Column(JSON)

    # Power Measurements
    initial_pmax = Column(Float)
    final_pmax = Column(Float)
    power_degradation = Column(Float)  # Percentage

    # Visual Inspection
    visual_inspection_pass = Column(Boolean)
    visual_defects = Column(Text)

    # Additional Data
    observations = Column(Text)
    data_file_path = Column(String(500))

    # Timestamps
    test_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    report = relationship("TestReport", back_populates="iec_61215_tests")
    data_points = relationship("TestDataPoint", back_populates="iec_61215_test", cascade="all, delete-orphan")


class IEC61730Test(Base):
    """IEC 61730: PV module safety qualification tests"""
    __tablename__ = "iec_61730_tests"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("test_reports.id"), nullable=False)

    # Test Identification
    test_sequence = Column(String(20))  # e.g., "MST 01", "MST 50"
    test_name = Column(String(200), nullable=False)
    test_clause = Column(String(20))

    # Safety Test Specific
    test_class = Column(String(20))  # Class A, Class B, Class C
    application_class = Column(String(20))  # Application class

    # Test Conditions
    temperature = Column(Float)
    voltage_applied = Column(Float)  # Volts
    current_applied = Column(Float)  # Amperes
    test_duration = Column(Integer)  # Minutes

    # Test Parameters
    test_parameters = Column(JSON)

    # Results
    result = Column(SQLEnum(TestResult), default=TestResult.NOT_TESTED)
    measured_values = Column(JSON)
    acceptance_criteria = Column(JSON)

    # Safety Measurements
    insulation_resistance = Column(Float)  # MΩ
    wet_leakage_current = Column(Float)  # mA
    dielectric_strength_pass = Column(Boolean)

    # Fire & Mechanical Safety
    fire_test_class = Column(String(10))
    mechanical_load_pass = Column(Boolean)
    impact_test_pass = Column(Boolean)

    # Additional Data
    observations = Column(Text)
    data_file_path = Column(String(500))

    # Timestamps
    test_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    report = relationship("TestReport", back_populates="iec_61730_tests")
    data_points = relationship("TestDataPoint", back_populates="iec_61730_test", cascade="all, delete-orphan")


class IEC61701Test(Base):
    """IEC 61701: Salt mist corrosion testing"""
    __tablename__ = "iec_61701_tests"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("test_reports.id"), nullable=False)

    # Test Identification
    test_name = Column(String(200), nullable=False)
    severity_level = Column(String(20))  # Level 1-6

    # Test Conditions
    salt_solution_concentration = Column(Float)  # g/L (typically 5%)
    chamber_temperature = Column(Float)  # Celsius (typically 35°C)
    exposure_duration = Column(Integer)  # Hours
    number_of_cycles = Column(Integer)

    # Test Parameters
    test_parameters = Column(JSON)

    # Pre-test Measurements
    initial_pmax = Column(Float)
    initial_voc = Column(Float)
    initial_isc = Column(Float)
    initial_ff = Column(Float)  # Fill factor

    # Post-test Measurements
    final_pmax = Column(Float)
    final_voc = Column(Float)
    final_isc = Column(Float)
    final_ff = Column(Float)

    # Degradation
    pmax_degradation = Column(Float)  # Percentage
    voc_degradation = Column(Float)
    isc_degradation = Column(Float)
    ff_degradation = Column(Float)

    # Results
    result = Column(SQLEnum(TestResult), default=TestResult.NOT_TESTED)
    acceptance_criteria = Column(JSON)

    # Visual Inspection
    corrosion_observed = Column(Boolean)
    corrosion_description = Column(Text)
    delamination_observed = Column(Boolean)
    bubble_formation = Column(Boolean)

    # Additional Data
    observations = Column(Text)
    data_file_path = Column(String(500))

    # Timestamps
    test_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    report = relationship("TestReport", back_populates="iec_61701_tests")
    data_points = relationship("TestDataPoint", back_populates="iec_61701_test", cascade="all, delete-orphan")


class TestDataPoint(Base):
    """Time-series data points for test measurements"""
    __tablename__ = "test_data_points"

    id = Column(Integer, primary_key=True, index=True)

    # Link to specific test type
    iec_61215_test_id = Column(Integer, ForeignKey("iec_61215_tests.id"), nullable=True)
    iec_61730_test_id = Column(Integer, ForeignKey("iec_61730_tests.id"), nullable=True)
    iec_61701_test_id = Column(Integer, ForeignKey("iec_61701_tests.id"), nullable=True)

    # Data Point Info
    timestamp = Column(DateTime, nullable=False)
    sequence_number = Column(Integer)

    # Measurement Data (flexible JSON structure)
    measurements = Column(JSON, nullable=False)
    # Example: {"voltage": 45.2, "current": 9.8, "power": 442.96, "temperature": 25.0}

    # Relationships
    iec_61215_test = relationship("IEC61215Test", back_populates="data_points")
    iec_61730_test = relationship("IEC61730Test", back_populates="data_points")
    iec_61701_test = relationship("IEC61701Test", back_populates="data_points")


class TestGraph(Base):
    """Generated graphs for test reports"""
    __tablename__ = "test_graphs"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("test_reports.id"), nullable=False)

    # Graph Info
    graph_type = Column(String(100), nullable=False)  # IV_Curve, Power_Curve, Temperature_Profile, etc.
    title = Column(String(200))
    description = Column(Text)

    # File Info
    file_path = Column(String(500), nullable=False)
    file_format = Column(String(20))  # png, pdf, svg

    # Graph Configuration
    x_axis_label = Column(String(100))
    y_axis_label = Column(String(100))
    graph_config = Column(JSON)  # Store matplotlib/plotly config

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    report = relationship("TestReport", back_populates="graphs")


class TestCertificate(Base):
    """Digital test certificates with QR codes"""
    __tablename__ = "test_certificates"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("test_reports.id"), nullable=False, unique=True)

    # Certificate Info
    certificate_number = Column(String(100), unique=True, nullable=False, index=True)
    issue_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime)

    # QR Code
    qr_code_data = Column(Text)  # URL or JSON data encoded in QR
    qr_code_image_path = Column(String(500))

    # Digital Signature
    signature_hash = Column(String(256))  # SHA-256 hash
    signature_data = Column(Text)  # Encrypted signature
    signed_by = Column(String(100))
    signing_timestamp = Column(DateTime)

    # Certificate Status
    is_valid = Column(Boolean, default=True)
    revoked = Column(Boolean, default=False)
    revocation_date = Column(DateTime)
    revocation_reason = Column(Text)

    # PDF
    certificate_pdf_path = Column(String(500))

    # Verification
    verification_url = Column(String(500))
    verification_count = Column(Integer, default=0)
    last_verified_at = Column(DateTime)

    # Relationships
    report = relationship("TestReport", back_populates="certificate")
