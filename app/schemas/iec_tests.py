"""
Pydantic schemas for IEC test reports
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.iec_tests import TestStatus, TestResult, IECStandard


# ============ Test Module Schemas ============
class TestModuleCreate(BaseModel):
    manufacturer: Optional[str] = None
    model_number: Optional[str] = None
    serial_number: Optional[str] = None
    technology_type: Optional[str] = None
    rated_power_pmax: Optional[float] = None
    open_circuit_voltage_voc: Optional[float] = None
    short_circuit_current_isc: Optional[float] = None
    max_power_voltage_vmp: Optional[float] = None
    max_power_current_imp: Optional[float] = None
    efficiency: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    thickness: Optional[float] = None
    weight: Optional[float] = None
    cell_count: Optional[int] = None
    junction_box_type: Optional[str] = None
    cable_length: Optional[float] = None
    connector_type: Optional[str] = None
    frame_material: Optional[str] = None


class TestModuleResponse(TestModuleCreate):
    id: int
    report_id: int

    model_config = ConfigDict(from_attributes=True)


# ============ IEC 61215 Test Schemas ============
class IEC61215TestCreate(BaseModel):
    test_sequence: Optional[str] = None
    test_name: str
    test_clause: Optional[str] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    irradiance: Optional[float] = None
    duration: Optional[int] = None
    test_parameters: Optional[Dict[str, Any]] = None
    result: TestResult = TestResult.NOT_TESTED
    measured_values: Optional[Dict[str, Any]] = None
    acceptance_criteria: Optional[Dict[str, Any]] = None
    initial_pmax: Optional[float] = None
    final_pmax: Optional[float] = None
    power_degradation: Optional[float] = None
    visual_inspection_pass: Optional[bool] = None
    visual_defects: Optional[str] = None
    observations: Optional[str] = None
    test_date: Optional[datetime] = None


class IEC61215TestResponse(IEC61215TestCreate):
    id: int
    report_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============ IEC 61730 Test Schemas ============
class IEC61730TestCreate(BaseModel):
    test_sequence: Optional[str] = None
    test_name: str
    test_clause: Optional[str] = None
    test_class: Optional[str] = None
    application_class: Optional[str] = None
    temperature: Optional[float] = None
    voltage_applied: Optional[float] = None
    current_applied: Optional[float] = None
    test_duration: Optional[int] = None
    test_parameters: Optional[Dict[str, Any]] = None
    result: TestResult = TestResult.NOT_TESTED
    measured_values: Optional[Dict[str, Any]] = None
    acceptance_criteria: Optional[Dict[str, Any]] = None
    insulation_resistance: Optional[float] = None
    wet_leakage_current: Optional[float] = None
    dielectric_strength_pass: Optional[bool] = None
    fire_test_class: Optional[str] = None
    mechanical_load_pass: Optional[bool] = None
    impact_test_pass: Optional[bool] = None
    observations: Optional[str] = None
    test_date: Optional[datetime] = None


class IEC61730TestResponse(IEC61730TestCreate):
    id: int
    report_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============ IEC 61701 Test Schemas ============
class IEC61701TestCreate(BaseModel):
    test_name: str
    severity_level: Optional[str] = None
    salt_solution_concentration: Optional[float] = None
    chamber_temperature: Optional[float] = None
    exposure_duration: Optional[int] = None
    number_of_cycles: Optional[int] = None
    test_parameters: Optional[Dict[str, Any]] = None
    initial_pmax: Optional[float] = None
    initial_voc: Optional[float] = None
    initial_isc: Optional[float] = None
    initial_ff: Optional[float] = None
    final_pmax: Optional[float] = None
    final_voc: Optional[float] = None
    final_isc: Optional[float] = None
    final_ff: Optional[float] = None
    pmax_degradation: Optional[float] = None
    voc_degradation: Optional[float] = None
    isc_degradation: Optional[float] = None
    ff_degradation: Optional[float] = None
    result: TestResult = TestResult.NOT_TESTED
    acceptance_criteria: Optional[Dict[str, Any]] = None
    corrosion_observed: Optional[bool] = None
    corrosion_description: Optional[str] = None
    delamination_observed: Optional[bool] = None
    bubble_formation: Optional[bool] = None
    observations: Optional[str] = None
    test_date: Optional[datetime] = None


class IEC61701TestResponse(IEC61701TestCreate):
    id: int
    report_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============ Test Data Point Schemas ============
class TestDataPointCreate(BaseModel):
    timestamp: datetime
    sequence_number: Optional[int] = None
    measurements: Dict[str, Any]


class TestDataPointResponse(TestDataPointCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ============ Test Graph Schemas ============
class TestGraphResponse(BaseModel):
    id: int
    report_id: int
    graph_type: str
    title: Optional[str] = None
    description: Optional[str] = None
    file_path: str
    file_format: Optional[str] = None
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============ Test Certificate Schemas ============
class TestCertificateResponse(BaseModel):
    id: int
    report_id: int
    certificate_number: str
    issue_date: datetime
    expiry_date: Optional[datetime] = None
    qr_code_data: Optional[str] = None
    qr_code_image_path: Optional[str] = None
    signature_hash: Optional[str] = None
    signed_by: Optional[str] = None
    signing_timestamp: Optional[datetime] = None
    is_valid: bool
    revoked: bool
    verification_url: Optional[str] = None
    certificate_pdf_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ============ Test Report Schemas ============
class TestReportCreate(BaseModel):
    report_number: str = Field(..., description="Unique report number")
    customer_name: str
    customer_id: Optional[str] = None
    sample_id: str
    module_model: str
    module_serial_number: Optional[str] = None
    iec_standard: IECStandard
    test_type: str
    test_objective: Optional[str] = None
    tested_by: Optional[str] = None
    test_start_date: Optional[datetime] = None
    remarks: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TestReportUpdate(BaseModel):
    customer_name: Optional[str] = None
    module_model: Optional[str] = None
    status: Optional[TestStatus] = None
    overall_result: Optional[TestResult] = None
    tested_by: Optional[str] = None
    reviewed_by: Optional[str] = None
    approved_by: Optional[str] = None
    test_end_date: Optional[datetime] = None
    remarks: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TestReportResponse(BaseModel):
    id: int
    report_number: str
    customer_name: str
    customer_id: Optional[str] = None
    sample_id: str
    module_model: str
    module_serial_number: Optional[str] = None
    iec_standard: IECStandard
    test_type: str
    test_objective: Optional[str] = None
    status: TestStatus
    overall_result: TestResult
    tested_by: Optional[str] = None
    reviewed_by: Optional[str] = None
    approved_by: Optional[str] = None
    test_start_date: Optional[datetime] = None
    test_end_date: Optional[datetime] = None
    report_date: datetime
    created_at: datetime
    updated_at: datetime
    remarks: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    # Related data
    test_modules: List[TestModuleResponse] = []
    iec_61215_tests: List[IEC61215TestResponse] = []
    iec_61730_tests: List[IEC61730TestResponse] = []
    iec_61701_tests: List[IEC61701TestResponse] = []
    graphs: List[TestGraphResponse] = []
    certificate: Optional[TestCertificateResponse] = None

    model_config = ConfigDict(from_attributes=True)


# ============ Bulk Test Execution Schemas ============
class TestExecutionRequest(BaseModel):
    report_id: int
    test_data_points: List[TestDataPointCreate]
    auto_evaluate: bool = True


class TestExecutionResponse(BaseModel):
    report_id: int
    status: str
    tests_executed: int
    data_points_recorded: int
    evaluation_results: Optional[Dict[str, Any]] = None
