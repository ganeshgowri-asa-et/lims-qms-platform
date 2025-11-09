# Session 2: Data Capture & Form Filling Engine

## Overview

This session implements a comprehensive **Data Capture & Form Filling Engine** for the Organization OS, building on Session 1's Document Management System. The engine provides dynamic form generation, workflow management, validation, digital signatures, and export capabilities.

## 🎯 Features Implemented

### 1. Dynamic Form Generation
- **Template Parser**: Auto-generate forms from Level 4 Excel/Word templates
- **Supported Input Types**:
  - Text, Number, Date, DateTime
  - Dropdown, Multiselect, Radio, Checkbox
  - File upload, Signature capture
  - Table, Section, Calculated fields
- **Smart Field Detection**: Automatically detect field types from template structure
- **Conditional Fields**: Support for parent-child field relationships
- **Field Validation**: Built-in validation rules (required, format, range, pattern)

### 2. Doer-Checker-Approver Workflow
- **Three-Tier Approval Mechanism**:
  - **Doer**: Creates and fills initial data
  - **Checker**: Reviews and validates data, can request changes
  - **Approver**: Final sign-off with digital signature
- **State Machine**: Robust workflow state transitions
- **Role-Based Access Control**: Permissions for each tier
- **Email/Notification Triggers**: Automated notifications at each stage
- **Workflow Tracking**: Complete audit trail of all transitions

### 3. Data Validation & Quality
- **Real-Time Validation**: Validate during data entry
- **Cross-Field Validation**: Rules spanning multiple fields
- **Duplicate Detection**: Configurable duplicate checking (exact/fuzzy)
- **Mandatory Field Enforcement**: Required field validation
- **Custom Validation Rules**: Extensible validation framework
- **Data Type Checking**: Type-safe validation for all field types

### 4. Record Generation (Level 5)
- **Unique Record IDs**: Format: `{TEMPLATE_CODE}-{YEAR}-{SEQUENCE}`
- **Hierarchical Linking**: Links to parent documents (Level 1-4)
- **Complete Audit Trail**: Track all changes with timestamps
- **Version Control**: Full history of record modifications
- **Batch Creation**: Support for bulk record creation

### 5. Electronic Signatures
- **Digital Signature Capture**: Base64 encoded signature images
- **Signature Verification**: SHA-256 hash verification
- **Certificate Management**: Digital certificates for non-repudiation
- **Timestamp & User Info**: Complete signature metadata
- **Role-Based Signing**: Separate signatures for doer/checker/approver

### 6. Export Capabilities
- **PDF Export**: Professional PDF reports with branding
- **Excel Export**: Structured Excel files with workflow history
- **Template Export**: Blank templates for bulk data entry
- **Customizable Output**: Include/exclude signatures and workflow

### 7. Integration Points
- **Document Management**: Seamless integration with Level 1-4 documents
- **Notification System**: Automated alerts for workflow events
- **Audit Logging**: Complete traceability of all actions
- **API-First Design**: RESTful APIs for all operations

---

## 📁 Project Structure

```
backend/
├── models/
│   ├── form.py                    # Core form models (Session 1)
│   ├── form_workflow.py           # NEW: Workflow, signatures, validation
│   └── __init__.py                # Updated with new models
├── services/
│   ├── template_parser.py         # NEW: Parse Excel/Word templates
│   ├── form_generator.py          # NEW: Generate forms from templates
│   ├── form_data_service.py       # NEW: Form data capture service
│   ├── workflow_engine.py         # NEW: Workflow state machine
│   ├── validation_engine.py       # NEW: Validation framework
│   ├── signature_service.py       # NEW: Digital signature management
│   └── export_service.py          # NEW: PDF/Excel export
├── api/endpoints/
│   ├── forms.py                   # Basic form endpoints (Session 1)
│   └── form_capture.py            # NEW: Enhanced form capture APIs
└── main.py                        # Updated with new routes

uploads/
├── templates/                     # Uploaded template files
└── ...

exports/
├── pdf/                          # PDF exports
├── excel/                        # Excel exports
└── templates/                    # Template files for bulk entry
```

---

## 🗄️ Database Schema

### New Tables

#### 1. `workflow_transitions`
Tracks all workflow state changes
```sql
- record_id → form_records.id
- from_status, to_status (enum)
- action (enum: submit, approve, reject, etc.)
- actor_id → users.id
- comments
- metadata (JSON)
- transition_time
```

#### 2. `form_signatures`
Digital signatures for records
```sql
- record_id → form_records.id
- user_id → users.id
- role (doer, checker, approver)
- signature_data (Base64)
- signature_hash (SHA-256)
- ip_address, user_agent
- signed_at
- certificate_data (JSON)
- is_verified
```

#### 3. `form_validation_rules`
Advanced validation rules
```sql
- field_id → form_fields.id
- rule_name, rule_type
- rule_config (JSON)
- error_message
- is_active
- priority
- depends_on_fields (JSON)
```

#### 4. `form_history`
Version history for records
```sql
- record_id → form_records.id
- version_number
- changed_by_id → users.id
- change_type
- changes (JSON)
- snapshot (JSON)
- comments
- changed_at
```

#### 5. `form_duplicate_checks`
Duplicate detection configuration
```sql
- template_id → form_templates.id
- check_name
- check_fields (JSON)
- check_logic (exact, fuzzy)
- tolerance
- is_active
- error_message
```

#### 6. `form_approval_matrix`
Approval workflow configuration
```sql
- template_id → form_templates.id
- condition (JSON)
- requires_checker, requires_approver
- auto_assign_checker, auto_assign_approver
- checker_role_id, approver_role_id
- escalation_hours
```

#### 7. `form_notification_templates`
Notification templates for workflow
```sql
- name
- trigger_event
- recipient_role
- subject_template, body_template
- notification_type
- is_active
```

#### 8. `form_data_sources`
External data sources for auto-population
```sql
- name
- source_type (api, database, file)
- connection_config (JSON)
- query_template
- field_mappings (JSON)
- cache_duration
```

---

## 🔌 API Endpoints

Base URL: `/api/v1/form-capture`

### Template Management

#### Upload Template
```http
POST /templates/upload
Content-Type: multipart/form-data

Body:
- file: Excel/Word template file
- document_id: (optional) Link to Level 4 document
- category: (optional) Template category

Response:
{
  "template_id": 1,
  "template_code": "EQP-A1B2",
  "template_name": "Equipment Qualification Form",
  "fields_count": 15
}
```

#### Get Template Details
```http
GET /templates/{template_id}

Response:
{
  "id": 1,
  "name": "Equipment Qualification Form",
  "code": "EQP-A1B2",
  "fields": [
    {
      "id": 1,
      "field_name": "equipment_name",
      "field_label": "Equipment Name *",
      "field_type": "TEXT",
      "is_required": true,
      "validation_rules": {...}
    },
    ...
  ]
}
```

#### Publish Template
```http
POST /templates/{template_id}/publish

Response:
{
  "message": "Template published successfully",
  "is_published": true
}
```

### Form Record Management

#### Create Record
```http
POST /records

Body:
{
  "template_id": 1,
  "title": "Equipment #123 Qualification",
  "form_data": {
    "equipment_name": "Spectrophotometer",
    "serial_number": "SN-12345",
    "calibration_date": "2024-01-15"
  },
  "auto_submit": false
}

Response:
{
  "record_id": 1,
  "record_number": "EQP-2024-0001",
  "status": "draft"
}
```

#### Get Record
```http
GET /records/{record_id}

Response:
{
  "record": {
    "id": 1,
    "record_number": "EQP-2024-0001",
    "status": "submitted",
    "doer_id": 5,
    "checker_id": 10,
    "approver_id": null
  },
  "template": {...},
  "fields": [...],
  "workflow_history": [...],
  "signatures": [...]
}
```

#### Update Record
```http
PUT /records/{record_id}

Body:
{
  "form_data": {
    "equipment_name": "Updated Name"
  },
  "partial": true
}
```

#### Delete Record
```http
DELETE /records/{record_id}
```

### Workflow Operations

#### Submit Record
```http
POST /records/{record_id}/submit

Body:
{
  "comments": "Submitted for review",
  "signature_data": "data:image/png;base64,..."
}

Response:
{
  "message": "Record submitted successfully",
  "status": "submitted"
}
```

#### Assign Checker
```http
POST /records/{record_id}/assign-checker

Body:
{
  "user_id": 10,
  "comments": "Please review"
}
```

#### Checker Review
```http
POST /records/{record_id}/checker-review

Body:
{
  "approved": true,
  "comments": "All data verified",
  "signature_data": "data:image/png;base64,..."
}
```

#### Assign Approver
```http
POST /records/{record_id}/assign-approver

Body:
{
  "user_id": 15,
  "comments": "For final approval"
}
```

#### Approver Review
```http
POST /records/{record_id}/approver-review

Body:
{
  "approved": true,
  "comments": "Approved",
  "signature_data": "data:image/png;base64,..."
}
```

#### Request Changes
```http
POST /records/{record_id}/request-changes

Body:
{
  "comments": "Please update field X"
}
```

### Validation

#### Validate Form Data
```http
POST /templates/{template_id}/validate

Body:
{
  "equipment_name": "Test",
  "serial_number": ""
}

Response:
{
  "is_valid": false,
  "errors": {
    "serial_number": ["Serial Number is required"]
  }
}
```

### Export

#### Export to PDF
```http
GET /records/{record_id}/export/pdf?include_signatures=true&include_workflow=true

Response: PDF file download
```

#### Export to Excel
```http
GET /records/{record_id}/export/excel?include_workflow=true

Response: Excel file download
```

#### Export Template
```http
GET /templates/{template_id}/export/excel

Response: Blank template Excel file
```

### Utilities

#### Auto-Populate Fields
```http
GET /templates/{template_id}/auto-populate

Response:
{
  "template_id": 1,
  "populated_fields": {
    "user_name": "John Doe",
    "date": "2024-01-15"
  }
}
```

#### Get Statistics
```http
GET /templates/{template_id}/statistics

Response:
{
  "template_id": 1,
  "total_records": 45,
  "by_status": {
    "draft": 5,
    "submitted": 10,
    "completed": 30
  }
}
```

---

## 🔄 Workflow States

```
┌─────────┐
│  DRAFT  │
└────┬────┘
     │ submit
     ▼
┌──────────┐
│SUBMITTED │
└────┬─────┘
     │ assign_checker
     ▼
┌────────────┐    checker_reject    ┌──────────────────┐
│ IN_REVIEW  ├────────────────────► │CHECKER_REJECTED  │
└────┬───────┘                      └──────────────────┘
     │ checker_approve
     ▼
┌───────────────────┐
│CHECKER_APPROVED   │
└────┬──────────────┘
     │ assign_approver
     ▼
┌────────────────┐   approver_reject   ┌───────────────────┐
│APPROVER_REVIEW ├────────────────────►│APPROVER_REJECTED  │
└────┬───────────┘                     └───────────────────┘
     │ approver_approve
     ▼
┌───────────┐
│ COMPLETED │
└───────────┘
```

---

## 🚀 Usage Examples

### Example 1: Upload and Parse Template

```python
# Upload Excel template
files = {'file': open('equipment_form.xlsx', 'rb')}
response = requests.post(
    'http://localhost:8000/api/v1/form-capture/templates/upload',
    files=files,
    headers={'Authorization': f'Bearer {token}'}
)
template_id = response.json()['template_id']
```

### Example 2: Create and Submit Record

```python
# Create record
record_data = {
    'template_id': 1,
    'title': 'Equipment Qualification',
    'form_data': {
        'equipment_name': 'HPLC System',
        'manufacturer': 'Waters',
        'model': 'Alliance e2695'
    }
}
response = requests.post(
    'http://localhost:8000/api/v1/form-capture/records',
    json=record_data,
    headers={'Authorization': f'Bearer {token}'}
)
record_id = response.json()['record_id']

# Submit for review
submit_data = {
    'comments': 'Ready for review',
    'signature_data': signature_base64
}
requests.post(
    f'http://localhost:8000/api/v1/form-capture/records/{record_id}/submit',
    json=submit_data,
    headers={'Authorization': f'Bearer {token}'}
)
```

### Example 3: Complete Workflow

```python
# 1. Doer submits
submit_record(record_id, user_id=doer_id)

# 2. Assign checker
assign_checker(record_id, checker_id=checker_id)

# 3. Checker reviews
checker_review(record_id, approved=True, checker_id=checker_id)

# 4. Assign approver
assign_approver(record_id, approver_id=approver_id)

# 5. Approver approves
approver_review(record_id, approved=True, approver_id=approver_id)

# 6. Export to PDF
pdf_file = export_to_pdf(record_id)
```

---

## 🛠️ Service Layer Architecture

### 1. TemplateParser
- Parses Excel (.xlsx, .xls) templates
- Parses Word (.docx, .doc) templates
- Parses PDF templates (basic)
- Auto-detects field types
- Generates field definitions

### 2. FormGenerator
- Creates FormTemplate from parsed data
- Manages form fields
- Publishes templates
- Clones templates
- Updates field definitions

### 3. ValidationEngine
- Validates form data
- Applies field type validation
- Executes custom validation rules
- Cross-field validation
- Duplicate detection
- Calculates computed fields

### 4. WorkflowEngine
- Manages state transitions
- Enforces workflow rules
- Creates workflow history
- Handles signature capture
- Sends notifications
- Validates workflow permissions

### 5. SignatureService
- Creates digital signatures
- Generates signature certificates
- Verifies signatures
- Creates signature tokens
- Generates QR codes
- Manages signature metadata

### 6. FormDataService
- Orchestrates form operations
- Creates/updates records
- Auto-populates fields
- Manages form values
- Batch operations
- Statistics and reporting

### 7. ExportService
- Exports to PDF
- Exports to Excel
- Template export
- Custom formatting
- Workflow history inclusion

---

## 🔐 Security Features

1. **JWT Authentication**: All endpoints protected
2. **Role-Based Access**: Doer/Checker/Approver roles
3. **Digital Signatures**: SHA-256 hashing
4. **Audit Trail**: Complete action logging
5. **Soft Deletes**: Records never truly deleted
6. **IP Tracking**: Record IP addresses for signatures
7. **Certificate Verification**: Validate signature integrity

---

## 📊 Key Metrics

- **35+ API Endpoints**: Complete CRUD + workflow operations
- **8 New Database Tables**: Comprehensive data model
- **7 Service Classes**: Modular, testable architecture
- **14 Field Types**: Support for all common input types
- **9 Workflow States**: Complete state machine
- **12 Workflow Actions**: All approval operations
- **2 Export Formats**: PDF and Excel

---

## 🎓 Integration with Session 1

This implementation seamlessly integrates with Session 1:

1. **Document Linking**: FormTemplate.document_id links to Level 4 documents
2. **User Management**: Uses existing User, Role, Permission models
3. **Notifications**: Extends existing Notification system
4. **Audit Trail**: Uses existing AuditLog and TraceabilityLink
5. **Authentication**: Leverages existing JWT auth system
6. **Database**: Extends existing PostgreSQL schema

---

## 📝 Next Steps

1. **Frontend Integration**: Build Streamlit UI for form filling
2. **Email Notifications**: Configure SMTP for workflow emails
3. **Advanced Validation**: Implement custom validation functions
4. **Bulk Import**: Excel import for bulk record creation
5. **Analytics Dashboard**: Workflow metrics and KPIs
6. **Mobile Support**: Responsive design for mobile devices
7. **AI Integration**: Auto-populate using AI suggestions

---

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all new models are in `backend/models/__init__.py`
   - Check circular import dependencies

2. **Database Errors**
   - Run database migrations
   - Ensure all foreign key relationships are valid

3. **File Upload Issues**
   - Check upload directory permissions
   - Verify file size limits in config

4. **Workflow State Errors**
   - Verify user has correct permissions
   - Check workflow state transitions are valid

---

## 📚 Documentation

- **API Documentation**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Models Documentation**: See `backend/models/form_workflow.py`
- **Service Documentation**: See individual service files

---

## 🏆 Session 2 Summary

Successfully implemented a production-ready **Data Capture & Form Filling Engine** with:

✅ Dynamic form generation from templates
✅ Complete Doer-Checker-Approver workflow
✅ Advanced validation framework
✅ Digital signature integration
✅ PDF/Excel export capabilities
✅ Comprehensive API endpoints
✅ Full audit trail and traceability
✅ Seamless integration with Session 1

The system is now ready for Level 5 record management with complete workflow automation!

---

**Built with ❤️ for LIMS-QMS Organization OS**
