# Workflow Automation Engine - Session 3

## Overview

The Workflow Automation Engine is a comprehensive task and workflow management system that provides enterprise-grade automation capabilities for the LIMS-QMS platform.

## Features

### 1. **Project Management**
- Create and track projects with multiple attributes
- **Milestones**: Define key project milestones with completion criteria
- **Deliverables**: Track project outputs and submissions
- **Gantt Charts**: Visual timeline representation of project tasks
- **Kanban Boards**: Agile task management interface
- **Resource Allocation**: Track team members, equipment, and materials
- **Budget Tracking**: Monitor project costs against budget
- **Risk Register**: Identify and manage project risks

### 2. **Task Management**
- **Task Creation**: Create tasks with rich metadata
- **Task Assignment**: Assign to team members
- **Dependencies**: Define task dependencies (blocks/depends_on)
- **Subtasks**: Hierarchical task breakdown
- **Priorities**: Critical, High, Medium, Low
- **Deadlines**: Track due dates
- **Checklists**: In-task checklist items
- **Time Tracking**: Log hours worked on tasks
- **Progress Tracking**: 0-100% completion
- **Comments**: Collaborate with task comments
- **Watchers**: Notify specific users of task updates

### 3. **Workflow Engine**
- **Custom Workflows**: Define any business process as a workflow
- **State Machine**: Robust state transition management
- **Conditional Routing**: Route based on data and rules
- **Parallel Execution**: Run multiple steps simultaneously
- **Sequential Steps**: Ordered step execution
- **Auto-escalation**: Automatic escalation for delays
- **SLA Tracking**: Monitor service level agreements
- **Approval Workflows**: Multi-level approvals
- **Notifications**: Email, in-app, webhook notifications

### 4. **Meeting Management**
- **Schedule Meetings**: Create meetings with agendas
- **Attendees**: Track meeting participants
- **Minutes**: Record meeting minutes
- **Action Items**: Convert discussions to tasks
- **Follow-up Reminders**: Automatic reminders
- **Calendar Integration**: iCalendar format export

### 5. **Equipment Lifecycle**
Complete equipment tracking from procurement to retirement:
- **Procurement**: RFQ, bid evaluation, PO creation
- **Installation**: Location tracking
- **Commissioning**: FAT/SAT documentation
- **Calibration Scheduling**: Automatic reminders
- **Maintenance Tracking**: Preventive and corrective
- **Equipment History Card**: Complete lifecycle record
- **Decommissioning**: End-of-life management

### 6. **CRM & Sales**
- **Lead Capture**: Track potential customers
- **Lead Tracking**: Monitor lead status
- **Customer Interactions**: Log all interactions
- **Opportunity Pipeline**: Sales funnel management
- **Quotation Generation**: Create professional quotes
- **Order Conversion**: Convert quotes to orders
- **Payment Tracking**: Monitor payments

### 7. **HR Workflows**
- **Hiring Process**: JD → Screening → Interviews → Offers
- **Onboarding**: Structured onboarding workflows
- **Training Management**: Track training programs
- **Performance Reviews**: Annual/quarterly reviews
- **Leave Management**: Leave applications and approvals
- **Attendance Tracking**: Daily attendance
- **Exit Process**: Structured offboarding

### 8. **Finance Workflows**
- **Expense Claims**: Employee expense submissions
- **Invoice Generation**: Create customer invoices
- **Payment Processing**: Track payments
- **Budget Approvals**: Multi-level approval workflows

## Technical Architecture

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Task Queue**: Celery
- **Message Broker**: Redis
- **State Machine**: Custom implementation

### Models

#### Core Workflow Models
- `WorkflowDefinition`: Workflow templates
- `WorkflowInstance`: Running workflow instances
- `WorkflowStepHistory`: Audit trail of steps
- `SLAViolation`: SLA tracking

#### Project Management Models
- `Project`: Project master
- `Task`: Task management
- `Milestone`: Project milestones
- `Deliverable`: Project outputs
- `Risk`: Risk register
- `ResourceAllocation`: Resource planning
- `TimeEntry`: Time tracking
- `TaskComment`: Task collaboration

#### Supporting Models
- `Meeting`: Meeting management
- `ActionItem`: Meeting action items
- `EquipmentLifecycleEvent`: Equipment tracking
- `Quotation`: Sales quotations

### API Endpoints

#### Workflows
```
POST   /api/v1/workflows/definitions          # Create workflow
GET    /api/v1/workflows/definitions          # List workflows
GET    /api/v1/workflows/definitions/{id}     # Get workflow
POST   /api/v1/workflows/instances            # Start instance
GET    /api/v1/workflows/instances            # List instances
GET    /api/v1/workflows/instances/{id}/status # Get status
POST   /api/v1/workflows/instances/{id}/advance # Advance workflow
POST   /api/v1/workflows/instances/{id}/cancel  # Cancel workflow
GET    /api/v1/workflows/sla-violations       # Check SLA
```

#### Milestones & Deliverables
```
POST   /api/v1/milestones                     # Create milestone
GET    /api/v1/milestones                     # List milestones
PUT    /api/v1/milestones/{id}                # Update milestone
POST   /api/v1/milestones/deliverables        # Create deliverable
GET    /api/v1/milestones/deliverables        # List deliverables
```

#### Risks
```
POST   /api/v1/risks                          # Create risk
GET    /api/v1/risks                          # List risks
PUT    /api/v1/risks/{id}                     # Update risk
```

#### Quotations
```
POST   /api/v1/quotations                     # Create quotation
GET    /api/v1/quotations                     # List quotations
PUT    /api/v1/quotations/{id}/status         # Update status
POST   /api/v1/quotations/{id}/convert-to-order # Convert to order
```

#### Equipment Lifecycle
```
POST   /api/v1/equipment-lifecycle            # Create event
GET    /api/v1/equipment-lifecycle            # List events
GET    /api/v1/equipment-lifecycle/equipment/{id}/history # Get history
```

#### Time Tracking
```
POST   /api/v1/time-tracking                  # Log time
GET    /api/v1/time-tracking                  # List entries
GET    /api/v1/time-tracking/summary          # Get summary
POST   /api/v1/time-tracking/comments         # Add comment
```

## Workflow Engine Usage

### 1. Define a Workflow

```python
workflow_definition = {
    "workflow_code": "EQUIPMENT_PROCUREMENT",
    "name": "Equipment Procurement Workflow",
    "category": "Equipment",
    "description": "Workflow for procuring new equipment",
    "steps": [
        {
            "step_id": "request",
            "name": "Procurement Request",
            "type": "task",
            "assignee_type": "role",
            "assignee_value": "procurement_manager",
            "next_steps": ["approval"]
        },
        {
            "step_id": "approval",
            "name": "Manager Approval",
            "type": "approval",
            "assignee_type": "role",
            "assignee_value": "department_head",
            "next_steps": ["rfq"],
            "conditions": {
                "approve": ["rfq"],
                "reject": []
            }
        },
        {
            "step_id": "rfq",
            "name": "Send RFQ",
            "type": "task",
            "assignee_type": "role",
            "assignee_value": "procurement_officer",
            "next_steps": ["evaluation"]
        },
        {
            "step_id": "evaluation",
            "name": "Bid Evaluation",
            "type": "task",
            "assignee_type": "role",
            "assignee_value": "procurement_manager",
            "next_steps": ["po_creation"]
        },
        {
            "step_id": "po_creation",
            "name": "Create Purchase Order",
            "type": "task",
            "assignee_type": "role",
            "assignee_value": "procurement_officer",
            "next_steps": []
        }
    ],
    "initial_step": "request",
    "sla_config": {
        "request": {"duration_hours": 24, "escalation_rules": {}},
        "approval": {"duration_hours": 48, "escalation_rules": {}},
        "rfq": {"duration_hours": 72, "escalation_rules": {}}
    }
}

# Create via API
response = requests.post(
    "http://localhost:8000/api/v1/workflows/definitions",
    json=workflow_definition,
    headers={"Authorization": f"Bearer {token}"}
)
```

### 2. Start a Workflow Instance

```python
instance_data = {
    "workflow_definition_id": 1,
    "entity_type": "equipment",
    "entity_id": 123,
    "initial_variables": {
        "equipment_name": "Solar Simulator",
        "estimated_cost": 500000
    }
}

response = requests.post(
    "http://localhost:8000/api/v1/workflows/instances",
    json=instance_data,
    headers={"Authorization": f"Bearer {token}"}
)
```

### 3. Advance Workflow

```python
action_data = {
    "action": "approve",
    "data": {
        "approved_amount": 500000
    },
    "comments": "Approved for procurement"
}

response = requests.post(
    f"http://localhost:8000/api/v1/workflows/instances/{instance_id}/advance",
    json=action_data,
    headers={"Authorization": f"Bearer {token}"}
)
```

## Celery Tasks

### Periodic Tasks

```python
# SLA violation checking (every 5 minutes)
check_sla_violations()

# Task reminders (hourly)
send_task_reminders()

# Meeting reminders (every 30 minutes)
send_meeting_reminders()

# Calibration schedule updates (daily)
update_calibration_schedules()
```

### Background Tasks

```python
# Auto-advance workflow
auto_advance_workflow.delay(instance_id, action, data)

# Process equipment lifecycle
process_equipment_lifecycle.delay(equipment_id, stage, event_data)

# Send notifications
send_email_notification.delay(to_emails, subject, body)
send_in_app_notification.delay(user_ids, title, message)
send_webhook_notification.delay(webhook_url, payload)
```

## Notification System

### Channels
1. **Email**: SMTP-based email notifications
2. **In-app**: Database-stored notifications
3. **Webhooks**: HTTP POST to external systems

### Events
- Task assignment
- Task status change
- Meeting scheduled
- SLA violation
- Workflow step entry
- Milestone approaching
- Equipment calibration due

## Gantt Chart & Kanban Board

### Gantt Chart Generation

```python
from backend.services.project_utils import GanttChartService

gantt_service = GanttChartService(db)
gantt_data = gantt_service.generate_project_gantt(project_id)

# Export to Mermaid
mermaid_diagram = gantt_service.export_to_mermaid_gantt(project_id)
```

### Kanban Board

```python
from backend.services.project_utils import KanbanBoardService

kanban_service = KanbanBoardService(db)
kanban_data = kanban_service.generate_kanban_board(
    project_id=1,
    assigned_to_id=5
)

# Move task to different column
kanban_service.move_task(task_id, TaskStatusEnum.IN_PROGRESS)
```

## Resource Utilization

```python
from backend.services.project_utils import ResourceUtilizationService

resource_service = ResourceUtilizationService(db)
utilization = resource_service.calculate_team_utilization(
    user_ids=[1, 2, 3],
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 1, 31)
)
```

## Calendar Integration

### iCalendar Export

```python
from backend.services.tasks.calendar_tasks import sync_calendar_event

# Sync meeting to calendar
sync_calendar_event.delay(
    event_type="meeting",
    event_id=123,
    action="create"
)
```

## Risk Management

### Risk Matrix

| Probability / Impact | Low | Medium | High | Critical |
|---------------------|-----|--------|------|----------|
| **Low**             | Low | Low    | Med  | Med      |
| **Medium**          | Low | Med    | High | High     |
| **High**            | Med | High   | High | Critical |
| **Critical**        | Med | High   | Crit | Critical |

## Best Practices

### 1. Workflow Design
- Keep workflows simple and linear when possible
- Use parallel steps only when truly necessary
- Define clear SLAs for each step
- Configure appropriate notifications

### 2. Task Management
- Always set due dates
- Use task dependencies wisely
- Assign tasks to specific individuals
- Break down large tasks into subtasks
- Track time regularly

### 3. Project Planning
- Define milestones upfront
- Identify and track risks early
- Allocate resources before starting
- Monitor budget regularly

### 4. Resource Management
- Monitor team utilization weekly
- Balance workload across team
- Account for leave and holidays
- Track billable vs non-billable hours

## Database Migrations

After implementing workflow automation, run migrations:

```bash
# Generate migration
alembic revision --autogenerate -m "Add workflow automation models"

# Apply migration
alembic upgrade head
```

## Starting Celery Worker

```bash
# Start Celery worker
celery -A backend.services.celery_app worker --loglevel=info

# Start Celery beat (for periodic tasks)
celery -A backend.services.celery_app beat --loglevel=info
```

## Environment Variables

Add to `.env`:

```bash
# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@lims-qms.com
```

## Testing

```bash
# Run tests
pytest tests/backend/test_workflow_engine.py
pytest tests/backend/test_project_management.py
pytest tests/backend/test_notifications.py
```

## Performance Considerations

- Use background tasks for heavy operations
- Implement pagination for large lists
- Cache frequently accessed workflow definitions
- Index foreign keys and commonly queried fields
- Monitor Celery queue length
- Set appropriate SLA timeouts

## Security

- All endpoints require authentication
- Role-based access control for sensitive operations
- Audit trail for all workflow actions
- Secure webhook endpoints
- Validate all user inputs

## Integration with Sessions 1 & 2

This workflow automation engine integrates seamlessly with:
- **Document Management**: Link documents to tasks/projects
- **Form Engine**: Generate forms from workflow steps
- **Traceability**: Full audit trail of all actions
- **Quality Management**: CAPA workflows
- **User Management**: Role-based workflow assignments

## Future Enhancements

- Workflow templates marketplace
- AI-powered task recommendations
- Advanced analytics dashboards
- Mobile app support
- Real-time collaboration
- Video conferencing integration
- Advanced reporting engine

## Support

For issues or questions:
- Check API documentation: http://localhost:8000/api/docs
- Review code in `backend/services/workflow_engine.py`
- Examine models in `backend/models/workflow.py`

---

**Built with ❤️ for Enterprise Workflow Automation**
