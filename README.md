# LIMS-QMS Platform

AI-Powered Laboratory Information Management System (LIMS) & Quality Management System (QMS) Platform for Solar PV Testing & R&D Laboratories - Complete Digital Transformation with ISO 17025/9001 Compliance

## 🎯 Overview

A comprehensive, modern LIMS-QMS platform built with FastAPI and Streamlit, designed specifically for solar PV testing and R&D laboratories. This platform ensures full compliance with ISO 17025:2017 and ISO 9001:2015 standards while providing powerful automation and analytics capabilities.

## ✨ Features

### Session 4: Training & Competency Management ✅
- **Training Program Management**: Complete CRUD for training catalog
- **Employee Training Matrix**: Track individual training requirements and competency levels
- **Training Attendance**: Record attendance with pre/post test scoring
- **Competency Gap Analysis**: Automated gap identification with multiple dimensions
- **Auto-Certificate Generation**: PDF certificates with QR codes
- **QSF Forms**: Automated generation of QSF0203, QSF0205, QSF0206

### Session 3: Equipment Calibration & Maintenance
- Auto EQP-ID generation
- Calibration due alerts (30/15/7 days)
- OEE tracking
- QR code generation for equipment
- Preventive maintenance scheduling

### Session 2: Document Management System
- Auto document numbering (QSF-YYYY-XXX)
- Version control (major.minor)
- Digital signatures
- Approval workflow (Doer-Checker-Approver)
- Full-text search
- PDF generation with watermarks

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
│           (Training Dashboard, Analytics, Forms)             │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
│  ┌─────────────┬──────────────┬─────────────────────────┐  │
│  │   API       │   Services   │   Business Logic        │  │
│  │ Endpoints   │   Layer      │   - Competency Analysis │  │
│  │             │              │   - Certificate Gen     │  │
│  │             │              │   - QSF Forms Gen       │  │
│  └─────────────┴──────────────┴─────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓ SQLAlchemy ORM
┌─────────────────────────────────────────────────────────────┐
│                   PostgreSQL Database                        │
│     (Training, Equipment, Documents, Calibration)            │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- pip

### 1. Clone Repository
```bash
git clone <repository-url>
cd lims-qms-platform
```

### 2. Setup Environment
```bash
./setup.sh
```

### 3. Configure Database
```bash
# Update .env with your PostgreSQL credentials
cp .env.example .env
nano .env

# Create database
createdb lims_qms_db

# Load schema
psql lims_qms_db < database/schema.sql
```

### 4. Run Application

**Terminal 1 - Backend:**
```bash
./run_backend.sh
```
Access API: http://localhost:8000
API Docs: http://localhost:8000/docs

**Terminal 2 - Frontend:**
```bash
./run_frontend.sh
```
Access UI: http://localhost:8501

## 📚 Documentation

- [Session 4: Training & Competency Management](README_SESSION4.md) - Detailed feature documentation
- [Project Structure](PROJECT_STRUCTURE.md) - Complete directory structure
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)

## 🗄️ Database Schema

### Training Management Tables
- `training_master` - Training program catalog
- `employee_training_matrix` - Employee training requirements
- `training_attendance` - Training records with scoring
- `training_effectiveness` - Effectiveness evaluations
- `competency_assessment` - Competency assessments

### Equipment Management Tables
- `equipment_master` - Equipment registry
- `calibration_records` - Calibration history
- `preventive_maintenance_schedule` - Maintenance planning
- `oee_tracking` - OEE metrics

### Document Management Tables
- `qms_documents` - Document master
- `document_revisions` - Version control
- `document_distribution` - Controlled copies

## 🔧 Technology Stack

### Backend
- **FastAPI**: Modern, high-performance web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Robust relational database
- **Pydantic**: Data validation using Python type hints
- **ReportLab**: PDF generation
- **QRCode**: QR code generation

### Frontend
- **Streamlit**: Fast web app framework
- **Plotly**: Interactive data visualization
- **Pandas**: Data manipulation and analysis

### Other Tools
- **Uvicorn**: ASGI server
- **Alembic**: Database migrations

## 📊 API Endpoints

### Training Management
```
POST   /api/training/trainings              # Create training
GET    /api/training/trainings              # List trainings
GET    /api/training/trainings/{id}         # Get training
PUT    /api/training/trainings/{id}         # Update training
DELETE /api/training/trainings/{id}         # Delete training

POST   /api/training/matrix                 # Assign training
GET    /api/training/matrix                 # List matrix

POST   /api/training/attendance             # Record attendance
GET    /api/training/attendance             # List attendance

GET    /api/training/competency-gaps        # Gap analysis
GET    /api/training/employee/{id}/development-plan
GET    /api/training/department/{dept}/competency-overview

POST   /api/training/certificates/generate  # Generate certificate
POST   /api/training/certificates/batch-generate

POST   /api/training/qsf/attendance-record  # QSF0203
POST   /api/training/qsf/effectiveness-evaluation  # QSF0205
POST   /api/training/qsf/needs-assessment   # QSF0206
```

## 🎓 Training Management Features

### Competency Gap Analysis
```python
GET /api/training/competency-gaps?department=Testing&gap_status=Expired
```

**Gap Status Categories:**
- **Expired**: Certificates expired
- **Expiring Soon**: Valid for ≤30 days
- **Not Trained**: No training completed
- **Gap Exists**: Current level ≠ Target level
- **Competent**: All requirements met

### Certificate Generation
```python
POST /api/training/certificates/generate
{
    "attendance_id": 1,
    "template": "default"
}
```

**Certificate Features:**
- Professional PDF design
- QR code for verification
- Numbering: TRN-YYYYMM-EMPID-DD
- Validity tracking
- Organization branding

### QSF Forms
- **QSF0203**: Training Attendance Record
- **QSF0205**: Training Effectiveness Evaluation
- **QSF0206**: Training Needs Assessment

## 📈 Analytics & Reporting

The Streamlit dashboard provides:
- Training statistics and metrics
- Competency compliance rates
- Gap analysis visualization
- Department-wise reports
- Training effectiveness trends
- Interactive charts with Plotly

## 🔒 ISO Compliance

### ISO 17025:2017
✅ Personnel competence (6.2.2)
✅ Training records and effectiveness
✅ Competency demonstration
✅ Authorization tracking

### ISO 9001:2015
✅ Competence requirements (7.2)
✅ Training provision and effectiveness
✅ Documented information (7.5)

## 🧪 Testing

Access interactive API testing:
```
http://localhost:8000/docs
```

Features:
- Try all endpoints
- View request/response schemas
- Example queries
- Authentication testing

## 📁 Project Structure

```
lims-qms-platform/
├── backend/               # FastAPI backend
│   └── app/
│       ├── api/          # API endpoints
│       ├── models/       # Database models
│       ├── schemas/      # Pydantic schemas
│       └── services/     # Business logic
├── frontend/             # Streamlit frontend
│   └── app.py           # Main dashboard
├── database/            # Database files
│   └── schema.sql       # Complete schema
├── uploads/             # Generated files
│   ├── certificates/    # Training certificates
│   └── qsf_forms/      # QSF forms
└── docs/               # Documentation
```

## 🔐 Security

- Environment-based configuration
- SQL injection protection via ORM
- Input validation with Pydantic
- CORS middleware configured
- Secure file upload handling

## 🚧 Development Roadmap

### Phase 1 ✅ (Completed)
- [x] Training & Competency Management
- [x] Competency Gap Analysis
- [x] Auto-Certificate Generation
- [x] QSF Forms (0203, 0205, 0206)

### Phase 2 (Planned)
- [ ] Equipment Management Integration
- [ ] Document Management System
- [ ] Email Notifications
- [ ] Advanced Analytics
- [ ] Mobile App

### Phase 3 (Future)
- [ ] AI-powered recommendations
- [ ] Automated scheduling
- [ ] Integration with external systems
- [ ] Multi-language support

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

LIMS-QMS Platform Development Team

## 🙏 Acknowledgments

- ISO 17025:2017 and ISO 9001:2015 standards
- FastAPI and Streamlit communities
- Solar PV testing laboratory requirements

## 📞 Support

For issues and questions:
- Create an issue in GitHub
- Check documentation at `/docs`
- Review API documentation at http://localhost:8000/docs

## 🎉 Get Started

Ready to transform your laboratory management?

```bash
./setup.sh
./run_backend.sh &
./run_frontend.sh
```

Visit http://localhost:8501 and start managing your training and competency!

---

**Built with ❤️ for Solar PV Testing & R&D Laboratories**
