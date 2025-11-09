# Document & Template Management Module

## Overview

Comprehensive document and template management system for LIMS-QMS platform with advanced features for document lifecycle, version control, traceability, and metadata management.

## Features

### 1. Template Repository & Indexing
- Auto-index Level 4 formats/templates
- Dynamic template addition support
- Categorization by: document type, ISO standard, department, process
- Advanced search and filtering
- Tag-based organization

### 2. Document Hierarchy & Linking
- **Level 1**: Quality Manual, Policy, Vision, Mission
- **Level 2**: Quality System Procedures (ISO 17025/9001)
- **Level 3**: Operation/Execution/Test Procedures (PV standards: IEC 61215, 61730, etc.)
- **Level 4**: Formats, Templates, Checklists, Test Protocols
- **Level 5**: Records generated from Level 4
- **Bi-directional traceability** (upside-down, downside-up)

### 3. Version Control & Revision History
- Automatic version numbering (1.0, 1.1, 2.0)
- Track all changes with timestamp, user, reason
- Change types: Minor, Major, Editorial
- File checksum verification (SHA-256)
- Retention policies

### 4. Document Metadata
- Table of Contents management
- Responsibility Matrix (RACI)
- Equipment/Software/Resources tracking
- KPI definitions and tracking
- Process flowcharts and infographics
- Custom metadata support (JSON)

### 5. Document Lifecycle Management
- Draft → In Review → Approved → Obsolete/Archived
- Doer-Checker-Approver workflow
- Review scheduling
- Retention policies

### 6. Access Control
- Role-based permissions (via existing RBAC)
- Audit trail for all actions
- Document library access

## Database Schema

### Core Tables

#### documents
Main document storage with comprehensive metadata
- Core identification: document_number, title, level, type
- Standards: iso_standard, pv_standard, standard_clause
- Lifecycle: status, effective_date, review_date, retention_policy
- Ownership: document_owner_id, process_owner_id
- Workflow: doer_id, checker_id, approver_id
- Categorization: tags, keywords, metadata (JSON)

#### document_versions
Version history and revision tracking
- Version numbering: version_number, revision_number
- Change tracking: change_summary, change_type, change_reason
- File management: file_path, file_size, checksum
- Retention: retention_until, is_current, is_obsolete

#### template_categories
Template categorization and organization
- Hierarchical categories (parent-child)
- ISO standard mapping
- Department and process area grouping

#### document_links
Bi-directional document linking for traceability
- Link types: derives_from, references, implements, supports
- Section references
- Compliance mapping

### Metadata Tables

#### document_table_of_contents
Structured table of contents
- Section numbering and hierarchy
- Page references
- Sort ordering

#### document_responsibilities
RACI matrix implementation
- Role definitions
- Responsibility flags (R, A, C, I)
- User and department mapping

#### document_equipment
Equipment and resource tracking
- Equipment details and specifications
- Calibration requirements
- Status and location tracking

#### document_kpis
Key Performance Indicators
- Measurement definitions
- Target values and thresholds
- Frequency and responsibility

#### document_flowcharts
Process diagrams and infographics
- Multiple flowchart types (Process Flow, Value Stream Map, Turtle Diagram, SIPOC)
- File attachments
- Structured data (JSON)

## API Endpoints

### Document CRUD

#### Create Document
```http
POST /api/v1/documents/
```

**Request Body:**
```json
{
  "title": "Calibration Procedure for PV Modules",
  "level": "Level 3",
  "document_type": "Procedure",
  "iso_standard": "ISO/IEC 17025",
  "pv_standard": "IEC 61215",
  "description": "Standard procedure for calibrating PV module testing equipment",
  "department": "Quality",
  "review_frequency_months": 12,
  "retention_policy": "Permanent",
  "tags": ["calibration", "pv-modules", "testing"],
  "keywords": ["calibration", "equipment", "IEC61215"]
}
```

**Response:**
```json
{
  "id": 1,
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "document_number": "PROC-2025-0001",
  "title": "Calibration Procedure for PV Modules",
  "level": "Level 3",
  "document_type": "Procedure",
  "status": "Draft",
  "created_at": "2025-01-15T10:30:00Z"
}
```

#### List Documents
```http
GET /api/v1/documents/?level=Level+4&status=Approved&is_template=true
```

**Query Parameters:**
- `level`: Filter by document level
- `status`: Filter by status (Draft, In Review, Approved, Obsolete, Archived)
- `document_type`: Filter by document type
- `iso_standard`: Filter by ISO standard
- `department`: Filter by department
- `is_template`: Filter templates only
- `search`: Search in title, document number, description
- `skip`: Pagination offset (default: 0)
- `limit`: Results per page (default: 100)

#### Get Document Details
```http
GET /api/v1/documents/{document_id}
```

Returns complete document details including all metadata.

#### Update Document
```http
PUT /api/v1/documents/{document_id}
```

#### Delete Document (Soft Delete)
```http
DELETE /api/v1/documents/{document_id}
```

### Document Lifecycle

#### Submit for Review
```http
PUT /api/v1/documents/{document_id}/submit-review
```

**Request Body:**
```json
{
  "checker_id": 5
}
```

#### Approve Document
```http
PUT /api/v1/documents/{document_id}/approve
```

**Request Body:**
```json
{
  "effective_date": "2025-02-01"
}
```

#### Mark as Obsolete
```http
PUT /api/v1/documents/{document_id}/obsolete
```

**Request Body:**
```json
{
  "reason": "Replaced by PROC-2025-0045"
}
```

#### Archive Document
```http
PUT /api/v1/documents/{document_id}/archive
```

### Version Control

#### Create New Version
```http
POST /api/v1/documents/{document_id}/versions
```

**Request:** Multipart form data
- `change_summary`: Description of changes (required)
- `change_type`: "Minor", "Major", or "Editorial" (required)
- `change_reason`: Reason for change (optional)
- `file`: Document file (required)

**Response:**
```json
{
  "id": 10,
  "document_id": 1,
  "version_number": "2.0",
  "revision_number": 5,
  "change_summary": "Updated calibration frequency requirements",
  "change_type": "Major",
  "released_at": "2025-01-15T14:30:00Z",
  "is_current": true
}
```

#### List Document Versions
```http
GET /api/v1/documents/{document_id}/versions
```

Returns all versions in reverse chronological order.

### Document Linking & Traceability

#### Create Document Link
```http
POST /api/v1/documents/links
```

**Request Body:**
```json
{
  "parent_document_id": 10,
  "child_document_id": 25,
  "link_type": "implements",
  "description": "Test protocol implements this procedure",
  "section_reference": "Section 5.2",
  "compliance_reference": "ISO/IEC 17025:2017, 6.4.13"
}
```

#### Get Document Hierarchy
```http
GET /api/v1/documents/{document_id}/hierarchy?direction=both
```

**Query Parameters:**
- `direction`: "up" (parent docs), "down" (child docs), or "both"

**Response:**
```json
{
  "document_id": 25,
  "parent_documents": [
    {
      "id": 10,
      "document_number": "PROC-2025-0001",
      "title": "Calibration Procedure",
      "level": "Level 3",
      "link_type": "implements",
      "section_reference": "Section 5.2"
    }
  ],
  "child_documents": [
    {
      "id": 42,
      "document_number": "FORM-2025-0010",
      "title": "Calibration Record",
      "level": "Level 4",
      "link_type": "derives_from",
      "section_reference": null
    }
  ]
}
```

### Document Metadata Management

#### Table of Contents

**Add TOC Entry:**
```http
POST /api/v1/documents/{document_id}/toc
```

**Request Body:**
```json
{
  "section_number": "5.2.1",
  "section_title": "Equipment Calibration Requirements",
  "page_number": 12,
  "level": 3,
  "parent_section_id": null
}
```

**Get TOC:**
```http
GET /api/v1/documents/{document_id}/toc
```

#### Responsibilities (RACI Matrix)

**Add Responsibility:**
```http
POST /api/v1/documents/{document_id}/responsibilities
```

**Request Body:**
```json
{
  "role_title": "Quality Manager",
  "description": "Oversee calibration process",
  "is_accountable": true,
  "is_consulted": false,
  "is_responsible": false,
  "is_informed": false,
  "user_id": 5,
  "department": "Quality Assurance",
  "tasks": ["Review calibration records", "Approve calibration schedule"]
}
```

**Get Responsibilities:**
```http
GET /api/v1/documents/{document_id}/responsibilities
```

#### Equipment

**Add Equipment:**
```http
POST /api/v1/documents/{document_id}/equipment
```

**Request Body:**
```json
{
  "name": "Solar Simulator AAA Class",
  "equipment_type": "Equipment",
  "model": "SS-1000X",
  "manufacturer": "Solar Test Inc.",
  "specifications": "AAA classification, 1000 W/m², Spectrum AM1.5G",
  "calibration_required": true
}
```

**Get Equipment:**
```http
GET /api/v1/documents/{document_id}/equipment
```

#### KPIs

**Add KPI:**
```http
POST /api/v1/documents/{document_id}/kpis
```

**Request Body:**
```json
{
  "name": "Calibration Compliance Rate",
  "description": "Percentage of equipment calibrated on schedule",
  "category": "Quality",
  "metric": "On-time calibrations / Total calibrations due",
  "unit_of_measure": "percentage",
  "target_value": 95.0,
  "measurement_frequency": "Monthly"
}
```

**Get KPIs:**
```http
GET /api/v1/documents/{document_id}/kpis
```

#### Flowcharts

**Add Flowchart:**
```http
POST /api/v1/documents/{document_id}/flowcharts
```

**Request Body:**
```json
{
  "title": "Calibration Process Flow",
  "flowchart_type": "Process Flow",
  "description": "End-to-end calibration workflow",
  "flowchart_data": {
    "nodes": [
      {"id": "1", "label": "Schedule Calibration"},
      {"id": "2", "label": "Prepare Equipment"},
      {"id": "3", "label": "Perform Calibration"}
    ],
    "edges": [
      {"from": "1", "to": "2"},
      {"from": "2", "to": "3"}
    ]
  }
}
```

**Get Flowcharts:**
```http
GET /api/v1/documents/{document_id}/flowcharts
```

### Template Management

#### Create Template Category
```http
POST /api/v1/documents/templates/categories
```

**Request Body:**
```json
{
  "name": "IEC 61215 Test Protocols",
  "description": "Standard test protocols for IEC 61215 certification",
  "iso_standard": "ISO/IEC 17025",
  "department": "Testing",
  "process_area": "PV Module Testing"
}
```

#### List Template Categories
```http
GET /api/v1/documents/templates/categories
```

#### Index Template
```http
POST /api/v1/documents/{document_id}/index-template
```

**Request Body:**
```json
{
  "category_name": "IEC 61215 Test Protocols",
  "tags": ["iec61215", "pv-modules", "testing"],
  "keywords": ["photovoltaic", "module", "certification", "thermal cycling"],
  "metadata": {
    "test_type": "Thermal Cycling",
    "standard_version": "IEC 61215-2:2021",
    "duration_hours": 200
  }
}
```

#### Bulk Index Templates
```http
POST /api/v1/documents/templates/bulk-index
```

**Request Body:**
```json
{
  "templates": [
    {
      "document_id": 100,
      "category": "Test Protocols",
      "tags": ["iec61215", "thermal"],
      "keywords": ["thermal cycling", "pv module"]
    },
    {
      "document_id": 101,
      "category": "Test Protocols",
      "tags": ["iec61730", "safety"],
      "keywords": ["safety testing", "pv module"]
    }
  ]
}
```

**Response:**
```json
{
  "success": 2,
  "total": 2,
  "indexed_templates": [100, 101]
}
```

#### Search Templates
```http
GET /api/v1/documents/templates/search?query=thermal&tags=iec61215,testing
```

**Query Parameters:**
- `query`: Search text (searches title, description, document number)
- `category_id`: Filter by category
- `iso_standard`: Filter by ISO standard
- `department`: Filter by department
- `tags`: Comma-separated list of tags

## Document Numbering System

### Auto-Generated Numbers

The system automatically generates unique document numbers based on:
- Document level
- Document type
- Year
- Sequential number

### Numbering Formats

| Level | Prefix | Format | Example |
|-------|--------|--------|---------|
| Level 1 | QM, POL | {prefix}-{year}-{seq:04d} | QM-2025-0001 |
| Level 2 | PROC | PROC-{year}-{seq:04d} | PROC-2025-0015 |
| Level 3 | WI, TP | {prefix}-{year}-{seq:04d} | TP-2025-0123 |
| Level 4 | FORM, TMPL, CHK | {prefix}-{year}-{seq:04d} | FORM-2025-0456 |
| Level 5 | REC | REC-{year}-{seq:04d} | REC-2025-0789 |

### Manual Override

You can specify a custom prefix when creating documents:
```json
{
  "custom_prefix": "CUST"
}
```

## Usage Examples

### Example 1: Create and Approve a Quality Procedure

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

# 1. Create document
doc_data = {
    "title": "Non-Conformance Management Procedure",
    "level": "Level 2",
    "document_type": "Procedure",
    "iso_standard": "ISO 9001",
    "department": "Quality",
    "description": "Procedure for managing non-conforming products",
    "review_frequency_months": 24,
    "tags": ["quality", "non-conformance", "iso9001"]
}

response = requests.post(f"{BASE_URL}/documents/", json=doc_data, headers=headers)
document = response.json()
doc_id = document["id"]

# 2. Add responsibilities
raci_data = {
    "role_title": "Quality Manager",
    "is_accountable": True,
    "department": "Quality"
}
requests.post(f"{BASE_URL}/documents/{doc_id}/responsibilities", json=raci_data, headers=headers)

# 3. Submit for review
requests.put(f"{BASE_URL}/documents/{doc_id}/submit-review",
             json={"checker_id": 5}, headers=headers)

# 4. Approve document
requests.put(f"{BASE_URL}/documents/{doc_id}/approve", headers=headers)
```

### Example 2: Create Template with Full Metadata

```python
# 1. Create Level 4 template
template_data = {
    "title": "IEC 61215 Thermal Cycling Test Protocol",
    "level": "Level 4",
    "document_type": "Test Protocol",
    "pv_standard": "IEC 61215",
    "tags": ["thermal-cycling", "iec61215", "pv-testing"],
    "keywords": ["thermal", "cycling", "temperature", "photovoltaic"]
}

response = requests.post(f"{BASE_URL}/documents/", json=template_data, headers=headers)
template = response.json()
template_id = template["id"]

# 2. Index as template
index_data = {
    "category_name": "IEC 61215 Test Protocols",
    "tags": ["iec61215", "thermal"],
    "keywords": ["thermal cycling test"]
}
requests.post(f"{BASE_URL}/documents/{template_id}/index-template",
              json=index_data, headers=headers)

# 3. Add equipment requirements
equipment_data = {
    "name": "Thermal Chamber",
    "equipment_type": "Equipment",
    "manufacturer": "Climate Systems Inc.",
    "specifications": "Temperature range: -40°C to +85°C",
    "calibration_required": True
}
requests.post(f"{BASE_URL}/documents/{template_id}/equipment",
              json=equipment_data, headers=headers)

# 4. Add KPIs
kpi_data = {
    "name": "Test Completion Time",
    "metric": "Average time to complete thermal cycling test",
    "unit_of_measure": "hours",
    "target_value": 200,
    "measurement_frequency": "Per Test"
}
requests.post(f"{BASE_URL}/documents/{template_id}/kpis",
              json=kpi_data, headers=headers)
```

### Example 3: Link Documents for Traceability

```python
# Link Level 2 procedure to Level 3 test procedure
link_data = {
    "parent_document_id": 10,  # Level 2 Quality Procedure
    "child_document_id": 25,    # Level 3 Test Procedure
    "link_type": "implements",
    "description": "Test procedure implements requirements from quality procedure",
    "section_reference": "Section 5.2.1",
    "compliance_reference": "ISO/IEC 17025:2017, 7.2"
}

requests.post(f"{BASE_URL}/documents/links", json=link_data, headers=headers)

# Get complete hierarchy
hierarchy = requests.get(f"{BASE_URL}/documents/25/hierarchy?direction=both",
                         headers=headers).json()
print(f"Parent documents: {hierarchy['parent_documents']}")
print(f"Child documents: {hierarchy['child_documents']}")
```

## Setup and Installation

### 1. Run Migration
```bash
cd /home/user/lims-qms-platform
python database/migrations/001_document_template_management.py
```

### 2. Verify Tables Created
```bash
psql -U postgres -d lims_qms -c "\dt"
```

### 3. Start Application
```bash
python backend/main.py
```

### 4. Access API Documentation
```
http://localhost:8000/api/docs
```

## Integration Points

### With Form Engine
- Level 4 documents can be linked to FormTemplates
- Records (Level 5) generated from form submissions

### With Quality Module
- CAPA documents link to quality procedures
- Audit checklists as Level 4 templates

### With Equipment Module
- Equipment calibration procedures
- Equipment-specific test protocols

### With Training Module
- Training records as Level 5
- Training procedures as Level 3

## Best Practices

1. **Document Numbering**: Let the system auto-generate numbers for consistency

2. **Versioning**: Always create new versions instead of editing files directly

3. **Linking**: Establish links between documents for complete traceability

4. **Metadata**: Fill in comprehensive metadata for better searchability

5. **Templates**: Index all Level 4 documents as templates for easy discovery

6. **Review Cycle**: Set appropriate review frequencies based on document criticality

7. **Retention**: Define retention policies according to regulatory requirements

8. **Tags and Keywords**: Use consistent tagging for effective searching

## Security and Compliance

- All document actions are logged in audit trail
- Role-based access control via existing RBAC system
- Document retention policies ensure compliance
- Version history provides complete change tracking
- Checksum verification ensures file integrity

## Performance Considerations

- Indexed fields: document_number, level, status, department, iso_standard
- Pagination recommended for large result sets (default: 100 items)
- Soft delete allows data recovery and maintains referential integrity

## Support

For issues or questions:
- API Documentation: http://localhost:8000/api/docs
- GitHub Issues: https://github.com/ganeshgowri-asa-et/lims-qms-platform/issues
