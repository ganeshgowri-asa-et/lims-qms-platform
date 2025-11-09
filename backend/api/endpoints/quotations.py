"""
Quotation Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core import get_db
from backend.models.workflow import Quotation
from backend.api.dependencies.auth import get_current_user
from backend.models.user import User
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date, datetime

router = APIRouter()


class QuotationCreate(BaseModel):
    lead_id: Optional[int] = None
    customer_id: Optional[int] = None
    quotation_date: date
    valid_until: Optional[date] = None
    items: List[Dict[str, Any]]
    subtotal: float
    tax_rate: Optional[float] = None
    tax_amount: Optional[float] = None
    discount: Optional[float] = None
    total_amount: float
    currency: str = "INR"
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    warranty_terms: Optional[str] = None
    notes: Optional[str] = None


class QuotationResponse(BaseModel):
    id: int
    quotation_number: str
    quotation_date: date
    status: str
    total_amount: float
    currency: str

    class Config:
        from_attributes = True


@router.post("/", response_model=QuotationResponse)
async def create_quotation(
    quotation: QuotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new quotation"""
    year = datetime.now().year
    count = db.query(Quotation).count() + 1
    quotation_number = f"QT-{year}-{count:05d}"

    new_quotation = Quotation(
        quotation_number=quotation_number,
        lead_id=quotation.lead_id,
        customer_id=quotation.customer_id,
        quotation_date=quotation.quotation_date,
        valid_until=quotation.valid_until,
        items=quotation.items,
        subtotal=quotation.subtotal,
        tax_rate=quotation.tax_rate,
        tax_amount=quotation.tax_amount,
        discount=quotation.discount,
        total_amount=quotation.total_amount,
        currency=quotation.currency,
        payment_terms=quotation.payment_terms,
        delivery_terms=quotation.delivery_terms,
        warranty_terms=quotation.warranty_terms,
        notes=quotation.notes,
        prepared_by_id=current_user.id,
        status="draft",
        created_by_id=current_user.id
    )

    db.add(new_quotation)
    db.commit()
    db.refresh(new_quotation)

    return new_quotation


@router.get("/", response_model=List[QuotationResponse])
async def list_quotations(
    lead_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List quotations"""
    query = db.query(Quotation).filter(Quotation.is_deleted == False)

    if lead_id:
        query = query.filter(Quotation.lead_id == lead_id)

    if customer_id:
        query = query.filter(Quotation.customer_id == customer_id)

    if status:
        query = query.filter(Quotation.status == status)

    quotations = query.offset(skip).limit(limit).all()
    return quotations


@router.put("/{quotation_id}/status")
async def update_quotation_status(
    quotation_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update quotation status"""
    quotation = db.query(Quotation).filter(
        Quotation.id == quotation_id,
        Quotation.is_deleted == False
    ).first()

    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found"
        )

    quotation.status = new_status

    if new_status == "sent":
        quotation.sent_date = datetime.now().date()
    elif new_status == "accepted":
        quotation.accepted_date = datetime.now().date()

    quotation.updated_by_id = current_user.id

    db.commit()

    return {"message": "Quotation status updated successfully"}


@router.post("/{quotation_id}/convert-to-order")
async def convert_quotation_to_order(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Convert quotation to customer order"""
    from backend.models.crm import Order, OrderStatusEnum

    quotation = db.query(Quotation).filter(
        Quotation.id == quotation_id,
        Quotation.is_deleted == False
    ).first()

    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found"
        )

    if quotation.status != "accepted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only accepted quotations can be converted to orders"
        )

    # Create order
    year = datetime.now().year
    count = db.query(Order).count() + 1
    order_number = f"ORD-{year}-{count:05d}"

    order = Order(
        order_number=order_number,
        customer_id=quotation.customer_id,
        order_date=datetime.now().date(),
        items=quotation.items,
        subtotal=quotation.subtotal,
        tax_amount=quotation.tax_amount,
        discount=quotation.discount,
        total_amount=quotation.total_amount,
        currency=quotation.currency,
        status=OrderStatusEnum.CONFIRMED,
        assigned_to_id=current_user.id,
        created_by_id=current_user.id
    )

    db.add(order)

    # Update quotation
    quotation.converted_to_order_id = order.id
    quotation.updated_by_id = current_user.id

    db.commit()
    db.refresh(order)

    return {
        "message": "Quotation converted to order successfully",
        "order_id": order.id,
        "order_number": order.order_number
    }
