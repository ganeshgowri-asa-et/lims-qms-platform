# LIMS-QMS Platform - Project Structure

## Overview
AI-Powered Laboratory Information Management System (LIMS) & Quality Management System (QMS) Platform for Solar PV Testing & R&D Laboratories with ISO 17025/9001 Compliance.

## Directory Structure

```
lims-qms-platform/
│
├── backend/                        # FastAPI Backend
│   └── app/
│       ├── __init__.py
│       ├── main.py                 # FastAPI application entry point
│       ├── config.py               # Configuration settings
│       ├── database.py             # Database connection & session
│       │
│       ├── models/                 # SQLAlchemy ORM models
│       │   ├── __init__.py
│       │   ├── training.py         # Training & competency models
│       │   ├── equipment.py        # Equipment & calibration models
│       │   └── document.py         # Document management models
│       │
│       ├── schemas/                # Pydantic schemas for validation
│       │   ├── __init__.py
│       │   └── training.py         # Training request/response schemas
│       │
│       ├── api/                    # API endpoints
│       │   ├── __init__.py
│       │   └── training.py         # Training management endpoints
│       │
│       ├── services/               # Business logic layer
│       │   ├── __init__.py
│       │   ├── competency_service.py      # Competency gap analysis
│       │   ├── certificate_service.py     # Certificate generation
│       │   └── qsf_forms_service.py       # QSF forms generation
│       │
│       └── utils/                  # Utility functions
│           └── __init__.py
│
├── frontend/                       # Streamlit Frontend
│   ├── app.py                      # Main Streamlit application
│   ├── pages/                      # Multi-page app pages
│   ├── components/                 # Reusable UI components
│   └── utils/                      # Frontend utilities
│
├── database/                       # Database files
│   ├── schema.sql                  # Complete database schema
│   └── migrations/                 # Database migrations
│
├── uploads/                        # File uploads (gitignored)
│   ├── certificates/               # Generated certificates
│   ├── qsf_forms/                  # Generated QSF forms
│   └── documents/                  # Uploaded documents
│
├── assets/                         # Static assets
│   └── logo.png                    # Organization logo
│
├── tests/                          # Test files
│   ├── test_api/
│   └── test_services/
│
├── .env                            # Environment variables (gitignored)
├── .env.example                    # Example environment file
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
├── setup.sh                        # Setup script
├── run_backend.sh                  # Run backend server
├── run_frontend.sh                 # Run frontend server
├── PROJECT_STRUCTURE.md            # This file
└── README.md                       # Project documentation
```

## Module Breakdown

### Session 4: Training & Competency Management

**Database Tables:**
- `training_master` - Training program catalog
- `employee_training_matrix` - Employee training requirements
- `training_attendance` - Training attendance records
- `training_effectiveness` - Training effectiveness evaluations
- `competency_assessment` - Competency assessment records

**Features:**
1. Training program management (CRUD)
2. Employee training matrix
3. Training attendance tracking with scoring
4. Competency gap analysis
5. Auto-certificate generation (PDF with QR code)
6. QSF Forms generation:
   - QSF0203: Training Attendance Record
   - QSF0205: Training Effectiveness Evaluation
   - QSF0206: Training Needs Assessment

**API Endpoints:**
- `POST /api/training/trainings` - Create training program
- `GET /api/training/trainings` - List training programs
- `POST /api/training/matrix` - Assign training to employee
- `POST /api/training/attendance` - Record attendance
- `GET /api/training/competency-gaps` - Analyze competency gaps
- `POST /api/training/certificates/generate` - Generate certificate
- `POST /api/training/qsf/*` - Generate QSF forms

### Session 3: Equipment Calibration & Maintenance

**Database Tables:**
- `equipment_master` - Equipment registry
- `calibration_records` - Calibration history
- `preventive_maintenance_schedule` - Maintenance schedule
- `oee_tracking` - OEE metrics

**Features:**
- Auto EQP-ID generation
- Calibration due alerts (30/15/7 days)
- OEE tracking
- QR code generation

### Session 2: Document Management System

**Database Tables:**
- `qms_documents` - Document master
- `document_revisions` - Version control
- `document_distribution` - Controlled copies

**Features:**
- Auto doc numbering (QSF-YYYY-XXX)
- Version control
- Digital signatures
- Approval workflow (Doer-Checker-Approver)

## Technology Stack

**Backend:**
- FastAPI - Modern web framework
- SQLAlchemy - ORM
- PostgreSQL - Database
- Pydantic - Data validation
- ReportLab - PDF generation
- QRCode - QR code generation

**Frontend:**
- Streamlit - Interactive dashboards
- Plotly - Data visualization
- Pandas - Data manipulation

## API Documentation

Once running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Running the Application

### 1. Setup
```bash
./setup.sh
```

### 2. Configure Database
Update `.env` with your PostgreSQL credentials

### 3. Initialize Database
```bash
createdb lims_qms_db
psql lims_qms_db < database/schema.sql
```

### 4. Start Backend
```bash
./run_backend.sh
```
Backend runs on: http://localhost:8000

### 5. Start Frontend
```bash
./run_frontend.sh
```
Frontend runs on: http://localhost:8501

## Key Features Implemented

### Training Management
✅ Training program CRUD operations
✅ Employee training matrix management
✅ Training attendance with scoring
✅ Pre/post test tracking
✅ Practical assessment scoring

### Competency Management
✅ Competency gap analysis
✅ Individual development plans
✅ Department competency overview
✅ Certificate validity tracking
✅ Expiration alerts

### Certificate Generation
✅ Auto-certificate generation (PDF)
✅ QR code for verification
✅ Certificate numbering (TRN-YYYYMM-EMPID-DD)
✅ Validity period tracking
✅ Batch certificate generation

### QSF Forms
✅ QSF0203 - Training Attendance Record
✅ QSF0205 - Training Effectiveness Evaluation
✅ QSF0206 - Training Needs Assessment

### Analytics & Reporting
✅ Training statistics
✅ Competency compliance rates
✅ Gap analysis by status
✅ Department-wise reports

## Database Views

Pre-built views for common queries:
- `v_competency_gaps` - Competency gap analysis
- `v_calibration_alerts` - Equipment calibration alerts
- `v_document_status` - Document review status

## ISO Compliance

The system supports:
- ISO 17025:2017 (Testing Laboratory)
- ISO 9001:2015 (Quality Management)

Features aligned with:
- Personnel competency requirements
- Training effectiveness evaluation
- Documented information control
- Competency demonstration records
