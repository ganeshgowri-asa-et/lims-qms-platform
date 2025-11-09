"""
Unit Tests for Data Capture Engine
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.database import Base
from backend.models import User, FormTemplate, FormField, FormRecord, FieldTypeEnum
from backend.services import (
    ValidationService,
    WorkflowService,
    RecordService,
    NotificationService
)


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db):
    """Create test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_template(db):
    """Create test template"""
    template = FormTemplate(
        name="Test Template",
        code="TEST",
        description="Test template"
    )
    db.add(template)
    db.commit()
    db.refresh(template)

    # Add fields
    fields = [
        FormField(
            template_id=template.id,
            field_name="name",
            field_label="Name",
            field_type=FieldTypeEnum.TEXT,
            is_required=True,
            order=1
        ),
        FormField(
            template_id=template.id,
            field_name="age",
            field_label="Age",
            field_type=FieldTypeEnum.NUMBER,
            is_required=True,
            validation_rules={"min": 0, "max": 150},
            order=2
        ),
        FormField(
            template_id=template.id,
            field_name="email",
            field_label="Email",
            field_type=FieldTypeEnum.TEXT,
            is_required=False,
            validation_rules={"email": True},
            order=3
        )
    ]

    for field in fields:
        db.add(field)

    db.commit()
    return template


# ============================================================================
# VALIDATION SERVICE TESTS
# ============================================================================

def test_validation_required_fields(db, test_template):
    """Test required field validation"""
    service = ValidationService(db)

    # Missing required field
    values = {"age": 25}
    is_valid, errors, warnings = service.validate_record(test_template.id, values)

    assert not is_valid
    assert len(errors) > 0
    assert any("name" in error["field"].lower() for error in errors)


def test_validation_number_range(db, test_template):
    """Test number range validation"""
    service = ValidationService(db)

    # Age out of range
    values = {"name": "John", "age": 200}
    is_valid, errors, warnings = service.validate_record(test_template.id, values)

    assert not is_valid
    assert any("age" in error["field"].lower() for error in errors)


def test_validation_email_format(db, test_template):
    """Test email format validation"""
    service = ValidationService(db)

    # Invalid email
    values = {"name": "John", "age": 25, "email": "not-an-email"}
    is_valid, errors, warnings = service.validate_record(test_template.id, values)

    assert not is_valid
    assert any("email" in error["field"].lower() for error in errors)


def test_validation_success(db, test_template):
    """Test successful validation"""
    service = ValidationService(db)

    values = {"name": "John Doe", "age": 25, "email": "john@example.com"}
    is_valid, errors, warnings = service.validate_record(test_template.id, values)

    assert is_valid
    assert len(errors) == 0


def test_completion_percentage(db, test_template):
    """Test completion percentage calculation"""
    service = ValidationService(db)

    # All fields filled
    values = {"name": "John", "age": 25, "email": "john@example.com"}
    percentage = service.calculate_completion_percentage(test_template.id, values)
    assert percentage == 100

    # Only required fields
    values = {"name": "John", "age": 25}
    percentage = service.calculate_completion_percentage(test_template.id, values)
    assert percentage < 100


# ============================================================================
# RECORD SERVICE TESTS
# ============================================================================

def test_create_record(db, test_template, test_user):
    """Test record creation"""
    service = RecordService(db)

    values = {"name": "John Doe", "age": 25}
    record = service.create_record(
        template_id=test_template.id,
        user_id=test_user.id,
        values=values,
        title="Test Record"
    )

    assert record.id is not None
    assert record.record_number is not None
    assert record.record_number.startswith("TEST-")
    assert record.doer_id == test_user.id
    assert record.completion_percentage >= 0


def test_record_number_generation(db, test_template, test_user):
    """Test unique record number generation"""
    service = RecordService(db)

    record1 = service.create_record(test_template.id, test_user.id, {"name": "Test1", "age": 25})
    record2 = service.create_record(test_template.id, test_user.id, {"name": "Test2", "age": 30})

    assert record1.record_number != record2.record_number


def test_update_record(db, test_template, test_user):
    """Test record update"""
    service = RecordService(db)

    # Create record
    record = service.create_record(
        test_template.id,
        test_user.id,
        {"name": "John", "age": 25}
    )

    # Update record
    updated = service.update_record(
        record.id,
        test_user.id,
        {"name": "John Doe", "age": 26}
    )

    assert updated.id == record.id
    assert updated.last_modified_at is not None


def test_save_and_retrieve_draft(db, test_template, test_user):
    """Test draft save and retrieval"""
    service = RecordService(db)

    # Save draft
    values = {"name": "Draft", "age": 30}
    draft = service.save_draft(test_template.id, test_user.id, values)

    assert draft.id is not None

    # Retrieve draft
    retrieved = service.get_draft(test_template.id, test_user.id)
    assert retrieved is not None
    assert retrieved["draft_data"] == values


# ============================================================================
# WORKFLOW SERVICE TESTS
# ============================================================================

def test_submit_record(db, test_template, test_user):
    """Test record submission"""
    record_service = RecordService(db)
    workflow_service = WorkflowService(db)

    # Create record
    record = record_service.create_record(
        test_template.id,
        test_user.id,
        {"name": "Test", "age": 25}
    )

    # Submit
    success, message = workflow_service.submit_record(record.id, test_user.id)

    assert success
    assert record.status.value == "submitted"


def test_workflow_permissions(db, test_template, test_user):
    """Test workflow permission checks"""
    record_service = RecordService(db)
    workflow_service = WorkflowService(db)

    # Create another user
    other_user = User(
        username="otheruser",
        email="other@example.com",
        hashed_password="hashed",
        full_name="Other User"
    )
    db.add(other_user)
    db.commit()

    # Create record as test_user
    record = record_service.create_record(
        test_template.id,
        test_user.id,
        {"name": "Test", "age": 25}
    )

    # Other user tries to submit
    can_submit, msg = workflow_service.check_workflow_permissions(
        record.id,
        other_user.id,
        "submit"
    )

    assert not can_submit


def test_workflow_history(db, test_template, test_user):
    """Test workflow history tracking"""
    record_service = RecordService(db)
    workflow_service = WorkflowService(db)

    record = record_service.create_record(
        test_template.id,
        test_user.id,
        {"name": "Test", "age": 25}
    )

    # Submit
    workflow_service.submit_record(record.id, test_user.id, "Initial submission")

    # Get history
    history = workflow_service.get_workflow_history(record.id)

    assert len(history) > 0
    assert history[0]["action"] == "submit"
    assert history[0]["comments"] == "Initial submission"


def test_add_and_resolve_comment(db, test_template, test_user):
    """Test comment functionality"""
    record_service = RecordService(db)
    workflow_service = WorkflowService(db)

    record = record_service.create_record(
        test_template.id,
        test_user.id,
        {"name": "Test", "age": 25}
    )

    # Add comment
    comment = workflow_service.add_comment(
        record.id,
        test_user.id,
        "Please verify the age"
    )

    assert comment.id is not None
    assert not comment.is_resolved

    # Resolve comment
    success, msg = workflow_service.resolve_comment(comment.id, test_user.id)
    assert success

    db.refresh(comment)
    assert comment.is_resolved


# ============================================================================
# NOTIFICATION SERVICE TESTS
# ============================================================================

def test_notification_creation(db, test_template, test_user):
    """Test notification creation"""
    record_service = RecordService(db)
    workflow_service = WorkflowService(db)
    notification_service = NotificationService(db)

    # Create and submit record
    record = record_service.create_record(
        test_template.id,
        test_user.id,
        {"name": "Test", "age": 25}
    )

    # Create another user as checker
    checker = User(
        username="checker",
        email="checker@example.com",
        hashed_password="hashed",
        full_name="Checker User"
    )
    db.add(checker)
    db.commit()

    # Update record with checker
    record.checker_id = checker.id
    db.commit()

    # Submit and notify
    workflow_service.submit_record(record.id, test_user.id)
    notification_service.notify_submission(record.id)

    # Check notifications
    notifications = notification_service.get_user_notifications(checker.id)
    assert len(notifications) > 0


def test_mark_notification_read(db, test_user):
    """Test marking notification as read"""
    notification_service = NotificationService(db)

    from backend.models import Notification

    # Create notification
    notif = Notification(
        user_id=test_user.id,
        title="Test",
        message="Test notification",
        notification_type="info",
        category="test"
    )
    db.add(notif)
    db.commit()

    # Mark as read
    success = notification_service.mark_as_read(notif.id, test_user.id)
    assert success

    db.refresh(notif)
    assert notif.is_read


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
