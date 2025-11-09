# API Documentation - Audit & Risk Management System

## Base URL
```
http://localhost:8000/api/v1/audit-risk
```

## Authentication
Currently, the API does not require authentication. Future versions will implement JWT-based authentication.

## Common Response Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `404` - Not Found
- `500` - Internal Server Error

## Endpoints

### Audit Programs

#### Create Audit Program
```http
POST /programs
Content-Type: application/json

{
  "program_year": 2025,
  "program_title": "Annual Internal Audit Program 2025",
  "scope": "Complete QMS and LIMS coverage",
  "objectives": "Verify ISO 17025 compliance",
  "prepared_by": "Quality Manager",
  "reviewed_by": "Technical Manager",
  "approved_by": "CEO",
  "status": "DRAFT",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31"
}
```

Response:
```json
{
  "id": 1,
  "program_number": "QSF1701-2025",
  "program_year": 2025,
  "program_title": "Annual Internal Audit Program 2025",
  "scope": "Complete QMS and LIMS coverage",
  "objectives": "Verify ISO 17025 compliance",
  "prepared_by": "Quality Manager",
  "reviewed_by": "Technical Manager",
  "approved_by": "CEO",
  "status": "DRAFT",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:30:00"
}
```

#### List Audit Programs
```http
GET /programs?year=2025&status=APPROVED
```

Query Parameters:
- `year` (optional) - Filter by program year
- `status` (optional) - Filter by status (DRAFT, APPROVED, ACTIVE, COMPLETED)

#### Get Single Audit Program
```http
GET /programs/{id}
```

#### Update Audit Program
```http
PUT /programs/{id}
Content-Type: application/json

{
  "status": "APPROVED",
  "approved_by": "CEO"
}
```

#### Delete Audit Program
```http
DELETE /programs/{id}
```

---

### Audit Schedules

#### Create Audit Schedule
```http
POST /schedules
Content-Type: application/json

{
  "program_id": 1,
  "audit_type": "INTERNAL",
  "audit_scope": "PROCESS",
  "department": "Testing Lab",
  "process_area": "Sample Management",
  "standard_reference": "ISO 17025:2017 - Clause 7.4",
  "planned_date": "2025-02-15",
  "duration_days": 1,
  "lead_auditor": "John Smith",
  "audit_team": "John Smith, Mary Johnson",
  "auditee": "Lab Manager",
  "status": "SCHEDULED"
}
```

Response:
```json
{
  "id": 1,
  "audit_number": "AUD-2025-001",
  "program_id": 1,
  "audit_type": "INTERNAL",
  "audit_scope": "PROCESS",
  "department": "Testing Lab",
  "process_area": "Sample Management",
  "standard_reference": "ISO 17025:2017 - Clause 7.4",
  "planned_date": "2025-02-15",
  "actual_date": null,
  "duration_days": 1,
  "lead_auditor": "John Smith",
  "audit_team": "John Smith, Mary Johnson",
  "auditee": "Lab Manager",
  "status": "SCHEDULED",
  "remarks": null,
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:30:00"
}
```

#### List Audit Schedules
```http
GET /schedules?audit_type=INTERNAL&status=SCHEDULED&department=Testing Lab
```

Query Parameters:
- `program_id` (optional) - Filter by program
- `audit_type` (optional) - Filter by type (INTERNAL, EXTERNAL, SURVEILLANCE, CERTIFICATION)
- `status` (optional) - Filter by status (SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED)
- `department` (optional) - Filter by department

---

### Audit Findings

#### Create Audit Finding
```http
POST /findings
Content-Type: application/json

{
  "audit_id": 1,
  "finding_type": "NCR",
  "severity": "MAJOR",
  "category": "DOCUMENTATION",
  "clause_reference": "ISO 17025:2017 - 7.5.1",
  "area_audited": "Document Control",
  "description": "Several controlled documents found without proper version control",
  "objective_evidence": "Documents QSF-2024-001 v1.2 and QSF-2024-003 v2.0 not updated",
  "requirement": "All controlled documents shall have proper version control",
  "responsible_person": "Quality Manager",
  "target_date": "2025-03-15",
  "status": "OPEN",
  "nc_reference": "NC-2025-001"
}
```

Response:
```json
{
  "id": 1,
  "finding_number": "FND-2025-001",
  "audit_id": 1,
  "finding_type": "NCR",
  "severity": "MAJOR",
  "category": "DOCUMENTATION",
  "clause_reference": "ISO 17025:2017 - 7.5.1",
  "area_audited": "Document Control",
  "description": "Several controlled documents found without proper version control",
  "objective_evidence": "Documents QSF-2024-001 v1.2 and QSF-2024-003 v2.0 not updated",
  "requirement": "All controlled documents shall have proper version control",
  "root_cause": null,
  "corrective_action": null,
  "responsible_person": "Quality Manager",
  "target_date": "2025-03-15",
  "actual_closure_date": null,
  "status": "OPEN",
  "nc_reference": "NC-2025-001",
  "effectiveness_verified": false,
  "verified_by": null,
  "verified_date": null,
  "attachments": null,
  "created_at": "2025-02-16T14:30:00",
  "updated_at": "2025-02-16T14:30:00"
}
```

#### List Audit Findings
```http
GET /findings?finding_type=NCR&status=OPEN&severity=MAJOR
```

Query Parameters:
- `audit_id` (optional) - Filter by audit
- `finding_type` (optional) - Filter by type (NCR, OFI, OBS)
- `status` (optional) - Filter by status (OPEN, IN_PROGRESS, CLOSED, VERIFIED)
- `severity` (optional) - Filter by severity (CRITICAL, MAJOR, MINOR)

---

### Risk Register

#### Create Risk
```http
POST /risks
Content-Type: application/json

{
  "risk_category": "TECHNICAL",
  "process_area": "Testing",
  "department": "Testing Lab",
  "risk_description": "Equipment breakdown during critical testing period",
  "risk_source": "Equipment age, heavy usage",
  "consequences": "Delayed test results, customer dissatisfaction",
  "existing_controls": "Preventive maintenance schedule, calibration program",
  "inherent_likelihood": 4,
  "inherent_impact": 4,
  "residual_likelihood": 2,
  "residual_impact": 3,
  "risk_treatment": "MITIGATE",
  "treatment_plan": "Implement predictive maintenance; Maintain backup equipment",
  "risk_owner": "Technical Manager",
  "review_frequency": "QUARTERLY",
  "status": "ACTIVE"
}
```

Response:
```json
{
  "id": 1,
  "risk_number": "RISK-2025-001",
  "risk_category": "TECHNICAL",
  "process_area": "Testing",
  "department": "Testing Lab",
  "risk_description": "Equipment breakdown during critical testing period",
  "risk_source": "Equipment age, heavy usage",
  "consequences": "Delayed test results, customer dissatisfaction",
  "existing_controls": "Preventive maintenance schedule, calibration program",
  "inherent_likelihood": 4,
  "inherent_impact": 4,
  "inherent_risk_score": 16,
  "inherent_risk_level": "HIGH",
  "residual_likelihood": 2,
  "residual_impact": 3,
  "residual_risk_score": 6,
  "residual_risk_level": "MEDIUM",
  "risk_treatment": "MITIGATE",
  "treatment_plan": "Implement predictive maintenance; Maintain backup equipment",
  "risk_owner": "Technical Manager",
  "target_date": null,
  "review_frequency": "QUARTERLY",
  "last_review_date": null,
  "next_review_date": null,
  "status": "ACTIVE",
  "remarks": null,
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:30:00"
}
```

#### List Risks
```http
GET /risks?risk_category=TECHNICAL&status=ACTIVE
```

Query Parameters:
- `risk_category` (optional) - Filter by category (OPERATIONAL, STRATEGIC, FINANCIAL, COMPLIANCE, TECHNICAL)
- `status` (optional) - Filter by status (ACTIVE, CLOSED, MONITORING)
- `department` (optional) - Filter by department
- `risk_level` (optional) - Filter by residual risk level (LOW, MEDIUM, HIGH, CRITICAL)

---

### Compliance Tracking

#### Create Compliance Record
```http
POST /compliance
Content-Type: application/json

{
  "standard_name": "ISO 17025:2017",
  "clause_number": "6.4",
  "clause_title": "Equipment",
  "requirement": "Laboratory shall have access to equipment required for correct performance",
  "compliance_status": "COMPLIANT",
  "evidence_reference": "Equipment Master List, Calibration Records",
  "responsible_person": "Technical Manager"
}
```

Response:
```json
{
  "id": 1,
  "standard_name": "ISO 17025:2017",
  "clause_number": "6.4",
  "clause_title": "Equipment",
  "requirement": "Laboratory shall have access to equipment required for correct performance",
  "compliance_status": "COMPLIANT",
  "evidence_reference": "Equipment Master List, Calibration Records",
  "last_audit_date": null,
  "next_audit_date": null,
  "responsible_person": "Technical Manager",
  "remarks": null,
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:30:00"
}
```

#### List Compliance Records
```http
GET /compliance?standard_name=ISO 17025:2017&compliance_status=COMPLIANT
```

Query Parameters:
- `standard_name` (optional) - Filter by standard
- `compliance_status` (optional) - Filter by status (COMPLIANT, NON_COMPLIANT, PARTIAL, NOT_APPLICABLE)

---

### Dashboard & Analytics

#### Dashboard Summary
```http
GET /dashboard/summary
```

Response:
```json
{
  "audits": {
    "total": 12,
    "scheduled": 5,
    "completed": 7
  },
  "findings": {
    "total": 23,
    "open": 8,
    "ncr": 5
  },
  "risks": {
    "total": 15,
    "high_critical": 3
  },
  "compliance": {
    "total_clauses": 45,
    "compliant": 42,
    "compliance_percentage": 93.33
  }
}
```

#### Risk Matrix
```http
GET /dashboard/risk-matrix
```

Response: Returns 5x5 matrix with risks grouped by likelihood × impact.

#### Upcoming Audits
```http
GET /dashboard/upcoming-audits?days=30
```

Query Parameters:
- `days` (optional) - Number of days to look ahead (default: 30)

#### Overdue Findings
```http
GET /dashboard/overdue-findings
```

Returns all open/in-progress findings past their target date.

---

## Data Models

### Audit Program
- `id`: integer
- `program_number`: string (QSF1701-YYYY)
- `program_year`: integer
- `program_title`: string
- `scope`: text
- `objectives`: text
- `prepared_by`: string
- `reviewed_by`: string
- `approved_by`: string
- `status`: enum (DRAFT, APPROVED, ACTIVE, COMPLETED)
- `start_date`: date
- `end_date`: date
- `created_at`: timestamp
- `updated_at`: timestamp

### Audit Schedule
- `id`: integer
- `audit_number`: string (AUD-YYYY-XXX)
- `program_id`: foreign key
- `audit_type`: enum (INTERNAL, EXTERNAL, SURVEILLANCE, CERTIFICATION)
- `audit_scope`: enum (DEPARTMENT, PROCESS, SYSTEM, PRODUCT)
- `department`: string
- `process_area`: string
- `standard_reference`: string
- `planned_date`: date
- `actual_date`: date (nullable)
- `duration_days`: integer
- `lead_auditor`: string
- `audit_team`: text
- `auditee`: string
- `status`: enum (SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED)
- `remarks`: text
- `created_at`: timestamp
- `updated_at`: timestamp

### Audit Finding
- `id`: integer
- `finding_number`: string (FND-YYYY-XXX)
- `audit_id`: foreign key
- `finding_type`: enum (NCR, OFI, OBS)
- `severity`: enum (CRITICAL, MAJOR, MINOR)
- `category`: enum (DOCUMENTATION, PROCESS, EQUIPMENT, PERSONNEL, CALIBRATION)
- `clause_reference`: string
- `area_audited`: string
- `description`: text
- `objective_evidence`: text
- `requirement`: text
- `root_cause`: text
- `corrective_action`: text
- `responsible_person`: string
- `target_date`: date
- `actual_closure_date`: date (nullable)
- `status`: enum (OPEN, IN_PROGRESS, CLOSED, VERIFIED)
- `nc_reference`: string (nullable, links to NC-YYYY-XXX)
- `effectiveness_verified`: boolean
- `verified_by`: string
- `verified_date`: date
- `attachments`: text (JSON)
- `created_at`: timestamp
- `updated_at`: timestamp

### Risk Register
- `id`: integer
- `risk_number`: string (RISK-YYYY-XXX)
- `risk_category`: enum (OPERATIONAL, STRATEGIC, FINANCIAL, COMPLIANCE, TECHNICAL)
- `process_area`: string
- `department`: string
- `risk_description`: text
- `risk_source`: string
- `consequences`: text
- `existing_controls`: text
- `inherent_likelihood`: integer (1-5)
- `inherent_impact`: integer (1-5)
- `inherent_risk_score`: computed (likelihood × impact)
- `inherent_risk_level`: computed (LOW/MEDIUM/HIGH/CRITICAL)
- `residual_likelihood`: integer (1-5)
- `residual_impact`: integer (1-5)
- `residual_risk_score`: computed
- `residual_risk_level`: computed
- `risk_treatment`: enum (ACCEPT, MITIGATE, TRANSFER, AVOID)
- `treatment_plan`: text
- `risk_owner`: string
- `target_date`: date
- `review_frequency`: enum (MONTHLY, QUARTERLY, ANNUALLY)
- `last_review_date`: date
- `next_review_date`: date
- `status`: enum (ACTIVE, CLOSED, MONITORING)
- `remarks`: text
- `created_at`: timestamp
- `updated_at`: timestamp

### Compliance Tracking
- `id`: integer
- `standard_name`: string
- `clause_number`: string
- `clause_title`: string
- `requirement`: text
- `compliance_status`: enum (COMPLIANT, NON_COMPLIANT, PARTIAL, NOT_APPLICABLE)
- `evidence_reference`: text
- `last_audit_date`: date
- `next_audit_date`: date
- `responsible_person`: string
- `remarks`: text
- `created_at`: timestamp
- `updated_at`: timestamp

## Error Handling

All endpoints return standard error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common errors:
- Missing required fields
- Invalid enum values
- Foreign key violations
- Duplicate entries (for unique fields)

## Rate Limiting

Currently no rate limiting is implemented. Future versions will include rate limiting.

## Versioning

API version is included in the URL path: `/api/v1/`

## Interactive API Documentation

Visit these URLs when the backend is running:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json
