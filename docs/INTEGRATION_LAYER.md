# LIMS-QMS Integration Layer & AI Orchestration
## SESSION 7: Complete Integration Hub Documentation

---

## 📋 Overview

The Integration Layer is the central nervous system of the LIMS-QMS Organization OS, connecting all modules together through:

- **Unified API Gateway** with middleware
- **Event-Driven Architecture** with pub/sub messaging
- **AI Orchestration** powered by Claude
- **Multi-Channel Notifications**
- **External System Integrations**
- **Background Task Processing**
- **System Monitoring & Health Checks**
- **Automated Backups & Recovery**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                         │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ Rate Limiting│ API Versioning│ Request Logging          │ │
│  │ Throttling   │ Security      │ CORS & Auth             │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Event Bus (Redis)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Pub/Sub Events • Event History • Real-time Updates │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              AI Orchestration (Claude)                       │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ Chat Assistant│ Smart Search │ Data Extraction         │ │
│  │ Compliance   │ Report Gen   │ Workflow Recommendations│ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│         Background Processing (Celery + RabbitMQ)            │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ Notifications│ Backups      │ ETL & Data Sync         │ │
│  │ Monitoring   │ AI Tasks     │ Scheduled Jobs          │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                External Integrations                         │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ Email/SMS    │ Cloud Storage│ ERP Systems             │ │
│  │ Calendar     │ Webhooks     │ Lab Equipment           │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### 1. Environment Setup

Create `.env` file with required configuration:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/lims_qms
ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/lims_qms

# Redis
REDIS_URL=redis://localhost:6379/0

# AI (Required for AI features)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=noreply@lims-qms.com

# Twilio (Optional - for SMS)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE=+1234567890

# Slack (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# AWS S3 (Optional)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=lims-qms-backups
```

### 2. Start Services with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Services will be available at:
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/api/docs
# - Frontend: http://localhost:8501
# - RabbitMQ Management: http://localhost:15672 (admin/admin)
# - Flower (Celery Monitor): http://localhost:5555
```

### 3. Start Individual Components

```bash
# Backend API
uvicorn backend.main:app --reload

# Celery Worker
celery -A backend.integrations.celery_app worker --loglevel=info

# Celery Beat (Scheduler)
celery -A backend.integrations.celery_app beat --loglevel=info

# Flower (Celery Monitoring)
celery -A backend.integrations.celery_app flower
```

---

## 📡 API Endpoints

### AI Orchestration

#### Chat with AI Assistant
```http
POST /api/v1/integrations/ai/chat
Content-Type: application/json
Authorization: Bearer {token}

{
  "message": "Show me all overdue tasks",
  "context": {
    "page": "tasks",
    "user_role": "manager"
  },
  "conversation_id": "optional-conversation-id"
}
```

#### Smart Search
```http
POST /api/v1/integrations/ai/search
Content-Type: application/json
Authorization: Bearer {token}

{
  "query": "Find all quality documents from last month",
  "scope": ["documents", "quality"]
}
```

#### Extract Data from Document
```http
POST /api/v1/integrations/ai/extract-data
Content-Type: application/json
Authorization: Bearer {token}

{
  "document_content": "Invoice text content...",
  "document_type": "invoice",
  "fields_to_extract": ["invoice_number", "date", "total_amount", "vendor"]
}
```

#### Check Compliance
```http
POST /api/v1/integrations/ai/check-compliance
Content-Type: application/json
Authorization: Bearer {token}

{
  "document_type": "SOP",
  "content": {...},
  "standards": ["ISO 9001", "FDA 21 CFR Part 11"]
}
```

#### Generate Report
```http
POST /api/v1/integrations/ai/generate-report
Content-Type: application/json
Authorization: Bearer {token}

{
  "prompt": "Generate a monthly quality metrics report",
  "data_sources": ["quality", "analytics"],
  "format": "markdown"
}
```

### Notifications

#### Send Notification
```http
POST /api/v1/integrations/notifications/send
Content-Type: application/json
Authorization: Bearer {token}

{
  "user_id": 1,
  "title": "Task Assigned",
  "message": "You have been assigned a new task",
  "channels": ["email", "in_app"],
  "priority": "normal",
  "action_url": "/tasks/123"
}
```

#### Get User Notifications
```http
GET /api/v1/integrations/notifications/user/{user_id}?unread_only=true&limit=50
Authorization: Bearer {token}
```

### Events

#### Publish Event
```http
POST /api/v1/integrations/events/publish
Content-Type: application/json
Authorization: Bearer {token}

{
  "event_type": "document.approved",
  "data": {
    "document_id": 123,
    "approver_id": 5
  }
}
```

#### Get Event History
```http
GET /api/v1/integrations/events/history/document.approved?limit=100
Authorization: Bearer {token}
```

### Data Exchange

#### Export Data
```http
POST /api/v1/integrations/export
Content-Type: application/json
Authorization: Bearer {token}

{
  "export_type": "projects",
  "format": "excel",
  "filters": {
    "status": "active",
    "date_from": "2024-01-01"
  }
}
```

#### Import Data
```http
POST /api/v1/integrations/import
Content-Type: application/json
Authorization: Bearer {token}

{
  "file_path": "/uploads/import.xlsx",
  "import_type": "vendors",
  "mapping": {
    "Vendor Name": "name",
    "Contact Email": "email"
  }
}
```

### System Management

#### Health Check
```http
GET /api/v1/integrations/system/health
```

Response:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "status": "healthy",
  "checks": {
    "cpu": {"status": "ok", "usage_percent": 45.2},
    "memory": {"status": "ok", "usage_percent": 62.1},
    "disk": {"status": "ok", "usage_percent": 35.8},
    "database": {"status": "ok", "connected": true},
    "redis": {"status": "ok", "connected": true},
    "api": {"status": "ok", "responsive": true}
  }
}
```

#### System Metrics
```http
GET /api/v1/integrations/system/metrics
Authorization: Bearer {token}
```

#### Trigger Database Backup
```http
POST /api/v1/integrations/system/backup/database
Authorization: Bearer {token}
```

#### Trigger File Backup
```http
POST /api/v1/integrations/system/backup/files
Authorization: Bearer {token}
```

### Webhooks

#### Receive Webhook
```http
POST /api/v1/integrations/webhooks/{webhook_name}
Content-Type: application/json

{
  "event_type": "order.created",
  "source": "erp_system",
  "data": {...},
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 🔔 Event System

### Event Types

The system supports 50+ event types across all modules:

**Documents**: `document.created`, `document.updated`, `document.approved`, `document.rejected`, `document.archived`

**Forms**: `form.submitted`, `form.approved`, `form.rejected`

**Projects**: `project.created`, `project.started`, `project.completed`, `project.cancelled`

**Tasks**: `task.created`, `task.assigned`, `task.started`, `task.completed`, `task.overdue`

**Quality**: `quality.nc_created`, `quality.capa_created`, `quality.audit_scheduled`, `quality.audit_completed`

**HR**: `hr.employee_onboarded`, `hr.training_completed`, `hr.training_due`, `hr.leave_requested`, `hr.leave_approved`

**Procurement**: `procurement.rfq_created`, `procurement.vendor_responded`, `procurement.po_created`, `procurement.po_approved`, `procurement.goods_received`

**Financial**: `financial.invoice_created`, `financial.invoice_paid`, `financial.payment_pending`, `financial.payment_completed`

**CRM**: `crm.lead_created`, `crm.lead_converted`, `crm.opportunity_won`, `crm.opportunity_lost`

**System**: `system.user_logged_in`, `system.user_logged_out`, `system.backup_completed`, `system.error`, `system.notification_sent`

### Publishing Events

```python
from backend.integrations.events import event_bus, Event, EventType

# Publish event
await event_bus.publish(Event(
    type=EventType.DOCUMENT_APPROVED,
    source="documents_api",
    data={
        "document_id": 123,
        "approver_id": 5,
        "approval_date": datetime.utcnow()
    },
    user_id=5
))
```

### Subscribing to Events

```python
from backend.integrations.events import on_event, EventType

@on_event(EventType.DOCUMENT_APPROVED)
async def handle_document_approval(event):
    # Send notification
    # Update workflows
    # Create audit trail
    print(f"Document {event.data['document_id']} approved")
```

---

## 🤖 AI Orchestration

### Conversational Interface

```python
from backend.integrations.ai_orchestrator import ai_orchestrator

# Chat with AI
result = await ai_orchestrator.chat(
    message="Show me all pending approvals",
    user_id=current_user.id,
    context={
        "page": "approvals",
        "user_role": "manager",
        "module": "documents"
    }
)

print(result['response'])
# Suggested actions
for action in result['actions']:
    print(action)
```

### Document Data Extraction

```python
# Extract data from invoice
result = await ai_orchestrator.extract_data_from_document(
    document_content=pdf_text,
    document_type="invoice",
    fields_to_extract=[
        "invoice_number",
        "vendor_name",
        "date",
        "total_amount",
        "line_items"
    ]
)

extracted_data = result['extracted_data']
```

### Compliance Checking

```python
# Check SOP compliance
result = await ai_orchestrator.check_compliance(
    document_type="SOP",
    content=sop_data,
    standards=["ISO 9001", "FDA 21 CFR Part 11", "GMP"]
)

if result['report']['compliant']:
    print("Document is compliant")
else:
    for issue in result['report']['issues']:
        print(f"Issue: {issue['description']} - Severity: {issue['severity']}")
```

---

## 📬 Notification Hub

### Multi-Channel Notifications

```python
from backend.integrations.notifications import notification_hub, NotificationChannel, NotificationPriority

# Send notification
await notification_hub.send_notification(
    user_id=123,
    title="Task Overdue",
    message="Your task 'Review SOP-001' is overdue by 2 days",
    channels=[
        NotificationChannel.EMAIL,
        NotificationChannel.IN_APP,
        NotificationChannel.SMS
    ],
    priority=NotificationPriority.HIGH,
    action_url="/tasks/456"
)
```

### Daily Digest

```python
# Send daily digest
await notification_hub.send_digest(
    user_id=123,
    digest_type="daily"
)
```

---

## ⚙️ Background Tasks

### Scheduled Tasks

The system runs several automated tasks:

**Daily (2:00 AM)**: Database backup
**Daily (3:00 AM)**: File system backup
**Every 5 minutes**: System health check
**Every hour**: Performance metrics collection
**Daily (9:00 AM)**: Daily digest emails
**Every 4 hours**: Overdue task reminders
**Every 6 hours**: External system sync
**Weekly (Sunday 1:00 AM)**: Old data cleanup

### Manual Task Execution

```python
from backend.integrations.tasks.backups import backup_database
from backend.integrations.tasks.notifications import send_notification_task
from backend.integrations.tasks.etl import export_data

# Queue task
task = backup_database.delay()

# Check task status
status = task.status  # PENDING, STARTED, SUCCESS, FAILURE
result = task.result

# Get task info via API
GET /api/v1/integrations/tasks/{task_id}
```

---

## 🔗 External Integrations

### Email Service

```python
from backend.integrations.external.email_service import email_service

# Send email
await email_service.send_email(
    to=["user@example.com"],
    subject="Welcome to LIMS-QMS",
    body="Welcome message...",
    html=True
)

# Send template email
await email_service.send_template_email(
    to=["user@example.com"],
    template_name="task_assigned",
    template_data={
        "user_name": "John Doe",
        "task_title": "Review Document",
        "due_date": "2024-01-20",
        "task_url": "http://localhost:8501/tasks/123"
    },
    subject="New Task Assigned"
)
```

### Calendar Integration

```python
from backend.integrations.external.calendar_service import calendar_service

# Create calendar event
event = await calendar_service.create_event(
    title="Quality Audit",
    start_time=datetime(2024, 1, 20, 10, 0),
    end_time=datetime(2024, 1, 20, 12, 0),
    description="Internal quality audit",
    attendees=["manager@example.com", "auditor@example.com"]
)
```

### Cloud Storage

```python
from backend.integrations.external.cloud_storage import cloud_storage

# Initialize S3
cloud_storage.initialize_s3(
    aws_access_key="...",
    aws_secret_key="...",
    region="us-east-1"
)

# Upload file
result = await cloud_storage.upload_to_s3(
    bucket="lims-qms-backups",
    key="backups/db_20240115.sql",
    file_content=backup_data
)

# Upload to Google Drive
result = await cloud_storage.upload_to_google_drive(
    file_name="report.pdf",
    file_content=pdf_content
)
```

---

## 📊 Monitoring & Health

### System Health Checks

Health checks run every 5 minutes and monitor:
- CPU usage
- Memory usage
- Disk space
- Database connectivity
- Redis connectivity
- API responsiveness

### Performance Metrics

Collected every hour:
- System resource usage
- Network I/O
- Process metrics
- API request counts
- Response times
- Error rates

### Accessing Monitoring Tools

- **Celery Flower**: http://localhost:5555
- **RabbitMQ Management**: http://localhost:15672
- **API Health**: http://localhost:8000/api/v1/integrations/system/health
- **API Metrics**: http://localhost:8000/api/v1/integrations/system/metrics

---

## 💾 Backup & Recovery

### Automated Backups

**Database Backups**:
- Schedule: Daily at 2:00 AM
- Format: PostgreSQL custom format (compressed)
- Retention: 7 days local, 30 days in S3
- Location: `/backups/database/`

**File Backups**:
- Schedule: Daily at 3:00 AM
- Format: tar.gz archive
- Includes: uploads, documents, exports
- Retention: 7 days local, 30 days in S3
- Location: `/backups/files/`

### Manual Backups

```bash
# Via API
curl -X POST http://localhost:8000/api/v1/integrations/system/backup/database \
  -H "Authorization: Bearer {token}"

# Via Celery
from backend.integrations.tasks.backups import backup_database, backup_files

backup_database.delay()
backup_files.delay()
```

### Restore Procedures

```bash
# Restore database from backup
pg_restore -d lims_qms --clean --if-exists /backups/database/lims_qms_20240115.sql

# Restore files
tar -xzf /backups/files/files_20240115.tar.gz
```

---

## 🔐 Security

### API Security Features

- **Rate Limiting**: 100 requests per 60 seconds per client
- **Request Throttling**: Max 10 concurrent requests per client
- **CORS Protection**: Configured allowed origins
- **Security Headers**: CSP, XSS Protection, Frame Options
- **JWT Authentication**: Bearer token authentication
- **Request Logging**: All API requests logged
- **API Versioning**: Support for multiple API versions

### Middleware Stack

1. CORSSecurityMiddleware - Security headers
2. RequestLoggingMiddleware - Request/response logging
3. APIVersioningMiddleware - API versioning
4. RateLimitMiddleware - Rate limiting
5. RequestThrottlingMiddleware - Concurrent request limiting

---

## 📈 Performance Optimization

### Caching Strategy

- **Redis Cache**: Session data, frequently accessed data
- **Query Results**: Cached with TTL
- **Event History**: Last 1000 events per type

### Background Processing

- **Celery Workers**: 4 concurrent workers
- **Task Queues**: Separate queues for different task types
- **Task Priorities**: High, normal, low priority queues
- **Result Backend**: Redis for task results

### Database Optimization

- **Connection Pooling**: Configured in SQLAlchemy
- **Async Queries**: Using asyncpg for async operations
- **Indexed Columns**: Critical fields indexed
- **Query Optimization**: N+1 query prevention

---

## 🐛 Troubleshooting

### Common Issues

**Event Bus Not Connected**:
```bash
# Check Redis
redis-cli ping
# Should return PONG

# Check logs
docker-compose logs backend
```

**Celery Workers Not Processing Tasks**:
```bash
# Check worker status
celery -A backend.integrations.celery_app inspect active

# Check Flower
http://localhost:5555
```

**AI Features Not Working**:
```bash
# Check ANTHROPIC_API_KEY is set
echo $ANTHROPIC_API_KEY

# Check API key validity
# View logs for API errors
```

**Database Backup Failing**:
```bash
# Check permissions
ls -la /backups

# Check disk space
df -h

# Manual backup test
pg_dump postgresql://postgres:postgres@localhost:5432/lims_qms -f test.sql
```

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
docker-compose logs -f celery-worker
docker-compose logs -f celery-beat

# View application logs
tail -f logs/app.log
```

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Celery Flower**: http://localhost:5555
- **RabbitMQ Management**: http://localhost:15672

---

## 🎯 Next Steps

1. Configure environment variables in `.env`
2. Set up ANTHROPIC_API_KEY for AI features
3. Configure email settings for notifications
4. Set up cloud storage (S3) for backups
5. Configure external integrations (Slack, Twilio, etc.)
6. Review and adjust scheduled task timings
7. Set up monitoring alerts
8. Configure backup retention policies

---

## 📝 License

Copyright © 2024 LIMS-QMS Organization OS
