# Document & Template Management System

## Overview

Comprehensive Document Management System for Organization OS with support for 5-level document hierarchy, workflow management, version control, and complete audit trail.

## Features

### 1. **5-Level Document Hierarchy**
- **Level 1**: Quality Manual, Policy, Vision & Mission
- **Level 2**: Quality System Procedures (ISO 17025/9001)
- **Level 3**: Operation/Execution/Test Procedures (PV Standards: IEC 61215, 61730, 61853, 62804, 62716, 61701, 62332, 63202, 60904)
- **Level 4**: Formats, Templates, Checklists, Test Protocols
- **Level 5**: Records (generated from Level 4)

### 2. **Comprehensive Metadata Tracking**
- Title, document owner, document number, revision history
- Table of contents, responsibilities
- Equipment, software, and resources per standards
- Process flowcharts, value stream mapping, turtle diagrams
- KPI definitions and measurement frequency
- Annexures, references, analysis, risk assessment
- Non-conformance control procedures
- Training requirements and safety compliance

### 3. **Unique Numbering System**
- Auto-generated document numbers based on level, category, and year
- Manual override option
- Customizable numbering formats
- Sequence tracking per level/category/year
- Format templates with placeholders

### 4. **Doer-Checker-Approver Workflow**
- Three-tier approval process
- Digital signatures and audit trail
- Workflow status tracking
- Comment and feedback mechanism
- Revision request capability
- Email notifications (integration ready)

### 5. **Version Control & Audit Trail**
- Complete version history
- Change tracking with checksums (SHA-256)
- Major and minor versioning
- Automatic archiving of previous versions
- Comprehensive audit log for all operations
- Rollback capability

### 6. **Bidirectional Linking & Traceability**
- Parent-child relationships
- Reference links
- Implementation links
- Superseded document tracking
- Traceability matrix
- Hierarchy visualization

### 7. **Dynamic Template Loader**
- Automatic indexing of Level 4 templates
- Template search and discovery
- Template code generation
- Usage tracking
- Fields schema and validation rules
- Template-based document creation

### 8. **Access Control Framework**
- User-based permissions
- Role-based access control (ready for integration)
- Department-based access (ready for integration)
- Granular permissions (view, edit, review, approve, delete)
- Time-based access validity
- Document confidentiality levels

### 9. **Document Retention Policies**
- Configurable retention periods
- Auto-archive and auto-destroy options
- Legal and regulatory compliance tracking
- Destruction date calculation
- Review workflow for expiring documents
- Retention reports and analytics

### 10. **File Storage with Versioning**
- Organized directory structure
- File integrity verification (checksums)
- Version-specific file storage
- Support for multiple file types
- File metadata tracking
- Storage statistics

## Architecture

### Database Models

#### Core Models
- **Document**: Main document entity with comprehensive fields
- **DocumentMetadata**: Extended metadata for detailed tracking
- **DocumentVersion**: Version history and change tracking
- **DocumentLevel**: Level configuration for numbering

#### Workflow Models
- **DocumentApproval**: Approval workflow tracking
- **DocumentAuditLog**: Comprehensive audit trail

#### Relationship Models
- **DocumentLink**: Bidirectional linking
- **DocumentAccess**: Access control permissions

#### Policy Models
- **DocumentRetentionPolicy**: Retention rules and lifecycle
- **TemplateIndex**: Template indexing and discovery
- **DocumentNumberSequence**: Numbering sequence tracking

### Services Layer

1. **DocumentService**: Main service integrating all functionality
2. **FileStorageService**: File operations and versioning
3. **NumberingService**: Document number generation
4. **WorkflowService**: Doer-Checker-Approver workflow
5. **LinkingService**: Bidirectional linking and traceability
6. **TemplateService**: Template indexing and management
7. **AccessControlService**: Permission management
8. **RetentionService**: Lifecycle and retention policies

### API Endpoints

#### Document CRUD
```
POST   /api/v1/documents/                    - Create document
GET    /api/v1/documents/{id}               - Get document
PUT    /api/v1/documents/{id}               - Update document
DELETE /api/v1/documents/{id}               - Delete document
GET    /api/v1/documents/                   - Search documents
```

#### File Management
```
POST   /api/v1/documents/{id}/upload        - Upload file
POST   /api/v1/documents/{id}/version       - Create new version
```

#### Metadata
```
PUT    /api/v1/documents/{id}/metadata      - Update extended metadata
```

#### Workflow
```
POST   /api/v1/documents/{id}/submit        - Submit for review
POST   /api/v1/documents/{id}/review        - Review document
POST   /api/v1/documents/{id}/approve       - Final approval
GET    /api/v1/documents/{id}/workflow/status - Get workflow status
GET    /api/v1/documents/pending/approvals  - Get pending approvals
```

#### Linking
```
POST   /api/v1/documents/{id}/links         - Create link
GET    /api/v1/documents/{id}/links         - Get links
GET    /api/v1/documents/{id}/hierarchy     - Get hierarchy
GET    /api/v1/documents/{id}/traceability  - Get traceability matrix
```

#### Templates
```
POST   /api/v1/documents/templates/index       - Index template
POST   /api/v1/documents/templates/auto-index  - Auto-index all templates
GET    /api/v1/documents/templates/search      - Search templates
GET    /api/v1/documents/templates/{code}      - Get template by code
```

#### Access Control
```
POST   /api/v1/documents/{id}/access/grant  - Grant access
GET    /api/v1/documents/{id}/access        - Get access list
```

#### Retention
```
POST   /api/v1/documents/retention/policies - Create retention policy
GET    /api/v1/documents/retention/policies - List policies
GET    /api/v1/documents/{id}/retention/policy - Get applicable policy
POST   /api/v1/documents/{id}/archive       - Archive document
GET    /api/v1/documents/retention/review   - Get documents for review
```

#### Numbering
```
GET    /api/v1/documents/numbering/preview  - Preview next number
GET    /api/v1/documents/numbering/status   - Get sequence status
```

## Usage Examples

### Creating a Document

```python
import requests

# Create a Quality Manual (Level 1)
response = requests.post(
    "http://localhost:8000/api/v1/documents/",
    headers={"Authorization": "Bearer <token>"},
    json={
        "title": "Quality Management System Manual",
        "level": "Level 1",
        "document_type": "Quality Manual",
        "category": "Quality",
        "standard": "ISO 17025",
        "description": "Comprehensive QMS manual for laboratory",
        "purpose": "Define quality management system requirements",
        "scope": "Applies to all laboratory operations",
        "tags": ["quality", "management", "iso17025"]
    }
)

document = response.json()
print(f"Created document: {document['document']['document_number']}")
```

### Uploading a File

```python
# Upload file to document
with open("quality_manual.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(
        f"http://localhost:8000/api/v1/documents/{document_id}/upload",
        headers={"Authorization": "Bearer <token>"},
        files=files
    )
```

### Submit for Review (Workflow)

```python
# Submit document for review
response = requests.post(
    f"http://localhost:8000/api/v1/documents/{document_id}/submit",
    headers={"Authorization": "Bearer <token>"},
    json={
        "checker_id": 2,  # User ID of checker
        "comments": "Please review for compliance"
    }
)
```

### Creating Document Links

```python
# Link procedure to quality manual
response = requests.post(
    f"http://localhost:8000/api/v1/documents/{procedure_id}/links",
    headers={"Authorization": "Bearer <token>"},
    json={
        "target_document_id": quality_manual_id,
        "link_type": "implements",
        "description": "Implements QMS requirements",
        "is_bidirectional": True
    }
)
```

### Auto-Index Templates

```python
# Auto-index all Level 4 templates
response = requests.post(
    "http://localhost:8000/api/v1/documents/templates/auto-index",
    headers={"Authorization": "Bearer <token>"}
)

print(f"Indexed {response.json()['indexed']} templates")
```

### Setting Retention Policy

```python
# Create retention policy for calibration records
response = requests.post(
    "http://localhost:8000/api/v1/documents/retention/policies",
    headers={"Authorization": "Bearer <token>"},
    json={
        "policy_name": "Calibration Records - 7 Years",
        "retention_years": 7,
        "document_level": "Level 5",
        "category": "Calibration",
        "auto_archive": True,
        "legal_requirement": True,
        "regulation_reference": "ISO 17025:2017 Section 6.4.13"
    }
)
```

## Configuration

### Document Level Configuration

Set up level-specific numbering formats:

```sql
INSERT INTO document_levels (level_number, level_name, numbering_format, auto_numbering, requires_approval, retention_years)
VALUES
(1, 'Level 1', 'L1-{category}-{year}-{seq:04d}', TRUE, TRUE, 10),
(2, 'Level 2', 'L2-{category}-{year}-{seq:04d}', TRUE, TRUE, 7),
(3, 'Level 3', 'L3-{category}-{year}-{seq:04d}', TRUE, TRUE, 7),
(4, 'Level 4', 'L4-TMPL-{category}-{year}-{seq:04d}', TRUE, FALSE, 5),
(5, 'Level 5', 'L5-REC-{category}-{year}-{seq:05d}', TRUE, FALSE, 7);
```

### File Storage Configuration

Configure upload directory in `backend/core/config.py`:

```python
UPLOAD_DIR = "uploads"
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'png', 'jpg', 'jpeg', 'gif'}
```

## Security Considerations

1. **Access Control**: All endpoints require authentication
2. **Permission Checking**: Edit/delete operations verify user permissions
3. **Audit Trail**: All operations are logged with user ID and timestamp
4. **File Integrity**: SHA-256 checksums verify file integrity
5. **Soft Delete**: Documents are soft-deleted to maintain audit trail
6. **Confidentiality Levels**: Support for public, internal, confidential, and restricted access levels

## Integration Points

### Future Modules
- **HR Module**: Link training records to documents
- **Equipment Module**: Link equipment to procedures
- **CRM Module**: Link customer-specific documents
- **Project Module**: Link project documents
- **Quality Module**: Link NC records to procedures
- **Procurement Module**: Link supplier documents

### Notification System
The system is ready for email/notification integration:
- Document approval requests
- Workflow status changes
- Document expiry alerts
- Retention policy notifications

## Performance Optimization

1. **Indexed Fields**: Document number, level, status, category for fast queries
2. **Pagination**: All list endpoints support pagination
3. **Lazy Loading**: Related data loaded only when requested
4. **File Storage**: Organized directory structure for efficient file access
5. **Caching**: Ready for Redis integration for frequently accessed data

## Compliance & Standards

Supports multiple industry standards:
- ISO 17025 (Laboratory Management)
- ISO 9001 (Quality Management)
- IEC 61215, 61730, 61853 (PV Module Testing)
- IEC 62804, 62716 (PV Durability)
- IEC 61701, 62332, 63202 (PV Environmental)
- IEC 60904 (PV Performance)

## Backup & Recovery

### Recommended Backup Strategy
1. **Database**: Daily automated backups
2. **File Storage**: Incremental backups with version retention
3. **Audit Logs**: Archive logs older than 1 year
4. **Version History**: Maintain all versions until document destruction

## Monitoring & Maintenance

### Key Metrics to Monitor
- Document creation rate
- Workflow bottlenecks (pending approvals)
- Storage usage
- Document expiry approaching
- Access control violations

### Maintenance Tasks
- Regular cleanup of temp files
- Archive old versions
- Review and update retention policies
- Audit access logs
- Update document level configurations

## Support & Documentation

For additional support:
- API Documentation: `/docs` (FastAPI auto-generated)
- Database Schema: See `backend/models/document.py`
- Service Documentation: See individual service files in `backend/services/`

## License

Part of the LIMS-QMS Organization OS Platform
