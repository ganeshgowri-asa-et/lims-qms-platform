"""
Workflow and Task Management models
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, DateTime, Enum, JSON, Boolean, Float
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class ProjectStatusEnum(str, enum.Enum):
    """Project status"""
    PLANNING = "Planning"
    IN_PROGRESS = "In Progress"
    ON_HOLD = "On Hold"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class TaskStatusEnum(str, enum.Enum):
    """Task status"""
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    IN_REVIEW = "In Review"
    COMPLETED = "Completed"
    BLOCKED = "Blocked"
    CANCELLED = "Cancelled"


class TaskPriorityEnum(str, enum.Enum):
    """Task priority"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class MilestoneStatusEnum(str, enum.Enum):
    """Milestone status"""
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    MISSED = "Missed"


class WorkflowStatusEnum(str, enum.Enum):
    """Workflow instance status"""
    INITIATED = "Initiated"
    IN_PROGRESS = "In Progress"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    FAILED = "Failed"


class RiskLevelEnum(str, enum.Enum):
    """Risk level"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class EquipmentLifecycleStageEnum(str, enum.Enum):
    """Equipment lifecycle stages"""
    PROCUREMENT = "Procurement"
    INSTALLATION = "Installation"
    COMMISSIONING = "Commissioning"
    OPERATIONAL = "Operational"
    MAINTENANCE = "Maintenance"
    CALIBRATION = "Calibration"
    REPAIR = "Repair"
    DECOMMISSIONING = "Decommissioning"
    RETIRED = "Retired"


class Project(BaseModel):
    """Project model"""
    __tablename__ = 'projects'

    project_number = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(ProjectStatusEnum), default=ProjectStatusEnum.PLANNING, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    project_manager_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    budget = Column(Float, nullable=True)
    actual_cost = Column(Float, nullable=True)
    currency = Column(String(10), default='INR')

    # Project tracking
    progress = Column(Integer, default=0)  # 0-100 percentage
    health_status = Column(String(50), nullable=True)  # On Track, At Risk, Off Track

    # Resources
    team_members = Column(JSON, nullable=True)  # List of user IDs
    allocated_resources = Column(JSON, nullable=True)  # Equipment, materials, etc.

    # Additional fields
    priority = Column(Enum(TaskPriorityEnum), default=TaskPriorityEnum.MEDIUM)
    tags = Column(JSON, nullable=True)
    attachments = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    tasks = relationship('Task', back_populates='project', cascade='all, delete-orphan')
    meetings = relationship('Meeting', back_populates='project')
    milestones = relationship('Milestone', back_populates='project', cascade='all, delete-orphan')
    deliverables = relationship('Deliverable', back_populates='project', cascade='all, delete-orphan')
    risks = relationship('Risk', back_populates='project', cascade='all, delete-orphan')
    resource_allocations = relationship('ResourceAllocation', back_populates='project')


class Task(BaseModel):
    """Task model"""
    __tablename__ = 'tasks'

    task_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.TODO, nullable=False)
    priority = Column(Enum(TaskPriorityEnum), default=TaskPriorityEnum.MEDIUM, nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    milestone_id = Column(Integer, ForeignKey('milestones.id'), nullable=True)
    parent_task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    assigned_to_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    watchers = Column(JSON, nullable=True)  # User IDs to notify

    # Dates
    start_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    completed_date = Column(Date, nullable=True)

    # Effort tracking
    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, nullable=True)
    progress = Column(Integer, default=0)  # 0-100

    # Dependencies
    depends_on = Column(JSON, nullable=True)  # List of task IDs that must complete first
    blocks = Column(JSON, nullable=True)  # List of task IDs that depend on this task

    # Checklists
    checklist = Column(JSON, nullable=True)  # [{item: "...", completed: true/false}]

    # Attachments & metadata
    attachments = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    custom_fields = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    project = relationship('Project', back_populates='tasks')
    milestone = relationship('Milestone', back_populates='tasks')
    parent_task = relationship('Task', remote_side='Task.id', foreign_keys=[parent_task_id])
    time_entries = relationship('TimeEntry', back_populates='task', cascade='all, delete-orphan')
    comments = relationship('TaskComment', back_populates='task', cascade='all, delete-orphan')


class Meeting(BaseModel):
    """Meeting model"""
    __tablename__ = 'meetings'

    meeting_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    meeting_date = Column(Date, nullable=False)
    start_time = Column(String(10), nullable=True)
    end_time = Column(String(10), nullable=True)
    location = Column(String(500), nullable=True)
    meeting_link = Column(String(500), nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    organizer_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    attendees = Column(JSON, nullable=True)  # List of user IDs
    agenda = Column(Text, nullable=True)
    minutes = Column(Text, nullable=True)
    recording_link = Column(String(500), nullable=True)
    attachments = Column(JSON, nullable=True)

    # Relationships
    project = relationship('Project', back_populates='meetings')
    action_items = relationship('ActionItem', back_populates='meeting')


class ActionItem(BaseModel):
    """Action item from meetings"""
    __tablename__ = 'action_items'

    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    description = Column(Text, nullable=False)
    assigned_to_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    due_date = Column(Date, nullable=True)
    status = Column(String(50), default='open')  # open, in_progress, completed, cancelled
    completion_notes = Column(Text, nullable=True)

    # Relationships
    meeting = relationship('Meeting', back_populates='action_items')


class Milestone(BaseModel):
    """Project milestones"""
    __tablename__ = 'milestones'

    milestone_number = Column(String(100), unique=True, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(MilestoneStatusEnum), default=MilestoneStatusEnum.PENDING)
    due_date = Column(Date, nullable=False)
    completed_date = Column(Date, nullable=True)
    completion_criteria = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Relationships
    project = relationship('Project', back_populates='milestones')
    tasks = relationship('Task', back_populates='milestone')
    deliverables = relationship('Deliverable', back_populates='milestone')


class Deliverable(BaseModel):
    """Project deliverables"""
    __tablename__ = 'deliverables'

    deliverable_number = Column(String(100), unique=True, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    milestone_id = Column(Integer, ForeignKey('milestones.id'), nullable=True)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(100), nullable=True)  # Document, Report, Software, Hardware
    status = Column(String(50), default='pending')  # pending, in_progress, completed, approved
    due_date = Column(Date, nullable=True)
    submitted_date = Column(Date, nullable=True)
    approved_date = Column(Date, nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    file_path = Column(String(500), nullable=True)
    version = Column(String(50), nullable=True)
    review_comments = Column(Text, nullable=True)

    # Relationships
    project = relationship('Project', back_populates='deliverables')
    milestone = relationship('Milestone', back_populates='deliverables')


class Risk(BaseModel):
    """Project risk register"""
    __tablename__ = 'risks'

    risk_number = Column(String(100), unique=True, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # Technical, Financial, Schedule, Resource
    probability = Column(Enum(RiskLevelEnum), nullable=False)
    impact = Column(Enum(RiskLevelEnum), nullable=False)
    overall_risk_level = Column(String(50), nullable=True)  # Calculated from probability * impact
    status = Column(String(50), default='identified')  # identified, analyzing, mitigating, closed
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    mitigation_plan = Column(Text, nullable=True)
    contingency_plan = Column(Text, nullable=True)
    identified_date = Column(Date, nullable=True)
    review_date = Column(Date, nullable=True)
    closed_date = Column(Date, nullable=True)

    # Relationships
    project = relationship('Project', back_populates='risks')


class ResourceAllocation(BaseModel):
    """Resource allocation for projects"""
    __tablename__ = 'resource_allocations'

    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    resource_type = Column(String(100), nullable=False)  # Human, Equipment, Material, Budget
    resource_name = Column(String(255), nullable=False)
    resource_id = Column(Integer, nullable=True)  # FK to users, equipment, etc.
    allocated_quantity = Column(Float, nullable=True)
    allocated_hours = Column(Float, nullable=True)
    allocated_cost = Column(Float, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    utilization = Column(Float, nullable=True)  # Percentage
    notes = Column(Text, nullable=True)

    # Relationships
    project = relationship('Project', back_populates='resource_allocations')


class TimeEntry(BaseModel):
    """Time tracking for tasks"""
    __tablename__ = 'time_entries'

    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    entry_date = Column(Date, nullable=False)
    hours = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    billable = Column(Boolean, default=True)

    # Relationships
    task = relationship('Task', back_populates='time_entries')


class TaskComment(BaseModel):
    """Comments on tasks"""
    __tablename__ = 'task_comments'

    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    comment = Column(Text, nullable=False)
    attachments = Column(JSON, nullable=True)

    # Relationships
    task = relationship('Task', back_populates='comments')


class WorkflowDefinition(BaseModel):
    """Workflow definition/template"""
    __tablename__ = 'workflow_definitions'

    workflow_code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # Equipment, HR, Finance, CRM, etc.
    version = Column(String(50), default='1.0')

    # Workflow structure
    steps = Column(JSON, nullable=False)  # [{step_id, name, type, config, next_steps, conditions}]
    initial_step = Column(String(100), nullable=False)
    variables = Column(JSON, nullable=True)  # Workflow variables and their types

    # SLA configuration
    sla_config = Column(JSON, nullable=True)  # {step_id: {duration_hours, escalation_rules}}

    # Notification configuration
    notification_config = Column(JSON, nullable=True)  # {step_id: {notify_users, notify_roles, templates}}

    is_active = Column(Boolean, default=True)

    # Relationships
    instances = relationship('WorkflowInstance', back_populates='definition')


class WorkflowInstance(BaseModel):
    """Workflow instance/execution"""
    __tablename__ = 'workflow_instances'

    instance_number = Column(String(100), unique=True, nullable=False, index=True)
    workflow_definition_id = Column(Integer, ForeignKey('workflow_definitions.id'), nullable=False)
    entity_type = Column(String(100), nullable=True)  # e.g., 'equipment', 'employee', 'order'
    entity_id = Column(Integer, nullable=True)  # FK to the entity
    status = Column(Enum(WorkflowStatusEnum), default=WorkflowStatusEnum.INITIATED)
    current_step = Column(String(100), nullable=True)
    started_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    variables = Column(JSON, nullable=True)  # Current workflow variable values

    # Relationships
    definition = relationship('WorkflowDefinition', back_populates='instances')
    step_history = relationship('WorkflowStepHistory', back_populates='instance', cascade='all, delete-orphan')
    sla_violations = relationship('SLAViolation', back_populates='workflow_instance')


class WorkflowStepHistory(BaseModel):
    """History of workflow step executions"""
    __tablename__ = 'workflow_step_history'

    instance_id = Column(Integer, ForeignKey('workflow_instances.id'), nullable=False)
    step_id = Column(String(100), nullable=False)
    step_name = Column(String(500), nullable=False)
    status = Column(String(50), nullable=False)  # entered, completed, failed, skipped
    entered_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    assigned_to_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    action_taken = Column(String(200), nullable=True)  # approve, reject, complete, etc.
    comments = Column(Text, nullable=True)
    data = Column(JSON, nullable=True)  # Step-specific data

    # Relationships
    instance = relationship('WorkflowInstance', back_populates='step_history')


class SLAViolation(BaseModel):
    """SLA violation tracking"""
    __tablename__ = 'sla_violations'

    workflow_instance_id = Column(Integer, ForeignKey('workflow_instances.id'), nullable=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=False)
    sla_type = Column(String(100), nullable=False)  # response_time, resolution_time, etc.
    expected_completion = Column(DateTime, nullable=False)
    actual_completion = Column(DateTime, nullable=True)
    violation_duration_hours = Column(Float, nullable=True)
    severity = Column(Enum(RiskLevelEnum), nullable=False)
    notified_users = Column(JSON, nullable=True)
    escalated = Column(Boolean, default=False)
    escalated_to_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # Relationships
    workflow_instance = relationship('WorkflowInstance', back_populates='sla_violations')


class EquipmentLifecycleEvent(BaseModel):
    """Equipment lifecycle events tracking"""
    __tablename__ = 'equipment_lifecycle_events'

    equipment_id = Column(Integer, ForeignKey('equipment.id'), nullable=False)
    event_number = Column(String(100), unique=True, nullable=False, index=True)
    stage = Column(Enum(EquipmentLifecycleStageEnum), nullable=False)
    event_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    performed_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Stage-specific fields
    rfq_id = Column(Integer, ForeignKey('rfqs.id'), nullable=True)  # For procurement
    po_id = Column(Integer, ForeignKey('purchase_orders.id'), nullable=True)  # For procurement
    installation_location = Column(String(200), nullable=True)  # For installation
    commissioning_report = Column(String(500), nullable=True)  # For commissioning
    fat_sat_report = Column(String(500), nullable=True)  # Factory/Site Acceptance Test
    calibration_id = Column(Integer, ForeignKey('calibrations.id'), nullable=True)  # For calibration
    maintenance_id = Column(Integer, ForeignKey('maintenance_records.id'), nullable=True)  # For maintenance
    decommission_reason = Column(Text, nullable=True)  # For decommissioning

    cost = Column(Float, nullable=True)
    documents = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)


class Quotation(BaseModel):
    """Quotations for CRM"""
    __tablename__ = 'quotations'

    quotation_number = Column(String(100), unique=True, nullable=False, index=True)
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    quotation_date = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=True)
    status = Column(String(50), default='draft')  # draft, sent, accepted, rejected, expired

    # Items and pricing
    items = Column(JSON, nullable=False)  # List of items with details
    subtotal = Column(Float, nullable=False)
    tax_rate = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)
    discount = Column(Float, nullable=True)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(10), default='INR')

    # Terms
    payment_terms = Column(String(200), nullable=True)
    delivery_terms = Column(String(200), nullable=True)
    warranty_terms = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Tracking
    prepared_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    sent_date = Column(Date, nullable=True)
    accepted_date = Column(Date, nullable=True)
    converted_to_order_id = Column(Integer, ForeignKey('customer_orders.id'), nullable=True)
    file_path = Column(String(500), nullable=True)
