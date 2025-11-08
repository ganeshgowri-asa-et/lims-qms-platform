"""
Calibration management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import base64

from app.core.database import get_db
from app.models.base import User
from app.models.calibration import CalibrationMaster, CalibrationRecord
from app.schemas.calibration import (
    CalibrationVendorCreate,
    CalibrationVendorUpdate,
    CalibrationVendorResponse,
    CalibrationRecordCreate,
    CalibrationRecordUpdate,
    CalibrationRecordResponse,
    CalibrationRecordListResponse,
    CalibrationDueListResponse,
    CalibrationCertificateUpload,
)
from app.services.calibration_service import CalibrationService
from app.services.ocr_service import OCRService
from app.services.workflow_service import WorkflowService
from app.api.dependencies.auth import get_current_active_user
from app.schemas.workflow import WorkflowSubmit, WorkflowCheck, WorkflowApprove

router = APIRouter()


# Vendor Management
@router.post("/vendors", response_model=CalibrationVendorResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    vendor: CalibrationVendorCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create calibration vendor"""
    # Check if vendor name exists
    result = await db.execute(
        select(CalibrationMaster).where(CalibrationMaster.vendor_name == vendor.vendor_name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vendor name already exists",
        )

    db_vendor = CalibrationMaster(**vendor.model_dump(), created_by_id=current_user.id)

    db.add(db_vendor)
    await db.commit()
    await db.refresh(db_vendor)

    return db_vendor


@router.get("/vendors", response_model=List[CalibrationVendorResponse])
async def list_vendors(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List calibration vendors"""
    query = select(CalibrationMaster).offset(skip).limit(limit)

    if active_only:
        query = query.where(CalibrationMaster.is_active == True)

    result = await db.execute(query)
    vendors = result.scalars().all()

    return vendors


@router.put("/vendors/{vendor_id}", response_model=CalibrationVendorResponse)
async def update_vendor(
    vendor_id: int,
    vendor_update: CalibrationVendorUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update calibration vendor"""
    result = await db.execute(
        select(CalibrationMaster).where(CalibrationMaster.id == vendor_id)
    )
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found"
        )

    update_data = vendor_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vendor, field, value)

    await db.commit()
    await db.refresh(vendor)

    return vendor


# Calibration Records
@router.post("/records", response_model=CalibrationRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_calibration_record(
    calibration: CalibrationRecordCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create calibration record"""
    db_calibration = await CalibrationService.create_calibration_record(
        db, calibration, current_user.id
    )

    # Create workflow for calibration record
    workflow = await WorkflowService.create_workflow(
        db, "calibration_records", db_calibration.id, current_user.id
    )

    db_calibration.workflow_id = workflow.id
    await db.commit()
    await db.refresh(db_calibration)

    # Update vendor performance if external calibration
    if db_calibration.vendor_id:
        await CalibrationService.update_vendor_performance(
            db, db_calibration.vendor_id, db_calibration
        )

    return db_calibration


@router.get("/records", response_model=CalibrationRecordListResponse)
async def list_calibration_records(
    skip: int = 0,
    limit: int = 100,
    equipment_id: Optional[int] = None,
    vendor_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List calibration records"""
    query = select(CalibrationRecord).offset(skip).limit(limit)

    if equipment_id:
        query = query.where(CalibrationRecord.equipment_id == equipment_id)
    if vendor_id:
        query = query.where(CalibrationRecord.vendor_id == vendor_id)

    # Get total count
    from sqlalchemy import func
    count_query = select(func.count(CalibrationRecord.id))
    if equipment_id:
        count_query = count_query.where(CalibrationRecord.equipment_id == equipment_id)
    if vendor_id:
        count_query = count_query.where(CalibrationRecord.vendor_id == vendor_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    result = await db.execute(query.order_by(CalibrationRecord.created_at.desc()))
    records = result.scalars().all()

    return {
        "items": records,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit,
    }


@router.get("/records/{calibration_id}", response_model=CalibrationRecordResponse)
async def get_calibration_record(
    calibration_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get calibration record by ID"""
    result = await db.execute(
        select(CalibrationRecord).where(CalibrationRecord.id == calibration_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Calibration record not found"
        )

    return record


@router.put("/records/{calibration_id}", response_model=CalibrationRecordResponse)
async def update_calibration_record(
    calibration_id: int,
    calibration_update: CalibrationRecordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update calibration record"""
    result = await db.execute(
        select(CalibrationRecord).where(CalibrationRecord.id == calibration_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Calibration record not found"
        )

    update_data = calibration_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)

    await db.commit()
    await db.refresh(record)

    return record


# Calibration Due Alerts
@router.get("/due", response_model=List[CalibrationDueListResponse])
async def get_calibrations_due(
    days_ahead: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get calibrations due within specified days"""
    due_list = await CalibrationService.get_calibrations_due(db, days_ahead)
    return due_list


@router.get("/overdue", response_model=List[CalibrationDueListResponse])
async def get_overdue_calibrations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get overdue calibrations"""
    overdue_list = await CalibrationService.get_overdue_calibrations(db)
    return overdue_list


# Certificate Upload and OCR
@router.post("/records/{calibration_id}/certificate/upload")
async def upload_calibration_certificate(
    calibration_id: int,
    file: UploadFile = File(...),
    extract_data: bool = True,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload calibration certificate with OCR extraction"""
    # Get calibration record
    result = await db.execute(
        select(CalibrationRecord).where(CalibrationRecord.id == calibration_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Calibration record not found"
        )

    # Read file content
    file_content = await file.read()
    file_content_b64 = base64.b64encode(file_content).decode()

    # Save file (in production, save to cloud storage)
    import os
    from app.core.config import settings

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(
        settings.UPLOAD_DIR, f"calibration_{calibration_id}_{file.filename}"
    )

    with open(file_path, "wb") as f:
        f.write(file_content)

    record.certificate_file_path = file_path

    # Extract data using OCR
    extracted_data = {}
    if extract_data:
        extracted_data = OCRService.extract_calibration_data(
            file_content_b64, file.filename
        )
        record.certificate_data = extracted_data

        # Update certificate number if extracted
        if extracted_data.get("certificate_number"):
            record.certificate_number = extracted_data["certificate_number"]

    await db.commit()
    await db.refresh(record)

    return {
        "message": "Certificate uploaded successfully",
        "file_path": file_path,
        "extracted_data": extracted_data if extract_data else None,
    }


# Workflow operations
@router.post("/records/{calibration_id}/submit")
async def submit_calibration_for_checking(
    calibration_id: int,
    submit_data: WorkflowSubmit,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit calibration record for checking"""
    result = await db.execute(
        select(CalibrationRecord).where(CalibrationRecord.id == calibration_id)
    )
    record = result.scalar_one_or_none()

    if not record or not record.workflow_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Calibration record or workflow not found"
        )

    workflow = await WorkflowService.submit_for_checking(
        db,
        record.workflow_id,
        current_user.id,
        submit_data.comments,
        submit_data.signature_data,
    )

    return {"message": "Calibration submitted for checking", "workflow_status": workflow.status}


@router.post("/records/{calibration_id}/check")
async def check_calibration(
    calibration_id: int,
    check_data: WorkflowCheck,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Checker reviews calibration record"""
    result = await db.execute(
        select(CalibrationRecord).where(CalibrationRecord.id == calibration_id)
    )
    record = result.scalar_one_or_none()

    if not record or not record.workflow_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Calibration record or workflow not found"
        )

    workflow = await WorkflowService.check_record(
        db,
        record.workflow_id,
        current_user.id,
        check_data.approved,
        check_data.comments,
        check_data.signature_data,
    )

    return {"message": "Calibration checked", "workflow_status": workflow.status}


@router.post("/records/{calibration_id}/approve")
async def approve_calibration(
    calibration_id: int,
    approve_data: WorkflowApprove,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Approver gives final approval to calibration record"""
    result = await db.execute(
        select(CalibrationRecord).where(CalibrationRecord.id == calibration_id)
    )
    record = result.scalar_one_or_none()

    if not record or not record.workflow_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Calibration record or workflow not found"
        )

    workflow = await WorkflowService.approve_record(
        db,
        record.workflow_id,
        current_user.id,
        approve_data.approved,
        approve_data.comments,
        approve_data.signature_data,
    )

    return {"message": "Calibration approval processed", "workflow_status": workflow.status}
