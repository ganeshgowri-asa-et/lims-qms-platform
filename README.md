# LIMS/QMS Platform - Test Request & Sample Management

## Session 5: LIMS Core Implementation

A comprehensive Laboratory Information Management System (LIMS) and Quality Management System (QMS) platform for test request and sample management with automated workflows.

## 🎯 Features

### Test Request Management (QSF0601)
- ✅ Auto-generated TRQ numbering (TRQ-YYYY-XXXXX)
- ✅ Barcode generation for test requests
- ✅ Multi-parameter test requests
- ✅ Priority-based workflow (Low, Medium, High, Urgent)
- ✅ Status tracking (Draft → Submitted → Approved → In Progress → Completed)
- ✅ Quote automation with pricing
- ✅ Approval workflow

### Sample Management
- ✅ Auto-generated sample numbering (SMP-YYYY-XXXXX)
- ✅ Barcode generation for samples
- ✅ Sample tracking lifecycle
- ✅ Batch/Lot tracking
- ✅ Storage location management
- ✅ Status updates (Pending → Received → In Testing → Completed)

### Quote Automation
- ✅ Automated quote generation based on test parameters
- ✅ Priority-based pricing multipliers
- ✅ Quote approval workflow
- ✅ Quote numbering (QTE-YYYY-XXXXX)

### Additional Features
- ✅ Customer management
- ✅ RESTful API with FastAPI
- ✅ Interactive Streamlit UI
- ✅ PostgreSQL database
- ✅ Docker containerization
- ✅ Comprehensive documentation

## 🏗️ Architecture

```
lims-qms-platform/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # Streamlit application
│   ├── pages/             # UI pages
│   ├── utils/             # API client
│   ├── Dockerfile
│   └── requirements.txt
├── docs/                  # Documentation
├── docker-compose.yml     # Docker orchestration
└── .env.example          # Environment variables template
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+ (for local development)

### Option 1: Docker Deployment (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd lims-qms-platform
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start all services:
```bash
docker-compose up -d
```

4. Access the applications:
- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

### Option 2: Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env

# Run the application
python -m app.main
```

Backend will be available at http://localhost:8000

#### Frontend Setup

```bash
cd frontend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run streamlit_app.py
```

Frontend will be available at http://localhost:8501

## 📚 Database Schema

### Core Tables

1. **customers** - Customer master data
2. **test_requests** - Test request records with TRQ numbering
3. **samples** - Sample tracking with SMP numbering
4. **test_parameters** - Test parameters for each request
5. **number_sequences** - Auto-numbering sequences

## 🔌 API Endpoints

### Test Requests
- `POST /api/v1/test-requests` - Create test request
- `GET /api/v1/test-requests` - List test requests
- `GET /api/v1/test-requests/{trq_number}` - Get test request
- `PUT /api/v1/test-requests/{trq_number}` - Update test request
- `POST /api/v1/test-requests/{trq_number}/submit` - Submit for approval
- `POST /api/v1/test-requests/{trq_number}/approve` - Approve request
- `POST /api/v1/test-requests/{trq_number}/generate-quote` - Generate quote
- `POST /api/v1/test-requests/{trq_number}/approve-quote` - Approve quote

### Samples
- `POST /api/v1/samples` - Create sample
- `GET /api/v1/samples` - List samples
- `GET /api/v1/samples/{sample_number}` - Get sample
- `PUT /api/v1/samples/{sample_number}` - Update sample
- `POST /api/v1/samples/{sample_number}/receive` - Mark as received
- `POST /api/v1/samples/{sample_number}/start-testing` - Start testing
- `POST /api/v1/samples/{sample_number}/complete-testing` - Complete testing

### Customers
- `POST /api/v1/customers` - Create customer
- `GET /api/v1/customers` - List customers
- `GET /api/v1/customers/{customer_id}` - Get customer

Full API documentation: http://localhost:8000/api/docs

## 🎨 UI Features

### Dashboard
- Summary statistics
- Recent activity feed
- Status distribution
- Quick metrics

### Test Request Management
- Create test requests with multiple parameters
- View and filter test requests
- Submit and approve workflows
- Generate quotes automatically
- View barcodes

### Sample Management
- Register new samples
- Track sample lifecycle
- Update sample status
- View sample barcodes
- Search samples

## 🔐 Security Features

- Input validation with Pydantic
- SQL injection protection with SQLAlchemy ORM
- CORS configuration
- Environment-based configuration

## 📊 Auto-Numbering System

The platform implements a robust auto-numbering system:

- **TRQ-YYYY-XXXXX** - Test Requests
- **SMP-YYYY-XXXXX** - Samples
- **QTE-YYYY-XXXXX** - Quotes
- **CUST-YYYY-XXXXX** - Customers

Format: `PREFIX-YEAR-SEQUENCE`
- Automatic year rollover
- Sequential numbering per year
- Thread-safe database transactions

## 🏷️ Barcode Generation

- Code128 barcodes for test requests and samples
- QR code support
- Base64 encoded image storage
- Printable barcode labels

## 💰 Quote Automation

Automated quote generation with:
- Predefined pricing for common test parameters
- Priority-based multipliers (Low: 1.0x, Medium: 1.2x, High: 1.5x, Urgent: 2.0x)
- Automatic calculation
- Approval workflow

## 🧪 Test Types Supported

- Chemical Analysis
- Microbiological Testing
- Physical Testing
- Mechanical Testing
- Electrical Testing
- Environmental Testing
- Performance Testing
- Safety Testing
- Stability Testing

## 📋 QSF0601 Form Reference

The platform implements QSF0601 (Quality Sample Form) standard for test request management with:
- Standardized data collection
- Approval workflows
- Traceability
- Audit trail

## 🔧 Technology Stack

**Backend:**
- FastAPI 0.104+
- SQLAlchemy 2.0+
- Pydantic v2
- PostgreSQL 15+
- python-barcode
- qrcode

**Frontend:**
- Streamlit 1.29+
- Python requests
- Pandas

**DevOps:**
- Docker & Docker Compose
- PostgreSQL container
- Multi-stage builds

## 📖 Documentation

- [Architecture](docs/architecture.md)
- [Database Schema](docs/database_schema.md)
- [API Documentation](http://localhost:8000/api/docs)

## 🧑‍💻 Development

### Running Tests

```bash
cd backend
pytest
```

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "Migration message"
alembic upgrade head
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

See LICENSE file for details.

## 👥 Support

For issues and questions, please open an issue in the repository.

## 🎯 Roadmap

Future enhancements:
- [ ] Equipment calibration tracking
- [ ] Document management integration
- [ ] Training records linkage
- [ ] Advanced reporting and analytics
- [ ] Mobile app for barcode scanning
- [ ] Email notifications
- [ ] Advanced search and filtering
- [ ] Export to Excel/PDF

## ✨ Acknowledgments

Built following LIMS/QMS industry standards and best practices.
