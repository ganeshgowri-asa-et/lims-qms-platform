"""
Financial Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core import get_db
from backend.models.financial import Expense, Invoice, Payment, ExpenseStatusEnum, InvoiceTypeEnum
from backend.api.dependencies.auth import get_current_user
from backend.models.user import User
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

router = APIRouter()


class ExpenseCreate(BaseModel):
    expense_date: date
    category: str
    description: str
    amount: float
    project_id: Optional[int] = None


class InvoiceCreate(BaseModel):
    invoice_type: InvoiceTypeEnum
    customer_id: int
    items: List[dict]
    subtotal: float
    total_amount: float


@router.post("/expenses", response_model=dict)
async def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create expense record"""
    year = datetime.now().year
    count = db.query(Expense).count() + 1
    expense_number = f"EXP-{year}-{count:04d}"

    # Get employee record
    from backend.models.hr import Employee
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()

    new_expense = Expense(
        expense_number=expense_number,
        employee_id=employee.id if employee else None,
        expense_date=expense.expense_date,
        category=expense.category,
        description=expense.description,
        amount=expense.amount,
        project_id=expense.project_id,
        status=ExpenseStatusEnum.DRAFT,
        created_by_id=current_user.id
    )

    db.add(new_expense)
    db.commit()

    return {
        "message": "Expense created successfully",
        "expense_number": expense_number
    }


@router.get("/expenses", response_model=List[dict])
async def list_expenses(
    status: Optional[ExpenseStatusEnum] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List expenses"""
    query = db.query(Expense).filter(Expense.is_deleted == False)

    if status:
        query = query.filter(Expense.status == status)

    expenses = query.offset(skip).limit(limit).all()

    return [
        {
            "id": e.id,
            "expense_number": e.expense_number,
            "category": e.category,
            "amount": e.amount,
            "status": e.status.value,
            "expense_date": str(e.expense_date)
        }
        for e in expenses
    ]


@router.post("/invoices", response_model=dict)
async def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create customer invoice"""
    year = datetime.now().year
    count = db.query(Invoice).count() + 1
    invoice_number = f"INV-{year}-{count:04d}"

    # Get customer details
    from backend.models.crm import Customer
    customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    new_invoice = Invoice(
        invoice_number=invoice_number,
        invoice_type=invoice.invoice_type,
        invoice_date=date.today(),
        customer_id=invoice.customer_id,
        bill_to_name=customer.company_name,
        bill_to_address=customer.billing_address,
        bill_to_gst=customer.gst_number,
        items=invoice.items,
        subtotal=invoice.subtotal,
        total_amount=invoice.total_amount,
        generated_by_id=current_user.id,
        created_by_id=current_user.id
    )

    db.add(new_invoice)
    db.commit()

    return {
        "message": "Invoice created successfully",
        "invoice_number": invoice_number
    }
