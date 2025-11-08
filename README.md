# LIMS-QMS Platform - Equipment Calibration & Maintenance Management System

AI-Powered Laboratory Information Management System (LIMS) & Quality Management System (QMS) Platform for Solar PV Testing & R&D Laboratories - Complete Digital Transformation with ISO 17025/9001 Compliance

## Overview

This is a comprehensive **Equipment Calibration & Maintenance Management System** built as part of the LIMS-QMS Platform. The system provides complete equipment lifecycle management with AI-powered predictive maintenance, automated calibration scheduling, and robust quality workflows.

## Key Features

### 1. Equipment Management
- **Unique Equipment ID Generator**: Auto-generates IDs in format `EQP-DEPT-YYYY-XXX`
- **QR Code Generation**: Automatic QR code creation for equipment tracking
- **Equipment Specifications**: Detailed tracking of measurement ranges, accuracy, and resolution
- **Equipment History Card**: Complete audit trail of all equipment changes
- **Equipment Utilization Tracking**: Track usage hours, downtime, and performance

### 2. Calibration Management
- **Auto-Calibration Due Date Calculator**: Intelligent calculation based on frequency
- **Multi-Level Alerts**: 30/15/7 day advance notifications for due calibrations
- **Certificate Upload with OCR**: Automatic data extraction from calibration certificates
- **Vendor Performance Metrics**: Track calibration vendor quality and turnaround time
- **Calibration Cost Tracking**: Complete financial tracking of calibration activities
- **Doer-Checker-Approver Workflow**: 3-level approval process with digital signatures

### 3. Preventive Maintenance
- **Maintenance Scheduling**: Automated preventive maintenance schedules
- **Downtime Tracking**: Track equipment downtime and production impact
- **Failure Logging**: Comprehensive equipment failure documentation
- **Work Order Management**: Complete maintenance work order system

### 4. OEE (Overall Equipment Effectiveness) Calculation
- **Availability Calculation**: Track planned vs. actual production time
- **Performance Metrics**: Monitor cycle time and throughput
- **Quality Tracking**: Track good count vs. reject count
- **Real-time OEE Dashboard**: Visualize equipment effectiveness

### 5. AI-Powered Features
- **Predictive Maintenance**: ML-based failure probability prediction
- **Failure Pattern Detection**: Identify patterns in equipment failures
- **Optimal Calibration Frequency**: AI recommendations for calibration intervals
- **Anomaly Detection**: Identify unusual equipment behavior

### 6. Compliance & Traceability
- **Audit Trail**: Complete tracking of all changes with user, timestamp, and IP
- **Document References**: Traceability to Level 1/2/3 QMS documents
- **Digital Signatures**: Cryptographic signatures for workflow approvals
- **ISO 17025 Compliance**: Full compliance with laboratory accreditation standards

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy 2.0**: Async ORM for database operations
- **PostgreSQL**: Robust relational database
- **Alembic**: Database migration management
- **Pydantic**: Data validation and settings management

### AI/ML
- **scikit-learn**: Machine learning models for predictive analytics
- **pandas & numpy**: Data processing and analysis
- **Prophet**: Time series forecasting (optional)

### Document Processing
- **Tesseract OCR**: Certificate data extraction
- **pdf2image**: PDF processing
- **OpenCV**: Image preprocessing for better OCR results

### Notifications
- **FastAPI-Mail**: Email notifications
- **Twilio**: SMS alerts for critical calibrations

### QR Code & Digital Signatures
- **qrcode**: QR code generation for equipment
- **cryptography**: Digital signature implementation

### DevOps
- **Docker & Docker Compose**: Containerization
- **Redis**: Background task queue (Celery)
- **uvicorn**: ASGI server

## Project Structure

```
lims-qms-platform/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── dependencies/
│   │   │   │   └── auth.py          # Authentication dependencies
│   │   │   └── endpoints/
│   │   │       ├── auth.py          # Authentication endpoints
│   │   │       ├── users.py         # User management
│   │   │       ├── equipment.py     # Equipment CRUD & OEE
│   │   │       ├── calibration.py   # Calibration management
│   │   │       ├── maintenance.py   # Maintenance tracking
│   │   │       └── analytics.py     # AI insights & reports
│   │   ├── core/
│   │   │   ├── config.py            # Application configuration
│   │   │   ├── database.py          # Database connection
│   │   │   └── security.py          # Authentication & hashing
│   │   ├── models/
│   │   │   ├── base.py              # User, Audit, Workflow models
│   │   │   ├── equipment.py         # Equipment models
│   │   │   ├── calibration.py       # Calibration models
│   │   │   └── maintenance.py       # Maintenance models
│   │   ├── schemas/
│   │   │   ├── auth.py              # Auth schemas
│   │   │   ├── equipment.py         # Equipment schemas
│   │   │   ├── calibration.py       # Calibration schemas
│   │   │   └── workflow.py          # Workflow schemas
│   │   ├── services/
│   │   │   ├── equipment_service.py # Equipment business logic
│   │   │   ├── calibration_service.py # Calibration logic
│   │   │   ├── workflow_service.py  # Doer-Checker-Approver
│   │   │   ├── notification_service.py # Email/SMS alerts
│   │   │   ├── ocr_service.py       # Certificate OCR
│   │   │   └── ai_service.py        # AI/ML predictions
│   │   ├── utils/
│   │   └── main.py                  # FastAPI application
│   ├── alembic/
│   │   ├── versions/                # Database migrations
│   │   ├── env.py                   # Alembic environment
│   │   └── script.py.mako           # Migration template
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── alembic.ini
│   └── .env.example
├── frontend/                        # (To be implemented)
├── docs/                            # Documentation
├── docker-compose.yml               # Docker orchestration
├── .gitignore
└── README.md
```

## Database Schema

### Core Tables

1. **users** - User accounts and roles
2. **audit_logs** - Complete audit trail
3. **document_references** - QMS document traceability
4. **workflow_records** - Doer-Checker-Approver workflow

### Equipment Tables

1. **equipment_master** - Main equipment registry
2. **equipment_specifications** - Detailed specifications
3. **equipment_history_card** - Equipment change history
4. **equipment_utilization** - Usage and OEE tracking

### Calibration Tables

1. **calibration_master** - Vendor information
2. **calibration_records** - Calibration history
3. **calibration_schedule** - Automatic scheduling

### Maintenance Tables

1. **preventive_maintenance_schedule** - PM schedules
2. **maintenance_records** - Maintenance history
3. **equipment_failure_log** - Failure tracking

## Installation & Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (optional)
- Tesseract OCR

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd lims-qms-platform
```

2. **Set up virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Set up database**
```bash
# Create PostgreSQL database
createdb lims_qms

# Run migrations
alembic upgrade head
```

6. **Run the application**
```bash
uvicorn app.main:app --reload
```

7. **Access the API**
- API Documentation: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Docker Setup

1. **Build and run with Docker Compose**
```bash
docker-compose up -d
```

2. **Run migrations**
```bash
docker-compose exec backend alembic upgrade head
```

3. **Access services**
- Backend API: http://localhost:8000
- PgAdmin: http://localhost:5050

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/change-password` - Change password

### Equipment Management
- `POST /api/equipment/` - Create equipment
- `GET /api/equipment/` - List equipment (with filters)
- `GET /api/equipment/{id}` - Get equipment details
- `PUT /api/equipment/{id}` - Update equipment
- `GET /api/equipment/{id}/history` - Get equipment history
- `POST /api/equipment/{id}/utilization` - Add utilization record
- `GET /api/equipment/{id}/oee` - Calculate OEE
- `GET /api/equipment/{id}/qr-code` - Get QR code

### Calibration Management
- `POST /api/calibration/vendors` - Create vendor
- `GET /api/calibration/vendors` - List vendors
- `POST /api/calibration/records` - Create calibration record
- `GET /api/calibration/records` - List calibration records
- `GET /api/calibration/due` - Get calibrations due
- `GET /api/calibration/overdue` - Get overdue calibrations
- `POST /api/calibration/records/{id}/certificate/upload` - Upload certificate
- `POST /api/calibration/records/{id}/submit` - Submit for checking
- `POST /api/calibration/records/{id}/check` - Checker review
- `POST /api/calibration/records/{id}/approve` - Final approval

### Maintenance Management
- `POST /api/maintenance/schedules` - Create PM schedule
- `GET /api/maintenance/schedules` - List PM schedules
- `GET /api/maintenance/schedules/due` - Get due maintenance
- `POST /api/maintenance/records` - Create maintenance record
- `GET /api/maintenance/records` - List maintenance records
- `POST /api/maintenance/failures` - Log equipment failure

### Analytics & AI
- `GET /api/analytics/equipment/{id}/failure-prediction` - Predict failure probability
- `GET /api/analytics/failure-patterns` - Detect failure patterns
- `GET /api/analytics/equipment/{id}/calibration-recommendation` - AI calibration frequency
- `GET /api/analytics/equipment/{id}/predictive-maintenance` - Predictive maintenance schedule
- `GET /api/analytics/dashboard/summary` - Dashboard metrics
- `GET /api/analytics/reports/equipment-performance` - Performance report
- `GET /api/analytics/reports/calibration-summary` - Calibration summary

## Configuration

### Environment Variables

See `.env.example` for all configuration options:

- **Application**: APP_NAME, DEBUG, SECRET_KEY
- **Database**: DATABASE_URL, DATABASE_URL_SYNC
- **Email**: MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD
- **SMS**: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
- **Alerts**: CALIBRATION_ALERT_DAYS_1/2/3 (30/15/7 days)
- **AI**: AI_MODEL_PATH, ENABLE_AI_FEATURES

## Workflow System

### Doer-Checker-Approver Pattern

1. **Doer** creates and submits record
2. **Checker** reviews and approves/rejects
3. **Approver** gives final approval
4. Digital signatures at each step
5. Complete audit trail

### Workflow States
- `draft` - Initial creation
- `submitted` - Submitted for checking
- `checked` - Checker approved
- `approved` - Final approval
- `rejected` - Rejected at any stage
- `revision_required` - Needs revision

## AI Features

### 1. Failure Prediction
- Uses Random Forest classifier
- Analyzes historical utilization and failure data
- Provides probability score (0-100%)
- Risk categorization (low/medium/high)

### 2. Pattern Detection
- Isolation Forest for anomaly detection
- Identifies patterns in failures:
  - Overdue calibration correlation
  - Overdue maintenance correlation
  - High usage patterns
  - Anomalous failures

### 3. Calibration Optimization
- Analyzes calibration pass/fail rates
- Recommends optimal frequency
- Considers equipment stability
- Cost-benefit analysis

## Security

- **Authentication**: JWT-based authentication
- **Authorization**: Role-based access control (RBAC)
- **Digital Signatures**: Cryptographic signatures for approvals
- **Audit Trail**: Complete logging of all actions
- **Password Hashing**: bcrypt hashing
- **SQL Injection Prevention**: SQLAlchemy ORM

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

## Deployment

### Production Checklist

1. Set strong `SECRET_KEY` in environment
2. Set `DEBUG=False`
3. Configure production database
4. Set up SSL/TLS certificates
5. Configure email/SMS services
6. Set up backup strategy
7. Configure monitoring and logging
8. Set up CI/CD pipeline

### Docker Production Deployment

```bash
# Build production image
docker build -t lims-qms-backend:latest ./backend

# Run with production settings
docker-compose -f docker-compose.prod.yml up -d
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in GitHub
- Email: support@lims-qms.com

## Acknowledgments

- Built with FastAPI
- AI/ML powered by scikit-learn
- OCR by Tesseract
- Database by PostgreSQL

---

**Version**: 1.0.0
**Last Updated**: 2025-11-08
**Status**: Production Ready
