"""
Import all models for Alembic to detect
"""
from app.models.base import (
    User,
    AuditLog,
    DocumentReference,
    WorkflowRecord,
    WorkflowStatus,
    UserRole,
)
from app.models.equipment import (
    EquipmentMaster,
    EquipmentSpecification,
    EquipmentHistoryCard,
    EquipmentUtilization,
    EquipmentStatus,
    EquipmentCategory,
    CalibrationFrequency,
)
from app.models.calibration import (
    CalibrationMaster,
    CalibrationRecord,
    CalibrationSchedule,
    CalibrationType,
    CalibrationResult,
)
from app.models.maintenance import (
    PreventiveMaintenanceSchedule,
    MaintenanceRecord,
    EquipmentFailureLog,
    MaintenanceType,
    MaintenancePriority,
    MaintenanceStatus,
)

__all__ = [
    # Base models
    "User",
    "AuditLog",
    "DocumentReference",
    "WorkflowRecord",
    "WorkflowStatus",
    "UserRole",
    # Equipment models
    "EquipmentMaster",
    "EquipmentSpecification",
    "EquipmentHistoryCard",
    "EquipmentUtilization",
    "EquipmentStatus",
    "EquipmentCategory",
    "CalibrationFrequency",
    # Calibration models
    "CalibrationMaster",
    "CalibrationRecord",
    "CalibrationSchedule",
    "CalibrationType",
    "CalibrationResult",
    # Maintenance models
    "PreventiveMaintenanceSchedule",
    "MaintenanceRecord",
    "EquipmentFailureLog",
    "MaintenanceType",
    "MaintenancePriority",
    "MaintenanceStatus",
]
