# LIMS-QMS Organization OS

Complete Organization Operating System - Unified LIMS-QMS Platform

## 🌟 Features

### Core Modules

1. **Document Management System (Level 1-5)**
   - Quality Manual, Policies, Procedures
   - Document numbering and revision control
   - Doer-Checker-Approver workflow
   - Full traceability

2. **Dynamic Form Engine**
   - Auto-generate forms from Excel/Word templates
   - Support all field types
   - Workflow integration
   - Level 5 records generation

3. **Traceability Engine**
   - Unique ID for all entities
   - Forward & backward traceability
   - Complete audit trail

4. **Workflow & Task Management**
   - Project lifecycle management
   - Task assignment and tracking
   - Meeting management
   - Kanban boards and Gantt charts

5. **HR & People Management**
   - Recruitment workflow
   - Training management
   - Leave and attendance
   - Performance reviews

6. **Procurement & Equipment**
   - RFQ and PO management
   - Vendor management
   - Equipment tracking
   - Calibration scheduling

7. **Financial Management**
   - Expense tracking
   - Invoice generation
   - Payment tracking
   - Financial reports

8. **CRM & Customer Management**
   - Lead management
   - Customer database
   - Order tracking
   - Support tickets

9. **Quality Management**
   - Non-conformance tracking
   - CAPA management
   - Audit planning
   - Risk assessment

10. **Analytics & BI**
    - KPI dashboards
    - Real-time metrics
    - Custom report builder

11. **AI Assistant**
    - Claude API integration
    - Document generation
    - Smart search
    - Natural language queries

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis (optional)
- Docker (optional)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ganeshgowri-asa-et/lims-qms-platform.git
cd lims-qms-platform
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
python database/init_db.py
```

6. **Run backend**
```bash
uvicorn backend.main:app --reload
```

7. **Run frontend (in new terminal)**
```bash
streamlit run frontend/app.py
```

## 🐳 Docker Deployment

```bash
# Start all services
docker-compose up -d

# Initialize database
docker-compose exec backend python database/init_db.py

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## 📖 Access Points

- **Frontend (Streamlit)**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 🔑 Default Credentials

```
Username: admin
Password: admin123
```

⚠️ **Important**: Change the admin password immediately after first login!

## 📁 Project Structure

```
lims-qms-platform/
├── backend/                 # FastAPI backend
│   ├── api/                # API endpoints
│   │   ├── endpoints/      # Route handlers
│   │   └── dependencies/   # Shared dependencies
│   ├── core/               # Core configuration
│   ├── models/             # Database models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   └── utils/              # Utility functions
├── frontend/               # Streamlit frontend
│   ├── pages/              # Page modules
│   ├── components/         # Reusable components
│   ├── utils/              # Utility functions
│   └── app.py              # Main application
├── database/               # Database scripts
│   ├── migrations/         # Alembic migrations
│   ├── seeds/              # Seed data
│   └── init_db.py          # Database initialization
├── docs/                   # Documentation
│   ├── api/                # API documentation
│   ├── user_manual/        # User guides
│   └── deployment/         # Deployment guides
├── tests/                  # Test suite
│   ├── backend/            # Backend tests
│   ├── frontend/           # Frontend tests
│   └── integration/        # Integration tests
├── docker/                 # Docker files
├── templates_uploaded/     # Template files (47 Excel/Word files)
├── uploads/                # User uploaded files
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore file
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## 🔧 Configuration

### Database

Edit `.env` file:
```
DATABASE_URL=postgresql://user:password@localhost:5432/lims_qms
```

### AI Assistant

Add your Anthropic API key in `.env`:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## 📚 Documentation

- [API Documentation](docs/api/README.md)
- [User Manual](docs/user_manual/README.md)
- [Deployment Guide](docs/deployment/README.md)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov=frontend

# Run specific test
pytest tests/backend/test_documents.py
```

## 🛠️ Development

### Adding a New Module

1. Create model in `backend/models/`
2. Create API endpoints in `backend/api/endpoints/`
3. Create frontend page in `frontend/pages/`
4. Update main app navigation

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🌍 Multi-Language Support

Supported languages:
- English (en)
- Hindi (hi)
- Tamil (ta)
- Telugu (te)
- Gujarati (gu)
- Marathi (mr)

## 📄 Standards Compliance

- ISO 17025 (Testing and Calibration Laboratories)
- ISO 9001 (Quality Management Systems)
- IEC 61215 (PV Module Testing)
- IEC 61730, 61853, 62804, 62716, 61701, 62332, 63202, 60904

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Support

For support, email support@lims-qms.com or create an issue in the repository.

## 🙏 Acknowledgments

- FastAPI for the backend framework
- Streamlit for the frontend framework
- Anthropic for Claude AI integration
- All contributors and testers

---

**Built with ❤️ for Quality Management Excellence**
