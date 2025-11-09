"""
CRM API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core import get_db
from backend.models.crm import Lead, Customer, Order, LeadStatusEnum, OrderStatusEnum
from backend.api.dependencies.auth import get_current_user
from backend.models.user import User
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

router = APIRouter()


class LeadCreate(BaseModel):
    company_name: Optional[str] = None
    contact_person: str
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None


class CustomerCreate(BaseModel):
    company_name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gst_number: Optional[str] = None


@router.post("/leads", response_model=dict)
async def create_lead(
    lead: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new lead"""
    year = datetime.now().year
    count = db.query(Lead).count() + 1
    lead_number = f"LEAD-{year}-{count:04d}"

    new_lead = Lead(
        lead_number=lead_number,
        company_name=lead.company_name,
        contact_person=lead.contact_person,
        email=lead.email,
        phone=lead.phone,
        source=lead.source,
        status=LeadStatusEnum.NEW,
        assigned_to_id=current_user.id,
        created_by_id=current_user.id
    )

    db.add(new_lead)
    db.commit()

    return {
        "message": "Lead created successfully",
        "lead_number": lead_number
    }


@router.get("/leads", response_model=List[dict])
async def list_leads(
    status: Optional[LeadStatusEnum] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List leads"""
    query = db.query(Lead).filter(Lead.is_deleted == False)

    if status:
        query = query.filter(Lead.status == status)

    leads = query.offset(skip).limit(limit).all()

    return [
        {
            "id": l.id,
            "lead_number": l.lead_number,
            "company_name": l.company_name,
            "contact_person": l.contact_person,
            "status": l.status.value
        }
        for l in leads
    ]


@router.post("/customers", response_model=dict)
async def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new customer"""
    year = datetime.now().year
    count = db.query(Customer).count() + 1
    customer_code = f"CUST-{year}-{count:04d}"

    new_customer = Customer(
        customer_code=customer_code,
        company_name=customer.company_name,
        contact_person=customer.contact_person,
        email=customer.email,
        phone=customer.phone,
        gst_number=customer.gst_number,
        account_manager_id=current_user.id,
        created_by_id=current_user.id
    )

    db.add(new_customer)
    db.commit()

    return {
        "message": "Customer created successfully",
        "customer_code": customer_code
    }


@router.get("/customers", response_model=List[dict])
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List customers"""
    customers = db.query(Customer).filter(
        Customer.is_deleted == False
    ).offset(skip).limit(limit).all()

    return [
        {
            "id": c.id,
            "customer_code": c.customer_code,
            "company_name": c.company_name,
            "contact_person": c.contact_person,
            "email": c.email
        }
        for c in customers
    ]
