# LIMS-QMS Streamlit Frontend Application

## Overview

This is a comprehensive, production-ready Streamlit frontend application for the LIMS-QMS Organization OS. It provides a complete user interface for managing documents, forms, workflows, quality management, and all organizational processes.

## Features

### 1. **Dashboard**
- KPI widgets and metrics
- Real-time charts and visualizations
- Quick access to pending tasks
- Recent activity feed
- Alert notifications

### 2. **Document Management**
- Browse document hierarchy (Level 1-5)
- Advanced search and filtering
- Document viewer with metadata
- Upload and version control
- Revision history with diff view
- Document lineage and relationships

### 3. **Forms & Data Capture**
- Dynamic form rendering
- Template-based form creation
- Field validation
- Auto-save drafts
- File attachments
- Digital signatures

### 4. **Workflow & Approvals**
- My Tasks dashboard
- Pending approvals interface
- Workflow status tracking
- Approve/Reject with comments
- Revision requests
- Notification center

### 5. **Traceability & Audit**
- Document lineage visualization
- Comprehensive audit trail
- Change history with diff view
- Traceability matrix
- Export audit reports

### 6. **Analytics & Reports**
- Performance dashboards
- KPI tracking
- Document statistics
- Custom report builder
- Data visualization
- Export to PDF/Excel

### 7. **Administration**
- User management
- Role-based access control
- System configuration
- Template management
- Backup and restore

### 8. **AI Assistant**
- Embedded chatbot
- Natural language queries
- Smart suggestions
- Document search
- Report generation

## Architecture

```
frontend/
├── app.py                  # Main Streamlit application
├── pages/                  # Page modules
│   ├── documents.py        # Document management
│   ├── forms.py            # Forms and data capture
│   ├── workflow.py         # Workflow and approvals
│   ├── traceability.py     # Traceability and audit
│   ├── projects.py         # Project management
│   ├── tasks.py            # Task management
│   ├── hr.py               # HR module
│   ├── procurement.py      # Procurement
│   ├── equipment.py        # Equipment management
│   ├── financial.py        # Financial management
│   ├── crm.py              # CRM
│   ├── quality.py          # Quality management
│   ├── analytics.py        # Analytics and BI
│   ├── ai_assistant.py     # AI chatbot
│   └── admin.py            # Administration
├── components/             # Reusable components
│   └── signature_pad.py    # Digital signature component
├── utils/                  # Utility modules
│   └── api_client.py       # Backend API client
├── .streamlit/             # Streamlit configuration
│   └── config.toml         # App configuration
└── README.md               # This file
```

## Installation

### Prerequisites
- Python 3.10+
- Backend API running (see backend/README.md)
- PostgreSQL database

### Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set environment variables:**
```bash
export BACKEND_URL=http://localhost:8000
```

3. **Run the application:**
```bash
streamlit run frontend/app.py
```

The application will be available at `http://localhost:8501`

## Configuration

### Environment Variables

- `BACKEND_URL`: Backend API URL (default: `http://localhost:8000`)
- `ANTHROPIC_API_KEY`: API key for AI assistant (optional)

### Streamlit Configuration

Configuration is in `.streamlit/config.toml`:
- Theme colors
- Server settings
- Upload size limits
- CORS settings

## Usage

### Login

The application includes a simple authentication flow:

1. Navigate to `http://localhost:8501`
2. Enter username and password
3. Access is role-based (Admin, Manager, Approver, Checker, User)

**Demo Mode:** Enter any username/password to login in development mode.

### Navigation

The sidebar provides access to all modules:

- **Dashboard**: Overview and KPIs
- **Documents**: Document management system
- **Forms**: Form templates and records
- **Workflow**: Approvals and tasks
- **Traceability**: Audit trails and lineage
- **Projects**: Project management
- **Tasks**: Task tracking
- **HR**: Human resources
- **Procurement**: Procurement management
- **Equipment**: Equipment tracking
- **Financial**: Financial management
- **CRM**: Customer relationship management
- **Quality**: Quality management
- **Analytics**: Business intelligence
- **AI Assistant**: Intelligent chatbot
- **Admin**: System administration

### Key Workflows

#### Creating a Document

1. Navigate to **Documents**
2. Click **Create Document** tab
3. Fill in required fields:
   - Title
   - Level (1-5)
   - Category
   - Description
4. Upload document file (PDF, DOCX, XLSX)
5. Submit for review or save as draft

#### Approval Workflow

1. Navigate to **Workflow**
2. View **Pending Approvals**
3. Review document/form details
4. Add comments
5. Click **Approve** or **Reject**

#### Digital Signatures

Forms and documents support multi-level digital signatures:

1. Open form/document requiring signature
2. Use digital signature pad or upload signature
3. Confirm signer details
4. Submit signature

#### Viewing Audit Trail

1. Navigate to **Traceability**
2. Select **Audit Trail** tab
3. Filter by entity type, action, user, or date
4. Export audit report as CSV

## API Integration

The frontend communicates with the FastAPI backend via the `api_client` utility:

```python
from frontend.utils.api_client import api_client

# Get documents
documents = api_client.get_documents(level="Level 1", status="Approved")

# Create document
new_doc = api_client.create_document({
    "title": "Quality Manual",
    "level": "Level 1",
    "category": "ISO 17025"
})

# Approve document
api_client.approve_document(document_id=123)
```

## Components

### Digital Signature Pad

```python
from frontend.components.signature_pad import signature_pad

# Single signature
signature = signature_pad(key="doer_signature")

# Multi-level signatures
from frontend.components.signature_pad import multi_signature_workflow

all_signed = multi_signature_workflow(roles=['Doer', 'Checker', 'Approver'])
```

## Customization

### Adding New Pages

1. Create new page in `frontend/pages/`:
```python
# frontend/pages/my_new_page.py
import streamlit as st

def show():
    st.header("My New Page")
    # Page content
```

2. Add to navigation in `app.py`:
```python
# Add to menu list
selected = option_menu(
    "Main Menu",
    [..., "My New Page"],
    ...
)

# Add route
elif selected == "My New Page":
    show_my_new_page()

# Add function
def show_my_new_page():
    from pages import my_new_page
    my_new_page.show()
```

### Customizing Theme

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#your-color"
backgroundColor = "#your-color"
secondaryBackgroundColor = "#your-color"
textColor = "#your-color"
font = "sans serif"  # or "serif", "monospace"
```

## Development

### Running in Development Mode

```bash
streamlit run frontend/app.py --server.runOnSave true
```

### Debugging

Enable detailed error messages in `.streamlit/config.toml`:

```toml
[client]
showErrorDetails = true
```

### Hot Reload

Streamlit automatically reloads when files change. Click "Rerun" in the UI or press 'R'.

## Production Deployment

### Docker

Build and run with Docker:

```bash
docker build -t lims-qms-frontend .
docker run -p 8501:8501 \
  -e BACKEND_URL=https://api.yourdomain.com \
  lims-qms-frontend
```

### Cloud Deployment

#### Streamlit Cloud
1. Push to GitHub
2. Connect repository to Streamlit Cloud
3. Set environment variables
4. Deploy

#### AWS/Azure/GCP
- Use Docker container
- Deploy to container service
- Configure load balancer
- Set up SSL/TLS

## Security

### Authentication
- JWT-based authentication with backend
- Session management via Streamlit session state
- Automatic token refresh

### Authorization
- Role-based access control (RBAC)
- Page-level access restrictions
- Action-level permissions

### Data Protection
- HTTPS required in production
- CSRF protection enabled
- XSS prevention
- Input validation

## Performance

### Optimization Tips

1. **Caching**: Use `@st.cache_data` for expensive operations
2. **Pagination**: Limit data displayed per page
3. **Lazy Loading**: Load data on-demand
4. **Session State**: Minimize session state size

### Monitoring

- Built-in Streamlit metrics
- Custom logging with loguru
- Error tracking with Sentry (optional)

## Troubleshooting

### Common Issues

**Connection Error to Backend:**
```
Check BACKEND_URL environment variable
Ensure backend is running on correct port
Verify network connectivity
```

**Slow Performance:**
```
Clear browser cache
Reduce data pagination limits
Enable caching for API calls
```

**Authentication Issues:**
```
Check JWT token expiration
Verify credentials with backend
Clear session state and re-login
```

## Support

For issues and questions:
- GitHub Issues: [repository]/issues
- Documentation: [link to docs]
- Email: support@yourdomain.com

## License

[Your License Here]

## Contributors

- Development Team
- QA Team
- Product Team

## Version History

- **v1.0.0** (2024-03): Initial production release
  - Complete document management
  - Workflow and approvals
  - Traceability and audit
  - Analytics dashboards
  - AI assistant integration
  - Multi-language support
