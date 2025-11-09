# Session 8: Audit & Risk Management System

## Overview

This module implements a comprehensive Audit & Risk Management System compliant with ISO 17025:2017 and ISO 9001:2015 requirements for laboratory and quality management systems.

## Features

### 1. Audit Program Management (QSF1701)
- Annual audit program planning
- Multi-year audit program tracking
- Approval workflow (Prepared-Reviewed-Approved)
- Program status tracking

### 2. Audit Scheduling
- Audit type management (Internal, External, Surveillance, Certification)
- Audit scope definition (Department, Process, System, Product)
- Lead auditor and team assignment
- Planned vs. actual date tracking
- Standard reference linkage (ISO 17025, ISO 9001, IEC standards)

### 3. Audit Findings with NC Linkage
- Finding types: NCR (Non-Conformance Report), OFI (Opportunity for Improvement), OBS (Observation)
- Severity classification: Critical, Major, Minor
- Root cause analysis integration
- Corrective action tracking
- NC reference linkage (Session 7 integration)
- Effectiveness verification
- Target date and closure tracking

### 4. Risk Register with 5x5 Risk Matrix
- Risk categories: Operational, Strategic, Financial, Compliance, Technical
- 5x5 Risk Matrix implementation
  - Likelihood scale: 1=Rare to 5=Almost Certain
  - Impact scale: 1=Insignificant to 5=Catastrophic
  - Risk score calculation: Likelihood × Impact
  - Risk levels: LOW (1-4), MEDIUM (5-12), HIGH (13-16), CRITICAL (17-25)
- Inherent vs. Residual risk assessment
- Risk treatment strategies: Accept, Mitigate, Transfer, Avoid
- Risk review history tracking
- Risk owner assignment

### 5. Compliance Tracking
- ISO 17025:2017 clause-level compliance
- ISO 9001:2015 clause-level compliance
- Compliance status: Compliant, Non-Compliant, Partial, Not Applicable
- Evidence reference documentation
- Audit schedule integration

## Database Schema

### Tables

1. **audit_program**
   - Annual audit program records (QSF1701)
   - Program year, scope, objectives
   - Approval workflow tracking

2. **audit_schedule**
   - Individual audit scheduling
   - Audit number: AUD-YYYY-XXX
   - Audit type, scope, and team assignment

3. **audit_findings**
   - Audit findings and observations
   - Finding number: FND-YYYY-XXX
   - NC linkage support
   - Corrective action tracking

4. **risk_register**
   - Risk identification and assessment
   - Risk number: RISK-YYYY-XXX
   - 5x5 matrix calculations
   - Risk treatment planning

5. **risk_review_history**
   - Historical risk assessment changes
   - Review tracking

6. **compliance_tracking**
   - ISO clause-level compliance
   - Evidence documentation
   - Audit scheduling

### Views

- `v_upcoming_audits`: Scheduled and in-progress audits
- `v_high_risks`: High and critical risks
- `v_open_findings`: Open and in-progress findings
- `v_compliance_summary`: Compliance statistics by standard

### Functions

- `generate_audit_number()`: Auto-generate AUD-YYYY-XXX
- `generate_finding_number()`: Auto-generate FND-YYYY-XXX
- `generate_risk_number()`: Auto-generate RISK-YYYY-XXX

## API Endpoints

### Base URL: `/api/v1/audit-risk`

#### Audit Programs
- `POST /programs` - Create audit program
- `GET /programs` - List audit programs (with filters)
- `GET /programs/{id}` - Get specific program
- `PUT /programs/{id}` - Update program
- `DELETE /programs/{id}` - Delete program

#### Audit Schedules
- `POST /schedules` - Schedule new audit
- `GET /schedules` - List scheduled audits (with filters)
- `GET /schedules/{id}` - Get specific audit
- `PUT /schedules/{id}` - Update audit schedule
- `DELETE /schedules/{id}` - Delete audit

#### Audit Findings
- `POST /findings` - Create finding
- `GET /findings` - List findings (with filters)
- `GET /findings/{id}` - Get specific finding
- `PUT /findings/{id}` - Update finding
- `DELETE /findings/{id}` - Delete finding

#### Risk Register
- `POST /risks` - Create risk
- `GET /risks` - List risks (with filters)
- `GET /risks/{id}` - Get specific risk
- `PUT /risks/{id}` - Update risk
- `DELETE /risks/{id}` - Delete risk

#### Compliance Tracking
- `POST /compliance` - Create compliance record
- `GET /compliance` - List compliance records (with filters)
- `GET /compliance/{id}` - Get specific record
- `PUT /compliance/{id}` - Update compliance record

#### Dashboard & Analytics
- `GET /dashboard/summary` - Overall statistics
- `GET /dashboard/risk-matrix` - 5x5 risk matrix data
- `GET /dashboard/upcoming-audits` - Upcoming audits (default: 30 days)
- `GET /dashboard/overdue-findings` - Overdue findings

## Frontend UI (Streamlit)

### Pages

1. **Dashboard**
   - Key metrics overview
   - Upcoming audits
   - High-priority risks
   - Recent activity

2. **Audit Program**
   - View all audit programs
   - Create new program
   - QSF1701 form generation

3. **Audit Schedule**
   - Audit calendar view
   - Schedule new audits
   - Audit team management

4. **Audit Findings**
   - Findings list with filters
   - Create new findings
   - NC linkage support
   - Corrective action tracking

5. **Risk Register**
   - Risk list with 5x5 matrix
   - Create and assess risks
   - Risk matrix visualization
   - Treatment plan management

6. **Compliance Tracking**
   - ISO clause compliance matrix
   - Add compliance records
   - Compliance summary dashboard

## Installation & Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
   ```bash
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

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Initialize database**
   ```bash
   # Create database
   createdb lims_qms

   # Run schema
   psql -U postgres -d lims_qms -f database/schema/08_audit_risk.sql
   ```

6. **Run backend API**
   ```bash
   cd backend
   python main.py
   # API will be available at http://localhost:8000
   ```

7. **Run frontend**
   ```bash
   cd frontend
   streamlit run app.py
   # UI will be available at http://localhost:8501
   ```

## Usage Examples

### Creating an Audit Program

```python
import requests

data = {
    "program_year": 2025,
    "program_title": "Annual Internal Audit Program 2025",
    "scope": "Complete QMS coverage",
    "objectives": "Verify ISO 17025 compliance",
    "prepared_by": "Quality Manager",
    "status": "DRAFT",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31"
}

response = requests.post(
    "http://localhost:8000/api/v1/audit-risk/programs",
    json=data
)
print(response.json())
```

### Creating a Risk

```python
data = {
    "risk_category": "TECHNICAL",
    "risk_description": "Equipment breakdown",
    "inherent_likelihood": 4,
    "inherent_impact": 4,
    "residual_likelihood": 2,
    "residual_impact": 3,
    "risk_treatment": "MITIGATE",
    "risk_owner": "Technical Manager",
    "status": "ACTIVE"
}

response = requests.post(
    "http://localhost:8000/api/v1/audit-risk/risks",
    json=data
)
print(response.json())
```

## Integration with Other Sessions

### Session 7: NC & CAPA Integration
- Audit findings can reference NC numbers (NC-YYYY-XXX)
- Seamless linkage between audit findings and non-conformances
- Root cause analysis alignment

### Session 2: Document Management Integration
- Audit reports linked to QMS documents
- Compliance evidence reference to controlled documents
- Procedure and form integration

## ISO Compliance

### ISO 17025:2017 Requirements
- Clause 8.8: Internal Audits
- Clause 6.1: Risk-based thinking
- Clause 8.9: Management Reviews

### ISO 9001:2015 Requirements
- Clause 9.2: Internal Audit
- Clause 6.1: Actions to address risks and opportunities
- Clause 10.1: Nonconformity and Corrective Action

## Best Practices

1. **Audit Planning**
   - Create annual audit program at year start
   - Schedule audits at least 2 weeks in advance
   - Assign competent lead auditors

2. **Finding Management**
   - Document findings immediately after audit
   - Link findings to NCs for major non-conformances
   - Set realistic target dates for closure
   - Verify effectiveness of corrective actions

3. **Risk Management**
   - Review risks quarterly
   - Update risk assessments after incidents
   - Document risk treatment plans
   - Track residual risk reduction

4. **Compliance Tracking**
   - Update after each audit
   - Review compliance status monthly
   - Link evidence to documents
   - Plan audits based on compliance gaps

## Security Considerations

- Role-based access control (future enhancement)
- Audit trail for all changes
- Digital signatures for approval workflows
- Data encryption at rest and in transit

## Maintenance

### Regular Tasks
- Monthly: Review open findings
- Quarterly: Review risk register
- Annually: Update audit program
- Continuous: Monitor compliance status

### Database Maintenance
```sql
-- Cleanup old review history (older than 5 years)
DELETE FROM risk_review_history
WHERE created_at < NOW() - INTERVAL '5 years';

-- Archive completed audits (older than 3 years)
-- Implement archival strategy as needed
```

## Troubleshooting

### Common Issues

1. **API Connection Error**
   - Ensure backend is running on port 8000
   - Check DATABASE_URL in .env

2. **Database Connection Failed**
   - Verify PostgreSQL is running
   - Check database credentials
   - Ensure database 'lims_qms' exists

3. **Frontend Not Loading**
   - Check Streamlit is running on port 8501
   - Verify API_URL in frontend code
   - Check CORS settings

## Future Enhancements

- [ ] Email notifications for upcoming audits
- [ ] Automated audit report generation
- [ ] Risk heat map visualization
- [ ] Advanced analytics dashboard
- [ ] Mobile app for audit data collection
- [ ] Integration with external audit management tools
- [ ] AI-powered risk prediction
- [ ] Automated compliance gap analysis

## Support & Documentation

- API Documentation: http://localhost:8000/docs
- OpenAPI Spec: http://localhost:8000/openapi.json
- Redoc: http://localhost:8000/redoc

## License

Internal use - Proprietary software for LIMS-QMS Platform

## Version History

- v1.0.0 (Session 8) - Initial release
  - Audit Program Management
  - Audit Scheduling
  - Audit Findings with NC Linkage
  - Risk Register with 5x5 Matrix
  - Compliance Tracking
