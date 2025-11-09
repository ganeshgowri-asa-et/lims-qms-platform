"""Pydantic schemas for request/response validation."""
from .documents import (
    QMSDocumentCreate,
    QMSDocumentUpdate,
    QMSDocumentResponse,
    DocumentRevisionCreate,
    DocumentRevisionResponse,
)
from .equipment import (
    EquipmentMasterCreate,
    EquipmentMasterUpdate,
    EquipmentMasterResponse,
    CalibrationRecordCreate,
    CalibrationRecordResponse,
    MaintenanceScheduleCreate,
    MaintenanceScheduleResponse,
)

__all__ = [
    "QMSDocumentCreate",
    "QMSDocumentUpdate",
    "QMSDocumentResponse",
    "DocumentRevisionCreate",
    "DocumentRevisionResponse",
    "EquipmentMasterCreate",
    "EquipmentMasterUpdate",
    "EquipmentMasterResponse",
    "CalibrationRecordCreate",
    "CalibrationRecordResponse",
    "MaintenanceScheduleCreate",
    "MaintenanceScheduleResponse",
]
