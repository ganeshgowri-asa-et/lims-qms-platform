# LIMS QMS Platform - Non-Conformance & CAPA Management System

AI-Powered Laboratory Information Management System (LIMS) & Quality Management System (QMS) Platform for Solar PV Testing & R&D Laboratories - SESSION 7: Non-Conformance & CAPA Management with AI-powered Root Cause Analysis

## 🌟 Features

### Non-Conformance Management
- ✅ **Automatic NC Numbering**: NC-YYYY-XXX format
- ✅ **Comprehensive Tracking**: Status, severity, source, impact assessment
- ✅ **Multi-source Detection**: Internal audit, customer complaints, process monitoring, calibration, testing, supplier, external audit
- ✅ **Severity Levels**: Critical, Major, Minor with color-coded indicators
- ✅ **Real-time Dashboard**: Visual analytics and metrics

### Root Cause Analysis (RCA)
- 🎯 **5-Why Methodology**: Systematic drill-down to root causes with guided templates
- 🎯 **Fishbone (Ishikawa) Diagram**: 6M analysis (Man, Machine, Method, Material, Measurement, Environment)
- 🤖 **AI-Powered Suggestions**: Automated root cause suggestions using Anthropic Claude or OpenAI GPT
- ✅ **Approval Workflow**: RCA review and approval tracking
- 📊 **Multiple Methods**: Support for Pareto, Fault Tree, and other RCA methodologies

### CAPA Management
- ✅ **Automatic CAPA Numbering**: CAPA-YYYY-XXX format
- ✅ **Corrective & Preventive Actions**: Separate workflows with clear distinction
- ✅ **Assignment & Tracking**: Owner, due dates, status updates, progress monitoring
- ✅ **Effectiveness Verification**: Built-in verification workflow with 1-5 rating scale
- ⏰ **Overdue Alerts**: Automatic identification and highlighting of overdue actions
- 📊 **Progress Monitoring**: Real-time CAPA status dashboard with visual indicators
- 💰 **Cost Tracking**: Estimated vs. actual cost monitoring

### AI Integration
- 🤖 **Anthropic Claude 3.5 Sonnet**: Primary AI model for intelligent suggestions
- 🤖 **OpenAI GPT-4**: Alternative AI provider
- 🧠 **Rule-based Fallback**: Smart keyword-based analysis when AI unavailable
- 📈 **Confidence Scoring**: AI suggestions include confidence ratings

### Technology Stack
- **Backend**: FastAPI (Python) - High-performance async API
- **Frontend**: Streamlit - Interactive web interface
- **Database**: PostgreSQL with SQLAlchemy ORM (SQLite supported for testing)
- **AI**: Anthropic Claude / OpenAI GPT with intelligent fallback
- **Visualization**: Plotly, Pandas, Matplotlib

## 📁 Project Structure

```
lims-qms-platform/
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── nc_routes.py       # NC CRUD endpoints
│   │   │   ├── rca_routes.py      # RCA and AI endpoints
│   │   │   └── capa_routes.py     # CAPA management endpoints
│   │   ├── schemas.py             # Pydantic validation schemas
│   │   └── __init__.py
│   ├── database/
│   │   ├── models.py              # SQLAlchemy ORM models
│   │   ├── database.py            # DB connection & session
│   │   └── __init__.py
│   └── services/
│       ├── nc_service.py          # NC business logic
│       ├── rca_service.py         # RCA business logic
│       ├── capa_service.py        # CAPA business logic
│       └── ai_service.py          # AI integration service
├── frontend/
│   ├── pages/
│   │   ├── 1_NC_Registration.py   # NC registration form
│   │   ├── 2_NC_List.py           # NC list & management
│   │   ├── 3_RCA_Analysis.py      # RCA with 5-Why/Fishbone
│   │   ├── 4_CAPA_Management.py   # CAPA tracking & verification
│   │   └── 5_Dashboard.py         # Analytics & metrics dashboard
│   ├── utils/
│   │   └── api_client.py          # API client wrapper
│   └── app.py                     # Main Streamlit application
├── config.py                      # Configuration management
├── main.py                        # FastAPI application entry point
├── requirements.txt               # Python dependencies
├── setup.sh                       # Setup script
├── run.sh                         # Run script
├── Dockerfile                     # Docker configuration
├── docker-compose.yml             # Docker Compose setup
├── .env.example                   # Environment variables template
├── README.md                      # This file
└── SETUP_GUIDE.md                 # Quick setup guide

```

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# 1. Clone the repository
git clone <repository-url>
cd lims-qms-platform

# 2. Run setup script
chmod +x setup.sh
./setup.sh

# 3. Configure .env file
nano .env  # Edit with your settings

# 4. Start the application
chmod +x run.sh
./run.sh
```

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Start backend (Terminal 1)
python main.py

# 5. Start frontend (Terminal 2)
cd frontend
streamlit run app.py
```

### Option 3: Docker Deployment

```bash
# Start with Docker Compose (includes PostgreSQL)
docker-compose up -d

# Access the application
# Frontend: http://localhost:8501
# Backend: http://localhost:8000
```

## 📚 Complete Usage Guide

### 1. Register Non-Conformance

Navigate to **NC Registration** page:

1. **Basic Information**:
   - Title: Brief description (min 5 characters)
   - Source: Select from predefined sources
   - Severity: Critical/Major/Minor
   - Detected by: Person who found the issue
   - Department: Where it occurred

2. **Detailed Description**:
   - Comprehensive description of what happened
   - Include conditions, observations, evidence

3. **Related Information**:
   - Link to QMS documents (QSF-YYYY-XXX)
   - Equipment ID if applicable (EQP-XXX)
   - Test request number (TRQ-YYYY-XXX)
   - Batch/lot numbers

4. **Impact Assessment**:
   - Quantity affected
   - Cost impact (USD)
   - Description of impact on quality/delivery/customer

5. **Immediate Actions**:
   - Document containment actions taken
   - Prevent further issues

6. **Assignment**:
   - Assign to responsible person
   - Set target closure date

**Result**: System generates NC-YYYY-XXX number automatically

### 2. Perform Root Cause Analysis

Navigate to **RCA Analysis** page:

1. **Select NC**: Choose from dropdown list

2. **Get AI Suggestions** (Optional):
   - Click "🚀 Get AI Suggestions"
   - Review 5-7 AI-generated potential root causes
   - Each includes category, reasoning, and likelihood

3. **Choose RCA Method**:

   **5-Why Analysis**:
   - Answer "Why?" five times
   - Each answer leads to next question
   - Drill down to root cause
   - Best for: Simple, linear problems

   **Fishbone Diagram**:
   - Analyze 6M categories:
     - Man: People, training, competency
     - Machine: Equipment, calibration
     - Method: Procedures, processes
     - Material: Raw materials, components
     - Measurement: Testing, instruments
     - Environment: Conditions, surroundings
   - Best for: Complex, multi-factor problems

4. **Document Root Cause**:
   - State identified root cause
   - List contributing factors
   - Add supporting evidence

5. **Save Analysis**: Creates RCA record linked to NC

### 3. Create CAPA Action

Navigate to **CAPA Management** > **Create CAPA**:

1. **Select Related NC**: Choose NC with completed RCA

2. **CAPA Details**:
   - **Type**:
     - Corrective: Fix existing problem
     - Preventive: Prevent future occurrence
   - **Title**: Action description
   - **Description**: Detailed action plan

3. **Assignment**:
   - Assign to: Responsible person
   - Due date: Target completion
   - Assigned by: Your name

4. **Implementation Plan**:
   - Detailed steps to implement
   - Resources required (list)
   - Estimated cost

5. **Verification Plan**:
   - How effectiveness will be verified
   - Verification criteria
   - Success measures

**Result**: System generates CAPA-YYYY-XXX number

### 4. Track & Update CAPA

Navigate to **CAPA Management** > **CAPA List**:

1. **Monitor Progress**:
   - View all CAPAs with filters
   - Identify overdue actions (highlighted)
   - Check days remaining

2. **Update Status**:
   - Pending → In Progress → Completed → Verified → Closed
   - Document actions taken
   - Add completion evidence

3. **Effectiveness Verification**:
   - Verify implementation
   - Rate effectiveness (1-5 scale)
   - Add verification comments
   - Mark as verified

4. **Close CAPA**:
   - Final review
   - Closure comments
   - Link to updated NC status

### 5. Monitor Dashboard

Navigate to **Dashboard**:

- **Key Metrics**: Total NCs, open count, closure rate, CAPA status
- **Charts**:
  - NC by severity (pie chart)
  - NC by status (bar chart)
  - CAPA by type (pie chart)
  - NC by source (bar chart)
  - Department analysis
- **Recent Activity**: Latest NCs and CAPAs
- **Alerts**: Overdue and upcoming actions

## 🤖 AI Root Cause Analysis

### Configuration

Add to `.env` file:

```env
# Primary (Recommended)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Alternative
OPENAI_API_KEY=sk-your-key-here

# Leave empty for rule-based fallback
```

### How It Works

1. **Input Analysis**: Processes NC description and problem details
2. **Category Mapping**: Maps to 6M categories
3. **Suggestion Generation**:
   - 5-7 potential root causes
   - Category classification
   - Reasoning explanation
   - Likelihood rating (High/Medium/Low)
4. **Confidence Scoring**: Overall confidence in suggestions

### AI Models

| Model | Quality | Speed | Cost |
|-------|---------|-------|------|
| Claude 3.5 Sonnet | ⭐⭐⭐⭐⭐ | Fast | Medium |
| GPT-4 Turbo | ⭐⭐⭐⭐ | Fast | Medium |
| Rule-based | ⭐⭐⭐ | Instant | Free |

## 📊 Database Schema

### Non-Conformances Table
```sql
- id (Primary Key)
- nc_number (Unique, NC-YYYY-XXX)
- title, description
- source, severity, status
- detected_date, detected_by
- department, location
- related_document, equipment, test_request, batch
- impact_description, quantity_affected, cost_impact
- immediate_action, containment info
- assigned_to, target/actual_closure_date
- verification details
- timestamps, audit fields
```

### Root Cause Analysis Table
```sql
- id (Primary Key)
- nc_id (Foreign Key)
- method (5-why, fishbone, etc.)
- five_why_data (JSON)
- fishbone_data (JSON)
- ai_suggestions (JSON)
- root_cause, contributing_factors
- approval workflow
- timestamps
```

### CAPA Actions Table
```sql
- id (Primary Key)
- capa_number (Unique, CAPA-YYYY-XXX)
- nc_id (Foreign Key)
- capa_type (corrective/preventive)
- title, description, status
- assignment details
- due_date, completed_date
- implementation_plan, resources
- cost tracking (estimated/actual)
- verification details
- effectiveness_rating (1-5)
- follow-up requirements
- timestamps, audit fields
```

## 🔒 Security Best Practices

### Production Deployment

1. **Environment Variables**:
   ```env
   DEBUG=False
   SECRET_KEY=<strong-random-key>
   DATABASE_URL=postgresql://secure-user:secure-pass@host/db
   ```

2. **Database Security**:
   - Use strong credentials
   - Restrict network access
   - Enable SSL/TLS
   - Regular backups

3. **API Security**:
   - Implement authentication (JWT recommended)
   - Add rate limiting
   - Use HTTPS only
   - Configure CORS properly

4. **Secrets Management**:
   - Never commit .env to repository
   - Use secrets manager (AWS Secrets Manager, etc.)
   - Rotate API keys regularly

## 📈 Performance Optimization

- **Database**: Add indexes on nc_number, capa_number, status fields
- **API**: Enable caching for statistics endpoints
- **Frontend**: Implement pagination for large datasets
- **AI**: Cache common suggestions to reduce API calls

## 🧪 Testing

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# API tests
pytest tests/api/

# Coverage report
pytest --cov=backend --cov-report=html
```

## 📦 Deployment Options

### Cloud Deployment

**AWS**:
```bash
# Deploy to Elastic Beanstalk
eb init -p python-3.11 lims-qms
eb create lims-qms-env
eb deploy
```

**Google Cloud**:
```bash
# Deploy to App Engine
gcloud app deploy
```

**Heroku**:
```bash
# Deploy to Heroku
heroku create lims-qms-platform
git push heroku main
```

### On-Premise

- Install on Linux server
- Use systemd for service management
- Nginx reverse proxy
- PostgreSQL on separate server

## 🔧 Customization

### Adding Custom Fields

Edit `backend/database/models.py`:
```python
class NonConformance(Base):
    # Add custom field
    custom_field = Column(String(100))
```

### Custom RCA Methods

Edit `backend/services/rca_service.py` to add new methodologies.

### Custom Reports

Add new pages in `frontend/pages/` for custom dashboards.

## 📄 API Documentation

Full API documentation available at: `http://localhost:8000/docs`

Key endpoints:
- `POST /api/nc/` - Create NC
- `GET /api/nc/` - List NCs
- `POST /api/rca/` - Create RCA
- `POST /api/rca/ai/suggestions` - Get AI suggestions
- `POST /api/capa/` - Create CAPA
- `GET /api/capa/overdue` - Get overdue CAPAs

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Streamlit for rapid UI development
- Anthropic and OpenAI for AI capabilities
- SQLAlchemy for robust ORM
- Plotly for beautiful visualizations

## 📞 Support

- **Documentation**: See SETUP_GUIDE.md
- **Issues**: Create GitHub issue
- **Email**: support@example.com

---

**Version**: 1.0.0 | **Session**: 7 - NC & CAPA Management
**Last Updated**: 2024 | **Status**: Production Ready ✅
