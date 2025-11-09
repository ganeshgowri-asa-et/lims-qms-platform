"""
Dynamic Form Engine models
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, JSON, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class FieldTypeEnum(str, enum.Enum):
    """Field types for dynamic forms"""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    DATETIME = "datetime"
    DROPDOWN = "dropdown"
    MULTISELECT = "multiselect"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    FILE = "file"
    SIGNATURE = "signature"
    TABLE = "table"
    SECTION = "section"
    CALCULATED = "calculated"


class FormTemplate(BaseModel):
    """Form template generated from Excel/Word files"""
    __tablename__ = 'form_templates'

    name = Column(String(500), nullable=False)
    code = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    source_file = Column(String(500), nullable=True)  # Original Excel/Word file
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=True)  # Link to Level 4 document
    is_published = Column(Boolean, default=False)
    version = Column(String(20), default="1.0")
    layout_config = Column(JSON, nullable=True)  # UI layout configuration

    # Relationships
    fields = relationship('FormField', back_populates='template', cascade='all, delete-orphan')
    records = relationship('FormRecord', back_populates='template')


class FormField(BaseModel):
    """Form field definition"""
    __tablename__ = 'form_fields'

    template_id = Column(Integer, ForeignKey('form_templates.id', ondelete='CASCADE'), nullable=False)
    field_name = Column(String(200), nullable=False)
    field_label = Column(String(500), nullable=False)
    field_type = Column(Enum(FieldTypeEnum), nullable=False)
    order = Column(Integer, default=0)
    is_required = Column(Boolean, default=False)
    is_readonly = Column(Boolean, default=False)
    default_value = Column(Text, nullable=True)
    placeholder = Column(String(500), nullable=True)
    help_text = Column(Text, nullable=True)
    validation_rules = Column(JSON, nullable=True)  # {"min": 0, "max": 100, "pattern": "..."}
    options = Column(JSON, nullable=True)  # For dropdown, radio, multiselect
    section = Column(String(200), nullable=True)  # Group fields into sections
    parent_field_id = Column(Integer, ForeignKey('form_fields.id'), nullable=True)  # For nested fields
    formula = Column(Text, nullable=True)  # For calculated fields
    metadata = Column(JSON, nullable=True)

    # Relationships
    template = relationship('FormTemplate', back_populates='fields')


class FormRecord(BaseModel):
    """Form record instance (Level 5 - Records)"""
    __tablename__ = 'form_records'

    template_id = Column(Integer, ForeignKey('form_templates.id'), nullable=False)
    record_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=True)
    status = Column(String(50), default='draft')  # draft, submitted, reviewed, approved, rejected
    submitted_at = Column(String(255), nullable=True)

    # Workflow
    doer_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    checker_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    approver_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    checked_at = Column(String(255), nullable=True)
    approved_at = Column(String(255), nullable=True)
    checker_comments = Column(Text, nullable=True)
    approver_comments = Column(Text, nullable=True)

    # Metadata
    metadata = Column(JSON, nullable=True)
    attachments = Column(JSON, nullable=True)  # List of file paths

    # Relationships
    template = relationship('FormTemplate', back_populates='records')
    values = relationship('FormValue', back_populates='record', cascade='all, delete-orphan')


class FormValue(BaseModel):
    """Form field values"""
    __tablename__ = 'form_values'

    record_id = Column(Integer, ForeignKey('form_records.id', ondelete='CASCADE'), nullable=False)
    field_id = Column(Integer, ForeignKey('form_fields.id'), nullable=True)
    field_name = Column(String(200), nullable=False)
    value = Column(Text, nullable=True)
    value_json = Column(JSON, nullable=True)  # For complex values like tables
    row_index = Column(Integer, nullable=True)  # For table fields

    # Relationships
    record = relationship('FormRecord', back_populates='values')
