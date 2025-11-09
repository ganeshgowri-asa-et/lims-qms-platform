"""
Constants and enums for the LIMS/QMS platform
"""
from enum import Enum


# Document Prefixes
class DocPrefix:
    TEST_REQUEST = "TRQ"  # Test Request
    SAMPLE = "SMP"        # Sample
    ANALYSIS = "ANL"      # Analysis
    REPORT = "RPT"        # Report
    QUOTE = "QTE"         # Quote


# Test Request Statuses
class TestRequestStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


# Sample Statuses
class SampleStatus(str, Enum):
    PENDING = "pending"
    RECEIVED = "received"
    IN_TESTING = "in_testing"
    TESTED = "tested"
    COMPLETED = "completed"
    REJECTED = "rejected"
    ARCHIVED = "archived"


# Test Types
TEST_TYPES = [
    "Chemical Analysis",
    "Microbiological Testing",
    "Physical Testing",
    "Mechanical Testing",
    "Electrical Testing",
    "Environmental Testing",
    "Performance Testing",
    "Safety Testing",
    "Stability Testing",
]


# Priorities
class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Sample Types
SAMPLE_TYPES = [
    "Solid",
    "Liquid",
    "Gas",
    "Powder",
    "Semi-Solid",
    "Other"
]


# Units
UNITS = [
    "mg",
    "g",
    "kg",
    "ml",
    "L",
    "pieces",
    "units",
    "samples"
]


# Customer Types
class CustomerType(str, Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"
    GOVERNMENT = "government"
    ACADEMIC = "academic"


# QSF Form Reference
QSF_FORM_NUMBER = "QSF0601"
QSF_FORM_TITLE = "Test Request Form"
QSF_FORM_VERSION = "1.0"
