# SESSION 6: IEC Test Report Generation - Implementation Guide

## Overview

This implementation provides a comprehensive IEC Test Report Generation system for Solar PV module testing laboratories. The system supports IEC 61215, 61730, and 61701 standards with automated test execution, data acquisition, graph generation, pass/fail evaluation, and digital certificate generation.

## Features Implemented

### 1. **Database Schema** ✅
- **Test Reports**: Main test report table with customer and sample information
- **Test Modules**: PV module specifications and electrical characteristics
- **IEC 61215 Tests**: Design qualification and type approval tests
- **IEC 61730 Tests**: Safety qualification tests
- **IEC 61701 Tests**: Salt mist corrosion tests
- **Test Data Points**: Time-series measurement data
- **Test Graphs**: Generated graph metadata
- **Test Certificates**: Digital certificates with QR codes

### 2. **Core Services** ✅

#### Graph Generator (`app/services/graph_generator.py`)
- I-V characteristic curves
- P-V power curves
- Temperature profiles
- Degradation analysis charts
- Interactive Plotly graphs
- Comparison charts

#### Pass/Fail Evaluator (`app/services/pass_fail_evaluator.py`)
- IEC 61215 criteria evaluation
- IEC 61730 safety criteria
- IEC 61701 degradation criteria
- Automated test sequence evaluation
- Degradation calculation

#### Report Generator (`app/services/report_generator.py`)
- Professional PDF reports with ReportLab
- Custom styling and branding
- Multi-page reports with graphs
- Module specifications tables
- Test results tables
- Signature sections

#### Certificate Generator (`app/services/certificate_generator.py`)
- Digital certificates with QR codes
- Certificate numbering system
- Validity period management
- Digital signatures
- Online verification URLs

#### Test Execution Service (`app/services/test_execution.py`)
- End-to-end test workflow
- Data point recording
- Graph generation orchestration
- Report PDF generation
- Certificate issuance

### 3. **Utilities** ✅

#### QR Code Generator (`app/utils/qr_generator.py`)
- High-quality QR code generation
- Styled QR codes with rounded modules
- Certificate verification encoding
- Multiple size and format options

#### Digital Signature (`app/utils/digital_signature.py`)
- RSA key pair generation
- Data signing and verification
- SHA-256 hashing
- Certificate data integrity

### 4. **API Endpoints** ✅

All endpoints are RESTful and documented:

```
POST   /api/v1/iec-tests/reports                    # Create test report
GET    /api/v1/iec-tests/reports                    # List all reports
GET    /api/v1/iec-tests/reports/{id}               # Get specific report
PUT    /api/v1/iec-tests/reports/{id}               # Update report
DELETE /api/v1/iec-tests/reports/{id}               # Delete report

POST   /api/v1/iec-tests/reports/{id}/modules       # Add module specs
POST   /api/v1/iec-tests/reports/{id}/iec-61215-tests
POST   /api/v1/iec-tests/reports/{id}/iec-61730-tests
POST   /api/v1/iec-tests/reports/{id}/iec-61701-tests

POST   /api/v1/iec-tests/tests/{type}/{id}/data-points
POST   /api/v1/iec-tests/tests/{type}/{id}/evaluate
POST   /api/v1/iec-tests/reports/{id}/graphs
POST   /api/v1/iec-tests/reports/{id}/generate-pdf
POST   /api/v1/iec-tests/reports/{id}/generate-certificate
```

### 5. **Streamlit UI** ✅

#### Main Dashboard (`streamlit_app/main.py`)
- System overview
- Quick statistics
- Feature summary
- System status monitoring

#### Test Execution Page (`streamlit_app/pages/1_Test_Execution.py`)
- Create test reports
- Configure test parameters
- Execute test sequences
- View real-time results
- Generate reports and certificates

#### Report Generation Page (`streamlit_app/pages/2_Report_Generation.py`)
- PDF report generation
- Digital certificate creation
- Graph generation
- Batch operations
- Download capabilities

#### Test History Page (`streamlit_app/pages/3_Test_History.py`)
- Search and filter tests
- View historical records
- Analytics and statistics
- Export to CSV/Excel
- Activity timeline

## Installation & Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- pip

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/lims_qms
LAB_NAME=Your Lab Name
LAB_ADDRESS=Your Lab Address
LAB_ACCREDITATION=ISO/IEC 17025:2017
```

### Step 3: Initialize Database

```bash
# Create database
createdb lims_qms

# Initialize tables (auto-created on first run)
python -c "from app.database import init_db; init_db()"
```

### Step 4: Run the Application

#### Start API Server

```bash
python -m app.main
# or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Start Streamlit UI

```bash
streamlit run streamlit_app/main.py
```

## Usage Examples

### 1. Create Test Report via API

```python
import requests

report_data = {
    "report_number": "RPT-20241109-001",
    "customer_name": "Solar Energy Corp",
    "sample_id": "SAMPLE-001",
    "module_model": "PV-300W-Mono",
    "iec_standard": "IEC 61215",
    "test_type": "Design Qualification",
    "tested_by": "John Doe"
}

response = requests.post(
    "http://localhost:8000/api/v1/iec-tests/reports",
    json=report_data
)

report = response.json()
print(f"Created report ID: {report['id']}")
```

### 2. Add Test Module Specifications

```python
module_data = {
    "manufacturer": "SolarTech Inc",
    "technology_type": "Mono-Si",
    "rated_power_pmax": 300.0,
    "open_circuit_voltage_voc": 45.5,
    "short_circuit_current_isc": 9.2,
    "efficiency": 19.5
}

requests.post(
    f"http://localhost:8000/api/v1/iec-tests/reports/{report_id}/modules",
    json=module_data
)
```

### 3. Execute IEC 61215 Test

```python
test_data = {
    "test_name": "MST 23 - Thermal Cycling",
    "temperature": 25.0,
    "initial_pmax": 300.0,
    "final_pmax": 295.0,
    "power_degradation": 1.67,
    "visual_inspection_pass": True,
    "result": "NOT_TESTED"
}

requests.post(
    f"http://localhost:8000/api/v1/iec-tests/reports/{report_id}/iec-61215-tests",
    json=test_data
)
```

### 4. Generate Graphs

```python
graph_configs = [{
    "graph_type": "iv_curve",
    "title": "I-V Characteristic Curve",
    "data": {
        "voltage": [0, 10, 20, 30, 40, 45.5],
        "current": [9.2, 9.1, 8.8, 8.2, 6.5, 0]
    }
}]

requests.post(
    f"http://localhost:8000/api/v1/iec-tests/reports/{report_id}/graphs",
    json=graph_configs
)
```

### 5. Generate PDF Report

```python
response = requests.post(
    f"http://localhost:8000/api/v1/iec-tests/reports/{report_id}/generate-pdf"
)

result = response.json()
print(f"PDF generated: {result['pdf_path']}")
```

### 6. Generate Digital Certificate

```python
response = requests.post(
    f"http://localhost:8000/api/v1/iec-tests/reports/{report_id}/generate-certificate"
)

certificate = response.json()
print(f"Certificate: {certificate['certificate_number']}")
print(f"QR Code: {certificate['qr_code_image_path']}")
print(f"Verify at: {certificate['verification_url']}")
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit UI Layer                       │
│  (Test Execution, Report Generation, Test History)          │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
┌──────────────────────┴──────────────────────────────────────┐
│                    FastAPI Application                       │
│                   (API Endpoints Layer)                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                   Business Logic Layer                       │
│  ┌────────────────┐ ┌─────────────────┐ ┌────────────────┐ │
│  │ Test Execution │ │ Graph Generator │ │ Pass/Fail Eval │ │
│  └────────────────┘ └─────────────────┘ └────────────────┘ │
│  ┌────────────────┐ ┌─────────────────┐                    │
│  │ Report Gen     │ │ Certificate Gen │                    │
│  └────────────────┘ └─────────────────┘                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                   Data Access Layer                          │
│              (SQLAlchemy ORM + Models)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                  PostgreSQL Database                         │
│   (Test Reports, Modules, Tests, Data Points, Certs)        │
└─────────────────────────────────────────────────────────────┘
```

## Key Technologies

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **Streamlit**: Web app framework for data science
- **Matplotlib/Plotly**: Graph generation
- **ReportLab**: PDF generation
- **Cryptography**: Digital signatures
- **QRCode**: QR code generation
- **PostgreSQL**: Relational database

## IEC Standards Compliance

### IEC 61215
- Design qualification tests
- Power degradation monitoring (≤5%)
- Visual inspection
- Insulation resistance
- Temperature coefficients

### IEC 61730
- Safety qualification
- Insulation resistance (wet/dry)
- Wet leakage current
- Dielectric strength
- Mechanical and impact tests

### IEC 61701
- Salt mist corrosion resistance
- Severity levels 1-6
- Power degradation limits
- Visual defect detection
- Corrosion, delamination, bubbles

## Future Enhancements

1. **Real-time Data Acquisition**: Integration with test equipment (via SCPI, Modbus, etc.)
2. **Advanced Analytics**: ML-based prediction of test outcomes
3. **Workflow Automation**: Automated test sequencing
4. **Multi-user Support**: Role-based access control
5. **Cloud Deployment**: AWS/Azure deployment with S3 storage
6. **Mobile App**: React Native app for field testing
7. **Integration**: Connect with existing ERP/LIMS systems

## Testing

Run unit tests:
```bash
pytest tests/
```

## Support & Documentation

- API Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Streamlit UI: http://localhost:8501

## License

MIT License - See LICENSE file

## Author

Implemented for SESSION 6: IEC Test Report Generation
Part of the LIMS-QMS Platform for Solar PV Testing Laboratories
