# Data Capture & Filling Engine - API Documentation

## Overview

The Data Capture & Filling Engine is a comprehensive system for creating, filling, validating, and approving forms in the LIMS-QMS platform. It implements a sophisticated Doer-Checker-Approver workflow with digital signatures, notifications, and complete audit trails.

## Table of Contents

1. [Architecture](#architecture)
2. [Features](#features)
3. [API Endpoints](#api-endpoints)
4. [Workflow States](#workflow-states)
5. [Usage Examples](#usage-examples)
6. [Integration Guide](#integration-guide)

---

## Architecture

### Components

1. **Database Models** (`backend/models/data_capture.py`)
   - Enhanced form record models with workflow support
   - Digital signature tracking
   - Validation history
   - Bulk upload management
   - Conditional field logic

2. **Services** (`backend/services/`)
   - **ValidationService**: Field and cross-field validation
   - **WorkflowService**: Doer-Checker-Approver workflow management
   - **NotificationService**: Email and in-app notifications
   - **RecordService**: Record creation and management
   - **BulkUploadService**: Batch data import from Excel/CSV
   - **SignatureService**: Digital signature capture and verification

3. **API Endpoints** (`backend/api/endpoints/data_capture.py`)
   - RESTful API for all data capture operations
   - Comprehensive validation and error handling

---

## Features

### 1. Dynamic Form Generation

Forms are automatically generated from Level 4 templates with support for:

- **Input Types**: Text, Number, Date, DateTime, Dropdown, Multiselect, Checkbox, Radio, File, Signature, Table, Calculated Fields
- **Conditional Fields**: Show/hide fields based on other field values
- **Default Values & Placeholders**
- **Real-time Validation**
- **Auto-save Drafts**

### 2. Doer-Checker-Approver Workflow

Three-tier approval process:

```
DRAFT → SUBMITTED → UNDER_REVIEW → APPROVED
          ↓              ↓
    REVISION_REQUIRED  REJECTED
```

**Status Transitions:**
- **DRAFT**: Initial state, editable by doer
- **SUBMITTED**: Submitted for checker review
- **UNDER_REVIEW**: Checked, awaiting approver
- **APPROVED**: Final approval
- **REJECTED**: Rejected by checker/approver
- **REVISION_REQUIRED**: Needs modification
- **CANCELLED**: Cancelled by user
- **ARCHIVED**: Archived for historical purposes

### 3. Validation Engine

**Field-Level Validation:**
- Required fields
- Data type validation (number, date, email, URL)
- Min/max length
- Min/max value
- Pattern/regex validation
- Custom validation expressions

**Cross-Field Validation:**
- Dependent field validation
- Conditional requirements
- Complex business rules

**Data Quality Rules:**
- Completeness checks
- Accuracy validation
- Consistency rules
- Uniqueness verification
- Timeliness constraints

**Duplicate Detection:**
- Configurable field combinations
- Exact, fuzzy, or phonetic matching
- Time-window based detection

### 4. Digital Signatures

Capture and verify digital signatures:
- **Methods**: Drawn, Typed, Uploaded, Certificate-based
- **Signature Types**: Doer, Checker, Approver
- **Verification**: Complete signature chain validation
- **Audit Trail**: IP address, timestamp, device info

### 5. Notifications

Automatic notifications at each workflow stage:
- **In-app Notifications**: Real-time alerts
- **Email Notifications**: Configurable SMTP
- **Notification Types**: Submission, Review, Approval, Rejection, Comments

### 6. Bulk Operations

Batch import from Excel/CSV:
- Template generation for bulk upload
- Row-by-row validation
- Detailed error reporting
- Success/failure tracking
- Download results

### 7. Audit Trail

Complete tracking of all changes:
- Workflow events with timestamps
- Field-level change history
- Version tracking
- User action logging
- IP address and device tracking

---

## API Endpoints

Base URL: `/api/v1/data-capture`

### Record Management

#### Create Record
```http
POST /records
Content-Type: application/json
Authorization: Bearer {token}

{
  "template_id": 1,
  "title": "Daily Quality Check",
  "values": {
    "date": "2025-01-15",
    "inspector": "John Doe",
    "temperature": 23.5,
    "humidity": 45,
    "remarks": "All checks passed"
  },
  "metadata": {},
  "auto_submit": false
}

Response: 201 Created
{
  "id": 123,
  "record_number": "QC-20250115-0001",
  "status": "draft",
  "completion_percentage": 100,
  "validation_score": 100,
  ...
}
```

#### Get Record
```http
GET /records/{record_id}?include_values=true
Authorization: Bearer {token}

Response: 200 OK
{
  "id": 123,
  "record_number": "QC-20250115-0001",
  "values": {...},
  "doer": {...},
  "checker": {...},
  ...
}
```

#### Update Record
```http
PUT /records/{record_id}
Content-Type: application/json
Authorization: Bearer {token}

{
  "values": {
    "temperature": 24.0
  }
}

Response: 200 OK
```

#### List Records
```http
GET /records?template_id=1&status=approved&skip=0&limit=50
Authorization: Bearer {token}

Response: 200 OK
{
  "total": 150,
  "records": [...],
  "skip": 0,
  "limit": 50
}
```

### Workflow Operations

#### Submit Record
```http
POST /records/{record_id}/submit
Content-Type: application/json
Authorization: Bearer {token}

{
  "comments": "Ready for review"
}

Response: 200 OK
{
  "success": true,
  "message": "Record submitted successfully"
}
```

#### Review Record (Checker)
```http
POST /records/{record_id}/review
Content-Type: application/json
Authorization: Bearer {token}

{
  "action": "approve",  // or "reject", "request_revision"
  "comments": "Looks good, approved for final approval"
}

Response: 200 OK
```

#### Approve Record (Approver)
```http
POST /records/{record_id}/approve
Content-Type: application/json
Authorization: Bearer {token}

{
  "action": "approve",  // or "reject", "request_revision"
  "comments": "Final approval granted"
}

Response: 200 OK
```

#### Revise Record
```http
POST /records/{record_id}/revise
Content-Type: application/json
Authorization: Bearer {token}

{
  "values": {
    "temperature": 23.0
  },
  "comments": "Updated temperature reading"
}

Response: 200 OK
```

#### Get Workflow History
```http
GET /records/{record_id}/history
Authorization: Bearer {token}

Response: 200 OK
[
  {
    "action": "submit",
    "from_status": "draft",
    "to_status": "submitted",
    "actor": {...},
    "timestamp": "2025-01-15T10:30:00Z",
    "comments": "Ready for review"
  },
  ...
]
```

#### Get Pending Approvals
```http
GET /pending-approvals
Authorization: Bearer {token}

Response: 200 OK
[
  {
    "record_id": 123,
    "record_number": "QC-20250115-0001",
    "role": "checker",
    "submitted_at": "2025-01-15T10:30:00Z"
  },
  ...
]
```

### Comments

#### Add Comment
```http
POST /records/{record_id}/comments
Content-Type: application/json
Authorization: Bearer {token}

{
  "content": "Please verify the temperature reading",
  "field_id": 5,
  "comment_type": "clarification"
}

Response: 201 Created
```

#### Get Comments
```http
GET /records/{record_id}/comments
Authorization: Bearer {token}

Response: 200 OK
[...]
```

#### Resolve Comment
```http
PUT /comments/{comment_id}/resolve
Authorization: Bearer {token}

Response: 200 OK
```

### Validation

#### Validate Data
```http
POST /validate
Content-Type: application/json
Authorization: Bearer {token}

{
  "template_id": 1,
  "values": {
    "temperature": 23.5,
    "humidity": 45
  }
}

Response: 200 OK
{
  "is_valid": true,
  "errors": [],
  "warnings": [],
  "completion_percentage": 80,
  "validation_score": 100,
  "duplicates": []
}
```

### Draft Operations

#### Save Draft
```http
POST /drafts
Content-Type: application/json
Authorization: Bearer {token}

{
  "template_id": 1,
  "values": {
    "temperature": 23.5
  }
}

Response: 200 OK
{
  "id": 456,
  "draft_data": {...},
  "last_saved_at": "2025-01-15T10:30:00Z"
}
```

#### Get Draft
```http
GET /drafts/{template_id}?record_id=123
Authorization: Bearer {token}

Response: 200 OK
```

### Digital Signatures

#### Capture Signature
```http
POST /records/{record_id}/signatures
Content-Type: application/json
Authorization: Bearer {token}

{
  "signature_type": "approver",
  "signature_data": "data:image/png;base64,...",
  "signature_method": "drawn",
  "ip_address": "192.168.1.1"
}

Response: 201 Created
```

#### Get Signatures
```http
GET /records/{record_id}/signatures
Authorization: Bearer {token}

Response: 200 OK
[...]
```

#### Verify Signature
```http
GET /signatures/{signature_id}/verify
Authorization: Bearer {token}

Response: 200 OK
{
  "signature_id": 789,
  "is_valid": true,
  "signer": {...},
  "signing_timestamp": "2025-01-15T10:30:00Z"
}
```

#### Get Signature Report
```http
GET /records/{record_id}/signature-report
Authorization: Bearer {token}

Response: 200 OK
{
  "record_id": 123,
  "signature_complete": true,
  "missing_signatures": [],
  "signatures": [...]
}
```

### Bulk Upload

#### Upload Bulk Data
```http
POST /bulk-upload/{template_id}
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: <CSV/Excel file>

Response: 200 OK
{
  "upload_id": 101,
  "success": true,
  "total_rows": 100,
  "successful_rows": 95,
  "failed_rows": 5,
  "error_log": [...]
}
```

#### Get Upload Status
```http
GET /bulk-uploads/{upload_id}
Authorization: Bearer {token}

Response: 200 OK
{
  "id": 101,
  "status": "completed",
  "total_rows": 100,
  "successful_rows": 95,
  ...
}
```

#### Download Bulk Template
```http
GET /templates/{template_id}/bulk-template
Authorization: Bearer {token}

Response: 200 OK
Content-Type: text/csv
Content-Disposition: attachment; filename=template_1.csv
```

### Traceability

#### Create Link
```http
POST /records/{record_id}/link
Content-Type: application/json
Authorization: Bearer {token}

{
  "parent_type": "Equipment",
  "parent_id": 42,
  "link_type": "related"
}

Response: 201 Created
```

#### Get Links
```http
GET /records/{record_id}/links
Authorization: Bearer {token}

Response: 200 OK
[...]
```

### Notifications

#### Get Notifications
```http
GET /notifications?unread_only=true&limit=50
Authorization: Bearer {token}

Response: 200 OK
[...]
```

#### Mark as Read
```http
PUT /notifications/{notification_id}/read
Authorization: Bearer {token}

Response: 200 OK
```

#### Get Unread Count
```http
GET /notifications/unread-count
Authorization: Bearer {token}

Response: 200 OK
{
  "count": 5
}
```

---

## Workflow States

### State Diagram

```
┌─────────┐
│  DRAFT  │◄───────────────┐
└────┬────┘                │
     │ submit()            │ revise()
     ▼                     │
┌───────────┐         ┌────────────────────┐
│ SUBMITTED │────────►│ REVISION_REQUIRED  │
└─────┬─────┘         └────────────────────┘
      │ review(approve)
      ▼
┌────────────────┐
│ UNDER_REVIEW   │
└────┬───────────┘
     │ approve(approve)
     ▼
┌──────────┐
│ APPROVED │
└──────────┘
```

### Permissions

| Action | Allowed User | Required Status |
|--------|-------------|----------------|
| Create | Any authenticated user | - |
| Edit | Doer | DRAFT, REVISION_REQUIRED |
| Submit | Doer | DRAFT |
| Review | Checker | SUBMITTED |
| Approve | Approver | UNDER_REVIEW |
| Revise | Doer | REVISION_REQUIRED |
| Cancel | Doer, Admin | Any (except APPROVED) |

---

## Usage Examples

### Complete Workflow Example

```python
import httpx

BASE_URL = "http://localhost:8000/api/v1/data-capture"
TOKEN = "your_jwt_token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# 1. Create a new record
record_data = {
    "template_id": 1,
    "title": "Daily Equipment Check",
    "values": {
        "equipment_id": "EQ-001",
        "date": "2025-01-15",
        "status": "operational",
        "temperature": 22.5,
        "vibration": "normal",
        "notes": "All systems functioning normally"
    }
}

response = httpx.post(f"{BASE_URL}/records", json=record_data, headers=headers)
record = response.json()
record_id = record["id"]

# 2. Validate before submitting
validation = httpx.post(
    f"{BASE_URL}/validate",
    json={"template_id": 1, "values": record_data["values"]},
    headers=headers
).json()

if validation["is_valid"]:
    # 3. Submit for review
    httpx.post(
        f"{BASE_URL}/records/{record_id}/submit",
        json={"comments": "Ready for review"},
        headers=headers
    )

    # 4. Checker reviews (as checker user)
    httpx.post(
        f"{BASE_URL}/records/{record_id}/review",
        json={"action": "approve", "comments": "Looks good"},
        headers=headers
    )

    # 5. Approver approves (as approver user)
    httpx.post(
        f"{BASE_URL}/records/{record_id}/approve",
        json={"action": "approve", "comments": "Approved"},
        headers=headers
    )

    # 6. Capture digital signature
    httpx.post(
        f"{BASE_URL}/records/{record_id}/signatures",
        json={
            "signature_type": "approver",
            "signature_data": "data:image/png;base64,...",
            "signature_method": "drawn"
        },
        headers=headers
    )
```

### Bulk Upload Example

```python
# 1. Download template
template = httpx.get(
    f"{BASE_URL}/templates/1/bulk-template",
    headers=headers
)

with open("template.csv", "wb") as f:
    f.write(template.content)

# 2. Fill in the template and upload
files = {"file": open("filled_template.csv", "rb")}
response = httpx.post(
    f"{BASE_URL}/bulk-upload/1",
    files=files,
    headers=headers
)

upload_result = response.json()
upload_id = upload_result["upload_id"]

# 3. Check upload status
status = httpx.get(
    f"{BASE_URL}/bulk-uploads/{upload_id}",
    headers=headers
).json()

print(f"Uploaded: {status['successful_rows']}/{status['total_rows']}")
```

---

## Integration Guide

### Integrating with Document Management

Records automatically link to their parent Level 4 templates:

```python
# Get record with document lineage
record = httpx.get(f"{BASE_URL}/records/{record_id}", headers=headers).json()
template = record["template"]
document_id = template.get("document_id")  # Level 4 document

# Create explicit traceability link
httpx.post(
    f"{BASE_URL}/records/{record_id}/link",
    json={
        "parent_type": "Document",
        "parent_id": document_id,
        "link_type": "derived_from"
    },
    headers=headers
)
```

### Integrating with Equipment Management

Link records to equipment for maintenance logs:

```python
httpx.post(
    f"{BASE_URL}/records/{record_id}/link",
    json={
        "parent_type": "Equipment",
        "parent_id": equipment_id,
        "link_type": "maintenance_record"
    },
    headers=headers
)
```

### Custom Validation Rules

Add custom validation to a field:

```python
from backend.models import FormFieldValidation, ValidationSeverityEnum

validation_rule = FormFieldValidation(
    field_id=field_id,
    validation_type="custom",
    custom_validator="value > 0 and value < 100",
    error_message="Value must be between 0 and 100",
    severity=ValidationSeverityEnum.ERROR
)
db.add(validation_rule)
db.commit()
```

### Conditional Fields

Show field based on another field's value:

```python
from backend.models import FormFieldCondition

condition = FormFieldCondition(
    field_id=dependent_field_id,
    condition_type="show",
    trigger_field_id=trigger_field_id,
    operator="equals",
    trigger_value="Yes"
)
db.add(condition)
db.commit()
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Best Practices

1. **Always validate before submitting**: Use the `/validate` endpoint
2. **Auto-save drafts**: Implement periodic auto-save using `/drafts`
3. **Check permissions**: Use workflow permission checks before actions
4. **Handle notifications**: Poll `/notifications` or implement WebSocket
5. **Track changes**: Use workflow history for audit compliance
6. **Batch operations**: Use bulk upload for large datasets
7. **Digital signatures**: Capture signatures at each approval stage
8. **Link to parents**: Maintain traceability to documents and equipment

---

## Support

For issues or questions:
- API Documentation: http://localhost:8000/api/docs
- GitHub Issues: https://github.com/ganeshgowri-asa-et/lims-qms-platform/issues
