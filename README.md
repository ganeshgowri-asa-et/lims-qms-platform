# LIMS-QMS Platform 🔬

**AI-Powered Laboratory Information Management System (LIMS) & Quality Management System (QMS) Platform**

Complete digital transformation solution for Solar PV Testing & R&D Laboratories with ISO 17025/9001 Compliance, featuring advanced AI/ML capabilities for predictive analytics and intelligent automation.

---

## 🎯 Features

### Core Modules (Sessions 2-9)

#### 📄 **Session 2: Document Management System**
- Auto-generated document numbering (QSF-YYYY-XXX)
- Version control with major.minor revisions
- Digital signature workflow (Doer-Checker-Approver)
- Controlled document distribution tracking
- Full-text search capabilities

#### ⚙️ **Session 3: Equipment Calibration & Maintenance**
- Auto-generated equipment IDs (EQP-XXX)
- Calibration due alerts (30/15/7 days)
- Preventive maintenance scheduling
- QR code generation for equipment tracking
- OEE (Overall Equipment Effectiveness) tracking

#### 🎓 **Session 4: Training & Competency Management**
- Training matrix management
- Competency gap analysis
- Auto-generated training certificates
- Skill assessment tracking
- Re-training alerts

#### 🧪 **Session 5: LIMS Core - Test Request & Sample Management**
- Test request workflow (TRQ-YYYY-XXX)
- Sample tracking with barcode generation
- Quote automation
- Real-time sample status tracking
- Customer portal integration

#### 📊 **Session 6: IEC Test Report Generation**
- Automated test execution for IEC 61215, 61730, 61701
- Real-time data acquisition and validation
- Automated graph generation
- Pass/fail criteria evaluation
- Digital certificates with QR codes

#### 🚨 **Session 7: Non-Conformance & CAPA**
- NC tracking (NC-YYYY-XXX)
- AI-powered root cause suggestions
- 5-Why and Fishbone analysis
- CAPA action management
- Effectiveness verification

#### 📋 **Session 8: Audit & Risk Management**
- Annual audit program (QSF1701)
- Audit scheduling and findings tracking
- 5x5 Risk matrix
- Risk mitigation planning
- ISO 17025/9001 compliance tracking

#### 📈 **Session 9: Analytics Dashboard & Customer Portal**
- Executive dashboard with KPIs
- Quality metrics visualization
- Operational metrics
- Customer portal with real-time tracking
- Interactive charts with Plotly

### 🤖 **Session 10: AI Integration (Advanced Features)**

1. **Predictive Maintenance**
   - Equipment failure forecasting using Random Forest
   - Risk level classification (Low/Medium/High/Critical)
   - Automated maintenance recommendations

2. **NC Root Cause Auto-Suggestion**
   - NLP-based analysis of historical NC data
   - Top-3 root cause suggestions with confidence scores
   - Rule-based fallback for new categories

3. **Test Duration Estimation**
   - ML regression model for duration prediction
   - Confidence intervals
   - Resource planning optimization

4. **Document Classification & Auto-Tagging**
   - Automatic document categorization
   - Smart tag suggestions
   - Improved searchability

---

## 🏗️ Architecture

### Technology Stack

**Backend:**
- FastAPI (Python 3.11)
- SQLAlchemy ORM
- PostgreSQL 15
- Redis (Caching & Celery)
- Pydantic (Validation)

**AI/ML:**
- scikit-learn (ML models)
- transformers (NLP)
- PyTorch
- NLTK

**Frontend:**
- Streamlit (Analytics Dashboard)
- Plotly (Visualizations)

**DevOps:**
- Docker & Docker Compose
- Nginx (Reverse Proxy)
- GitHub Actions (CI/CD)
- PostgreSQL automated backups

**Standards Compliance:**
- ISO 17025:2017
- ISO 9001:2015
- IEC 61215, 61730, 61701

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git
- (Optional) Python 3.11+ for local development

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/your-org/lims-qms-platform.git
cd lims-qms-platform
```

2. **Configure environment variables**

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Important:** Update these values in `.env`:
- `POSTGRES_PASSWORD` - Strong password for database
- `SECRET_KEY` - Generate using: `openssl rand -hex 32`
- Email SMTP settings (if using notifications)

3. **Start the platform**

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

4. **Access the platform**

- **API Documentation:** http://localhost/api/docs
- **Analytics Dashboard:** http://localhost/dashboard/
- **API Endpoint:** http://localhost/api/v1/

5. **Initialize the database**

```bash
# Run migrations (if using Alembic)
docker-compose exec backend alembic upgrade head

# Or use the init script
docker-compose exec backend python scripts/init_data.py
```

---

## 📖 API Documentation

### Interactive API Documentation

Once the platform is running, access the interactive Swagger UI:

**Swagger UI:** http://localhost/api/docs
**ReDoc:** http://localhost/api/redoc

### Key API Endpoints

#### Documents Module
```
POST   /api/v1/documents/                 - Create document
GET    /api/v1/documents/                 - List documents
GET    /api/v1/documents/{id}             - Get document
POST   /api/v1/documents/{id}/revise      - Create revision
PUT    /api/v1/documents/{id}/approve     - Approve document
```

#### Equipment Module
```
POST   /api/v1/equipment/                 - Create equipment
GET    /api/v1/equipment/                 - List equipment
GET    /api/v1/equipment/calibration-due  - Get calibration alerts
POST   /api/v1/equipment/calibration      - Record calibration
```

#### LIMS Module
```
POST   /api/v1/lims/customers             - Create customer
POST   /api/v1/lims/test-requests         - Create test request
POST   /api/v1/lims/samples               - Create sample
POST   /api/v1/lims/test-results          - Record test result
```

#### AI Models
```
POST   /api/v1/ai/predict-equipment-failure  - Predict equipment failure
POST   /api/v1/ai/suggest-root-cause         - NC root cause suggestion
POST   /api/v1/ai/estimate-test-duration     - Estimate test duration
POST   /api/v1/ai/classify-document          - Classify document
```

#### Analytics
```
GET    /api/v1/analytics/executive-dashboard  - Executive KPIs
GET    /api/v1/analytics/quality-metrics      - Quality metrics
GET    /api/v1/analytics/operational-metrics  - Operational data
GET    /api/v1/analytics/traceability/{type}/{id} - Audit trail
```

---

## 🔧 Development

### Local Development Setup

1. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up local database**

```bash
# Install PostgreSQL locally or use Docker
docker run -d \
  --name lims-postgres-dev \
  -e POSTGRES_DB=lims_qms_db \
  -e POSTGRES_USER=lims_user \
  -e POSTGRES_PASSWORD=lims_password \
  -p 5432:5432 \
  postgres:15-alpine
```

4. **Run the backend**

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. **Run Streamlit dashboard**

```bash
streamlit run streamlit_app/Home.py
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio httpx

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Code Quality

```bash
# Format code
black backend/

# Sort imports
isort backend/

# Lint code
flake8 backend/ --max-line-length=120
```

---

## 🗄️ Database Management

### Backup Database

```bash
# Manual backup
./scripts/backup_database.sh

# The script creates compressed backups in /backups/postgres/
# Format: lims_qms_db_YYYYMMDD_HHMMSS.sql.gz
```

### Restore Database

```bash
# Restore from backup
./scripts/restore_database.sh /backups/postgres/lims_qms_db_20240615_120000.sql.gz
```

### Automated Backups

Set up a cron job for automated backups:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/lims-qms-platform/scripts/backup_database.sh
```

---

## 🎨 Streamlit Dashboard

### Role-Based Views

The dashboard provides different views based on user roles:

1. **Executive Dashboard**
   - Monthly test requests
   - Active non-conformances
   - Revenue tracking
   - KPI trends

2. **Quality Manager Dashboard**
   - NC trend analysis
   - CAPA effectiveness
   - Audit findings
   - Risk matrix (5x5)

3. **Laboratory Technician Dashboard**
   - Equipment status
   - Sample tracking
   - Calibration alerts
   - Test completion rates

4. **Customer Portal**
   - Real-time test tracking
   - Sample status
   - Test progress timeline
   - Submit new requests

### Customization

Dashboard can be customized by editing:
- `streamlit_app/Home.py` - Main dashboard
- Add pages in `streamlit_app/pages/` for additional views

---

## 🔐 Security

### Authentication & Authorization

The platform uses JWT-based authentication:

```python
# Login endpoint
POST /api/v1/auth/login
{
  "username": "user@example.com",
  "password": "your-password"
}

# Returns JWT token
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}

# Use token in subsequent requests
Authorization: Bearer eyJ...
```

### Security Best Practices

1. **Change default credentials** in production
2. **Use HTTPS** with valid SSL certificates
3. **Set strong SECRET_KEY** (use `openssl rand -hex 32`)
4. **Enable firewall** rules for database access
5. **Regular security updates** via CI/CD pipeline
6. **Database encryption** at rest and in transit
7. **Regular backups** with encrypted storage

---

## 🚢 Deployment

### Production Deployment

1. **Update environment configuration**

```bash
cp .env.production .env
# Edit .env with production values
```

2. **SSL Certificates**

```bash
# Place SSL certificates in nginx/ssl/
# Update nginx/conf.d/lims.conf with SSL configuration
```

3. **Deploy with Docker Compose**

```bash
docker-compose -f docker-compose.yml up -d
```

4. **Health Checks**

```bash
# API health
curl http://localhost/health

# Database connection
docker-compose exec backend python -c "from backend.core.database import engine; engine.connect()"
```

### CI/CD Pipeline

GitHub Actions workflow automatically:
- Runs linting (Black, isort, Flake8)
- Executes unit tests
- Builds Docker images
- Deploys to staging (develop branch)
- Deploys to production (main branch)

**Workflow file:** `.github/workflows/ci-cd.yml`

---

## 📊 Monitoring & Logging

### Application Logs

```bash
# View backend logs
docker-compose logs -f backend

# View all logs
docker-compose logs -f

# Export logs
docker-compose logs > logs/app_$(date +%Y%m%d).log
```

### Database Monitoring

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U lims_user -d lims_qms_db

# Check database size
SELECT pg_size_pretty(pg_database_size('lims_qms_db'));

# Active connections
SELECT count(*) FROM pg_stat_activity;
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Maintenance tasks

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Support

For support and questions:

- **Issues:** [GitHub Issues](https://github.com/your-org/lims-qms-platform/issues)
- **Documentation:** [Wiki](https://github.com/your-org/lims-qms-platform/wiki)
- **Email:** support@your-organization.com

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Dashboard powered by [Streamlit](https://streamlit.io/)
- Charts using [Plotly](https://plotly.com/)
- ML models with [scikit-learn](https://scikit-learn.org/)

---

## 📝 Changelog

### Version 1.0.0 (Session 10)
- ✅ Complete LIMS-QMS platform implementation
- ✅ AI/ML integration (predictive maintenance, NC root cause, test duration, document classification)
- ✅ Analytics dashboard with role-based views
- ✅ Customer portal
- ✅ Docker deployment with Nginx reverse proxy
- ✅ CI/CD pipeline with GitHub Actions
- ✅ Automated database backups
- ✅ Comprehensive API documentation
- ✅ End-to-end traceability

---

## 🗺️ Roadmap

**Future Enhancements:**
- [ ] Mobile app for field technicians
- [ ] Advanced analytics with predictive insights
- [ ] Integration with external LIMS systems
- [ ] Multi-language support
- [ ] Enhanced AI models with deep learning
- [ ] Blockchain for document integrity
- [ ] IoT integration for real-time equipment monitoring

---

**Built with ❤️ for Solar PV Testing Laboratories**
