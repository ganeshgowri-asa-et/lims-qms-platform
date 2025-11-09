# LIMS & QMS Platform

AI-Powered Laboratory Information Management System (LIMS) & Quality Management System (QMS) Platform for Solar PV Testing & R&D Laboratories - Complete Digital Transformation with ISO 17025/9001 Compliance

## 🚀 Features

### 📄 Document Management System (SESSION 2)

Complete QMS document control system with:

#### Database Tables
- **qms_documents**: Master document records with auto-numbering
- **document_revisions**: Complete revision history tracking
- **document_distribution**: Controlled copy distribution management

#### Key Features
- ✅ **Auto Document Numbering**: QSF-YYYY-XXX format
- ✅ **Version Control**: Major.Minor versioning system (e.g., 2.1)
- ✅ **Digital Signatures**: Built-in signature tracking
- ✅ **Approval Workflow**: Doer → Checker → Approver workflow
- ✅ **Full-text Search**: Search across titles, content, and keywords
- ✅ **PDF Generation**: Automatic PDF creation with watermarks
- ✅ **Document Types**: Procedures, Forms, Policies, Manuals, Work Instructions, Specifications, Records
- ✅ **Status Tracking**: Draft → Pending Review → Pending Approval → Approved → Obsolete

#### API Endpoints
- `POST /api/v1/documents/` - Create new document
- `GET /api/v1/documents/` - List all documents
- `GET /api/v1/documents/{id}` - Get document details
- `PUT /api/v1/documents/{id}` - Update document
- `POST /api/v1/documents/{id}/revise` - Create revision
- `POST /api/v1/documents/{id}/approve` - Approve document
- `GET /api/v1/documents/search/` - Search documents

### 🔧 Equipment Calibration & Maintenance (SESSION 3)

Complete equipment lifecycle management with:

#### Database Tables
- **equipment_master**: Equipment master data with auto-ID
- **calibration_records**: Calibration history and certificates
- **preventive_maintenance_schedule**: Maintenance planning and tracking

#### Key Features
- ✅ **Auto Equipment ID**: EQP-YYYY-XXXX format
- ✅ **Calibration Due Alerts**: 30/15/7 day advance notifications
- ✅ **OEE Tracking**: Overall Equipment Effectiveness monitoring
- ✅ **QR Code Generation**: Automatic QR codes for equipment identification
- ✅ **Calibration Management**: Complete calibration lifecycle tracking
- ✅ **Preventive Maintenance**: Scheduled maintenance planning
- ✅ **Equipment Status**: Operational, Under Calibration, Under Maintenance, Out of Service, Retired
- ✅ **Traceability**: Full calibration chain traceability

#### API Endpoints
- `POST /api/v1/equipment/` - Create equipment
- `GET /api/v1/equipment/` - List equipment
- `GET /api/v1/equipment/{id}` - Get equipment details
- `PUT /api/v1/equipment/{id}` - Update equipment
- `POST /api/v1/equipment/{id}/calibration` - Record calibration
- `POST /api/v1/equipment/{id}/maintenance` - Schedule maintenance
- `GET /api/v1/equipment/alerts/calibration` - Get calibration alerts
- `POST /api/v1/equipment/{id}/calculate-oee` - Calculate OEE
- `POST /api/v1/equipment/{id}/generate-qr` - Generate QR code

## 🏗️ Architecture

```
lims-qms-platform/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   │   └── v1/
│   │   │       └── endpoints/
│   │   │           ├── documents.py    # Document endpoints
│   │   │           └── equipment.py    # Equipment endpoints
│   │   ├── core/              # Core configuration
│   │   │   ├── config.py      # Settings
│   │   │   └── database.py    # Database setup
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── documents.py   # Document models
│   │   │   └── equipment.py   # Equipment models
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── documents.py   # Document schemas
│   │   │   └── equipment.py   # Equipment schemas
│   │   ├── services/          # Business logic
│   │   │   ├── document_service.py
│   │   │   └── equipment_service.py
│   │   ├── utils/             # Utilities
│   │   │   ├── pdf_generator.py    # PDF generation
│   │   │   └── qr_generator.py     # QR code generation
│   │   └── main.py            # FastAPI app
│   └── run.py                 # Run script
├── frontend/                   # Streamlit Frontend
│   ├── pages/
│   │   ├── 1_📄_Documents.py  # Document management UI
│   │   └── 2_🔧_Equipment.py  # Equipment management UI
│   ├── utils/
│   │   └── api_client.py      # API client
│   └── app.py                 # Main app
├── scripts/                    # Utility scripts
│   ├── init_db.py             # Database initialization
│   └── run_all.sh             # Start all services
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (or SQLite for development)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd lims-qms-platform
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. **Initialize database**
```bash
cd scripts
python init_db.py
```

5. **Start the backend API**
```bash
cd backend
python run.py
```
The API will be available at http://localhost:8000
API documentation at http://localhost:8000/docs

6. **Start the frontend UI** (in a new terminal)
```bash
cd frontend
streamlit run app.py
```
The UI will be available at http://localhost:8501

### Quick Start (All Services)
```bash
chmod +x scripts/run_all.sh
./scripts/run_all.sh
```

## 📖 Usage Guide

### Document Management

#### Creating a Document
1. Navigate to the "Documents" page
2. Click the "Create Document" tab
3. Fill in the required fields:
   - Document Title
   - Document Type (Procedure, Form, Policy, etc.)
   - Owner
   - Department
   - Created By
4. Click "Create Document"
5. Document number is automatically generated (QSF-YYYY-XXX)

#### Approval Workflow
1. Navigate to "Approval Queue" tab
2. Select a pending document
3. Enter your name as reviewer
4. Choose action: Review, Approve, or Reject
5. Submit the approval

#### Document Revisions
1. Select a document from the list
2. Navigate to revisions section
3. Create a new revision with reason for change
4. Choose major or minor version increment
5. Submit revision

### Equipment Management

#### Adding Equipment
1. Navigate to the "Equipment" page
2. Click the "Add Equipment" tab
3. Fill in equipment details:
   - Equipment Name
   - Manufacturer, Model, Serial Number
   - Location and Department
   - Calibration frequency
4. Click "Add Equipment"
5. Equipment ID is automatically generated (EQP-YYYY-XXXX)
6. QR code is automatically created

#### Recording Calibration
1. Select equipment from the list
2. Navigate to "Calibration" tab
3. Enter calibration details:
   - Calibration date
   - Performed by
   - Certificate number
   - Results
4. Submit calibration record
5. Next calibration date is automatically calculated

#### Viewing Alerts
1. Navigate to "Alerts" tab
2. Select threshold: 7, 15, or 30 days
3. View equipment requiring calibration
4. Alerts are color-coded:
   - 🔴 Overdue/Critical (< 7 days)
   - 🟡 Warning (< 15 days)
   - 🟢 Info (< 30 days)

## 🔧 API Documentation

Complete API documentation is available at http://localhost:8000/docs when the backend is running.

### Key Endpoints

#### Documents
- **POST** `/api/v1/documents/` - Create document
- **GET** `/api/v1/documents/` - List documents
- **POST** `/api/v1/documents/{id}/revise` - Create revision
- **POST** `/api/v1/documents/{id}/approve` - Approve document
- **GET** `/api/v1/documents/search/` - Search documents

#### Equipment
- **POST** `/api/v1/equipment/` - Create equipment
- **GET** `/api/v1/equipment/` - List equipment
- **POST** `/api/v1/equipment/{id}/calibration` - Record calibration
- **POST** `/api/v1/equipment/{id}/maintenance` - Schedule maintenance
- **GET** `/api/v1/equipment/alerts/calibration` - Get alerts

## 🗄️ Database Schema

### Document Management Tables

#### qms_documents
- `id`: Primary key
- `doc_number`: Auto-generated (QSF-YYYY-XXX)
- `title`: Document title
- `type`: Document type (enum)
- `current_revision`: Current version (e.g., "2.1")
- `status`: Document status (enum)
- `owner`, `department`: Ownership info
- `created_by`, `reviewed_by`, `approved_by`: Workflow tracking
- Timestamps: `created_at`, `updated_at`, `approved_at`, etc.

#### document_revisions
- `id`: Primary key
- `document_id`: Foreign key to qms_documents
- `revision_number`: Version number
- `major_version`, `minor_version`: Version components
- `revision_reason`: Why revision was created
- `changes_summary`: Summary of changes
- Approval and timestamp tracking

#### document_distribution
- `id`: Primary key
- `document_id`: Foreign key
- `copy_number`: Controlled copy number
- `recipient_name`, `department`, `location`: Distribution details
- `distributed_at`, `acknowledged_at`: Tracking

### Equipment Management Tables

#### equipment_master
- `id`: Primary key
- `equipment_id`: Auto-generated (EQP-YYYY-XXXX)
- `name`, `manufacturer`, `model_number`, `serial_number`: Basic info
- `location`, `department`, `responsible_person`: Assignment
- `status`: Equipment status (enum)
- Calibration: `next_calibration_date`, `calibration_frequency_days`
- Maintenance: `next_maintenance_date`, `maintenance_frequency_days`
- OEE: `oee_percentage`, `availability_percentage`, etc.
- `qr_code_path`: Path to QR code image

#### calibration_records
- `id`: Primary key
- `equipment_id`: Foreign key
- `calibration_date`, `next_calibration_date`: Dates
- `performed_by`, `calibration_agency`: Who performed
- `certificate_number`: Certificate reference
- `result`: Pass/Fail/Conditional
- `as_found_readings`, `as_left_readings`: Measurement data
- Environmental conditions: `temperature`, `humidity`, `pressure`

#### preventive_maintenance_schedule
- `id`: Primary key
- `equipment_id`: Foreign key
- `maintenance_type`: Type (enum)
- `scheduled_date`, `completed_date`: Dates
- `assigned_to`, `performed_by`: Personnel
- `parts_replaced`, `parts_cost`, `labor_cost`: Cost tracking
- `observations`, `issues_found`, `corrective_actions`: Details

## 🔐 Security & Compliance

- **ISO 17025 Compliance**: Calibration traceability and documentation
- **ISO 9001 Compliance**: Document control and quality management
- **Audit Trail**: Complete revision history and approval tracking
- **Access Control**: Role-based access (to be implemented)
- **Data Integrity**: Validation and verification workflows
- **Electronic Signatures**: Digital signature tracking

## 🚧 Future Enhancements

- [ ] User authentication and authorization
- [ ] Role-based access control (RBAC)
- [ ] Email notifications for approvals and alerts
- [ ] Advanced reporting and analytics
- [ ] Dashboard widgets and KPIs
- [ ] Mobile app for equipment scanning
- [ ] Integration with external calibration systems
- [ ] Advanced search with Elasticsearch
- [ ] Audit log viewer
- [ ] Batch operations

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For support, please contact the development team or create an issue in the repository.

---

**Built with ❤️ for Laboratory Quality Management**
