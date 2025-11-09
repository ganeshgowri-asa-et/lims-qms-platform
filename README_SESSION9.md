# LIMS-QMS Platform - Session 9: Analytics Dashboards & Customer Portal

## Overview

This is the complete implementation of **Session 9** for the LIMS-QMS Platform, featuring:

### 📊 Analytics Dashboards
- **Executive Dashboard**: High-level KPIs, revenue tracking, quality metrics, and strategic insights
- **Operational Dashboard**: Lab operations, sample tracking, equipment calibration, and training compliance
- **Quality Dashboard**: Non-conformance trends, CAPA effectiveness, audit findings, and risk management

### 🌐 Customer Portal
- **Test Request Submission**: Online form for customers to submit test requests
- **Real-Time Sample Tracking**: Live tracking of sample status and test progress
- **Request Management**: View all test requests with filtering and status updates
- **Reports & Certificates**: Access and download completed test reports

### 🔐 Role-Based Access
- Executive
- Lab Manager
- Quality Manager
- Technician
- Customer

## Technology Stack

### Backend
- **FastAPI**: High-performance REST API framework
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL/SQLite**: Database (SQLite for development)
- **Pydantic**: Data validation

### Frontend
- **Streamlit**: Multi-page web application framework
- **Plotly**: Interactive charts and visualizations
- **Pandas**: Data manipulation

## Project Structure

```
lims-qms-platform/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models (Sessions 2-8)
│   └── api/
│       ├── analytics.py     # Analytics endpoints
│       ├── customer_portal.py  # Customer portal endpoints
│       └── samples.py       # Sample management endpoints
├── streamlit_app/
│   ├── app.py               # Main Streamlit app
│   └── pages/
│       ├── 1_📊_Executive_Dashboard.py
│       ├── 2_⚙️_Operational_Dashboard.py
│       ├── 3_🎯_Quality_Dashboard.py
│       └── 4_🌐_Customer_Portal.py
├── scripts/
│   └── generate_sample_data.py  # Sample data generation
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README_SESSION9.md      # This file
```

## Installation & Setup

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings (optional for development)
# Default uses SQLite database
```

### Step 3: Initialize Database & Generate Sample Data

```bash
# Generate sample data (will also initialize database)
python scripts/generate_sample_data.py
```

## Running the Application

### Option 1: Run Both Services Separately

#### Terminal 1 - Start FastAPI Backend
```bash
cd backend
python main.py
```
The API will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

#### Terminal 2 - Start Streamlit Frontend
```bash
streamlit run streamlit_app/app.py
```
The web app will be available at: `http://localhost:8501`

### Option 2: Run with Background Process

```bash
# Start backend in background
cd backend
python main.py &

# Start frontend
streamlit run streamlit_app/app.py
```

## Features by Dashboard

### 📊 Executive Dashboard

**Key Metrics:**
- Test Requests (current month vs previous)
- Revenue (current month vs previous)
- Active Samples count
- Quality Rate percentage
- On-Time Delivery percentage
- Non-Conformances count

**Visualizations:**
- Test volume trend (12 months)
- Revenue trend (12 months)
- Performance gauge charts
- Strategic insights

### ⚙️ Operational Dashboard

**Key Metrics:**
- Average Turnaround Time
- Equipment Calibration Compliance
- Training Compliance
- Sample Status Distribution

**Visualizations:**
- Sample status pie chart and bar chart
- Equipment by category
- Training compliance by department
- Weekly workload analysis
- Calibration compliance gauge

**Features:**
- Equipment calibration alerts
- Training reminders
- Lab capacity status

### 🎯 Quality Dashboard

**Key Metrics:**
- Non-Conformances (month-to-date)
- CAPA Effectiveness
- Audit Findings (year-to-date)
- Total NC (year-to-date)

**Visualizations:**
- NC trend analysis (6 months)
- NC distribution by severity
- NC distribution by category
- CAPA effectiveness gauge
- CAPA status funnel
- Audit findings by type
- Quality rate trend (12 months)
- Risk assessment matrix (5x5)

**Features:**
- Risk register with likelihood/impact scoring
- Audit findings analysis
- Root cause tracking

### 🌐 Customer Portal

**Capabilities:**

1. **Dashboard Overview**
   - Total test requests
   - Active requests
   - Completed requests
   - Active samples count

2. **Submit Test Request**
   - Sample description
   - Test type selection (IEC 61215, 61730, 61701, 62716)
   - Required completion date
   - Priority selection
   - Number of samples
   - Additional notes

3. **Real-Time Sample Tracking**
   - Live sample status updates
   - Test progress percentage
   - Detailed test parameter status
   - Sample information view
   - Auto-refresh capability

4. **My Test Requests**
   - View all requests with filters
   - Status filtering
   - Date range filtering
   - Test type filtering
   - Request statistics visualization

5. **Reports & Certificates**
   - Download completed reports
   - Access test certificates
   - Report history

## Database Schema

The application includes comprehensive database models from Sessions 2-8:

### Session 2: Document Management
- qms_documents
- document_revisions
- document_distribution

### Session 3: Equipment & Calibration
- equipment_master
- calibration_records
- preventive_maintenance_schedule

### Session 4: Training & Competency
- training_master
- employee_training_matrix
- training_attendance

### Session 5: LIMS Core
- customers
- test_requests
- samples
- test_parameters

### Session 6: IEC Test Reports
- iec_test_execution
- iec_test_reports

### Session 7: NC & CAPA
- nonconformances
- root_cause_analysis
- capa_actions

### Session 8: Audit & Risk
- audit_program
- audit_schedule
- audit_findings
- risk_register

### Session 9: Analytics & Portal
- customer_portal_users
- analytics_kpis

## API Endpoints

### Analytics Endpoints

```
GET /api/analytics/kpis/executive      # Executive KPIs
GET /api/analytics/kpis/operational    # Operational KPIs
GET /api/analytics/kpis/quality        # Quality KPIs
GET /api/analytics/trends/test-volume  # Test volume trend
GET /api/analytics/trends/quality-metrics  # Quality metrics trend
```

### Customer Portal Endpoints

```
POST /api/portal/test-requests         # Create test request
GET /api/portal/test-requests/{customer_id}  # Get customer requests
GET /api/portal/samples/track/{customer_id}  # Track samples
GET /api/portal/samples/{sample_id}/details  # Sample details
GET /api/portal/dashboard/{customer_id}      # Customer dashboard
```

### Sample Management Endpoints

```
GET /api/samples/status-summary       # Sample status summary
GET /api/samples/{sample_id}          # Get sample details
```

## Usage Guide

### Switching User Roles

In the sidebar, select your user role:
- **Executive**: Access to Executive Dashboard
- **Lab Manager**: Access to all dashboards
- **Quality Manager**: Access to Quality Dashboard
- **Technician**: Access to Operational Dashboard
- **Customer**: Access to Customer Portal only

### For Customers

1. Select "Customer" role in sidebar
2. Enter Customer ID (use 1, 2, or 3 for demo)
3. Navigate to "Customer Portal"
4. Submit test requests, track samples, view reports

### Dashboard Features

- **Auto-refresh**: Enable auto-refresh for real-time data updates
- **Interactive Charts**: Click and hover on charts for details
- **Filters**: Use filters to customize data views
- **Export**: Download data and reports (where available)

## Development Notes

### Mock Data vs Real Data

The application is designed to work with both:
- **Real API Data**: When backend is running, dashboards fetch live data
- **Mock Data**: When API is unavailable, dashboards display sample data for demonstration

### Extending the Application

To add new features:

1. **Add Database Model**: Update `backend/models.py`
2. **Create API Endpoint**: Add to `backend/api/`
3. **Create Dashboard Page**: Add to `streamlit_app/pages/`
4. **Update Sample Data**: Modify `scripts/generate_sample_data.py`

## Troubleshooting

### Database Issues

```bash
# Reset database
rm lims_qms.db  # If using SQLite
python scripts/generate_sample_data.py
```

### Port Already in Use

```bash
# Change API port in .env
API_PORT=8001

# Change Streamlit port
streamlit run streamlit_app/app.py --server.port 8502
```

### Import Errors

```bash
# Ensure you're in the project root directory
cd /path/to/lims-qms-platform

# Reinstall dependencies
pip install -r requirements.txt
```

## Performance Optimization

- **Caching**: Dashboards use `@st.cache_data` with 5-minute TTL
- **Pagination**: Large datasets can be paginated in future versions
- **Database Indexing**: Key fields are indexed for faster queries
- **Query Optimization**: Uses SQLAlchemy ORM with optimized queries

## Security Considerations

For production deployment:

1. **Change SECRET_KEY**: Update in `.env`
2. **Enable HTTPS**: Configure SSL certificates
3. **Database Security**: Use PostgreSQL with proper authentication
4. **API Authentication**: Implement JWT tokens
5. **CORS Configuration**: Restrict allowed origins
6. **Input Validation**: Already implemented with Pydantic

## Future Enhancements

- Real-time notifications (WebSocket)
- Email alerts for important events
- Advanced analytics with ML predictions
- Mobile-responsive design
- Multi-language support
- Report generation in PDF format
- Digital signatures for certificates

## Support

For issues or questions:
- Check API documentation: `http://localhost:8000/docs`
- Review logs in terminal
- Verify database connection
- Ensure all dependencies are installed

## License

This project is part of the LIMS-QMS Platform implementation.

---

**Session 9 Implementation Complete** ✅

Built with FastAPI, Streamlit, Plotly, and SQLAlchemy
