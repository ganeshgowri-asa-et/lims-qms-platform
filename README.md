# LIMS-QMS Platform

AI-Powered Laboratory Information Management System (LIMS) & Quality Management System (QMS) Platform for Solar PV Testing & R&D Laboratories - Complete Digital Transformation with ISO 17025/9001 Compliance

## Overview

The LIMS-QMS Platform is a comprehensive digital solution for laboratory management, quality control, and compliance. Built with modern technologies, it provides a robust foundation for managing laboratory workflows, sample tracking, quality assurance, and regulatory compliance.

## Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Streamlit
- **Database**: PostgreSQL 15
- **Authentication**: JWT (JSON Web Tokens)
- **Containerization**: Docker & Docker Compose
- **Migrations**: Alembic

## Project Structure

```
lims-qms-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI application
│   │   ├── config.py         # Configuration settings
│   │   ├── database.py       # Database connection
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── schemas.py        # Pydantic schemas
│   │   ├── auth.py           # Authentication utilities
│   │   └── routers/
│   │       ├── auth.py       # Auth endpoints
│   │       └── health.py     # Health check
│   ├── alembic/              # Database migrations
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── streamlit_app.py      # Streamlit application
│   ├── requirements.txt
│   └── Dockerfile
├── database/
│   └── init.sql              # Database initialization
├── docker-compose.yml
└── README.md
```

## Features

### Core Foundation (Session 1)

- ✅ RESTful API with FastAPI
- ✅ PostgreSQL database with connection pooling
- ✅ JWT-based authentication
- ✅ User management (register, login, profile)
- ✅ Audit trail system for all database changes
- ✅ Health check endpoint
- ✅ Streamlit-based frontend
- ✅ Docker containerization
- ✅ API documentation (Swagger/OpenAPI)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ganeshgowri-asa-et/lims-qms-platform.git
   cd lims-qms-platform
   ```

2. **Create environment file** (optional)
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Wait for services to be ready**
   ```bash
   # Check logs
   docker-compose logs -f

   # Wait until you see "Application startup complete"
   ```

5. **Access the applications**
   - Frontend (Streamlit): http://localhost:8501
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Database: localhost:5432

### Default Credentials

- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Change these credentials in production!**

## Development

### Running Without Docker

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://lims_user:lims_password@localhost:5432/lims_qms_db"
export SECRET_KEY="your-secret-key"

# Run the application
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export API_BASE_URL="http://localhost:8000"

# Run the application
streamlit run streamlit_app.py
```

### Database Migrations

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1
```

## API Endpoints

### Health Check
- `GET /health` - Check API and database health

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login (OAuth2 form)
- `POST /api/v1/auth/login-json` - Login (JSON)
- `GET /api/v1/auth/me` - Get current user info

### Documentation
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc UI

## Database Schema

### Users Table
```sql
users (
  user_id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE,
  email VARCHAR(200) UNIQUE,
  password_hash VARCHAR(255),
  full_name VARCHAR(200),
  role VARCHAR(50),
  is_active BOOLEAN,
  created_at TIMESTAMP
)
```

### Audit Log Table
```sql
audit_log (
  audit_id BIGSERIAL PRIMARY KEY,
  table_name VARCHAR(100),
  record_id INTEGER,
  action VARCHAR(20),
  user_id INTEGER REFERENCES users,
  timestamp TIMESTAMP,
  old_values JSONB,
  new_values JSONB
)
```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key (generate a strong random string)
- `DEBUG` - Enable debug mode (True/False)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - JWT token expiration time

## Testing

### Test API with curl

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

## Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps

# View database logs
docker-compose logs db

# Restart services
docker-compose restart
```

### Port Conflicts
If ports 8000, 8501, or 5432 are already in use, modify the port mappings in `docker-compose.yml`.

### Reset Database
```bash
# Stop services
docker-compose down

# Remove volumes
docker volume rm lims-qms-platform_postgres_data

# Restart
docker-compose up -d
```

## Security Notes

- Change default credentials immediately
- Generate a strong `SECRET_KEY` for production
- Use HTTPS in production
- Review CORS settings for production deployment
- Keep dependencies updated
- Regular security audits

## Future Development

This is Session 1 (Core Foundation). Future sessions will include:
- Session 2: Sample management
- Session 3: Test management
- Session 4: Quality management
- Session 5: Reporting and analytics
- Session 6: Compliance and auditing

## License

[Your License Here]

## Support

For issues and questions, please open an issue on GitHub.
