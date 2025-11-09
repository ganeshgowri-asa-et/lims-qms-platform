"""
HR Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core import get_db
from backend.models.hr import Employee, Leave, Training, LeaveTypeEnum
from backend.api.dependencies.auth import get_current_user
from backend.models.user import User
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

router = APIRouter()


class LeaveRequest(BaseModel):
    leave_type: LeaveTypeEnum
    start_date: date
    end_date: date
    num_days: float
    reason: Optional[str] = None


class LeaveResponse(BaseModel):
    id: int
    leave_type: str
    start_date: date
    end_date: date
    num_days: float
    status: str

    class Config:
        from_attributes = True


@router.post("/leave", response_model=dict)
async def request_leave(
    leave: LeaveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit leave request"""
    # Get employee record
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee record not found"
        )

    new_leave = Leave(
        employee_id=employee.id,
        leave_type=leave.leave_type,
        start_date=leave.start_date,
        end_date=leave.end_date,
        num_days=leave.num_days,
        reason=leave.reason,
        status='pending',
        created_by_id=current_user.id
    )

    db.add(new_leave)
    db.commit()

    return {"message": "Leave request submitted successfully"}


@router.get("/leave", response_model=List[LeaveResponse])
async def list_leaves(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List leave requests"""
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()

    if not employee:
        return []

    query = db.query(Leave).filter(Leave.employee_id == employee.id)

    if status:
        query = query.filter(Leave.status == status)

    leaves = query.offset(skip).limit(limit).all()
    return leaves


@router.put("/leave/{leave_id}/approve")
async def approve_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve leave request"""
    leave = db.query(Leave).filter(Leave.id == leave_id).first()

    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )

    leave.status = 'approved'
    leave.approver_id = current_user.id
    leave.approved_at = str(date.today())

    db.commit()

    return {"message": "Leave approved successfully"}
