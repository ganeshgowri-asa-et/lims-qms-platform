# Quick Start Guide - Document Management System

Get up and running with the LIMS-QMS Document Management System in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher (or use SQLite for development)

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# For quick start with SQLite (no PostgreSQL needed)
# Edit .env and change DATABASE_URL to:
# DATABASE_URL=sqlite:///./lims_qms.db
```

### 3. Initialize Database

```bash
# Create tables
python init_db.py
```

## Running the Application

### Terminal 1: Start API Server

```bash
./run_api.sh
# or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs

### Terminal 2: Start UI

```bash
./run_ui.sh
# or
streamlit run streamlit_app/app.py
```

UI will be available at:
- **Streamlit UI**: http://localhost:8501

## Quick Test

### 1. Create Your First Document (via UI)

1. Open http://localhost:8501
2. Go to "📝 Create Document"
3. Fill in:
   - Title: "Quality Management Manual"
   - Type: MANUAL
   - Owner: Your Name
4. Click "Create Document"
5. Note the Document Number (e.g., QSF-2025-001)

### 2. Add Approvals

1. Go to "✅ Approval Queue" → "Sign Document" tab
2. Fill in:
   - Document ID: 1 (from step 1)
   - Role: DOER
   - Your Name and Email
3. Click "Add Signature"
4. Repeat for CHECKER and APPROVER roles

### 3. Search Documents

1. Go to "🔍 Search Documents"
2. Search for "Quality"
3. View results

## API Quick Test

### Create Document (cURL)

```bash
curl -X POST "http://localhost:8000/documents/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Procedure",
    "type": "PROCEDURE",
    "owner": "John Doe",
    "department": "Quality"
  }'
```

### List Documents

```bash
curl "http://localhost:8000/documents/"
```

### Search Documents

```bash
curl "http://localhost:8000/documents/search/?q=quality"
```

## Key Features to Try

### ✅ Document Numbering
- Documents auto-number as QSF-YYYY-XXX
- Try creating multiple documents to see sequence

### ✅ Version Control
- Edit a document
- Use "Revise" to create new version (1.0 → 1.1 or 2.0)

### ✅ Approval Workflow
- Sign as DOER → status: PENDING_REVIEW
- Sign as CHECKER → status: PENDING_APPROVAL
- Sign as APPROVER → status: APPROVED

### ✅ Full-Text Search
- Add content when creating documents
- Search across all document fields

### ✅ PDF Generation
- Use API endpoint: GET /documents/{id}/pdf
- Generates PDF with watermark for controlled copies

## File Structure

```
storage/
├── documents/     # Uploaded document files
├── signatures/    # Signature data
└── search_index/  # Full-text search index
```

## Next Steps

1. **Configure PostgreSQL** (for production)
   - Create database: `createdb lims_qms`
   - Update .env with PostgreSQL URL
   - Run migrations: `alembic upgrade head`

2. **Customize Settings** (.env)
   - Document numbering prefix
   - Watermark text
   - Storage paths

3. **Add Authentication** (future enhancement)
   - User management
   - Role-based access control

4. **Integrate with Existing Systems**
   - Use REST API endpoints
   - Import existing documents

## Troubleshooting

### Issue: Database errors
**Solution**: Make sure database is created and credentials in .env are correct

### Issue: Port already in use
**Solution**: Change ports in run scripts or kill existing processes

### Issue: Search not working
**Solution**: Ensure storage/search_index directory exists and is writable

### Issue: PDF generation fails
**Solution**: Check that reportlab and PyPDF2 are installed

## Support

- **Documentation**: See README_DMS.md for detailed information
- **API Docs**: http://localhost:8000/docs (when API is running)
- **Issues**: Open an issue on GitHub

---

Happy document managing! 📄✨
