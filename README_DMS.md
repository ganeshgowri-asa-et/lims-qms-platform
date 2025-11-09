# Document Management System (DMS) - LIMS/QMS Platform

Comprehensive Document Management System with version control, approval workflows, and digital signatures for ISO 17025/9001 compliance.

## Features

### 📄 Document Control
- **Auto Document Numbering**: QSF-YYYY-XXX format (e.g., QSF-2025-001)
- **Version Control**: Major.Minor versioning (e.g., 1.0, 1.1, 2.0)
- **Document Types**: Procedures, Work Instructions, Forms, Specifications, Manuals, Policies, Records, Reports
- **Status Tracking**: Draft → Pending Review → Pending Approval → Approved → Effective → Obsolete/Superseded

### ✍️ Digital Signatures
- **Three-tier Approval Workflow**: Doer → Checker → Approver
- **Digital Signature Hash**: SHA-256 based signatures
- **Audit Trail**: IP address, timestamp, user agent tracking
- **Approval Comments**: Support for reviewer/approver comments

### 📋 Revision Control
- **Complete Revision History**: Track all changes with timestamps
- **Change Description**: Mandatory change descriptions for each revision
- **File Integrity**: SHA-256 hash verification
- **Previous Version Linking**: Chain of custody for all revisions

### 🔍 Full-Text Search
- **Whoosh-based Search Engine**: Fast full-text search across documents
- **Multi-field Search**: Search in title, description, and content
- **Relevance Scoring**: Results ranked by relevance

### 📤 Document Distribution
- **Controlled Copies**: Track distribution of controlled copies
- **Copy Numbering**: Automatic copy number assignment (COPY-001, COPY-002, etc.)
- **Distribution Tracking**: Recipient, department, location tracking
- **Return Tracking**: Track when copies are returned

### 📄 PDF Generation
- **Automated PDF Creation**: Generate PDFs for any document
- **Watermarking**: Configurable watermarks for controlled copies
- **Approval Sheets**: Generate signature approval sheets
- **Professional Formatting**: Clean, professional document layout

## Database Schema

### Tables

#### `qms_documents`
Main document table with the following key fields:
- `doc_number` (unique): Auto-generated document number
- `title`: Document title
- `type`: Document type (enum)
- `major_version`, `minor_version`: Version tracking
- `owner`: Document owner
- `status`: Document status (enum)
- `file_path`, `file_hash`: File storage and integrity
- `content_text`: Extracted text for search

#### `document_revisions`
Revision history tracking:
- `revision_number`: Sequential revision number
- `major_version`, `minor_version`: Version at time of revision
- `revised_by`: User who made the revision
- `change_description`: Description of changes
- `file_hash`: File integrity hash

#### `document_distribution`
Controlled copy distribution:
- `copy_number`: Unique copy identifier
- `recipient`: Copy recipient
- `distributed_date`: Distribution timestamp
- `is_controlled`: Whether copy is controlled
- `version_distributed`: Version distributed

#### `document_signatures`
Digital signature tracking:
- `role`: Approval role (DOER, CHECKER, APPROVER)
- `signer`: Name of signer
- `signature_hash`: Digital signature
- `signature_timestamp`: Signature timestamp
- `major_version`, `minor_version`: Document version signed

## API Endpoints

### Document Operations

#### `POST /documents/`
Create a new document
```json
{
  "title": "Quality Procedure 001",
  "type": "PROCEDURE",
  "owner": "John Doe",
  "department": "Quality Assurance",
  "description": "Document description",
  "content_text": "Document content for search"
}
```

#### `GET /documents/{id}`
Get document by ID

#### `GET /documents/number/{doc_number}`
Get document by document number

#### `GET /documents/`
List documents with filters
- Query params: `status`, `doc_type`, `owner`, `skip`, `limit`

#### `PUT /documents/{id}`
Update document metadata

#### `PUT /documents/{id}/revise`
Create new revision (increment version)
```json
{
  "is_major": false,
  "revised_by": "John Doe",
  "change_description": "Updated procedure steps",
  "change_reason": "Customer feedback"
}
```

#### `POST /documents/{id}/approve`
Add approval signature
```json
{
  "role": "CHECKER",
  "signer": "Jane Smith",
  "signer_email": "jane@example.com",
  "signature_hash": "abc123...",
  "comments": "Reviewed and approved",
  "is_approved": true
}
```

#### `POST /documents/{id}/upload`
Upload document file (multipart/form-data)

#### `POST /documents/{id}/distribute`
Create controlled copy distribution
```json
{
  "recipient": "Lab Manager",
  "recipient_email": "lab@example.com",
  "department": "Laboratory",
  "location": "Building A",
  "is_controlled": true
}
```

### Search & Retrieval

#### `GET /documents/search/?q={query}`
Full-text search across documents

#### `GET /documents/{id}/revisions`
Get revision history for a document

#### `GET /documents/{id}/signatures`
Get all signatures for a document

#### `GET /documents/{id}/distributions`
Get all distributions for a document

#### `GET /documents/{id}/pdf?include_watermark=true`
Generate PDF with optional watermark

## Streamlit UI

### Pages

#### 📝 Create Document
- Form to create new documents
- All document types supported
- Automatic document number assignment

#### 📋 Document List
- Filterable document list
- Filter by status, type, owner
- View details, revisions, signatures
- Responsive data table

#### ✅ Approval Queue
- Pending Review (for Checkers)
- Pending Approval (for Approvers)
- Digital signature form
- Real-time status updates

#### 🔍 Search Documents
- Full-text search interface
- Ranked results
- Expandable result details
- Document preview

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
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
# Edit .env with your database credentials and settings
```

5. **Create database**
```bash
createdb lims_qms
```

6. **Run migrations**
```bash
alembic upgrade head
```

## Running the Application

### Backend (FastAPI)

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

API Documentation: http://localhost:8000/docs

### Frontend (Streamlit)

```bash
streamlit run streamlit_app/app.py
```

UI: http://localhost:8501

## Configuration

### Environment Variables

Create `.env` file with:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/lims_qms

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Document Storage
DOCUMENT_STORAGE_PATH=./storage/documents
SIGNATURE_STORAGE_PATH=./storage/signatures

# PDF Watermark
WATERMARK_TEXT=CONTROLLED COPY
WATERMARK_OPACITY=0.3
```

## Document Numbering

### Format: `QSF-YYYY-XXX`

- **QSF**: Quality System Form/Document prefix
- **YYYY**: Four-digit year
- **XXX**: Three-digit sequential number (001-999)

Examples:
- `QSF-2025-001` - First document of 2025
- `QSF-2025-042` - 42nd document of 2025

Numbers reset each year.

## Version Control

### Format: `Major.Minor`

- **Major Version**: Significant changes (1.0 → 2.0)
  - Complete rewrite
  - Major procedural changes
  - Structural modifications

- **Minor Version**: Minor changes (1.0 → 1.1)
  - Typo corrections
  - Clarifications
  - Minor updates

New documents start at version 1.0.

## Approval Workflow

### Three-Tier Workflow

1. **DOER** (Author)
   - Creates the document
   - Signs as DOER
   - Status: DRAFT → PENDING_REVIEW

2. **CHECKER** (Reviewer)
   - Reviews the document
   - Signs as CHECKER
   - Status: PENDING_REVIEW → PENDING_APPROVAL

3. **APPROVER** (Approver)
   - Approves the document
   - Signs as APPROVER
   - Status: PENDING_APPROVAL → APPROVED → EFFECTIVE

## File Storage

Documents are stored in the following structure:

```
storage/
├── documents/
│   ├── 1/
│   │   ├── original_file.pdf
│   │   └── QSF-2025-001_v1.0.pdf
│   ├── 2/
│   └── ...
├── signatures/
└── search_index/
```

## Security Features

- SHA-256 file integrity hashing
- Digital signature tracking
- IP address logging
- Timestamp verification
- Audit trail for all changes
- Role-based access control (RBAC) ready

## Compliance

### ISO 17025 / ISO 9001 Requirements

✅ Document control and identification
✅ Version control
✅ Approval and authorization
✅ Controlled distribution
✅ Change management
✅ Document retention
✅ Obsolete document control
✅ Audit trail

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

## API Examples

### Create Document
```bash
curl -X POST "http://localhost:8000/documents/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Procedure",
    "type": "PROCEDURE",
    "owner": "John Doe",
    "department": "QA"
  }'
```

### Search Documents
```bash
curl "http://localhost:8000/documents/search/?q=quality&limit=10"
```

### Add Signature
```bash
curl -X POST "http://localhost:8000/documents/1/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "CHECKER",
    "signer": "Jane Smith",
    "signer_email": "jane@example.com",
    "signature_hash": "abc123hash",
    "is_approved": true
  }'
```

## Project Structure

```
lims-qms-platform/
├── app/
│   ├── api/
│   │   ├── documents.py      # API endpoints
│   │   └── schemas.py        # Pydantic schemas
│   ├── core/
│   │   ├── config.py         # Configuration
│   │   └── database.py       # Database setup
│   ├── models/
│   │   └── document.py       # SQLAlchemy models
│   ├── services/
│   │   ├── document_service.py    # Business logic
│   │   ├── document_numbering.py  # Auto-numbering
│   │   ├── pdf_service.py         # PDF generation
│   │   └── search_service.py      # Full-text search
│   ├── utils/
│   └── main.py               # FastAPI app
├── streamlit_app/
│   └── app.py                # Streamlit UI
├── alembic/
│   └── versions/             # Database migrations
├── tests/
├── requirements.txt
├── alembic.ini
└── README_DMS.md
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

See LICENSE file for details.

## Support

For issues and questions, please open an issue on GitHub.

---

**Version:** 1.0.0
**Last Updated:** 2025-11-09
