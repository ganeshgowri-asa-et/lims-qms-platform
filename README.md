# LIMS-QMS Platform

AI-Powered Laboratory Information Management System (LIMS) & Quality Management System (QMS) Platform for Solar PV Testing & R&D Laboratories - Complete Digital Transformation with ISO 17025/9001 Compliance

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29-red)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-blue)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-Proprietary-yellow)](LICENSE)

## 🎯 Overview

This platform provides a comprehensive, integrated solution for managing laboratory operations, quality management, and compliance requirements for Solar PV testing and R&D laboratories. Built with modern web technologies, it ensures ISO 17025:2017 and ISO 9001:2015 compliance while leveraging AI for intelligent decision-making.

## 🚀 Current Implementation: Session 8

### Audit & Risk Management System

**Status:** ✅ Completed

This session implements a complete audit and risk management system with the following features:

#### Key Features

1. **📅 Annual Audit Program (QSF1701)**
   - Multi-year audit planning
   - Approval workflow (Prepared-Reviewed-Approved)
   - Program tracking and status management

2. **📆 Audit Scheduling & Execution**
   - Multiple audit types (Internal, External, Surveillance, Certification)
   - Audit scope management (Department, Process, System, Product)
   - Lead auditor and team assignment
   - Standard reference linkage (ISO 17025, ISO 9001, IEC standards)

3. **🔍 Audit Findings Management**
   - Finding types: NCR (Non-Conformance), OFI (Opportunity for Improvement), OBS (Observation)
   - Severity classification: Critical, Major, Minor
   - **NC Linkage** - Direct integration with NC/CAPA system
   - Root cause analysis and corrective action tracking
   - Effectiveness verification workflow

4. **⚠️ Risk Register with 5x5 Risk Matrix**
   - Comprehensive risk assessment
   - 5x5 Risk Matrix implementation:
     - Likelihood: 1 (Rare) to 5 (Almost Certain)
     - Impact: 1 (Insignificant) to 5 (Catastrophic)
     - Risk Levels: LOW (1-4), MEDIUM (5-12), HIGH (13-16), CRITICAL (17-25)
   - Inherent vs. Residual risk assessment
   - Risk treatment strategies: Accept, Mitigate, Transfer, Avoid
   - Risk review history tracking

5. **✅ Compliance Tracking**
   - ISO 17025:2017 clause-level compliance
   - ISO 9001:2015 clause-level compliance
   - Compliance status tracking
   - Evidence documentation and audit linkage

#### Database Schema

- **audit_program** - Annual audit programs (QSF1701)
- **audit_schedule** - Scheduled audits (AUD-YYYY-XXX)
- **audit_findings** - Audit findings with NC linkage (FND-YYYY-XXX)
- **risk_register** - Risk assessment and management (RISK-YYYY-XXX)
- **risk_review_history** - Historical risk assessments
- **compliance_tracking** - ISO clause compliance matrix

#### Technology Stack

- **Backend:** FastAPI with SQLAlchemy ORM
- **Frontend:** Streamlit with responsive UI
- **Database:** PostgreSQL with advanced functions and triggers
- **API:** RESTful with automatic OpenAPI documentation

## 📋 Planned Sessions (Architecture Roadmap)

### Session 1: Project Foundation *(Planned)*
- Project structure setup
- Database architecture design
- Authentication & authorization framework

### Session 2: Document Management System *(Planned)*
- QMS document control (QSF-YYYY-XXX numbering)
- Version control and digital signatures
- Approval workflow (Doer-Checker-Approver)
- Full-text search and PDF generation

### Session 3: Equipment Calibration & Maintenance *(Planned)*
- Equipment master (EQP-ID)
- Calibration scheduling and alerts
- Preventive maintenance
- OEE tracking and QR codes

### Session 4: Training & Competency *(Planned)*
- Training master database
- Employee training matrix
- Competency gap analysis
- Auto-certificate generation

### Session 5: LIMS Core - Test Request & Sample Management *(Planned)*
- Customer management
- Test request creation (TRQ numbering)
- Sample tracking with barcodes
- Quote automation

### Session 6: IEC Test Report Generation *(Planned)*
- IEC 61215, 61730, 61701 support
- Test data acquisition
- Automated report generation
- Digital certificates with QR codes

### Session 7: Non-Conformance & CAPA *(Planned)*
- NC management (NC-YYYY-XXX)
- AI-powered root cause analysis
- 5-Why and Fishbone diagrams
- CAPA tracking and effectiveness verification

### Session 8: Audit & Risk Management ✅ **COMPLETED**
- Annual audit program (QSF1701)
- Audit scheduling and findings
- 5x5 Risk matrix
- Compliance tracking

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.9 or higher
- PostgreSQL 13 or higher
- pip package manager
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/lims-qms-platform.git
   cd lims-qms-platform
   ```

2. **Run setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure environment**
   ```bash
   # Edit .env file with your settings
   nano .env
   ```

4. **Set up database**
   ```bash
   # Create database
   createdb lims_qms

   # Run schema
   psql -U postgres -d lims_qms -f database/schema/08_audit_risk.sql
   ```

5. **Start backend API**
   ```bash
   source venv/bin/activate
   cd backend
   python main.py
   # API available at http://localhost:8000
   ```

6. **Start frontend UI (in new terminal)**
   ```bash
   source venv/bin/activate
   cd frontend
   streamlit run app.py
   # UI available at http://localhost:8501
   ```

### Manual Installation

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Create directories
mkdir -p logs uploads backups
```

## 📚 Documentation

- **[Session 8 Documentation](docs/SESSION_8_README.md)** - Detailed audit & risk management guide
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete API reference
- **[Interactive API Docs](http://localhost:8000/docs)** - Swagger UI (when running)
- **[ReDoc](http://localhost:8000/redoc)** - Alternative API documentation

## 🏗️ Project Structure

```
lims-qms-platform/
├── backend/                    # FastAPI backend
│   ├── api/                   # API endpoints
│   │   └── audit_risk.py     # Audit & risk management routes
│   ├── database/              # Database models
│   │   └── models.py         # SQLAlchemy ORM models
│   ├── config.py             # Configuration
│   └── main.py               # FastAPI application
├── frontend/                  # Streamlit frontend
│   ├── pages/                # UI pages
│   │   ├── audit_program.py
│   │   ├── audit_schedule.py
│   │   ├── audit_findings.py
│   │   ├── risk_register.py
│   │   └── compliance_tracking.py
│   └── app.py                # Main Streamlit app
├── database/                  # Database schemas
│   └── schema/
│       └── 08_audit_risk.sql # Session 8 schema
├── docs/                      # Documentation
├── logs/                      # Application logs
├── uploads/                   # File uploads
├── .env.example              # Environment template
├── requirements.txt          # Python dependencies
├── setup.sh                  # Setup script
└── README.md                 # This file
```

## 🔑 Key Features

### Audit Management
- ✅ Annual audit program planning (QSF1701)
- ✅ Multi-type audit support (Internal, External, Surveillance, Certification)
- ✅ Audit scheduling with team assignment
- ✅ Findings management (NCR, OFI, OBS)
- ✅ Corrective action tracking
- ✅ Effectiveness verification

### Risk Management
- ✅ 5x5 Risk matrix implementation
- ✅ Inherent vs. Residual risk assessment
- ✅ Risk treatment planning
- ✅ Review history tracking
- ✅ Risk owner assignment
- ✅ Automated risk level calculation

### Compliance Management
- ✅ ISO 17025:2017 compliance tracking
- ✅ ISO 9001:2015 compliance tracking
- ✅ Clause-level status monitoring
- ✅ Evidence documentation
- ✅ Compliance percentage calculation

### Integration
- ✅ NC/CAPA linkage for findings
- ⏳ Document management integration (planned)
- ⏳ Training records integration (planned)
- ⏳ Equipment calibration integration (planned)

## 🔌 API Endpoints

### Base URL: `http://localhost:8000/api/v1/audit-risk`

#### Audit Programs
- `POST /programs` - Create audit program
- `GET /programs` - List programs (with filters)
- `GET /programs/{id}` - Get specific program
- `PUT /programs/{id}` - Update program
- `DELETE /programs/{id}` - Delete program

#### Audit Schedules
- `POST /schedules` - Schedule audit
- `GET /schedules` - List audits
- `GET /schedules/{id}` - Get audit details
- `PUT /schedules/{id}` - Update audit
- `DELETE /schedules/{id}` - Delete audit

#### Audit Findings
- `POST /findings` - Create finding
- `GET /findings` - List findings
- `GET /findings/{id}` - Get finding
- `PUT /findings/{id}` - Update finding
- `DELETE /findings/{id}` - Delete finding

#### Risk Register
- `POST /risks` - Create risk
- `GET /risks` - List risks
- `GET /risks/{id}` - Get risk
- `PUT /risks/{id}` - Update risk
- `DELETE /risks/{id}` - Delete risk

#### Compliance Tracking
- `POST /compliance` - Add compliance record
- `GET /compliance` - List compliance
- `GET /compliance/{id}` - Get record
- `PUT /compliance/{id}` - Update record

#### Dashboard
- `GET /dashboard/summary` - Overall statistics
- `GET /dashboard/risk-matrix` - 5x5 risk matrix
- `GET /dashboard/upcoming-audits` - Upcoming audits
- `GET /dashboard/overdue-findings` - Overdue findings

Full API documentation available at: http://localhost:8000/docs

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test
pytest tests/test_audit_risk.py
```

## 🔒 Security

- Environment-based configuration
- SQL injection prevention via ORM
- Input validation with Pydantic
- CORS protection
- Password hashing (when authentication is implemented)
- Audit trail for all changes

## 📈 ISO Compliance

### ISO 17025:2017
- ✅ Clause 8.8: Internal Audits
- ✅ Clause 6.1: Risk-based thinking
- ✅ Clause 8.9: Management Reviews

### ISO 9001:2015
- ✅ Clause 9.2: Internal Audit
- ✅ Clause 6.1: Actions to address risks and opportunities
- ✅ Clause 10.1: Nonconformity and Corrective Action

## 🤝 Contributing

This is a proprietary project. Internal contributors should:

1. Create feature branch from main
2. Follow coding standards (PEP 8)
3. Write tests for new features
4. Update documentation
5. Submit pull request for review

## 📝 License

Proprietary - Internal use only. See [LICENSE](LICENSE) file for details.

## 👥 Authors & Support

- **Development Team:** Internal Development Team
- **Quality Manager:** [Name]
- **Technical Manager:** [Name]

For support or questions:
- Email: support@your-lab.com
- Internal Wiki: [Link]
- Issue Tracker: [Link]

## 🗺️ Roadmap

### Q1 2025
- ✅ Session 8: Audit & Risk Management
- ⏳ Session 7: NC & CAPA
- ⏳ Session 6: IEC Test Reports

### Q2 2025
- ⏳ Session 5: LIMS Core (Test Requests & Samples)
- ⏳ Session 4: Training & Competency
- ⏳ Session 3: Equipment Calibration

### Q3 2025
- ⏳ Session 2: Document Management
- ⏳ Session 1: Authentication & Authorization
- ⏳ Integration & Testing

### Q4 2025
- ⏳ User Acceptance Testing
- ⏳ Production Deployment
- ⏳ Training & Documentation

## 🎯 Success Metrics

- ✅ Database schema implemented with constraints and triggers
- ✅ RESTful API with auto-generated documentation
- ✅ Interactive web UI with Streamlit
- ✅ 5x5 Risk matrix calculation
- ✅ NC linkage for audit findings
- ✅ Compliance tracking for ISO standards

## 📞 Contact

For questions or support:
- Project Lead: [Email]
- Technical Support: [Email]
- Quality Assurance: [Email]

---

**Built with ❤️ for Laboratory Excellence and Quality Management**

*Ensuring compliance, managing risks, and driving continuous improvement through digital transformation.*
