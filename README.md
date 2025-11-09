# 🔬 LIMS-QMS Platform

AI-Powered Laboratory Information Management System (LIMS) & Quality Management System (QMS) Platform for Solar PV Testing & R&D Laboratories - Complete Digital Transformation with ISO 17025/9001 Compliance

## 🎯 SESSION 6: IEC Test Report Generation System

This implementation provides a comprehensive **IEC Test Report Generation** system supporting:
- **IEC 61215**: Terrestrial PV modules - Design qualification and type approval
- **IEC 61730**: PV module safety qualification
- **IEC 61701**: Salt mist corrosion testing

### ✨ Key Features

- ✅ **Test Data Acquisition**: Real-time data collection and storage
- ✅ **Automated Graph Generation**: I-V curves, P-V curves, temperature profiles, degradation charts
- ✅ **Pass/Fail Criteria Evaluation**: Automated compliance checking against IEC standards
- ✅ **PDF Report Generation**: Professional test reports with graphs and signatures
- ✅ **Digital Certificates**: QR-coded certificates with digital signatures
- ✅ **Certificate Verification**: Online verification portal with QR code scanning

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Start all services with Docker Compose
docker-compose up -d

# Access the application
# API: http://localhost:8000
# UI:  http://localhost:8501
```

### Option 2: Local Installation

```bash
# Clone the repository
git clone <repository-url>
cd lims-qms-platform

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run the application
./run.sh  # Linux/Mac
# or
run.bat   # Windows
```

## 📚 Documentation

- **[Implementation Guide](README_IMPLEMENTATION.md)** - Detailed technical documentation
- **[Docker Setup](DOCKER_SETUP.md)** - Docker deployment guide
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running)

## 🏗️ Architecture

```
lims-qms-platform/
├── app/                          # FastAPI Application
│   ├── main.py                  # Main application entry
│   ├── config.py                # Configuration management
│   ├── database.py              # Database connection
│   ├── models/                  # SQLAlchemy models
│   │   └── iec_tests.py        # IEC test data models
│   ├── schemas/                 # Pydantic schemas
│   │   └── iec_tests.py        # API request/response schemas
│   ├── api/                     # API endpoints
│   │   └── iec_tests.py        # IEC test API routes
│   ├── services/                # Business logic
│   │   ├── test_execution.py   # Test workflow orchestration
│   │   ├── graph_generator.py  # Graph generation service
│   │   ├── pass_fail_evaluator.py  # Criteria evaluation
│   │   ├── report_generator.py # PDF report generation
│   │   └── certificate_generator.py  # Digital certificates
│   └── utils/                   # Utilities
│       ├── qr_generator.py     # QR code generation
│       └── digital_signature.py # Digital signing
├── streamlit_app/               # Streamlit UI
│   ├── main.py                 # Dashboard
│   └── pages/                  # UI pages
│       ├── 1_Test_Execution.py
│       ├── 2_Report_Generation.py
│       └── 3_Test_History.py
├── reports/                     # Generated reports
│   ├── pdf/                    # PDF reports
│   ├── graphs/                 # Generated graphs
│   └── certificates/           # Digital certificates
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Multi-container setup
└── README.md                   # This file
```

## 🔧 Technology Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Frontend**: Streamlit
- **Database**: PostgreSQL
- **Graphs**: Matplotlib, Plotly
- **Reports**: ReportLab (PDF generation)
- **Security**: Cryptography (digital signatures)
- **QR Codes**: python-qrcode

## 📊 API Endpoints

### Test Reports
- `POST /api/v1/iec-tests/reports` - Create test report
- `GET /api/v1/iec-tests/reports` - List all reports
- `GET /api/v1/iec-tests/reports/{id}` - Get specific report
- `PUT /api/v1/iec-tests/reports/{id}` - Update report
- `DELETE /api/v1/iec-tests/reports/{id}` - Delete report

### Test Execution
- `POST /api/v1/iec-tests/reports/{id}/iec-61215-tests` - Add IEC 61215 test
- `POST /api/v1/iec-tests/reports/{id}/iec-61730-tests` - Add IEC 61730 test
- `POST /api/v1/iec-tests/reports/{id}/iec-61701-tests` - Add IEC 61701 test
- `POST /api/v1/iec-tests/tests/{type}/{id}/data-points` - Record data points
- `POST /api/v1/iec-tests/tests/{type}/{id}/evaluate` - Evaluate test

### Report Generation
- `POST /api/v1/iec-tests/reports/{id}/graphs` - Generate graphs
- `POST /api/v1/iec-tests/reports/{id}/generate-pdf` - Generate PDF report
- `POST /api/v1/iec-tests/reports/{id}/generate-certificate` - Generate certificate

## 🧪 Usage Example

```python
import requests

# Create test report
report = requests.post("http://localhost:8000/api/v1/iec-tests/reports", json={
    "report_number": "RPT-20241109-001",
    "customer_name": "Solar Energy Corp",
    "sample_id": "SAMPLE-001",
    "module_model": "PV-300W-Mono",
    "iec_standard": "IEC 61215",
    "test_type": "Design Qualification"
}).json()

# Add test
requests.post(f"http://localhost:8000/api/v1/iec-tests/reports/{report['id']}/iec-61215-tests", json={
    "test_name": "Thermal Cycling",
    "initial_pmax": 300.0,
    "final_pmax": 295.0,
    "visual_inspection_pass": True
})

# Generate report
pdf = requests.post(f"http://localhost:8000/api/v1/iec-tests/reports/{report['id']}/generate-pdf")

# Generate certificate
cert = requests.post(f"http://localhost:8000/api/v1/iec-tests/reports/{report['id']}/generate-certificate")
```

## 🎓 IEC Standards Compliance

### IEC 61215 - Design Qualification
- Visual inspection
- Maximum power determination
- Insulation testing
- Temperature coefficients
- Thermal cycling (≤5% degradation)

### IEC 61730 - Safety Qualification
- Insulation resistance (wet/dry)
- Wet leakage current
- Dielectric strength
- Mechanical and impact tests

### IEC 61701 - Salt Mist Testing
- Corrosion resistance (6 severity levels)
- Power degradation monitoring
- Visual defect detection

## 🤝 Contributing

This is SESSION 6 of the LIMS-QMS Platform implementation. Previous sessions covered:
- SESSION 2: Document Management System
- SESSION 3: Equipment Calibration & Maintenance
- SESSION 4: Training & Competency
- SESSION 5: Test Request & Sample Management

## 📄 License

MIT License - See LICENSE file for details

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the [Implementation Guide](README_IMPLEMENTATION.md)
- Review [API Documentation](http://localhost:8000/docs)

---

**Built for Solar PV Testing Laboratories** | ISO/IEC 17025:2017 Compliant | Version 1.0.0