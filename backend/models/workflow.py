"""
Workflow and Task Management models
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Enum, JSON, Boolean
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
    budget = Column(Integer, nullable=True)
    actual_cost = Column(Integer, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    tasks = relationship('Task', back_populates='project', cascade='all, delete-orphan')
    meetings = relationship('Meeting', back_populates='project')


class Task(BaseModel):
    """Task model"""
    __tablename__ = 'tasks'

    task_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.TODO, nullable=False)
    priority = Column(Enum(TaskPriorityEnum), default=TaskPriorityEnum.MEDIUM, nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    parent_task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    assigned_to_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    due_date = Column(Date, nullable=True)
    estimated_hours = Column(Integer, nullable=True)
    actual_hours = Column(Integer, nullable=True)
    progress = Column(Integer, default=0)  # 0-100
    tags = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    project = relationship('Project', back_populates='tasks')
    parent_task = relationship('Task', remote_side='Task.id', foreign_keys=[parent_task_id])


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
