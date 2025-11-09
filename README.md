# LIMS-QMS Platform

**AI-Powered Laboratory Information Management System (LIMS) & Quality Management System (QMS) Platform for Solar PV Testing & R&D Laboratories**

Complete Digital Transformation with ISO 17025/9001 Compliance

## 🌟 Overview

The LIMS-QMS Platform is a comprehensive, integrated solution for managing laboratory operations and quality management systems in solar PV testing and R&D laboratories. Built with modern technologies, it provides end-to-end digital transformation from sample receipt to test report generation, while maintaining full compliance with ISO/IEC 17025:2017 and ISO 9001:2015 standards.

## 📋 Features

### Session 2: Document Management System
- Automated document numbering (QSF-YYYY-XXX)
- Version control (major.minor)
- Digital signatures and approval workflow
- Full-text search capabilities
- PDF generation with watermarks

### Session 3: Equipment Calibration & Maintenance
- Automated equipment ID generation (EQP-XXXX)
- Calibration due alerts (30/15/7 days)
- Preventive maintenance scheduling
- OEE (Overall Equipment Effectiveness) tracking
- QR code generation for equipment

### Session 4: Training & Competency
- Training master database
- Employee training matrix
- Competency gap analysis
- Automatic certificate generation
- Training compliance tracking (QSF0203/0205/0206)

### Session 5: LIMS Core - Test Request & Sample Management
- Test request management (TRQ numbering)
- Sample tracking with barcode generation
- Quote automation
- Sample lifecycle management
- Test parameter configuration

### Session 6: IEC Test Report Generation
- IEC 61215, 61730, 61701 test execution
- Automated test data acquisition
- Graph generation for test results
- Pass/fail criteria evaluation
- Digital certificates with QR codes

### Session 7: Non-Conformance & CAPA
- NC management with NC-YYYY-XXX numbering
- AI-powered root cause suggestions
- 5-Why and Fishbone analysis
- CAPA action tracking
- Effectiveness verification

### Session 8: Audit & Risk Management
- Annual audit program (QSF1701)
- 5x5 risk assessment matrix
- Audit findings with NC linkage
- Compliance tracking
- Risk mitigation planning

### Session 9: Analytics Dashboard & Customer Portal ⭐ NEW
- **Executive Dashboard**: KPIs, revenue, quality metrics
- **Operational Dashboard**: Lab operations, equipment, training
- **Quality Dashboard**: NC trends, CAPA effectiveness, audit findings
- **Customer Portal**: Test request submission, real-time sample tracking
- **Interactive Visualizations**: Plotly charts and graphs
- **Role-Based Access**: Different views for different roles

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, high-performance web framework for APIs
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM)
- **PostgreSQL/SQLite**: Relational database
- **Pydantic**: Data validation using Python type annotations

### Frontend
- **Streamlit**: Multi-page web application framework
- **Plotly**: Interactive scientific graphing library
- **Pandas**: Data manipulation and analysis

### Additional Tools
- **ReportLab**: PDF generation
- **QRCode**: QR code generation
- **python-jose**: JWT token handling
- **passlib**: Password hashing

## 📁 Project Structure

```
lims-qms-platform/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection and session
│   ├── models.py               # SQLAlchemy database models
│   └── api/
│       ├── analytics.py        # Analytics endpoints
│       ├── customer_portal.py  # Customer portal endpoints
│       └── samples.py          # Sample management endpoints
├── streamlit_app/
│   ├── app.py                  # Main Streamlit application
│   └── pages/
│       ├── 1_📊_Executive_Dashboard.py
│       ├── 2_⚙️_Operational_Dashboard.py
│       ├── 3_🎯_Quality_Dashboard.py
│       └── 4_🌐_Customer_Portal.py
├── scripts/
│   └── generate_sample_data.py # Sample data generation script
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── run.sh                     # Linux/Mac startup script
├── run.bat                    # Windows startup script
├── README.md                  # This file
├── README_SESSION9.md         # Detailed Session 9 documentation
└── LICENSE                    # License file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Git (optional)

### Installation

1. **Clone the repository** (or download as ZIP)
```bash
git clone <repository-url>
cd lims-qms-platform
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables** (optional)
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Generate sample data**
```bash
python scripts/generate_sample_data.py
```

### Running the Application

#### Option 1: Use the startup script (Recommended)

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

**Windows:**
```bash
run.bat
```

#### Option 2: Manual startup

**Terminal 1 - Start Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Start Frontend:**
```bash
streamlit run streamlit_app/app.py
```

### Access the Application

- **Streamlit Web App**: http://localhost:8501
- **FastAPI Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📊 Dashboards

### Executive Dashboard
High-level strategic metrics including:
- Test request volume and trends
- Revenue tracking and growth
- Quality rate and on-time delivery
- Performance gauge charts
- Strategic insights

### Operational Dashboard
Day-to-day operations metrics:
- Sample status distribution
- Equipment calibration compliance
- Training compliance by department
- Workload analysis
- Alert notifications

### Quality Dashboard
Quality management metrics:
- Non-conformance trend analysis
- CAPA effectiveness tracking
- Audit findings distribution
- Risk assessment matrix (5x5)
- Quality rate trends

### Customer Portal
Customer-facing features:
- Submit test requests online
- Real-time sample tracking with progress bars
- View all test requests with filtering
- Access reports and certificates
- Dashboard with customer statistics

## 🔐 User Roles

The platform supports role-based access control:

- **Executive**: Access to Executive Dashboard
- **Lab Manager**: Access to all dashboards
- **Quality Manager**: Access to Quality Dashboard
- **Technician**: Access to Operational Dashboard
- **Customer**: Access to Customer Portal only

Switch roles in the sidebar to see different views.

## 🗄️ Database Schema

The platform includes comprehensive database models covering:

- **Document Management**: QMS documents, revisions, distribution
- **Equipment**: Equipment master, calibration records, maintenance
- **Training**: Training master, employee matrix, attendance
- **LIMS Core**: Customers, test requests, samples, parameters
- **Testing**: IEC test execution, test reports
- **Quality**: Non-conformances, root cause analysis, CAPA
- **Audit**: Audit programs, schedules, findings
- **Risk**: Risk register with likelihood/impact scoring
- **Analytics**: KPIs and customer portal data

## 📡 API Endpoints

### Analytics
- `GET /api/analytics/kpis/executive` - Executive KPIs
- `GET /api/analytics/kpis/operational` - Operational KPIs
- `GET /api/analytics/kpis/quality` - Quality KPIs
- `GET /api/analytics/trends/test-volume` - Test volume trend
- `GET /api/analytics/trends/quality-metrics` - Quality metrics trend

### Customer Portal
- `POST /api/portal/test-requests` - Create test request
- `GET /api/portal/test-requests/{customer_id}` - Get customer requests
- `GET /api/portal/samples/track/{customer_id}` - Track samples
- `GET /api/portal/samples/{sample_id}/details` - Sample details
- `GET /api/portal/dashboard/{customer_id}` - Customer dashboard

### Samples
- `GET /api/samples/status-summary` - Sample status summary
- `GET /api/samples/{sample_id}` - Get sample by ID

Full API documentation available at: http://localhost:8000/docs

## 📈 Key Features

### Real-Time Tracking
- Live sample status updates
- Test progress percentage
- Equipment calibration status
- Training compliance monitoring

### Interactive Visualizations
- Plotly charts for all metrics
- Gauge charts for KPIs
- Trend lines and bar charts
- Pie charts for distributions
- Funnel charts for workflow

### Data Caching
- 5-minute cache for dashboard data
- 1-minute cache for real-time tracking
- Optimized database queries

### Mobile Responsive
- Streamlit's responsive design
- Works on tablets and mobile devices

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./lims_qms.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=your-secret-key-here

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

### Database Options

**SQLite (Development):**
```
DATABASE_URL=sqlite:///./lims_qms.db
```

**PostgreSQL (Production):**
```
DATABASE_URL=postgresql://user:password@localhost:5432/lims_qms_db
```

## 🧪 Testing

### Sample Data

The platform includes a comprehensive sample data generator:

```bash
python scripts/generate_sample_data.py
```

This creates:
- 3 sample customers
- 50 test requests
- 30+ samples with test parameters
- 45 equipment items
- 33 non-conformances
- Audit programs and schedules
- Risk register entries

### Demo Credentials

**Customer Portal:**
- Customer ID: 1, 2, or 3

## 📚 Documentation

- **README.md**: This file - General overview
- **README_SESSION9.md**: Detailed Session 9 documentation
- **API Docs**: http://localhost:8000/docs (when running)

## 🛡️ Security

For production deployment:

1. Change `SECRET_KEY` in `.env`
2. Enable HTTPS with SSL certificates
3. Use PostgreSQL with authentication
4. Implement JWT authentication for API
5. Configure CORS properly
6. Enable rate limiting
7. Set up database backups

## 🤝 Contributing

This is an implementation project for LIMS-QMS Platform development.

## 📝 License

See LICENSE file for details.

## 🆘 Troubleshooting

### Database Issues
```bash
# Reset database
rm lims_qms.db
python scripts/generate_sample_data.py
```

### Port Already in Use
```bash
# Change ports in .env or use different ports
streamlit run streamlit_app/app.py --server.port 8502
```

### Module Import Errors
```bash
# Ensure you're in the project root
cd /path/to/lims-qms-platform
pip install -r requirements.txt
```

## 🎯 Roadmap

Future enhancements:
- [ ] Real-time WebSocket notifications
- [ ] Email alerts and notifications
- [ ] Advanced ML-based analytics
- [ ] PDF report generation
- [ ] Digital signature integration
- [ ] Multi-language support
- [ ] Advanced search capabilities
- [ ] Workflow automation
- [ ] Integration with lab instruments
- [ ] Mobile app

## 📧 Support

For issues, questions, or feature requests:
- Check the API documentation
- Review the README_SESSION9.md for detailed information
- Check logs in the terminal
- Verify database connection and dependencies

## 🌟 Acknowledgments

Built with:
- FastAPI
- Streamlit
- Plotly
- SQLAlchemy
- Pandas
- And many other amazing open-source libraries

---

**LIMS-QMS Platform** - Digital Transformation for Laboratory Management

Version 1.0.0 | Session 9 Complete ✅
